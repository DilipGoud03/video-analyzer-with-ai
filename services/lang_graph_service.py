from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai
from decouple import config
import os
import mimetypes


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY")


# Define the State
class UploadedFile(TypedDict):
    mime_type: str
    data: bytes


class MainState(TypedDict):
    video_path: str
    uploaded_file: Optional[UploadedFile]
    summary: Optional[str]
    prompt: Optional[str]


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
    if 'prompt' in state and state['prompt'] != '':
        prompt = state['prompt']
    else:
        prompt = "Give me short summary of the uploaded video. Give me the summary in the bullet points with heading like video language, category is movie or song or cartoon, the audio and video is suitable for childer under 5 years of age or not."
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
