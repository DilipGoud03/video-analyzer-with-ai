import streamlit as st
from services.utility_service import UtilityService
from datetime import timedelta

utility_service = UtilityService()


if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")

st.divider()


def custom_prompt():
    prompt_parts = []
    summary_type = st.radio(
        "Summary Type:", ["Short summary", "Full explanation"])
    
    summary_bullet = None
    summary_duration = None
    if summary_type and summary_type == "Short summary":
        summary_duration = st.number_input("Select Time")
        summary_bullet = st.checkbox("Summary in bullet point")

    
    age = st.selectbox("Select Age:", ['5', '10', '15', '18+'])
    detect_harmful_words = st.checkbox("Detect harmful words")
    detect_harmful_pictures = st.checkbox("Detect harmful pictures")
    summary_language = st.selectbox(
        "Summary language:", ["Hindi", "English", "Hinglish", "Video Language"])

    if summary_type:
        prompt_parts.append(
            f"Generate a {summary_type.lower()} of the given video.")

    if summary_duration:
        prompt_parts.append(f"summary should be in {summary_duration} minutes.")

    if summary_language:
        prompt_parts.append(
            f"The summary should be written in {summary_language}.")

    if age:
        prompt_parts.append(
            f"Check the audio and video is suitable for under {age} years of age or not.")

    if summary_bullet:
        prompt_parts.append(
            "Present the summary in bullet points like video language, category is movie or song or cartoon.")

    if detect_harmful_words:
        prompt_parts.append(
            "Also, detect and highlight any harmful or offensive words in the transcript.")

    if detect_harmful_pictures:
        prompt_parts.append(
            "Analyze the video for any harmful or inappropriate visual content.")

    combine_prompt = " ".join(prompt_parts)

    return st.text_area("Prompt", value=combine_prompt, height=150)


if st.session_state.get("show_video"):
    st.video(st.session_state["show_video"])

    prompt = ''
    if st.checkbox("Want to create custom prompt"):
        prompt = custom_prompt()

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
