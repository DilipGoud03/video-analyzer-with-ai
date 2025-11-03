from services.lang_graph_service import app
import streamlit as st


# Class: UtilityService
# ---------------------
# Provides helper functions for formatting time, generating video summaries,
# answering questions about videos, and creating custom prompts for the model.
class UtilityService:
    def __init__(self) -> None:
        self.__user_config = {
            "configurable": {
                "thread_id": st.session_state.get("user_name", "12312")
            }
        }

    # Function: format_time
    # ---------------------
    # Converts total seconds into "minutes:seconds" format.
    def format_time(self, seconds: int) -> str:
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m}:{s:02d}"

    # Function: generate_summary
    # --------------------------
    # Generates a detailed summary of the video by invoking the LangGraph workflow.
    def generate_summary(self, path, video_name: str, is_new_video: bool, prompt=''):
        summary = 'summary not available'
        inputs = {"video_path": path, "video_name": video_name,
                  "is_new_video": is_new_video, "prompt": prompt}
        state = app.invoke(inputs)  # type:ignore
        if 'summary' in state:
            summary = state['summary']
        return summary

    # Function: generate_answer
    # -------------------------
    # Generates an answer to a question related to the video content using stored summaries.
    def generate_answer(self, path, video_name, question):
        answer = ''
        input = {"video_path": path, "video_name": video_name, "question": question}
        state = app.invoke(input)
        if 'answer' in state:
            answer = state['answer']
        return answer

    # Function: custom_prompt
    # -----------------------
    # Builds a custom summary generation prompt based on user-selected preferences
    # like summary type, duration, language, age group, and content filters.
    def custom_prompt(self):
        prompt_parts = []
        col0, col1, col2 = st.columns([2, 3, 1])

        with col0:
            summary_type = st.radio(
                "Summary Type:", ["Short summary", "Full explanation"])

            summary_duration = st.number_input(
                "Select Duration (in minutes):",
                min_value=0,
                value=1
            )

        with col1:
            summary_bullet = st.checkbox("Show summary as bullet points")
            detect_harmful_words = st.checkbox("Detect harmful words")
            detect_harmful_pictures = st.checkbox("Detect harmful visuals")

        with col2:
            age = st.selectbox(
                "Select Age Group:",
                [
                    0,
                    5,
                    10,
                    15,
                    18,
                    19
                ]
            )

            summary_language = st.selectbox(
                "Summary Language:", [
                    "Hindi",
                    "English",
                    "Hinglish",
                    "Video Language"
                ]
            )

        if summary_type:
            prompt_parts.append(
                f"Generate a {summary_type.lower()} of the given video.")

        if summary_duration:
            prompt_parts.append(
                f"The summary should bee in {summary_duration} minute(s).")

        if summary_language:
            prompt_parts.append(
                f"Write the summary in {summary_language} language.")

        if age:
            if age <= 18:
                prompt_parts.append(
                    f"Evaluate whether the video content (both audio and visuals) is appropriate for viewers under {age} years old."
                )
            else:
                prompt_parts.append(
                    "Evaluate whether the video content (both audio and visuals) is appropriate for a general adult audience")

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
