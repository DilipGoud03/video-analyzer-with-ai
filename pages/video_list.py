import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility import UtilityService
from database.video_table import VideoTableService
from decouple import config
from enumeration.suitability import SuitabilityEnum

# Initialize services and configuration
video_table = VideoTableService()
utility_service = UtilityService()
ORG_DIR = config("ORG_DIR")


# Section: Page Header
# --------------------
# Displays the title for the video list interface.
st.header("Videos")


# Section: Initialize Session State
# ---------------------------------
# Ensures the session state variables are ready to store video data and summaries.
st.session_state["view_video"] = None
st.session_state["summary"] = None
st.session_state["qa_listing"] = []


# Method: filter_videos
# -----------------------
# Retrieves the list of videos from the database.
# - Uses search and category filters from session state.
# - Returns a list of filtered video records.
def filter_videos() -> list:
    search_val = st.session_state.get("search", "")
    suitable_val = st.session_state.get("suitable", "")
    return video_table.video_list(suitable_val, search_val)

# Section: Filter Controls
# ------------------------
# Provides user input fields for searching and filtering videos by category.
col0, col1 = st.columns([1, 1])
with col0:
    search = st.text_input(
        "**Search**",
        key="search",
    )
with col1:
    suitable = st.selectbox(
        label="**suitable**",
        key="suitable",
        options=SuitabilityEnum
    )

# Section: Video Listing
# ----------------------
# Displays all videos retrieved from the database.
# - Shows each video's ID, name, and duration.
# - Provides a button to open and view the video in detail.
video_files = [f for f in os.listdir(ORG_DIR) if f.endswith('.mp4')]
results = filter_videos()
if len(results) > 0:
    with st.container(height=600):
        if os.path.exists(ORG_DIR):
            for video_file in results:
                if video_file and video_file["video_name"] in video_files:
                    video_path = os.path.join(ORG_DIR, video_file["video_name"])

                    col2, col3 = st.columns([1, 3])
                    # Display video
                    with col2:
                        with st.container(width=100):
                            st.video(video_path)

                    # Display video name and duration
                    with col3:
                        st.write(f"**Name:** {video_file['video_name']}")
                        try:
                            clip = VideoFileClip(video_path)
                            duration = int(clip.duration)
                            clip.close()
                            st.write(
                                f"**Duration:** {utility_service.format_time(duration)}")
                        except:
                            st.write("**Duration:** N/A")
                            duration = 0

                    # Button to open and view selected video
                        if st.button("**View**", key=f"view_video_{video_file['id']}"):
                            st.session_state["view_video"] = video_path
                            st.session_state["video_name"] = video_file['video_name']
                            st.session_state["duration"] = duration
                            st.switch_page("pages/view_video.py")
                    st.divider()

        else:
            st.warning("Video directory not found.")
else:
    st.warning("Videos not available!")
