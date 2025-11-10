"""Batch quiz mode implementation."""

from rich.console import Console

from quli.engine import QuizEngine
from quli.ui.display import display_question, display_results
from quli.ui.input import get_answer_interactive, get_answer_simple

console = Console()


def run_batch_mode(engine: QuizEngine) -> None:
    """Run quiz in batch mode (all questions, then score)."""
    console.print("\n[bold green]Starting Batch Quiz Mode[/bold green]\n")
    console.print("Answer all questions, then we'll show your results.\n")
    engine.start()

    # Collect all answers
    answers_map = {}
    for i, question in enumerate(engine.quiz.questions):
        question_num = i + 1
        total = len(engine.quiz.questions)

        display_question(question, question_num, total)

        try:
            answer = get_answer_interactive(question)
        except (OSError, ImportError):
            answer = get_answer_simple(question)

        answers_map[i] = answer
        console.print()

    # Submit all answers
    for i, answer in answers_map.items():
        engine.submit_answer(answer, question_index=i)

    # Show results
    result = engine.get_result()
    display_results(result, show_answers=True)

