import streamlit as st
from dotenv import load_dotenv
import atexit
import os
from decouple import config


# Load environment variables from .env file
load_dotenv()

# Configure Google API key if not already set in environment
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = str(config("GOOGLE_API_KEY"))


# Define Streamlit pages
upload_page = st.Page("pages/upload.py", title="Upload Video")
video_list_page = st.Page("pages/video_list.py",
                          title="Video List", default=True)
view_video = st.Page("pages/view_video.py")


# Navigation configuration and app entry point
pg = st.navigation(
    [upload_page, video_list_page, view_video], position="top", expanded=True
)
st.title("Video Analyzer")

# Run selected page
pg.run()
