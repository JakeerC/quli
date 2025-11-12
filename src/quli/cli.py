"""CLI interface for the quiz app."""

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule

from quli.engine import QuizEngine
from quli.generator import QuizGenerator
from quli.models import Difficulty, QuestionType, QuizConfig
from quli.modes import run_batch_mode, run_interactive_mode
from quli.ui.styles import build_console, detect_style
from quli.utils.selection import select_option

console = Console()


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
@click.option(
    "--style",
    type=click.Choice(["auto", "classic", "high-contrast"]),
    default="auto",
    show_default=True,
    help="CLI color theme",
)
@click.option(
    "--ascii",
    "ascii_override",
    flag_value=True,
    default=None,
    help="Force ASCII-only symbols",
)
@click.option(
    "--unicode",
    "ascii_override",
    flag_value=False,
    help="Force Unicode symbols (if supported)",
)
@click.option(
    "--nerd-font",
    "nerd_font",
    flag_value=True,
    default=None,
    help="Prefer Nerd Font glyphs (JetBrains Mono Nerd Font recommended)",
)
@click.option(
    "--no-nerd-font",
    "nerd_font",
    flag_value=False,
    help="Disable Nerd Font glyphs",
)
def main(
    topic: str | None,
    interactive: bool,
    batch: bool,
    advanced: bool,
    style: str,
    ascii_override: bool | None,
    nerd_font: bool | None,
) -> None:
    """Quli - CLI Quiz App powered by Gemini Flash 2.5."""
    # Build console with style
    style_config = detect_style(style)  # auto/classic/high-contrast
    if ascii_override is True:
        style_config.use_unicode = False
        style_config.use_nerd_font = False
        style_config.symbols = style_config.symbols  # will be reset below
    if nerd_font is not None:
        style_config.use_nerd_font = bool(nerd_font) and style_config.use_unicode
    # Refresh symbols based on final toggles
    # Re-import helper to avoid circular import
    from quli.ui.styles import _select_symbols as _sym_sel  # type: ignore

    style_config.symbols = _sym_sel(style_config.use_unicode, style_config.use_nerd_font)
    global console
    console = build_console(style_config)

    title = "[app.title]Quli Quiz App[/app.title]"
    subtitle = "[app.subtitle]Tip: use --help for available features/commands\n\tarrow keys to change options\n\tspace to select answer\n\tenter to submit answer[/app.subtitle]"
    console.print(Panel.fit(f"{title}\n{subtitle}", border_style="app.subtitle"))
    console.print(Rule(style="dim"))

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
