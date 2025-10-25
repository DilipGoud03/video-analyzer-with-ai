from typing import TypedDict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
import mimetypes
import base64

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
    uploaded = state.get("uploaded_file")
    if not uploaded:
        raise ValueError("No uploaded_file found in state")

    video_bytes = uploaded.get("data")
    mime_type = uploaded.get("mime_type")

    if not video_bytes:
        raise ValueError("Uploaded file does not contain video bytes")

    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Generate a concise one-paragraph summary for this video.",
            },
            {
                "type": "file",
                "source_type": "base64",
                "mime_type": mime_type,
                "data": video_base64,
            },
            {
                "type": "video",
                "base64": video_base64,
                "mime_type": mime_type,
            },
            {
                "type": "media",
                "file_uri": "https://www.youtube.com/watch?v=9hE5-98ZeCg",
                "mime_type": "video/mp4",
            },
        ]
    )

    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    response = model.invoke([message])
    return {"summary": response.content}


# Build the Pipline

pipline = StateGraph(MainState)

pipline.add_node("upload_video", upload_video)
pipline.add_node("summarize_video", summarize_video)

pipline.set_entry_point("upload_video")
pipline.add_edge("upload_video", "summarize_video")
pipline.add_edge("summarize_video", END)

app = pipline.compile()
