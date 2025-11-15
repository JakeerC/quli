"""Configuration management for the quiz app."""

import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


def detect_zsh_available() -> bool:
    """Check if zsh shell is installed and available."""
    return shutil.which("zsh") is not None


def parse_env_line(line: str) -> tuple[str, str] | None:
    """
    Parse a single environment variable line.

    Supports:
    - KEY=value
    - export KEY=value
    - Ignores comments (lines starting with #)
    - Ignores empty lines

    Returns:
        Tuple of (key, value) if valid, None otherwise
    """
    # Strip whitespace
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return None

    # Handle export KEY=value format
    if line.startswith("export "):
        line = line[7:].strip()  # Remove "export " prefix

    # Parse KEY=value
    if "=" in line:
        parts = line.split("=", 1)  # Split on first = only
        key = parts[0].strip()
        value = parts[1].strip()

        # Remove quotes if present
        if (
            value.startswith('"')
            and value.endswith('"')
            or value.startswith("'")
            and value.endswith("'")
        ):
            value = value[1:-1]

        if key:
            return (key, value)

    return None


def read_zsh_env_file(path: Path) -> dict[str, str]:
    """
    Read and parse a .zshenv file.

    Args:
        path: Path to the .zshenv file

    Returns:
        Dictionary of environment variables
    """
    env_vars: dict[str, str] = {}

    if not path.exists():
        return env_vars

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                parsed = parse_env_line(line)
                if parsed:
                    key, value = parsed
                    env_vars[key] = value
    except OSError:
        # Silently fail if file can't be read
        pass

    return env_vars


def read_env_from_stdin() -> dict[str, str]:
    """
    Read environment variables from standard input.

    Supports both KEY=value and export KEY=value formats.
    Only reads if stdin is not a TTY (i.e., data is piped).

    Returns:
        Dictionary of environment variables
    """
    env_vars: dict[str, str] = {}

    # Only read from stdin if it's not a TTY (i.e., data is piped)
    if sys.stdin.isatty():
        return env_vars

    try:
        for line in sys.stdin:
            parsed = parse_env_line(line)
            if parsed:
                key, value = parsed
                env_vars[key] = value
    except (EOFError, KeyboardInterrupt):
        # Handle Ctrl+D or Ctrl+C gracefully
        pass

    return env_vars


def load_environment_variables(
    env_file: Path | None = None,
    load_stdin: bool = True,
    load_zsh_env: bool = True,
) -> None:
    """
    Load environment variables from multiple sources in priority order.

    Priority order (higher priority overrides lower):
    1. CLI arguments (--env-file) - Highest Priority
    2. Standard input (stdin)
    3. .zshenv file (if zsh available)
    4. .env file
    5. System environment (lowest priority, already loaded)

    Variables are loaded in order, with later sources overriding earlier ones.

    Args:
        env_file: Optional path to a specific .env file to load (highest priority)
        load_stdin: Whether to read from stdin (default: True)
        load_zsh_env: Whether to load from .zshenv files (default: True)
    """
    # 1. Load from default .env file (overrides system env, but lower priority than other sources)
    # Only load if no custom env_file is specified (custom file will be loaded last)
    if not env_file:
        default_env_path = Path(__file__).parent.parent.parent / ".env"
        load_dotenv(default_env_path, override=True)  # Override system env

    # 2. Load from .zshenv file (if zsh is available, overrides .env)
    if load_zsh_env and detect_zsh_available():
        # Check current directory first, then home directory
        current_dir_zsh = Path.cwd() / ".zshenv"
        home_zsh = Path.home() / ".zshenv"

        zsh_env_vars: dict[str, str] = {}
        if current_dir_zsh.exists():
            zsh_env_vars.update(read_zsh_env_file(current_dir_zsh))
        if home_zsh.exists():
            zsh_env_vars.update(read_zsh_env_file(home_zsh))

        # Apply .zshenv variables (override .env)
        for key, value in zsh_env_vars.items():
            os.environ[key] = value  # Override .env and system env

    # 3. Load from stdin (override .zshenv and .env)
    if load_stdin:
        stdin_env_vars = read_env_from_stdin()
        for key, value in stdin_env_vars.items():
            os.environ[key] = value  # Override previous sources

    # 4. Load from custom env_file (--env-file, highest priority, overrides everything)
    if env_file:
        load_dotenv(env_file, override=True)  # Override all previous sources


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file, .zshenv file, stdin, or environment."
        )
    return api_key


def get_default_config() -> dict[str, int | None | list[str]]:
    """Get default configuration values."""
    return {
        "num_questions": 5,
        "difficulty": None,
        "question_types": ["multiple_choice", "true_false"],
    }
