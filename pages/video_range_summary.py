import streamlit as st
import os
import uuid
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility_service import UtilityService
from decouple import config


utility_service = UtilityService()

TEMP_DIR = config("TEMP_DIR")
st.header("Summarize Selected Range")
st.session_state["temp_video_path"] = None


def video_range_summary(video_path, video_name, prompt):
    summary = None
    duration = st.session_state['duration']
    if video_path:
        start_time, end_time = st.slider(
            "Select time range (in seconds)",
            min_value=0,
            max_value=duration,
            value=(0, min(30, duration)),
            step=1
        )
        st.write(f"Selected Range: {utility_service.format_time(start_time)} → {utility_service.format_time(end_time)}")
        
        if st.button("View Selected Range"):
                clip = VideoFileClip(video_path).subclipped(start_time, end_time)
                new_file = f"{int(time.time())}_{uuid.uuid4().hex}.mp4"
                temp_path = os.path.join(TEMP_DIR, new_file) #type:ignore
                clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", logger=None)
                clip.close()
                with st.spinner("Generating summary..."):
                    summary = utility_service.generate_summary(temp_path, video_name, False, prompt)
    return summary