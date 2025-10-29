from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
from decouple import config
import os
import mimetypes
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain.schema import Document

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

class VectorStoreService:
    def __init__(self):
        os.makedirs(str(config("VECTOR_DB_DIR")), exist_ok=True)
        self.__embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )

    def vector_db(self):
        vector_store = Chroma(
            collection_name="video_summaries",
            embedding_function=self.__embeddings,
            persist_directory=str(config("VECTOR_DB_DIR")),
        )
        return vector_store


class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


class MainState(TypedDict):
    video_path: str
    video_name: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    is_new_video: bool
    prompt: Optional[str]
    question: Optional[str]
    answer: Optional[str]


# Define the Nodes
def upload_video(state: MainState):
    path = state["video_path"]
    try:
        mime_type, _ = mimetypes.guess_type(path)
        video_bytes = open(path, "rb").read()

        uploaded_file = {
            "mime_type": mime_type if mime_type else "video/mp4",
            "data": video_bytes,
        }

        return {"uploaded_file": uploaded_file}
    except Exception as e:
        print(f"Error loading video: {e}")
        raise


def summarize_video(state: MainState):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    uploaded_file = state["uploaded_file"]

    prompt = "Provide a detailed and comprehensive description of this video. Your response must be in a natural human-readable format describing what happens in the video, including scenes, actions, objects, and emotions if visible. Do not include any introductory or meta phrases such as 'Okay, here is a detailed description of the video' or similar. Start directly with the description."
    
    if 'prompt' in state and state['prompt'] != '':
        prompt = f"{state['prompt']} Avoid adding introductory phrases like 'Here is the summary' or 'Okay, here’s the explanation'. Start directly with the summary content."

    response = genai.GenerativeModel(
        "gemini-2.0-flash").generate_content([uploaded_file, prompt])
    return {"summary": response.text}


def store_summary_in_db(state: MainState):
    if state.get("is_new_video") and state.get("summary"):
        try:
            print(f"Storing summary for {state['video_name']} into Chroma DB...")
            vector_service = VectorStoreService()
            vector_db = vector_service.vector_db()

            document = Document(
                page_content=state["summary"],
                metadata={"video_name": state["video_name"], "path": state["video_path"]},
            )
            vector_db.add_documents([document])
            print("Summary successfully stored in Chroma.")
        except Exception as e:
            print(f"Error saving summary: {e}")
    return {}


def ask_question(state: MainState):
    question = state.get("question")
    video_name = state.get("video_name")

    if not question:
        print("No question provided.")
        return {}

    try:
        vector_service = VectorStoreService()
        vector_db = vector_service.vector_db()

        filter_query = {"video_name": video_name} if video_name else None

        docs = vector_db.similarity_search(
            question, 
            k=3,
            filter=filter_query
        )

        context = "\n\n".join([d.page_content for d in docs])
        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer briefly and accurately based on the context."

        print(f"Running QA for video '{video_name}' using Gemini...")
        response = model.invoke(prompt)

        return {
            "answer": getattr(response, "content", str(response))
        }

    except Exception as e:
        return {"answer": "Error processing the question."}



pipeline = StateGraph(MainState)

pipeline.add_node("upload_video", upload_video)
pipeline.add_node("summarize_video", summarize_video)
pipeline.add_node("store_summary_in_db", store_summary_in_db)
pipeline.add_node("ask_question", ask_question)

# Define flow
pipeline.add_edge(START, "upload_video")
pipeline.add_edge("upload_video", "summarize_video")
pipeline.add_edge("summarize_video", "store_summary_in_db")
pipeline.add_edge("store_summary_in_db", "ask_question")
pipeline.add_edge("ask_question", END)

app = pipeline.compile()