import streamlit as st
from services.utility_service import UtilityService
utility_service = UtilityService()

# Initialize session state
if "qa_listing" not in st.session_state:
    st.session_state["qa_listing"] = []
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""

if st.button("Back", key="back"):
    st.switch_page("pages/video_list.py")

st.divider()
if st.session_state.get("show_video"):
    st.video(st.session_state["show_video"])
    st.write(st.session_state.get('show_video_name', 'unknown'))

    prompt = ""
    if st.checkbox("Use Custom Prompt"):
        prompt = utility_service.custom_prompt()

    summary = None
    if st.button("Summary"):
        with st.spinner("Generating summary..."):
            summary = utility_service.generate_summary(
                st.session_state["show_video"], st.session_state["show_video_name"], False, prompt)
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
        on_change=utility_service.handle_question_submit
    )
else:
    st.warning(
        "No video selected yet. Go to **Video List** and click any video to view it."
    )
