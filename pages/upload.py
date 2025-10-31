import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.lang_graph_service import app
from services.utility_service import UtilityService
from database.video_table import VideoTableService
from decouple import config

video_table = VideoTableService()
utility_service = UtilityService()
ORG_DIR = str(config("ORG_DIR"))
st.header("Upload Video")

st.session_state["show_video"] = None
st.session_state["summary"] = None
st.session_state["qa_listing"] = []

uploaded_file = st.file_uploader("Choose a video file", type=[
    "mp4"], help="Upload your video file here")

if uploaded_file and st.button("Process Video"):
    is_new_video = False
    if video_table.add_video(uploaded_file.name, 0):
        is_new_video = True

    save_path = os.path.join(ORG_DIR, uploaded_file.name)
    open(save_path, "wb").write(uploaded_file.getbuffer())
    clip = VideoFileClip(save_path)
    duration = int(clip.duration)
    clip.close()

    if save_path:
        st.video(save_path)
        st.write(f"**Duration:** {duration} seconds ({utility_service.format_time(duration)})")

        with st.spinner("Generating summary..."):
            summary = utility_service.generate_summary(save_path, uploaded_file.name, is_new_video)
            st.session_state["summary"] = summary
        
        if st.session_state.get("summary"):
            st.write("**Summary:**")
            st.write(st.session_state["summary"])



  