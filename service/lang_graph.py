from typing import TypedDict, Annotated, List, Optional
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
import google.generativeai as genai
from dotenv import load_dotenv
import operator
import os
import mimetypes
import base64

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyD0D5lO9oajtO-THvXKpMQy902QL8zGgFU"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")



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
        video_bytes = open(path, "rb").read()

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
    response = genai.GenerativeModel("gemini-2.0-flash").generate_content([uploaded_file, prompt])
    return {"summary": response.text, "analysis_log": ["Video summarized."]}


# def summarize_video(state: VideoAnalysisState):
#     uploaded = state.get("uploaded_file")
#     if not uploaded:
#         raise ValueError("No uploaded_file found in state")

#     if "inline_data" in uploaded and isinstance(uploaded["inline_data"], dict):
#         inline = uploaded["inline_data"]
#         video_bytes = inline.get("data")
#         mime_type = inline.get("mime_type") or "video/mp4"
#     else:
#         video_bytes = uploaded.get("data")
#         mime_type = uploaded.get("mime_type") or "video/mp4"

#     print(mime_type)
#     if not video_bytes:
#         raise ValueError("Uploaded file does not contain video bytes")

#     video_base64 = base64.b64encode(video_bytes).decode("utf-8")

#     message = HumanMessage(
#         content=[
#             {
#                 "type": "text",
#                 "text": "describe what's in this video in a sentence",
#             },
#             {
#                 "type": "video",
#                 "base64": video_base64,
#                 "mime_type": "video/mp4",
#             },
#         ]
#     )
#     response = model.invoke([message])

#     print("Response", response)
#     summary = getattr(response, "content", None)
#     if summary is None and isinstance(response, (list, tuple)) and len(response) > 0:
#         summary = getattr(response[0], "content", None)
#     return {"summary": summary, "analysis_log": ["Video summarized."]}


# Build the Pipline
pipline = StateGraph(VideoAnalysisState)

pipline.add_node("upload_video", upload_video)
pipline.add_node("summarize_video", summarize_video)

pipline.set_entry_point("upload_video")
pipline.add_edge("upload_video", "summarize_video")
pipline.add_edge("summarize_video", END)

app = pipline.compile()
