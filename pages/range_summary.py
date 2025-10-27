import streamlit as st
import os
import uuid
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility_service import UtilityService


utility_service = UtilityService()

TEMP_DIR = "temp_videos"
st.header("Summarize Selected Range")

if st.session_state.get("save_path"):
    duration = st.session_state["duration"]
    
    start_time, end_time = st.slider(
        "Select time range (in seconds)",
        min_value=0,
        max_value=duration,
        value=(0, min(30, duration)),
        step=1
    )
    st.write(f"Selected Range: {utility_service.format_time(start_time)} → {utility_service.format_time(end_time)}")
    
    if st.button("View Selected Range"):
        with st.spinner("Generating Selected Range video..."):
            clip = VideoFileClip(st.session_state["save_path"]).subclipped(start_time, end_time)
            temp_path = os.path.join(TEMP_DIR, f"{int(time.time())}_{uuid.uuid4().hex}.mp4")
            clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", logger=None)
            clip.close()
            st.session_state["temp_video_path"] = temp_path
    
    if st.session_state.get("temp_video_path"):
        st.video(st.session_state["temp_video_path"])
        
        summary = None
        if st.button("Summarize Selected Range"):
            with st.spinner("Generating summary..."):
                summary = utility_service.generate_summary(st.session_state["temp_video_path"])

        if summary:
            st.write("**Summary:**")
            st.write(summary)
else:
    st.warning("Please upload a video first in the 'Upload Video' page.")