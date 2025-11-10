"""Interactive quiz mode implementation."""

from rich.console import Console
from rich.prompt import Prompt

from quli.engine import QuizEngine
from quli.ui.display import display_question, display_results
from quli.ui.input import get_answer_interactive, get_answer_simple

console = Console()


def run_interactive_mode(engine: QuizEngine) -> None:
    """Run quiz in interactive mode (question-by-question)."""
    console.print("\n[bold green]Starting Interactive Quiz Mode[/bold green]\n")
    engine.start()

    while not engine.is_complete():
        question = engine.get_current_question()
        if question is None:
            break

        question_num = engine.current_question_index + 1
        total = len(engine.quiz.questions)

        display_question(question, question_num, total)

        try:
            answer = get_answer_interactive(question)
        except (OSError, ImportError):
            # Fallback if arrow keys don't work
            answer = get_answer_simple(question)

        user_answer = engine.submit_answer(answer)

        # Show immediate feedback
        if user_answer.is_correct:
            console.print("\n[bold green]✓ Correct![/bold green]")
        else:
            console.print("\n[bold red]✗ Incorrect[/bold red]")
            console.print(f"[yellow]Correct answer: {question.correct_answer}[/yellow]")

        if question.explanation:
            console.print(f"[dim]{question.explanation}[/dim]")

        if question_num < total:
            Prompt.ask("\nPress Enter to continue", default="")

    # Show results
    result = engine.get_result()
    display_results(result)
