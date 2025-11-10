"""Input handling functions for quiz answers."""

import sys

from rich.console import Console
from rich.prompt import Prompt

from quli.models import Question, QuestionType
from quli.utils.selection import select_option, select_with_arrows

console = Console()


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

