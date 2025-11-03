import streamlit as st
import os
import uuid
import time
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility_service import UtilityService
from decouple import config


# Initialize utility service
utility_service = UtilityService()

# Load temporary directory configuration
TEMP_DIR = config("TEMP_DIR")

# Section: Page Header
# --------------------
# Displays the header for video range summarization.
st.header("Summarize Selected Range")

# Initialize temporary video path in session state
st.session_state["temp_video_path"] = None


# Function: video_range_summary
# -----------------------------
# Generates a summary for a selected time range within a video.
# - Allows the user to select start and end times via a slider.
# - Creates a temporary video clip for the chosen segment.
# - Generates an AI-based summary for that specific range.
def video_range_summary(video_path, video_name, prompt):
    summary = None
    duration = st.session_state['duration']
    if video_path:
        # Slider to select start and end times for summarization
        start_time, end_time = st.slider(
            "Select time range (in seconds)",
            min_value=0,
            max_value=duration,
            value=(0, min(30, duration)),
            step=1
        )

        st.write(f"Selected Range: {utility_service.format_time(start_time)} → {utility_service.format_time(end_time)}")

        # Button to preview and summarize the selected range
        if st.button("View Selected Range"):
            clip = VideoFileClip(video_path).subclipped(start_time, end_time)
            new_file = f"{int(time.time())}_{uuid.uuid4().hex}.mp4"
            temp_path = os.path.join(TEMP_DIR, new_file)  # type: ignore
            clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", logger=None)
            clip.close()

            with st.spinner("Generating summary..."):
                summary = utility_service.generate_summary(temp_path, video_name, False, prompt)
    return summary
