import streamlit as st
from dotenv import load_dotenv
from services.background_service import scheduler
import atexit
import os
from decouple import config

load_dotenv()

if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = str(config("GOOGLE_API_KEY"))

if "scheduler_started" not in st.session_state:
    if not scheduler.running:
        scheduler.start()
    st.session_state["scheduler_started"] = True
    atexit.register(lambda: scheduler.shutdown(wait=False))


upload_page = st.Page("pages/upload.py", title="Upload Video")
video_list_page = st.Page("pages/video_list.py",
                          title="Video List", default=True)
show_video = st.Page("pages/show_video.py")

pg = st.navigation(
    [upload_page, video_list_page, show_video], position="top", expanded=True
)
st.title("Video Analyzer")

pg.run()
