from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from decouple import config
import os
import mimetypes
import base64

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.vector_store_service import VectorStoreService
from services.llm_service import LLMService
from uuid import uuid4

# ------------------------------------------------------------
# Global Initializations
# ------------------------------------------------------------
# Initializes the vector store service and chat model for use
# throughout the LangGraph workflow. This allows persistence
# of summaries and intelligent responses using embeddings.
# ------------------------------------------------------------
vector_service = VectorStoreService()
llm = LLMService().get_chat_model()


# ------------------------------------------------------------
# TypedDict: UploadedFile
# Description:
#   Represents an uploaded video file, including its MIME type
#   and raw binary data for model input.
# ------------------------------------------------------------
class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


# ------------------------------------------------------------
# TypedDict: MainState
# Description:
#   Defines the shared state for the LangGraph workflow.
#   Stores input video, model-generated summary, and
#   question-answer pairs for the interactive session.
# ------------------------------------------------------------
class MainState(TypedDict):
    video_path: Optional[str]
    video_name: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    is_new_video: bool
    prompt: Optional[str]
    question: Optional[str]
    answer: Optional[str]


# ------------------------------------------------------------
# Function: upload_video
# Description:
#   Loads a video file from the given path, verifies its
#   existence, detects MIME type, and converts the video
#   into binary data for further processing.
# ------------------------------------------------------------
def upload_video(state: MainState):
    path = state.get("video_path")
    if not path or not os.path.exists(path):
        raise FileNotFoundError("Video path not provided or invalid")

    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "video/mp4"

    with open(path, "rb") as f:
        video_bytes = f.read()

    return {"uploaded_file": {"mime_type": mime_type, "data": video_bytes}}


# ------------------------------------------------------------
# Function: summarize_video
# Description:
#   Sends the uploaded video to the Gemini model for analysis
#   and generates a natural, human-readable summary describing
#   scenes, actions, and emotions without introductory phrases.
# ------------------------------------------------------------
def summarize_video(state: MainState):
    uploaded_file = state["uploaded_file"]
    prompt = """
        Provide a detailed and comprehensive description of this video. 
        Your response must be in a natural human-readable format describing 
        what happens in the video, including scenes, actions, objects, and emotions. 
        Do not include any meta phrases like 'Here is the summary' — start directly.
    """

    if 'prompt' in state and state['prompt'] != '':
        prompt = f"{state['prompt']} Avoid adding introductory phrases like 'Here is the summary' or 'Okay, here’s the explanation'. Start directly with the summary content."

    encoded_video = base64.b64encode(uploaded_file["data"]).decode("utf-8")
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "media", "data": encoded_video, "mime_type": uploaded_file["mime_type"]},
        ]
    )

    response = llm.invoke([message])
    return {"summary": response.content}


# ------------------------------------------------------------
# Function: store_summary_in_db
# Description:
#   Persists the generated video summary into the Chroma vector
#   database for future semantic retrieval and question-answering.
#   Skips storage if not marked as a new video.
# ------------------------------------------------------------
def store_summary_in_db(state: MainState):
    vector_db = vector_service.vector_db()
    if state.get("is_new_video") and state["is_new_video"] is True:
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=200,
                chunk_overlap=50,
                length_function=len,  # Measure by characters
                separators=["\n\n", "\n", " ", ""]
            )
            # Create chunks with metadata
            chunks = text_splitter.split_text(state["summary"])
            documents = []
            if chunks and len(chunks) > 0:
                for chunk in chunks:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={"source": state["video_name"]}
                        )
                    )
            if len(documents) > 0:
                uuids = [str(uuid4()) for _ in range(len(documents))]
                vector_db.add_documents(documents=documents, ids=uuids)
            return {}
        except Exception as e:
            print(f"Error saving summary: {e}")
    return {}


# ------------------------------------------------------------
# Function: ask_question
# Description:
#   Retrieves stored summaries from the vector DB and uses a
#   retrieval-augmented generation (RAG) chain to answer user
#   questions based on the video content.
# ------------------------------------------------------------
def ask_question(state: MainState):
    vector_service.get_documents()
    question = state.get("question")
    video_name = state.get("video_name")

    if not question:
        return {"answer": "No question provided."}

    vector_db = vector_service.vector_db()
    filter_query = {"source": video_name}
    retriever = vector_db.as_retriever(search_kwargs={'filter': filter_query})

    rag_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an intelligent AI assistant. Use the following context to answer the question directly and clearly. "
         "Do not say things like 'Based on the provided text' or 'According to the context'.\n\n"
         "Context:\n{context}"),
        ("human", "{input}")
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, rag_prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    result = retrieval_chain.invoke({"input": question})
    return {"answer": result["answer"]}


# ------------------------------------------------------------
# Function: route_start
# Description:
#   Determines which node in the workflow to start from based
#   on the user's input type — a question or a new video upload.
# ------------------------------------------------------------
def route_start(state: MainState) -> str:
    if state.get("question") and state['question'] != '':
        return "ask_question"
    return "upload_video"


# ------------------------------------------------------------
# Workflow Definition: LangGraph Pipeline
# Description:
#   Builds the complete LangGraph workflow for processing videos,
#   summarizing content, storing results, and answering questions.
# ------------------------------------------------------------
pipeline = StateGraph(MainState)

# --- Define workflow nodes ---
pipeline.add_node("upload_video", upload_video)
pipeline.add_node("summarize_video", summarize_video)
pipeline.add_node("store_summary_in_db", store_summary_in_db)
pipeline.add_node("ask_question", ask_question)

# --- Define conditional and sequential transitions ---
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
pipeline.add_edge("ask_question", END)


# ------------------------------------------------------------
# Function: run
# Description:
#   Compiles and returns the LangGraph pipeline. If the process
#   involves question-answering, a MemorySaver checkpoint is used
#   to maintain conversational context across interactions.
# ------------------------------------------------------------
def run(is_questioning: bool = False):
    if is_questioning:
        checkpointer = MemorySaver()
        return pipeline.compile(checkpointer=checkpointer)
    else:
        return pipeline.compile()
