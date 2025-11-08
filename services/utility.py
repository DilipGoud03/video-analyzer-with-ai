import streamlit as st
from services.lang_graph import LanggraphService

# ------------------------------------------------------------
# Class: UtilityService
# Description:
#   Provides helper methods for:
#     - Formatting time values
#     - Generating detailed video summaries
#     - Answering user questions about video content
#     - Building custom prompts for summary generation
#   Integrates Streamlit for interactive user input and
#   LangGraph workflows for model execution.
# ------------------------------------------------------------


class UtilityService:   
    # ------------------------------------------------------------
    # Method: __init__
    # Description:
    #   Initializes a configuration dictionary that stores
    #   a unique thread_id for each Streamlit session.
    # ------------------------------------------------------------
    def __init__(self) -> None:
        self.__langgraph_service = LanggraphService()
        self.__graph = self.__langgraph_service.build_pipeline()  # Compile once

        self.__config = {
            "configurable": {
                "thread_id": st.session_state.get("video_name", "1234")
            }
        }

    # ------------------------------------------------------------
    # Method: generate_answer
    # Description:
    #   Answers user questions about the video content using
    #   previously generated summaries stored in the vector DB.
    #   The response is produced via the LangGraph workflow.
    # ------------------------------------------------------------
    def generate_answer(self, path, video_name, question):        
        input = {"video_path": path, "video_name": video_name, "question": question,"messages": []}
        state = self.__graph.invoke(input, self.__config)
        return state.get('answer', '')

    # ------------------------------------------------------------
    # Method: generate_summary
    # Description:
    #   Generates a detailed video summary using LangGraph's
    #   workflow execution. If available, returns the model-
    #   generated summary text from the state dictionary.
    # ------------------------------------------------------------
    def generate_summary(self, path, video_name: str, is_new_video: bool, prompt=''):
        inputs = {"video_path": path, "video_name": video_name, "is_new_video": is_new_video, "prompt": prompt}
        state = self.__graph.invoke(inputs, self.__config)  # type:ignore
        return state.get('summary', '')

    # ------------------------------------------------------------
    # Method: custom_prompt
    # Description:
    #   Builds a dynamic custom prompt for summary generation
    #   based on user-selected preferences in Streamlit, such as:
    #     - Summary type and duration
    #     - Age appropriateness
    #     - Language and bullet-point options
    #     - Detection of harmful content (words or visuals)
    #   Returns a text area for user review or manual editing.
    # ------------------------------------------------------------
    def custom_prompt(self):
        prompt_parts = []
        col0, col1, col2 = st.columns([2, 3, 1])

        # --- Left Column: Type & Duration ---
        with col0:
            summary_type = st.radio("**Summary Type:**", ["Short summary", "Full explanation"])
            summary_duration = st.number_input(
                "**Select Duration (in minutes):**",
                min_value=0,
                value=1
            )

        # --- Middle Column: Format & Detection ---
        with col1:
            summary_bullet = st.checkbox("**Show summary as bullet points**")
            detect_harmful_words = st.checkbox("**Detect harmful words**")
            detect_harmful_pictures = st.checkbox("**Detect harmful visuals**")

        # --- Right Column: Age & Language ---
        with col2:
            age = st.selectbox(
                "**Select Age Group:**",
                [0, 5, 10, 15, 18, 19]
            )
            summary_language = st.selectbox(
                "**Summary Language:**",
                ["Hindi", "English", "Hinglish", "Video Language"]
            )

        # --- Build Prompt Based on Selections ---
        if summary_type:
            prompt_parts.append(f"Generate a {summary_type.lower()} of the given video.")

        if summary_duration:
            prompt_parts.append(f"The summary should be in {summary_duration} minute(s).")

        if summary_language:
            prompt_parts.append(f"Write the summary in {summary_language} language.")

        if age:
            if age <= 18:
                prompt_parts.append(
                    f"Evaluate whether the video content (audio & visuals) is appropriate for viewers under {age} years old."
                )
            else:
                prompt_parts.append(
                    "Evaluate whether the video content (audio & visuals) is appropriate for a general adult audience."
                )

        if summary_bullet:
            prompt_parts.append(
                "Present the summary in well-structured bullet points, covering aspects such as video language, category (movie, song, cartoon), and tone."
            )

        if detect_harmful_words:
            prompt_parts.append(
                "Identify and highlight any harmful, offensive, or inappropriate words in the transcript."
            )

        if detect_harmful_pictures:
            prompt_parts.append(
                "Analyze and mention if the video contains harmful, violent, or inappropriate visuals."
            )

        # --- Combine & Display Prompt ---
        combine_prompt = " ".join(prompt_parts)
        return st.text_area(
            "Generated Prompt",
            value=combine_prompt.strip(),
            height=180,
            help="You can also create or edit a custom prompt here."
        )

    # ------------------------------------------------------------
    # Method: format_time
    # Description:
    #   Converts total seconds into a human-readable
    #   "minutes:seconds" (mm:ss) format.
    # ------------------------------------------------------------
    def format_time(self, seconds: int) -> str:
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m}:{s:02d}"