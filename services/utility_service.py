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
        col0, col1, col2 = st.columns([2, 3, 1])

        with col0:
            summary_type = st.radio(
                "Summary Type:", ["Short summary", "Full explanation"])

            summary_duration = st.number_input("Select Duration (in minutes):", min_value=0, value=1)

        with col1:
            summary_bullet = st.checkbox("Show summary as bullet points")
            detect_harmful_words = st.checkbox("Detect harmful words")
            detect_harmful_pictures = st.checkbox("Detect harmful visuals")

        with col2:
            age = st.selectbox("Select Age Group:", ['5', '10', '15', '18+'])
            summary_language = st.selectbox(
                "Summary Language:", ["Hindi", "English", "Hinglish", "Video Language"]
            )

        if summary_type:
            prompt_parts.append(f"Generate a {summary_type.lower()} of the given video.")

        if summary_duration:
            prompt_parts.append(f"The summary should bee in {summary_duration} minute(s).")

        if summary_language:
            prompt_parts.append(f"Write the summary in {summary_language} language.")

        if age:
            prompt_parts.append(
                f"Evaluate whether the video content (both audio and visuals) is appropriate for viewers under {age} years old."
            )

        if summary_bullet:
            prompt_parts.append(
                "Present the summary in well-structured bullet points, including key aspects such as video language, category (e.g., movie, song, cartoon), and tone."
            )

        if detect_harmful_words:
            prompt_parts.append(
                "Identify and highlight any harmful, offensive, or inappropriate words in the transcript."
            )

        if detect_harmful_pictures:
            prompt_parts.append(
                "Analyze and mention if the video contains any harmful, violent, or inappropriate visuals."
            )

        combine_prompt = " ".join(prompt_parts)
        return st.text_area("Generated Prompt", value=combine_prompt.strip(), height=180, help="Also you can create a custom prompt")