from services.lang_graph_service import app
import streamlit as st


class UtilityService:
    def __init__(self) -> None:
        pass

    def format_time(self, seconds: int) -> str:
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m}:{s:02d}"

    def generate_summary(self, path, prompt=''):
        summary = 'summary not available'
        inputs = {"video_path": path, "prompt": prompt}
        state = app.invoke(inputs)  # type:ignore
        if 'summary' in state:
            summary = state['summary']
        return summary

    def custom_prompt(self):
        prompt_parts = []
        col0, col1, col2,  = st.columns([2, 3, 1])

        with col0:
            summary_type = st.radio(
                "Summary Type:", ["Short summary", "Full explanation"])

            summary_duration = None
            if summary_type and summary_type == "Short summary":
                summary_duration = st.number_input("Select Time")

        with col1:
            summary_bullet = st.checkbox("Summary in bullet point")
            detect_harmful_words = st.checkbox("Detect harmful words")
            detect_harmful_pictures = st.checkbox("Detect harmful pictures")

        with col2:
            age = st.selectbox("Select Age:", ['5', '10', '15', '18+'])
            summary_language = st.selectbox(
                "Summary language:", ["Hindi", "English", "Hinglish", "Video Language"])

        if summary_type:
            prompt_parts.append(
                f"Generate a {summary_type.lower()} of the given video.")

        if summary_duration:
            prompt_parts.append(
                f"summary should be in {summary_duration} minutes.")

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
