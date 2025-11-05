import streamlit as st
from services.utility_service import UtilityService
from pages import video_range_summary
import html

# Initialize UtilityService instance for handling summaries and Q&A
utility_service = UtilityService()


# Section: Initialize Session State
# ---------------------------------
# Ensures required session variables are available and initialized.
if "qa_listing" not in st.session_state:
    st.session_state["qa_listing"] = []
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""


# Button: Back Navigation
# -----------------------
# Navigates the user back to the video list page.
if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")


# Function: handle_question_submit
# --------------------------------
# Handles the user's question input and generates an AI-based answer.
# - Uses the UtilityService to generate an answer related to the selected video.
# - Appends question-answer pairs to the session state for display.
# - Clears the input field after submission.
def handle_question_submit():
    question = st.session_state.question_input.strip()
    if question:
        answer = utility_service.generate_answer(
            st.session_state["show_video"],
            st.session_state.get("show_video_name", "video.mp4"),
            question,
        )
        st.session_state.qa_listing.append(
            {"question": question, "answer": answer}
        )
        st.session_state.question_input = ""


# Section: Video Display and Summary Controls
# -------------------------------------------
# Displays the selected video, shows details, and allows summary generation.
st.divider()
if st.session_state.get("show_video"):
    # Display the selected video
    st.video(st.session_state["show_video"])

    # Display video metadata such as name and duration
    col5, col6 = st.columns([1, 1])
    with col5:
        st.write(
            f"**VIDEO:** {st.session_state.get('show_video_name', 'unknown')}")
    with col6:
        st.write(f"**DURATION:** {st.session_state.get('duration', 0)}")

    # Option to use a custom AI prompt for summarization
    prompt = ""
    if st.checkbox("Use Custom Prompt"):
        prompt = utility_service.custom_prompt()

    summary = None

    # Columns for Summary and Time Range Summary options
    col0, col1 = st.columns([1, 1])

    # Button: Generate Full Summary
    with col0:
        if st.button("Summary"):
            with st.spinner("Generating summary..."):
                summary = utility_service.generate_summary(
                    st.session_state["show_video"],
                    st.session_state["show_video_name"],
                    False,
                    prompt,
                )

    # Checkbox: Generate Summary for Custom Time Range
    with col1:
        if st.checkbox("Custom Time Range Summary", help="Generate a summary for a specific time duration"):
            summary = video_range_summary.video_range_summary(
                st.session_state["show_video"],
                st.session_state["show_video_name"],
                prompt,
            )

    # Display generated summary if available
    if summary:
        st.write("**Summary:**")
        st.write(summary)

    # Section: Q&A Interaction
    # ------------------------
    # Allows users to ask questions about the video content.
    st.divider()
    st.write("Ask Questions About the Video")

    # Display existing question-answer pairs
    if st.session_state["qa_listing"]:
        with st.container(height=300):
            for qa in st.session_state["qa_listing"]:
                with st.chat_message("human"):
                    st.write(qa['question'])
                
                with st.chat_message("ai"):
                    st.write(qa["answer"])

    # Text Input: User Question Field
    st.chat_input(
        placeholder="e.g. What is the main topic discussed in the video?",
        key="question_input",
        on_submit=handle_question_submit,
    )

# Section: Empty State Warning
# ----------------------------
# Displays a message when no video is selected.
else:
    st.warning(
        "No video selected yet. Go to **Video List** and click any video to view it."
    )
