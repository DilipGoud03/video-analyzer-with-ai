import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility import UtilityService
from database.video_table import VideoTableService
from decouple import config


# Initialize required services and configuration
video_table = VideoTableService()
utility_service = UtilityService()
ORG_DIR = str(config("ORG_DIR"))


# Section: Page Header
# --------------------
# Displays the title for the video upload interface.
st.header("Upload Video")


# Section: Initialize Session State
# ---------------------------------
# Ensures session variables are initialized properly to store video data and summaries.
st.session_state["view_video"] = None
st.session_state["summary"] = None
st.session_state["qa_listing"] = []


# Section: File Uploader
# ----------------------
# Allows users to upload video files in MP4 format.
# Displays a help tooltip explaining the upload purpose.
uploaded_file = st.file_uploader(
    "Choose a video file",
    type=["mp4"],
    help="Upload your video file here"
)


# Section: Process Uploaded Video
# -------------------------------
# When the user uploads and processes a video:
# - Saves it to the configured ORG_DIR.
# - Adds video metadata to the database if it's a new upload.
# - Displays the uploaded video and its duration.
# - Automatically generates and displays an AI-based summary.
if uploaded_file and st.button("Process Video"):
    is_new_video = False

    # Add video entry to the database if not already existing
    if video_table.add_video(uploaded_file.name, 0):
        is_new_video = True

    # Save uploaded video to the local directory
    save_path = os.path.join(ORG_DIR, uploaded_file.name)
    open(save_path, "wb").write(uploaded_file.getbuffer())

    # Get video duration using MoviePy
    clip = VideoFileClip(save_path)
    duration = int(clip.duration)
    clip.close()

    # Display video preview and duration details
    if save_path:
        st.video(save_path)
        st.write(f"**Duration:** {duration} seconds ({utility_service.format_time(duration)})")

        # Generate AI-based summary for the uploaded video
        with st.spinner("Generating summary..."):
            summary = utility_service.generate_summary(save_path, uploaded_file.name, is_new_video)
            st.session_state["summary"] = summary

        # Display summary if generated
        if st.session_state.get("summary"):
            st.write("**Summary:**")
            st.write(st.session_state["summary"])
