import streamlit as st
from services.utility_service import UtilityService
from pages import video_range_summary

utility_service = UtilityService()

# Initialize session state
if "qa_listing" not in st.session_state:
    st.session_state["qa_listing"] = []
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""

if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")


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


st.divider()
if st.session_state.get("show_video"):
    st.video(st.session_state["show_video"])
    st.write(st.session_state.get('show_video_name', 'unknown'))

    prompt = ""
    if st.checkbox("Use Custom Prompt"):
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
            summary = video_range_summary.video_range_summary(
                st.session_state["show_video"], st.session_state["show_video_name"], prompt)

    if summary:
        st.write("**Summary:**")
        st.write(summary)

    st.divider()
    st.write("Ask Questions About the Video")

    if st.session_state["qa_listing"]:
        with st.container(height=300):
            for qa in st.session_state["qa_listing"]:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"{qa['question']}")
                with col2:
                    st.write("")
                    st.write(qa['answer'])
                st.divider()

    # Text input
    st.text_input(
        "Type your question here:",
        placeholder="e.g., What is the main topic discussed in the video?",
        key="question_input",
        on_change=handle_question_submit
    )
else:
    st.warning(
        "No video selected yet. Go to **Video List** and click any video to view it."
    )
