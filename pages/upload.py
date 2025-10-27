import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.lang_graph_service import app
from services.utility_service import UtilityService
from database.video_table import VideoTableService

video_table = VideoTableService()
utility_service = UtilityService()
st.session_state = {}
SAVE_DIR = "org_videos"
st.header("Upload Video")

uploaded_file = st.file_uploader("Choose a video file", type=[ 
    "mp4"], help="Upload your video file here")

if uploaded_file and st.button("Process Video"):
    save_path = os.path.join(SAVE_DIR, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    clip = VideoFileClip(save_path)
    duration = int(clip.duration)
    clip.close()

    video_table.add_video(uploaded_file.name, save_path, 0)

    st.session_state["save_path"] = save_path
    st.session_state["duration"] = duration

if st.session_state.get("save_path"):
    st.header("Full Video Summary")

    st.video(st.session_state["save_path"])

    duration = st.session_state["duration"]
    st.write(f"**Duration:** {duration} seconds ({utility_service.format_time(duration)})")

    if st.button("Summarize Full Video"):
        with st.spinner("Generating summary..."):
            summary = utility_service.generate_summary(st.session_state["save_path"])
            st.session_state["full_summary"] = summary

    if st.session_state.get("full_summary"):
        st.write("**Summary:**")
        st.write(st.session_state["full_summary"])



  