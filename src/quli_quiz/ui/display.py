"""Display functions for quiz questions and results."""

from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from quli_quiz.models import Question, QuestionType, QuizResult
from quli_quiz.ui.styles import get_console, get_symbols


def display_question(question: Question, question_num: int, total: int) -> None:
    """Display a question with formatting."""
    console = get_console()
    symbols = get_symbols()

    # Build question content with left padding
    question_content = f"    [bold]{question.question_text}[/bold]\n"

    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        for i, option in enumerate(question.options, 1):
            question_content += f"    {symbols.arrow} {i}. {option}\n"
    elif question.question_type == QuestionType.TRUE_FALSE:
        question_content += f"    {symbols.arrow} 1. True\n"
        question_content += f"    {symbols.arrow} 2. False\n"

    # Display question in a bordered panel
    console.print(
        Panel(
            question_content.rstrip(),
            title=f"[section.title]Question {question_num}/{total}[/section.title]",
            border_style="section.title",
        )
    )


def display_results(result: QuizResult, show_answers: bool = False) -> None:
    """Display quiz results."""
    console = get_console()
    symbols = get_symbols()
    console.print(Rule(title="[section.title]Quiz Results[/section.title]"))

    score_color = "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"
    console.print(f"Score: [{score_color}]{result.score:.1f}%[/{score_color}]")
    console.print(f"Correct: {result.correct_answers}/{result.total_questions}")

    if result.time_taken:
        console.print(f"Time: {result.time_taken:.1f} seconds\n")

    if show_answers:
        table = Table(title="Question Review", show_lines=False, header_style="section.title")
        table.add_column("Question", style="cyan")
        table.add_column("Your Answer", style="yellow")
        table.add_column("Correct Answer", style="green")
        table.add_column("Result", justify="center")

        for answer in result.answers:
            question = result.quiz.questions[answer.question_index]
            mark = symbols.check if answer.is_correct else symbols.cross
            mark_color = "green" if answer.is_correct else "red"
            result_mark = f"[{mark_color}]{mark}[/{mark_color}]"
            table.add_row(
                question.question_text[:50] + "...",
                answer.answer,
                question.correct_answer,
                result_mark,
            )

        console.print(table)
