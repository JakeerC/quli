"""Main Streamlit application for Quli Quiz App."""

import streamlit as st

from quli.engine import QuizEngine
from quli.generator import QuizGenerator
from quli.ui.streamlit import config, question, results, utils

# Page configuration
st.set_page_config(
    page_title="Quli Quiz App",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
utils.initialize_session_state()


def main() -> None:
    """Main application entry point."""
    # Title and header
    st.title("📚 Quli Quiz App")
    st.markdown("**Powered by Gemini Flash 2.5** - Generate and take quizzes on any topic!")

    # Sidebar configuration
    quiz_config = config.render_quiz_config()

    # Main content area
    if quiz_config is None:
        st.info("👈 Configure your quiz in the sidebar to get started!")
        return

    # Check if we need to generate a new quiz
    current_config = st.session_state.get("quiz_config")
    config_changed = (
        current_config is None
        or current_config.topic != quiz_config.topic
        or current_config.num_questions != quiz_config.num_questions
        or current_config.difficulty != quiz_config.difficulty
        or set(current_config.question_types) != set(quiz_config.question_types)
    )

    if config_changed or st.session_state.get("quiz") is None:
        # Store config
        st.session_state.quiz_config = quiz_config

        # Generate quiz button
        if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
            generate_quiz(quiz_config)

    # Display quiz if available
    current_quiz = utils.get_quiz()
    if current_quiz is not None:
        display_quiz_interface(current_quiz)

    # Display results if quiz is complete
    result = utils.get_result()
    if result is not None:
        st.divider()
        results.render_results(result)

        # Option to start a new quiz
        if st.button("🔄 Start New Quiz", type="primary", use_container_width=True):
            utils.reset_quiz_state()
            st.rerun()


def generate_quiz(quiz_config) -> None:
    """Generate a quiz based on the configuration."""
    with st.spinner(
        f"Generating {quiz_config.num_questions} questions on '{quiz_config.topic}'..."
    ):
        try:
            generator = QuizGenerator()
            quiz = generator.generate_quiz(quiz_config)

            # Store quiz and create engine
            utils.set_quiz(quiz)
            engine = QuizEngine(quiz)
            utils.set_engine(engine)

            # Reset quiz state
            st.session_state.answers = {}
            st.session_state.current_question_index = 0
            st.session_state.quiz_started = False
            st.session_state.quiz_complete = False
            st.session_state.result = None

            st.success(f"✅ Generated {len(quiz)} questions!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating quiz: {str(e)}")
            st.info(
                "Please check your API key configuration. "
                "Make sure GEMINI_API_KEY is set in your environment or .env file."
            )


def display_quiz_interface(quiz) -> None:
    """Display the quiz interface for taking the quiz."""
    engine = utils.get_engine()
    if engine is None:
        return

    # Start quiz timer if not started
    if not st.session_state.get("quiz_started", False):
        engine.start()
        st.session_state.quiz_started = True

    current_index = utils.get_current_question_index()
    total_questions = len(quiz.questions)

    # Check if quiz is complete
    if current_index >= total_questions:
        # Calculate results
        if not st.session_state.get("quiz_complete", False):
            result = engine.get_result()
            utils.set_result(result)
            st.rerun()
        return

    # Get current question
    current_question = quiz.questions[current_index]
    question_num = current_index + 1

    # Display question
    question.render_question(current_question, question_num, total_questions)

    # Get answer input
    user_answer = question.render_answer_input(current_question, current_index)

    # Store answer
    if user_answer:
        st.session_state.answers[current_index] = user_answer

    mode = st.session_state.get("quiz_mode", "interactive")

    # Show feedback in interactive mode if answer was already submitted
    answer_submitted_to_engine = any(ans.question_index == current_index for ans in engine.answers)
    if mode == "interactive" and answer_submitted_to_engine:
        submitted_answer = st.session_state.answers.get(current_index)
        if submitted_answer:
            # Find the answer object
            user_answer_obj = next(
                (ans for ans in engine.answers if ans.question_index == current_index), None
            )
            if user_answer_obj:
                question.render_feedback(
                    current_question,
                    submitted_answer,
                    user_answer_obj.is_correct,
                    show_explanation=True,
                )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_index > 0 and st.button("⬅️ Previous", use_container_width=True):
            utils.set_current_question_index(current_index - 1)
            st.rerun()

    with col2:
        if mode == "interactive":
            # In interactive mode, submit answer and show feedback
            if user_answer and not answer_submitted_to_engine:
                if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                    submit_answer_and_continue(engine, current_question, user_answer, current_index)
            elif (
                answer_submitted_to_engine
                and current_index < total_questions - 1
                and st.button("➡️ Next Question", type="primary", use_container_width=True)
            ):
                # Answer submitted, show next button
                utils.set_current_question_index(current_index + 1)
                st.rerun()
        else:  # batch mode
            # In batch mode, just move to next question
            if current_index < total_questions - 1 and st.button(
                "➡️ Next", use_container_width=True
            ):
                utils.set_current_question_index(current_index + 1)
                st.rerun()

    with col3:
        # Last question - show submit quiz button for batch mode
        if (
            mode == "batch"
            and current_index == total_questions - 1
            and st.button("✅ Submit Quiz", type="primary", use_container_width=True)
        ):
            submit_all_answers(engine)


def submit_answer_and_continue(
    engine: QuizEngine, current_question, user_answer: str, question_index: int
) -> None:
    """Submit answer and move to next question in interactive mode."""
    user_answer_obj = engine.submit_answer(user_answer, question_index)

    # Move to next question
    if question_index < len(engine.quiz.questions) - 1:
        utils.set_current_question_index(question_index + 1)
    else:
        # Quiz complete
        result = engine.get_result()
        utils.set_result(result)

    st.rerun()


def submit_all_answers(engine: QuizEngine) -> None:
    """Submit all answers in batch mode."""
    # Submit all stored answers
    for index, answer in st.session_state.answers.items():
        if index < len(engine.quiz.questions):
            engine.submit_answer(answer, question_index=index)

    # Calculate results
    result = engine.get_result()
    utils.set_result(result)
    st.rerun()


def run_streamlit() -> None:
    """Entry point for streamlit script command."""
    import sys
    from pathlib import Path

    # Get the path to this file
    app_path = Path(__file__).resolve()
    # Run streamlit
    import streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", str(app_path)]
    stcli.main()


if __name__ == "__main__":
    main()
