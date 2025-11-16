"""Shared utilities for Streamlit UI components."""

import streamlit as st

from quli_quiz.engine import QuizEngine
from quli_quiz.models import Quiz, QuizResult


def initialize_session_state() -> None:
    """Initialize session state variables for quiz flow."""
    if "quiz_config" not in st.session_state:
        st.session_state.quiz_config = None
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "quiz_mode" not in st.session_state:
        st.session_state.quiz_mode = "interactive"  # or "batch"
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_complete" not in st.session_state:
        st.session_state.quiz_complete = False
    if "result" not in st.session_state:
        st.session_state.result = None


def reset_quiz_state() -> None:
    """Reset all quiz-related session state."""
    st.session_state.quiz_config = None
    st.session_state.quiz = None
    st.session_state.engine = None
    st.session_state.answers = {}
    st.session_state.current_question_index = 0
    st.session_state.quiz_started = False
    st.session_state.quiz_complete = False
    st.session_state.result = None


def format_time(seconds: float | None) -> str:
    """Format time in seconds to a human-readable string."""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def get_current_question_index() -> int:
    """Get the current question index from session state."""
    return st.session_state.get("current_question_index", 0)


def set_current_question_index(index: int) -> None:
    """Set the current question index in session state."""
    st.session_state.current_question_index = index


def get_quiz() -> Quiz | None:
    """Get the current quiz from session state."""
    return st.session_state.get("quiz")


def get_engine() -> QuizEngine | None:
    """Get the current quiz engine from session state."""
    return st.session_state.get("engine")


def set_quiz(quiz: Quiz) -> None:
    """Set the quiz in session state."""
    st.session_state.quiz = quiz


def set_engine(engine: QuizEngine) -> None:
    """Set the quiz engine in session state."""
    st.session_state.engine = engine


def get_result() -> QuizResult | None:
    """Get the quiz result from session state."""
    return st.session_state.get("result")


def set_result(result: QuizResult) -> None:
    """Set the quiz result in session state."""
    st.session_state.result = result
    st.session_state.quiz_complete = True
