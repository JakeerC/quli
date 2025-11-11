"""Centralized CLI styling: themes, symbols, and auto-detection."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Literal

from rich.console import Console
from rich.theme import Theme

# ---------------------------
# Public data structures
# ---------------------------


@dataclass(frozen=True)
class SymbolSet:
    check: str
    cross: str
    arrow: str
    bullet: str
    spinner_name: str


@dataclass
class StyleConfig:
    theme: Literal["classic", "high-contrast"]
    use_color: bool
    use_unicode: bool
    use_nerd_font: bool
    symbols: SymbolSet


# ---------------------------
# Symbol sets
# ---------------------------

NERD_SYMBOLS = SymbolSet(
    check="󰄬",  # Nerd font check
    cross="󰅖",  # Nerd font cross
    arrow="󰁔",  # Nerd font arrow
    bullet="•",
    spinner_name="dots",
)

UNICODE_SYMBOLS = SymbolSet(
    check="✓",
    cross="✗",
    arrow="➜",
    bullet="•",
    spinner_name="dots",
)

ASCII_SYMBOLS = SymbolSet(
    check="OK",
    cross="X",
    arrow=">",
    bullet="*",
    spinner_name="line",
)


# ---------------------------
# Theme palettes
# ---------------------------

CLASSIC_THEME = Theme(
    {
        "app.title": "bold blue",
        "app.subtitle": "cyan",
        "section.title": "bold cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
        "dim": "dim",
    }
)

HIGH_CONTRAST_THEME = Theme(
    {
        "app.title": "bold bright_white on black",
        "app.subtitle": "bright_white",
        "section.title": "bold bright_cyan",
        "success": "bold bright_green",
        "warning": "bold bright_yellow",
        "error": "bold bright_red",
        "dim": "bright_white",
    }
)


# ---------------------------
# Global state and helpers
# ---------------------------

_GLOBAL_CONSOLE: Console | None = None
_GLOBAL_SYMBOLS: SymbolSet = ASCII_SYMBOLS
_GLOBAL_STYLE: StyleConfig | None = None


def _detect_color_enabled() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    term = os.environ.get("TERM", "")
    if term == "dumb":
        return False
    try:
        tmp_console = Console()
        return tmp_console.color_system is not None
    except Exception:
        return False


def _detect_unicode_enabled() -> bool:
    # Basic heuristic: Windows terminals pre-10 were problematic; Python's stdout encoding helps
    encoding = getattr(sys.stdout, "encoding", "") or ""
    # If encoding supports UTF-8, consider unicode usable
    return "UTF" in encoding.upper()


def _detect_nerd_font_hint() -> bool:
    # Heuristics: explicit env, popular terminal emulators with NF, or user-set hint
    if os.environ.get("NERD_FONT", "").lower() in {"1", "true", "yes", "on"}:
        return True
    if os.environ.get("NO_NERD_FONT", "").lower() in {"1", "true", "yes", "on"}:
        return False
    emulator = (os.environ.get("TERMINAL_EMULATOR") or os.environ.get("TERM_PROGRAM") or "").lower()
    # This is only a weak hint; we still require unicode capability
    return any(name in emulator for name in ["iterm", "alacritty", "wezterm", "kitty"])


def _select_symbols(use_unicode: bool, use_nerd_font: bool) -> SymbolSet:
    if use_unicode and use_nerd_font:
        return NERD_SYMBOLS
    if use_unicode:
        return UNICODE_SYMBOLS
    return ASCII_SYMBOLS


def detect_style(preference: Literal["auto", "classic", "high-contrast"] = "auto") -> StyleConfig:
    """Detect a reasonable default StyleConfig based on terminal capabilities."""
    color = _detect_color_enabled()
    unicode_ok = _detect_unicode_enabled()
    nerd_hint = _detect_nerd_font_hint()

    theme = ("high-contrast" if not color else "classic") if preference == "auto" else preference

    use_nerd = bool(nerd_hint and unicode_ok)
    symbols = _select_symbols(use_unicode=unicode_ok, use_nerd_font=use_nerd)

    return StyleConfig(
        theme=theme,  # type: ignore[arg-type]
        use_color=color,
        use_unicode=unicode_ok,
        use_nerd_font=use_nerd,
        symbols=symbols,
    )


def build_console(style: StyleConfig) -> Console:
    """Create a Rich Console per style, caching as global."""
    global _GLOBAL_CONSOLE, _GLOBAL_SYMBOLS, _GLOBAL_STYLE
    palette = CLASSIC_THEME if style.theme == "classic" else HIGH_CONTRAST_THEME
    console = Console(
        theme=palette, color_system=None if not style.use_color else "auto", soft_wrap=False
    )
    _GLOBAL_CONSOLE = console
    _GLOBAL_SYMBOLS = style.symbols
    _GLOBAL_STYLE = style
    return console


def get_console() -> Console:
    """Get the global console. Falls back to a default if not initialized."""
    global _GLOBAL_CONSOLE
    if _GLOBAL_CONSOLE is None:
        # Initialize with auto-detected default
        build_console(detect_style("auto"))
    return _GLOBAL_CONSOLE  # type: ignore[return-value]


def get_symbols() -> SymbolSet:
    return _GLOBAL_SYMBOLS


def get_style() -> StyleConfig | None:
    return _GLOBAL_STYLE
