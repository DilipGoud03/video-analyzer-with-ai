import streamlit as st
from services.utility_service import UtilityService
from pages import video_range_summary

utility_service = UtilityService()

st.session_state["summary"] = None

if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")

st.divider()
if st.session_state.get("show_video"):
    st.video(st.session_state["show_video"])

    prompt = ''
    if st.checkbox("Custom Prompt"):
        prompt = utility_service.custom_prompt()

    summary = None
    col0, col1 = st.columns([1, 1])

    with col0:
        if st.button("Summary"):
            with st.spinner("Generating summary..."):
                summary = utility_service.generate_summary(
                    st.session_state["show_video"], st.session_state["show_video_name"], False, prompt)
    with col1:
        if st.checkbox("Selected Range", help="if you want to selected time duration summary"):
            summary = video_range_summary.video_range_summary(st.session_state["show_video"], st.session_state["show_video_name"], prompt)
    
    if summary:
        st.write("**Summary:**")
        st.write(summary)

    question = st.text_input("Question", help="Write your question regarding your video.")
    if question:
        with st.spinner("Please wait..."):
            anwer = utility_service.generate_answer(
                st.session_state["show_video"], st.session_state["show_video_name"], question)

else:
    st.info("No videos selected yet. Go to 'Video List' click any one 'Show video'")
