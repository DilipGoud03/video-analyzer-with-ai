from typing import TypedDict, Annotated, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv
import operator
import os
import mimetypes

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD0D5lO9oajtO-THvXKpMQy902QL8zGgFU"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")



# Define the State
class VideoAnalysisState(TypedDict):
    video_path: str
    uploaded_file: Optional[dict]
    summary: Optional[str]
    analysis_log: Annotated[List[str], operator.add]


# Define the Nodes
def upload_video(state: VideoAnalysisState):
    path = state["video_path"]
    try:
        mime_type, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            video_bytes = f.read()

        uploaded_file = {
            "inline_data": {
                "mime_type": mime_type or "video/mp4",
                "data": video_bytes
            }
        }

        return {"uploaded_file": uploaded_file, "analysis_log": [f"Loaded {path} inline."]}
    except Exception as e:
        print(f"Error loading video: {e}")
        raise


def summarize_video(state: VideoAnalysisState):
    uploaded_file = state["uploaded_file"]
    prompt = "Generate a concise one-paragraph summary for this video."
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content([uploaded_file, prompt]
                                                                          )

    return {"summary": response.text, "analysis_log": ["Video summarized."]}


# Build the Pipline
pipline = StateGraph(VideoAnalysisState)

pipline.add_node("upload_video", upload_video)
pipline.add_node("summarize_video", summarize_video)

pipline.set_entry_point("upload_video")
pipline.add_edge("upload_video", "summarize_video")
pipline.add_edge("summarize_video", END)

app = pipline.compile()
