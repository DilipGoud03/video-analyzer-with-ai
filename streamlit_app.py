import streamlit as st
from dotenv import load_dotenv


load_dotenv()
upload_page = st.Page("pages/upload.py", title="Upload Video")
video_list_page = st.Page("pages/video_list.py",
                          title="Video List", default=True)
show_video = st.Page("pages/show_video.py")

pg = st.navigation(
    [upload_page, video_list_page, show_video], position="top", expanded=True
)
st.title("Video Analyzer")

pg.run()
