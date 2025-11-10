"""Selection utilities for interactive prompts."""

import sys

from rich.console import Console
from rich.prompt import Prompt

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

