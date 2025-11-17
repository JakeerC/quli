"""Results display and visualization components."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from quli_quiz.models import QuizResult


def render_results(result: QuizResult) -> None:
    """Render quiz results with statistics and review."""
    st.header("Quiz Results")

    # Score display with color coding
    score_color = "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", f"{result.score:.1f}%", delta=None)

    with col2:
        st.metric("Correct Answers", f"{result.correct_answers}/{result.total_questions}")

    with col3:
        time_str = format_time(result.time_taken) if result.time_taken else "N/A"
        st.metric("Time Taken", time_str)

    # Visualizations
    render_visualizations(result)

    # Question review
    st.subheader("Question Review")
    render_question_review(result)


def format_time(seconds: float | None) -> str:
    """Format time in seconds to a human-readable string."""
    if seconds is None:
        return "N/A"
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def render_visualizations(result: QuizResult) -> None:
    """Render visualizations for quiz results."""
    st.subheader("Performance Analysis")

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Score Overview", "Difficulty Breakdown", "Time Analysis"])

    with tab1:
        render_score_gauge(result)

    with tab2:
        render_difficulty_breakdown(result)

    with tab3:
        render_time_analysis(result)


def render_score_gauge(result: QuizResult) -> None:
    """Render a gauge chart for the score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=result.score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Score (%)"},
            delta={"reference": 70},
            gauge={
                "axis": {"range": [None, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 50], "color": "lightgray"},
                    {"range": [50, 70], "color": "gray"},
                    {"range": [70, 100], "color": "lightgreen"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 70,
                },
            },
        )
    )

    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


def render_difficulty_breakdown(result: QuizResult) -> None:
    """Render breakdown of performance by difficulty level."""
    # Group answers by difficulty
    difficulty_stats = {}
    for answer in result.answers:
        question = result.quiz.questions[answer.question_index]
        difficulty = question.difficulty.value

        if difficulty not in difficulty_stats:
            difficulty_stats[difficulty] = {"correct": 0, "incorrect": 0, "total": 0}

        difficulty_stats[difficulty]["total"] += 1
        if answer.is_correct:
            difficulty_stats[difficulty]["correct"] += 1
        else:
            difficulty_stats[difficulty]["incorrect"] += 1

    if not difficulty_stats:
        st.info("No difficulty breakdown available")
        return

    # Prepare data for chart
    difficulties = list(difficulty_stats.keys())
    correct_counts = [difficulty_stats[d]["correct"] for d in difficulties]
    incorrect_counts = [difficulty_stats[d]["incorrect"] for d in difficulties]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Correct",
                x=difficulties,
                y=correct_counts,
                marker_color="green",
            ),
            go.Bar(
                name="Incorrect",
                x=difficulties,
                y=incorrect_counts,
                marker_color="red",
            ),
        ]
    )

    fig.update_layout(
        barmode="group",
        title="Performance by Difficulty Level",
        xaxis_title="Difficulty",
        yaxis_title="Number of Questions",
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display percentage for each difficulty
    st.markdown("**Accuracy by Difficulty:**")
    for difficulty in difficulties:
        stats = difficulty_stats[difficulty]
        if stats["total"] > 0:
            accuracy = (stats["correct"] / stats["total"]) * 100
            st.metric(
                difficulty.capitalize(),
                f"{accuracy:.1f}%",
                f"{stats['correct']}/{stats['total']}",
            )


def render_time_analysis(result: QuizResult) -> None:
    """Render time analysis if time data is available."""
    # Check if we have time data per question
    times_per_question = []
    for answer in result.answers:
        if answer.time_taken is not None:
            times_per_question.append(answer.time_taken)

    if not times_per_question:
        st.info("Time data not available for individual questions")
        return

    # Time per question chart
    question_numbers = list(range(1, len(times_per_question) + 1))
    fig = px.bar(
        x=question_numbers,
        y=times_per_question,
        labels={"x": "Question Number", "y": "Time (seconds)"},
        title="Time Spent per Question",
        color=times_per_question,
        color_continuous_scale="Viridis",
    )

    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Time statistics
    if times_per_question:
        avg_time = sum(times_per_question) / len(times_per_question)
        max_time = max(times_per_question)
        min_time = min(times_per_question)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Time", f"{avg_time:.1f}s")
        with col2:
            st.metric("Max Time", f"{max_time:.1f}s")
        with col3:
            st.metric("Min Time", f"{min_time:.1f}s")


def render_question_review(result: QuizResult) -> None:
    """Render detailed review of all questions and answers."""
    for i, answer in enumerate(result.answers):
        question = result.quiz.questions[answer.question_index]
        question_num = i + 1

        with st.expander(
            f"Question {question_num}: {question.question_text[:60]}...",
            expanded=False,
        ):
            st.markdown(f"**Question:** {question.question_text}")

            # Display options
            if question.question_type.value == "multiple_choice":
                st.markdown("**Options:**")
                for j, option in enumerate(question.options, 1):
                    marker = "✓" if option == question.correct_answer else ""
                    user_marker = "← Your answer" if option == answer.answer else ""
                    st.markdown(f"{j}. {option} {marker} {user_marker}")
            else:
                st.markdown("**Options:** True / False")

            # Answer comparison
            col1, col2 = st.columns(2)
            with col1:
                status = "✅ Correct" if answer.is_correct else "❌ Incorrect"
                st.markdown(f"**Your Answer:** {answer.answer} {status}")

            with col2:
                st.markdown(f"**Correct Answer:** {question.correct_answer}")

            # Explanation
            if question.explanation:
                st.markdown(f"**Explanation:** {question.explanation}")

            # Time taken (if available)
            if answer.time_taken:
                st.caption(f"Time taken: {answer.time_taken:.1f} seconds")
