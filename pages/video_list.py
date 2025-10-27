import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from services.utility_service import UtilityService
from database.video_table import VideoTableService



video_table = VideoTableService()
utility_service = UtilityService()
SAVE_DIR = "org_videos"


st.header("Videos")
st.session_state = {}

# Get all video files
if os.path.exists(SAVE_DIR):
    video_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.mp4')]
    if video_files:
        # Create table header
        for video_file in video_files:
            video_data = video_table.get_video_by_name(video_file)
            if video_data:
                video_id = 1
                video_path = os.path.join(SAVE_DIR, video_file)

                # Display video info
                st.divider()

                col0, col1, col2 = st.columns([1, 2, 1])
                with col0:
                    st.write(f"**{video_data['id']}**")

                with col1:
                    st.write(f"**Name:** {video_file}")

                    # Get video duration
                    try:
                        clip = VideoFileClip(video_path)
                        duration = int(clip.duration)
                        clip.close()
                        st.write(f"**Duration:** {utility_service.format_time(duration)}")
                    except:
                        st.write("**Duration:** N/A")
                        duration = 0

                with col2:
                    # Show Video button
                    if st.button("Show Video", key=f"show_video_{video_data['id']}"):
                        st.session_state["show_video"] = video_path
                        st.session_state["duration"] = duration
                        st.switch_page("pages/show_video.py")
    else:
        st.info("No videos uploaded yet. Go to 'Upload Video' to add videos.")
else:
    st.warning("Video directory not found.")
