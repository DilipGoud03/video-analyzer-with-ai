from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
from dotenv import load_dotenv
import os
import mimetypes

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD0D5lO9oajtO-THvXKpMQy902QL8zGgFU"


# Define the State

class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


class MainState(TypedDict):
    video_path: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]


# Define the Nodes
def upload_video(state: MainState):
    path = state["video_path"]
    try:
        mime_type, _ = mimetypes.guess_type(path) if path else "video/mp4"
        video_bytes = open(path, "rb").read()

        uploaded_file = {
            "mime_type": mime_type,
            "data": video_bytes
        }

        return {"uploaded_file": uploaded_file}
    except Exception as e:
        print(f"Error loading video: {e}")
        raise


def summarize_video(state: MainState):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    uploaded_file = state["uploaded_file"]
    prompt = "Generate a summary for this video."
    response = genai.GenerativeModel(
        "gemini-2.0-flash").generate_content([uploaded_file, prompt])
    return {"summary": response.text}


# Build the Pipline

pipline = StateGraph(MainState)

pipline.add_node("upload_video", upload_video)
pipline.add_node("summarize_video", summarize_video)

pipline.add_edge(START, "upload_video")
pipline.add_edge("upload_video", "summarize_video")
pipline.add_edge("summarize_video", END)

app = pipline.compile()
