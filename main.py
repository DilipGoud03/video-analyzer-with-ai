import os
import uuid
import time
import atexit
import streamlit
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.lang_graph_service import app
from services.background_service import scheduler


SAVE_DIR = "org_videos"
TEMP_DIR = "temp_videos"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


# time formation
def format_time(seconds: int) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


# Job
def setup_scheduler():
    if "scheduler_started" not in streamlit.session_state:
        if not scheduler.running:
            scheduler.start()
        streamlit.session_state["scheduler_started"] = True
        atexit.register(lambda: scheduler.shutdown(wait=False))


# upload video
def upload_video_section():
    uploaded_file = streamlit.file_uploader(
        "Choose a video file", type="mp4", help="Upload your video file here")

    if uploaded_file and streamlit.button("Process Video"):
        save_path = os.path.join(SAVE_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        clip = VideoFileClip(save_path)
        duration = int(clip.duration)
        clip.close()

        streamlit.session_state["save_path"] = save_path
        streamlit.session_state["duration"] = duration

    return streamlit.session_state.get("save_path"), streamlit.session_state.get("duration", 0)


# summarize full video
def summarize_full_video():
    if streamlit.session_state.get("save_path"):
        streamlit.subheader("Full Video Summary")

        streamlit.video(streamlit.session_state["save_path"])

        duration = streamlit.session_state["duration"]
        streamlit.write(
            f"**Duration:** {duration} seconds ({format_time(duration)})")
        summary = None
        if streamlit.button("Summarize Full Video"):
            with streamlit.spinner("Generating summary..."):
                summary = generate_summary(
                    streamlit.session_state["save_path"])

        if summary:
            streamlit.write("Summary")
            streamlit.write(summary)


# summarize video range
def summarize_video_range():
    if streamlit.session_state.get("save_path"):
        streamlit.divider()
        streamlit.subheader("Summarize Selected Range")

        duration = streamlit.session_state["duration"]

        start_time, end_time = streamlit.slider(
            "Select time range (in seconds)",
            min_value=0,
            max_value=duration,
            value=(0, min(30, duration)),
            step=1
        )
        streamlit.write(
            f"Selected Range: {format_time(start_time)} → {format_time(end_time)}")

        if streamlit.button("View Selected Range"):
            with streamlit.spinner("Generating Selected Range video..."):
                clip = VideoFileClip(streamlit.session_state["save_path"]).subclipped(
                    start_time, end_time)
                temp_path = os.path.join(
                    TEMP_DIR, f"{int(time.time())}_{uuid.uuid4().hex}.mp4")
                clip.write_videofile(temp_path, codec="libx264", audio_codec="aac", logger=None)
                clip.close()
                streamlit.session_state["temp_video_path"] = temp_path
        summary = None
        if streamlit.session_state.get("temp_video_path"):
            streamlit.video(streamlit.session_state["temp_video_path"])

            if streamlit.button("Summarize Selected Range"):
                with streamlit.spinner("Generating summary..."):
                    summary = generate_summary(
                        streamlit.session_state["temp_video_path"])

        # Display range summary if available
        if summary:
            streamlit.write("Summary")
            streamlit.write(summary)


def generate_summary(path):
    summary = 'summary not available'
    inputs = {"video_path": path}
    state = app.invoke(inputs)
    if 'summary' in state:
        summary = state['summary']
    return summary


def main():
    streamlit.title("Video Analyzer")
    setup_scheduler()
    upload_video_section()
    summarize_full_video()
    summarize_video_range()


if __name__ == "__main__":
    main()
