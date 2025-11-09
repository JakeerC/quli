"""CLI interface for the quiz app."""

import sys

import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from quli.engine import QuizEngine
from quli.generator import QuizGenerator
from quli.models import Difficulty, Question, QuestionType, QuizConfig

console = Console()


def select_option(
    options: list[str], prompt_text: str = "Select an option", default: int = 0
) -> str:
    """Select an option using arrow keys."""
    from rich.prompt import Prompt

    # Use rich's Confirm for simple yes/no, but for multiple options we'll use a custom approach
    # For now, we'll use a numbered list with input
    console.print(f"\n[bold]{prompt_text}[/bold]")
    for i, option in enumerate(options, 1):
        marker = "→" if i == default + 1 else " "
        console.print(f"  {marker} {i}. {option}")

    while True:
        try:
            choice = Prompt.ask(
                f"\nEnter your choice (1-{len(options)})",
                default=str(default + 1),
            )
            index = int(choice) - 1
            if 0 <= index < len(options):
                return options[index]
            console.print(
                f"[red]Invalid choice. Please enter a number between 1 and {len(options)}[/red]"
            )
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            sys.exit(0)


def select_with_arrows(options: list[str], prompt_text: str = "Select an option") -> str:
    """Select an option using arrow keys with prompt_toolkit."""
    try:
        from prompt_toolkit.application import Application
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.layout import HSplit, Layout
        from prompt_toolkit.widgets import RadioList

        # Create radio list for selection
        radio_list = RadioList(values=[(i, opt) for i, opt in enumerate(options)])

        app = Application(
            layout=Layout(HSplit([radio_list])),
            key_bindings=KeyBindings(),
            full_screen=False,
        )

        result = app.run()
        return options[result]
    except (ImportError, Exception):
        # Fallback to simple selection
        return select_option(options, prompt_text)


def get_advanced_config() -> QuizConfig:
    """Get advanced configuration through interactive prompts."""
    console.print("\n[bold cyan]Advanced Quiz Configuration[/bold cyan]\n")

    topic = Prompt.ask("Enter quiz topic", default="General Knowledge")

    num_questions = int(Prompt.ask("Number of questions", default="5", show_default=True))

    difficulty_options = ["Easy", "Medium", "Hard", "Mixed (default)"]
    difficulty_choice = select_option(difficulty_options, "Select difficulty level", default=3)
    difficulty = None if "Mixed" in difficulty_choice else Difficulty(difficulty_choice.lower())

    question_type_options = ["Multiple Choice only", "True/False only", "Both (default)"]
    type_choice = select_option(question_type_options, "Select question types", default=2)

    question_types = []
    if "Multiple Choice" in type_choice or "Both" in type_choice:
        question_types.append(QuestionType.MULTIPLE_CHOICE)
    if "True/False" in type_choice or "Both" in type_choice:
        question_types.append(QuestionType.TRUE_FALSE)

    return QuizConfig(
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty,
        question_types=question_types,
    )


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


def get_answer_interactive(question: Question) -> str:
    """Get answer interactively with arrow key navigation."""
    options = question.options.copy()
    if question.question_type == QuestionType.TRUE_FALSE:
        options = ["True", "False"]

    selected = select_with_arrows(options, "Select your answer")
    return selected


def get_answer_simple(question: Question) -> str:
    """Get answer using simple input (fallback)."""
    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        options_text = "\n".join([f"  {i + 1}. {opt}" for i, opt in enumerate(question.options)])
        console.print(options_text)
        while True:
            try:
                choice = Prompt.ask("\nEnter your answer (number or text)", default="1")
                # Try as number first
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(question.options):
                        return question.options[index]
                except ValueError:
                    pass
                # Try as direct text match
                if choice in question.options:
                    return choice
                console.print("[red]Invalid answer. Please try again.[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Cancelled[/yellow]")
                sys.exit(0)
    else:  # TRUE_FALSE
        options = ["True", "False"]
        selected = select_option(options, "Select True or False")
        return selected


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


def display_results(result, show_answers: bool = False) -> None:
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


@click.command()
@click.option(
    "--topic",
    "-t",
    help="Topic for the quiz",
    default=None,
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Run in interactive mode (question-by-question)",
)
@click.option(
    "--batch",
    "-b",
    is_flag=True,
    help="Run in batch mode (all questions, then score)",
)
@click.option(
    "--advanced",
    "-a",
    is_flag=True,
    help="Use advanced configuration",
)
def main(topic: str | None, interactive: bool, batch: bool, advanced: bool) -> None:
    """Quli - CLI Quiz App powered by Gemini Flash 2.5."""
    console.print("[bold blue]Quli Quiz App[/bold blue]\n")

    # Determine mode
    mode = "interactive" if interactive else "batch" if batch else "interactive"

    # Get configuration
    if advanced or topic is None:  # noqa: SIM108
        config = get_advanced_config()
    else:
        # Minimal config
        config = QuizConfig(topic=topic)
    # ternary code of above
    # config = get_advanced_config() if advanced or topic is None else QuizConfig(topic=topic)

    # Generate quiz
    console.print(f"\n[bold]Generating quiz on '{config.topic}'...[/bold]")
    try:
        generator = QuizGenerator()
        quiz = generator.generate_quiz(config)
        console.print(f"[green]Generated {len(quiz)} questions![/green]\n")
    except Exception as e:
        console.print(f"[red]Error generating quiz: {str(e)}[/red]")
        sys.exit(1)

    # Create engine and run quiz
    engine = QuizEngine(quiz)

    if mode == "interactive":
        run_interactive_mode(engine)
    else:
        run_batch_mode(engine)


if __name__ == "__main__":
    main()
