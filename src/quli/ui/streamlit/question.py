"""Question display and input components."""

import streamlit as st

from quli.models import Question, QuestionType


def render_question(question: Question, question_num: int, total: int) -> None:
    """Render a question with its options."""
    # Progress indicator
    progress = question_num / total
    st.progress(progress, text=f"Question {question_num} of {total}")

    # Question display
    st.markdown(f"### Question {question_num}/{total}")
    st.markdown(f"**{question.question_text}**")

    # Display difficulty badge
    difficulty_color = {
        "easy": "🟢",
        "medium": "🟡",
        "hard": "🔴",
    }
    difficulty_emoji = difficulty_color.get(question.difficulty.value, "⚪")
    st.caption(f"{difficulty_emoji} {question.difficulty.value.capitalize()}")

    # Display options
    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        st.markdown("**Options:**")
        for i, option in enumerate(question.options, 1):
            st.markdown(f"{i}. {option}")
    elif question.question_type == QuestionType.TRUE_FALSE:
        st.markdown("**Options:**")
        st.markdown("1. True")
        st.markdown("2. False")


def render_answer_input(question: Question, question_index: int) -> str | None:
    """Render answer input UI and return selected answer."""
    # Get stored answer if exists
    stored_answer = st.session_state.answers.get(question_index)

    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        # Radio buttons for multiple choice
        options = question.options
        option_labels = [f"{i + 1}. {opt}" for i, opt in enumerate(options)]

        selected_label = st.radio(
            "Select your answer:",
            options=option_labels,
            index=(
                options.index(stored_answer) if stored_answer and stored_answer in options else None
            ),
            key=f"answer_{question_index}",
        )

        if selected_label is not None:
            # Extract the actual answer from the selected label
            # Find the index of the selected label in option_labels
            label_index = option_labels.index(selected_label)
            answer = options[label_index]
            return answer

    elif question.question_type == QuestionType.TRUE_FALSE:
        # Radio buttons for True/False
        options = ["True", "False"]
        selected = st.radio(
            "Select your answer:",
            options=options,
            index=options.index(stored_answer) if stored_answer in options else None,
            key=f"answer_{question_index}",
        )
        return selected

    return None


def render_feedback(
    question: Question, user_answer: str, is_correct: bool, show_explanation: bool = True
) -> None:
    """Render feedback for a submitted answer."""
    if is_correct:
        st.success("✓ Correct!")
    else:
        st.error("✗ Incorrect")
        st.info(f"**Correct answer:** {question.correct_answer}")

    if show_explanation and question.explanation:
        with st.expander("Explanation"):
            st.markdown(question.explanation)
