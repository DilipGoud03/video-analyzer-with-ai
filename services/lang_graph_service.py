from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from decouple import config
import os
import mimetypes
from langchain_chroma import Chroma
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage
import base64


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = str(config("GOOGLE_API_KEY"))

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    max_output_tokens=None,
    timeout=None,
    max_retries=2,
)


class VectorStoreService:
    def __init__(self):
        os.makedirs(str(config("VECTOR_DB_DIR")), exist_ok=True)
        self.__embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )

    def vector_db(self):
        return Chroma(
            collection_name="video_summaries",
            embedding_function=self.__embeddings,
            persist_directory=str(config("VECTOR_DB_DIR")),
        )


class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


class MainState(TypedDict):
    video_path: Optional[str]
    video_name: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    is_new_video: bool
    prompt: Optional[str]
    question: Optional[str]
    answer: Optional[str]


def upload_video(state: MainState):
    path = state.get("video_path")
    if not path or not os.path.exists(path):
        raise FileNotFoundError("Video path not provided or invalid")

    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "video/mp4"

    with open(path, "rb") as f:
        video_bytes = f.read()

    return {"uploaded_file": {"mime_type": mime_type, "data": video_bytes}}


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
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "media",
                "data": encoded_video,
                "mime_type": uploaded_file["mime_type"]
            },
        ]
    )
    response = llm.invoke([message])
    return {"summary": response.content}


def store_summary_in_db(state: MainState):
    if state.get("is_new_video") and state["is_new_video"] == True:
        try:
            vector_service = VectorStoreService()
            vector_db = vector_service.vector_db()
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


def ask_question(state: MainState):
    question = state.get("question")
    video_name = state.get("video_name")

    if not question:
        return {"answer": "No question provided."}

    vector_service = VectorStoreService()
    vector_db = vector_service.vector_db()

    filter_query = {"video_name": video_name} if video_name else None
    docs = vector_db.similarity_search(question, k=3, filter=filter_query)

    if not docs:
        return {"answer": f"No stored summary found for video '{video_name}'. Please summarize first."}

    context = "\n---\n".join([doc.page_content for doc in docs])
    prompt = (
        f"The following are summaries of a video:\n{context}\n\n"
        f"Based on this information, answer the question:\n{question}\n\n"
        "Give a precise and factual answer."
    )

    response = llm.invoke(prompt)
    return {"answer": getattr(response, "content", str(response))}


def route_start(state: MainState) -> str:
    if state.get("question"):
        return "ask_question"
    return "upload_video"


pipeline = StateGraph(MainState)

pipeline.add_node("upload_video", upload_video)
pipeline.add_node("summarize_video", summarize_video)
pipeline.add_node("store_summary_in_db", store_summary_in_db)
pipeline.add_node("ask_question", ask_question)

# Define flow
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

app = pipeline.compile()
