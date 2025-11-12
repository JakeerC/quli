"""Configuration UI components for quiz setup."""

import streamlit as st

from quli.models import Difficulty, QuestionType, QuizConfig


def render_quiz_config() -> QuizConfig | None:
    """Render quiz configuration form in sidebar and return QuizConfig."""
    st.sidebar.header("Quiz Configuration")

    # Topic input
    topic = st.sidebar.text_input(
        "Topic",
        value="Python programming",
        help="Enter the topic for your quiz",
        key="config_topic",
    )

    # Number of questions
    num_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=50,
        value=5,
        help="Select how many questions you want in the quiz",
        key="config_num_questions",
    )

    # Difficulty selection
    difficulty_options = ["Mixed", "Easy", "Medium", "Hard"]
    difficulty_choice = st.sidebar.selectbox(
        "Difficulty Level",
        options=difficulty_options,
        index=0,
        help="Select difficulty level (Mixed includes all levels)",
        key="config_difficulty",
    )

    difficulty = None if difficulty_choice == "Mixed" else Difficulty(difficulty_choice.lower())

    # Question types
    question_type_options = ["Both", "Multiple Choice only", "True/False only"]
    type_choice = st.sidebar.selectbox(
        "Question Types",
        options=question_type_options,
        index=0,
        help="Select which types of questions to include",
        key="config_question_types",
    )

    question_types = []
    if "Multiple Choice" in type_choice or "Both" in type_choice:
        question_types.append(QuestionType.MULTIPLE_CHOICE)
    if "True/False" in type_choice or "Both" in type_choice:
        question_types.append(QuestionType.TRUE_FALSE)

    # Quiz mode selection
    mode = st.sidebar.radio(
        "Quiz Mode",
        options=["Interactive", "Batch"],
        index=0,
        help="Interactive: See feedback after each question. Batch: See results at the end.",
        key="config_mode",
    )

    # Validate topic
    if not topic or not topic.strip():
        st.sidebar.error("Please enter a topic for the quiz")
        return None

    # Create and return config
    config = QuizConfig(
        topic=topic.strip(),
        num_questions=num_questions,
        difficulty=difficulty,
        question_types=question_types,
    )

    # Store mode in session state
    st.session_state.quiz_mode = mode.lower()

    return config
