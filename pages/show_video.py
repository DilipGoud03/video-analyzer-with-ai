import streamlit as st
from services.utility_service import UtilityService
from datetime import timedelta

utility_service = UtilityService()
st.session_state["save_path"] = None


if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")

st.divider()


if st.session_state.get("show_video"):
    st.video(st.session_state["show_video"])

    prompt = ''
    if st.checkbox("Want to create custom prompt"):
        prompt = utility_service.custom_prompt()

    summary = None
    if st.button("Summarize Full Video"):
        with st.spinner("Generating summary..."):
            summary = utility_service.generate_summary(
                st.session_state["show_video"], prompt)
            st.session_state["full_summary"] = summary

    if summary:
        st.write("**Summary:**")
        st.write(summary)
else:
    st.info("No videos selected yet. Go to 'Video List' click any one 'Show video'")
