"""Selection utilities for interactive prompts."""

import sys

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.widgets import RadioList
from rich.console import Console
from rich.prompt import Prompt

from quli.ui.styles import get_console, get_symbols

console = Console()


def select_option(
    options: list[str], prompt_text: str = "Select an option", default: int = 0
) -> str:
    """Select an option using arrow keys."""

    # Use rich's Confirm for simple yes/no, but for multiple options we'll use a custom approach
    # For now, we'll use a numbered list with input
    console = get_console()
    symbols = get_symbols()
    console.print(f"\n[bold]{prompt_text}[/bold]")
    for i, option in enumerate(options, 1):
        marker = symbols.arrow if i == default + 1 else " "
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
        # Use a nerd font select character if available, otherwise fallback to default
        try:
            open_character: str = "["
            select_character = ""
            close_character: str = "]"
        except Exception:
            open_character: str = "("
            select_character = "●"
            close_character: str = ")"
        # Create radio list for selection, customizing the marker if possible (prompt_toolkit 3.0.30+)
        radio_list = RadioList(
            values=[(i, opt) for i, opt in enumerate(options)],
            open_character=open_character,
            select_character=select_character,
            close_character=close_character,
            show_scrollbar=False,
        )

        # Create key bindings
        kb = KeyBindings()

        # Enter key submits the selection
        # Use eager=True to ensure this binding takes precedence over default RadioList behavior
        @kb.add("enter", eager=True)
        def submit(event):
            # Get the currently selected value from the radio list
            selected_index = radio_list.current_value
            event.app.exit(result=selected_index)

        # Control+C quits the quiz
        @kb.add("c-c")
        def quit_app(event):
            get_console().print("\n[yellow]Quiz cancelled[/yellow]")
            sys.exit(0)

        app = Application(
            layout=Layout(HSplit([radio_list])),
            key_bindings=kb,
            full_screen=False,
        )

        result = app.run()
        if result is not None:
            return options[result]
        else:
            # If no result, return the first option as fallback
            return options[0]
    except KeyboardInterrupt:
        get_console().print("\n[yellow]Quiz cancelled[/yellow]")
        sys.exit(0)
    except (ImportError, Exception):
        # Fallback to simple selection
        return select_option(options, prompt_text)
