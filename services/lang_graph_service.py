from typing import TypedDict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
import mimetypes
import base64
import google.generativeai as genai
import time

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD0D5lO9oajtO-THvXKpMQy902QL8zGgFU"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# Define the State


class UploadedFile(TypedDict):
    path: str
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
            'path': path,
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
    path = uploaded.get("path")

    # if not video_bytes:
    #     raise ValueError("Uploaded file does not contain video bytes")

    # video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    video_file = genai.upload_file(path=path)

    # Wait for processing
    while video_file.state.name == "PROCESSING":
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": "Generate a summary for this video."
            },
            {
                "type": "media",
                "mime_type": video_file.mime_type,
                "file_uri": video_file.uri
            }
        ]
    )

    response = model.invoke([message])
    genai.delete_file(video_file.name)
    return {"summary": response.content}


# Build the Pipline

pipline = StateGraph(MainState)

pipline.add_node("upload_video", upload_video)
pipline.add_node("summarize_video", summarize_video)

pipline.set_entry_point("upload_video")
pipline.add_edge("upload_video", "summarize_video")
pipline.add_edge("summarize_video", END)

app = pipline.compile()
