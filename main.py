import os
import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
from service.lang_graph import app
import uuid

save_dir = "org_videos"
temp_dir = "temp_videos"
os.makedirs(temp_dir, exist_ok=True)


def format_time(seconds: int) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


st.set_page_config(page_title="Video Analyzer", layout="centered")
st.title("Video Analyzer")

save_path = None
duration = 0
uploaded_name = None
trimmed_path = None
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

if uploaded_file:
    save_path = None
    duration = 0
    uploaded_name = None
    trimmed_path = None

# Process uploaded video
if uploaded_file is not None:
    if st.button("Process Video"):
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Video saved temporarily for processing")

        # Get video duration
        clip = VideoFileClip(save_path)
        duration = int(clip.duration)
        clip.close()

if save_path:
    st.write(
        f"**Video duration:** {duration} seconds ({format_time(duration)})")

    # Time range slider
    start_time, end_time = st.slider(
        "Select time range (in seconds)", 0, duration, (0, min(30, duration)), step=1)
    st.write(
        f"Selected Range: {format_time(start_time)} ---> {format_time(end_time)}")

    if st.button("Preview selected range"):
        with st.spinner("Trimming video..."):
            clip = VideoFileClip(save_path).subclipped(start_time, end_time)
            trimmed_video_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}.mp4")
            clip.write_videofile(trimmed_video_path, codec="libx264", audio_codec="aac", logger=None)
            clip.close()
        st.video(trimmed_path)

    # Summarize trimmed video
    if trimmed_path:
        if st.button("Summarize selected range"):
            with st.spinner("Generating summary..."):
                inputs = {"video_path": trimmed_path, "analysis_log": []}
                state = app.invoke(inputs)
                if 'summary' in state:
                    st.write(state['summary'])

                # Remove trimmed video after summarization
                if os.path.exists(trimmed_path):
                    os.remove(trimmed_path)
                    trimmed_path = None
