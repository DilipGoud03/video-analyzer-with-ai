import os
import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.lang_graph_service import app
import uuid
import time



SAVE_DIR = "org_videos"
TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)


def format_time(seconds: int) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


st.title("Video Analyzer")

if "save_path" not in st.session_state:
    st.session_state["save_path"] = None
if "duration" not in st.session_state:
    st.session_state["duration"] = 0
if "uploaded_name" not in st.session_state:
    st.session_state["uploaded_name"] = None
if "trimmed_path" not in st.session_state:
    st.session_state["trimmed_path"] = None

save_path = None
duration = 0
uploaded_name = None
trimmed_path = None
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"], help="upload you video file here")

# Handle new upload
if uploaded_file and uploaded_file.name != st.session_state["uploaded_name"]:
    st.session_state["save_path"] = None
    st.session_state["duration"] = 0
    st.session_state["uploaded_name"] = None
    st.session_state["trimmed_path"] = None

# Process uploaded video
if uploaded_file is not None:
    if st.button("Process Video"):
        save_path = os.path.join(SAVE_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["save_path"] = save_path
        st.session_state["uploaded_name"] = uploaded_file.name

        # Get video duration
        clip = VideoFileClip(save_path)
        st.session_state["duration"] = int(clip.duration)
        clip.close()


# If video is ready
if st.session_state.get("save_path"):
    st.video(st.session_state["save_path"])
    duration = st.session_state["duration"]
    st.write(
        f"**Video duration:** {duration} seconds ({format_time(duration)})")

    # Time range slider
    start_time, end_time = st.slider(
        label="Select time range (in seconds)",
        min_value=0,
        max_value=duration,
        value=(0, min(30, duration)),
        step=1,
        help="Drag the sliders to choose the start and end times for the video segment you want to analyze."
    )

    st.write(f"Selected Range: {format_time(start_time)} → {format_time(end_time)}")

    if st.button("Preview selected range"):
        with st.spinner("Trimming video..."):
            clip = VideoFileClip(st.session_state["save_path"]).subclipped(start_time, end_time)
            temp_path = os.path.join(TEMP_DIR, f"{int(time.time())}_{uuid.uuid4().hex}.mp4")
            clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", logger=None)
            clip.close()
            st.session_state["trimmed_path"] = temp_path

    # Summarize trimmed video
    if st.session_state.get("trimmed_path"):
        st.video(st.session_state["trimmed_path"])
        if st.button("Summarize selected range"):
            with st.spinner("Generating summary..."):
                inputs = {
                    "video_path": st.session_state["trimmed_path"]}
                state = app.invoke(inputs)
                if 'summary' in state:
                    st.write(state['summary'])