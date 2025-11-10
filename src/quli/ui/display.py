"""Display functions for quiz questions and results."""

from rich.console import Console
from rich.table import Table

from quli.models import Question, QuestionType, QuizResult

console = Console()


def display_question(question: Question, question_num: int, total: int) -> None:
    """Display a question with formatting."""
    console.print(f"\n[bold cyan]Question {question_num}/{total}[/bold cyan]")
    console.print(f"[bold]{question.question_text}[/bold]\n")

    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        for i, option in enumerate(question.options, 1):
            console.print(f"  {i}. {option}")
    elif question.question_type == QuestionType.TRUE_FALSE:
        console.print("  1. True")
        console.print("  2. False")


def display_results(result: QuizResult, show_answers: bool = False) -> None:
    """Display quiz results."""
    console.print("\n" + "=" * 50)
    console.print("[bold cyan]Quiz Results[/bold cyan]")
    console.print("=" * 50 + "\n")

    score_color = "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"
    console.print(f"Score: [{score_color}]{result.score:.1f}%[/{score_color}]")
    console.print(f"Correct: {result.correct_answers}/{result.total_questions}")

    if result.time_taken:
        console.print(f"Time: {result.time_taken:.1f} seconds\n")

    if show_answers:
        table = Table(title="Question Review")
        table.add_column("Question", style="cyan")
        table.add_column("Your Answer", style="yellow")
        table.add_column("Correct Answer", style="green")
        table.add_column("Result", justify="center")

        for answer in result.answers:
            question = result.quiz.questions[answer.question_index]
            result_mark = "[green]✓[/green]" if answer.is_correct else "[red]✗[/red]"
            table.add_row(
                question.question_text[:50] + "...",
                answer.answer,
                question.correct_answer,
                result_mark,
            )

        console.print(table)
