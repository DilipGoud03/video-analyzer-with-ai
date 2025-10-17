import os
import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip

save_dir = "uploads"


def format_time(seconds: int) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


st.set_page_config(page_title="Video Analyzer", layout="centered")
st.title("Video Analyzer")

uploaded_file = st.file_uploader(
    "Choose a video file", type=["mp4", "mov", "avi", "mkv"]
)

# Initialize session state
if "save_path" not in st.session_state:
    st.session_state["save_path"] = None
if "duration" not in st.session_state:
    st.session_state["duration"] = 0
if "uploaded_name" not in st.session_state:
    st.session_state["uploaded_name"] = None

# Reset session if new video uploaded
if uploaded_file is not None and uploaded_file.name != st.session_state["uploaded_name"]:
    st.session_state["save_path"] = None
    st.session_state["duration"] = 0
    st.session_state["uploaded_name"] = None

save_path = None
if uploaded_file is not None:
    if st.button("Process Video"):
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Saved to `{save_path}`")

        # Read video duration
        try:
            clip = VideoFileClip(save_path)
            duration = clip.duration
            clip.close()
        except Exception as e:
            st.error(f"Could not read video duration: {e}")
            duration = 0

        st.session_state["save_path"] = save_path
        st.session_state["duration"] = int(duration)
        st.session_state["uploaded_name"] = uploaded_file.name

selected_time = 0
if st.session_state["save_path"]:
    duration = st.session_state["duration"]
    default_seconds = max(1, int(duration * 0.1))

    st.write(
        f"**Video duration:** {int(duration)} seconds "
        f"({format_time(int(duration))})"
    )

    start_time, end_time = st.slider(
        "Select time range (in seconds)",
        0, duration, (0, min(30, duration)),
        step=1
    )

    st.write(
        f"Selected Range: {format_time(start_time)} → {format_time(end_time)}")


if selected_time > 0:
    st.write(f"Selected summary time: {format_time(selected_time)}")
