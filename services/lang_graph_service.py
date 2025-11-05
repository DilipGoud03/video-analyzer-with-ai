from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from decouple import config
import os
import mimetypes
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import base64
from services.vector_store_service import VectorStoreService

# Initialize vector store service
vector_service = VectorStoreService()
llm = vector_service.llm()


# TypedDict: UploadedFile
# -----------------------
# Represents an uploaded file with MIME type and binary data.
class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


# TypedDict: MainState
# --------------------
# Defines the shared state for the LangGraph workflow.
class MainState(TypedDict):
    video_path: Optional[str]
    video_name: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    is_new_video: bool
    prompt: Optional[str]
    question: Optional[str]
    answer: Optional[str]


# Function: upload_video
# ----------------------
# Reads a video file from the given path and prepares it for processing
# by encoding it into bytes and storing metadata such as MIME type.
def upload_video(state: MainState):
    path = state.get("video_path")
    if not path or not os.path.exists(path):
        raise FileNotFoundError("Video path not provided or invalid")

    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "video/mp4"

    with open(path, "rb") as f:
        video_bytes = f.read()

    return {"uploaded_file": {"mime_type": mime_type, "data": video_bytes}}


# Function: summarize_video
# -------------------------
# Sends the uploaded video to the Gemini model to generate a detailed
# human-readable summary of the content.
def summarize_video(state: MainState):
    uploaded_file = state["uploaded_file"]
    prompt = """
            Provide a detailed and comprehensive description of this video. 
            Your response must be in a natural human-readable format describing what happens in the video, including scenes, actions, objects, and emotions if visible. 
            Do not include any introductory or meta phrases such as 'Okay, here is a detailed description of the video' or similar. Start directly with the description.
        """

    if 'prompt' in state and state['prompt'] != '':
        prompt = f"{state['prompt']} Avoid adding introductory phrases like 'Here is the summary' or 'Okay, here’s the explanation'. Start directly with the summary content."

    encoded_video = base64.b64encode(uploaded_file["data"]).decode("utf-8")
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "media", "data": encoded_video,
                "mime_type": uploaded_file["mime_type"]},
        ]
    )
    response = llm.invoke([message])
    return {"summary": response.content}


# Function: store_summary_in_db
# -----------------------------
# Stores the generated video summary in the vector database
# for future retrieval and similarity search.
def store_summary_in_db(state: MainState):
    vector_db = vector_service.vector_db()
    if state.get("is_new_video") and state["is_new_video"] == True:
        try:
            doc = Document(
                page_content=state["summary"],
                metadata={
                    "video_name": state["video_name"],
                    "path": state.get("video_path", ""),
                },
            )
            vector_db.add_documents([doc])
        except Exception as e:
            pass
            print(f"Error saving summary: {e}")
    return {}


# Function: ask_question
# ----------------------
# Answers user questions based on stored video summaries
# using context retrieval and the Gemini model.
def ask_question(state: MainState):
    question = state.get("question")
    video_name = state.get("video_name")

    if not question:
        return {"answer": "No question provided."}

    vector_db = vector_service.vector_db()
    filter_query = {"video_name": video_name}

    retriever = vector_db.as_retriever(search_kwargs={'filter': filter_query})
    rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an intelligent AI assistant. Use the following context to answer the question: {context}"),
    ("human", "{input}")
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, rag_prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
    
    # Invoke and return the answer
    result = retrieval_chain.invoke({"input": question})
    return {"answer": result["answer"]}


# Function: route_start
# ---------------------
# Determines the starting node for the graph based on
# whether the user provided a question or a video upload.
def route_start(state: MainState) -> str:
    if state.get("question"):
        return "ask_question"
    return "upload_video"


# Workflow Definition
# -------------------
# Builds and compiles the LangGraph workflow for video processing.
pipeline = StateGraph(MainState)

pipeline.add_node("upload_video", upload_video)
pipeline.add_node("summarize_video", summarize_video)
pipeline.add_node("store_summary_in_db", store_summary_in_db)
pipeline.add_node("ask_question", ask_question)

# Define graph flow logic
pipeline.add_conditional_edges(
    START,
    route_start,
    {
        "upload_video": "upload_video",
        "ask_question": "ask_question",
    },
)
pipeline.add_edge("upload_video", "summarize_video")
pipeline.add_edge("summarize_video", "store_summary_in_db")
pipeline.add_edge("store_summary_in_db", END)

pipeline.add_edge('ask_question', END)


def run(is_questioning: bool = False):
    if is_questioning:
        checkpointer = MemorySaver()
        return pipeline.compile(checkpointer=checkpointer)
    else:
        return pipeline.compile()
