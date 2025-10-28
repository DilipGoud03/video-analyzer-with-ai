import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility_service import UtilityService
from database.video_table import VideoTableService
from decouple import config

video_table = VideoTableService()
utility_service = UtilityService()
ORG_DIR = config("ORG_DIR")

st.header("Videos")

st.session_state = {}


def filter_videos():
    search_val = st.session_state.get("search", "")
    category_val = st.session_state.get("category", "")
    return video_table.video_list(search_val, category_val)


video_files = [f for f in os.listdir(ORG_DIR) if f.endswith('.mp4')]
results = filter_videos()
if results:
    col3, col4 = st.columns([1, 1])
    with col3:
        search = st.text_input(
            "Search",
            key="search",
        )

    with col4:
        category = st.selectbox(
            "Category",
            ["All", "Education", "Entertainment"],
            key="category",
        )

    st.session_state["search"] = search
    st.session_state["category"] = category

    if os.path.exists(ORG_DIR):
        for video_file in results:
            if video_file and video_file["video_name"] in video_files:
                video_path = os.path.join(ORG_DIR, video_file["video_name"])

                st.divider()
                col0, col1, col2 = st.columns([1, 2, 1])
                with col0:
                    st.write(f"**{video_file['id']}**")
                with col1:
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
                with col2:
                    if st.button("Show Video", key=f"show_video_{video_file['id']}"):
                        st.session_state["show_video"] = video_path
                        st.session_state["duration"] = duration
                        st.switch_page("pages/show_video.py")
    else:
        st.warning("Video directory not found.")
