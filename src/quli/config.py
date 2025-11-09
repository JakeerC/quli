"""Configuration management for the quiz app."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment."
        )
    return api_key


def get_default_config() -> dict[str, int | None | list[str]]:
    """Get default configuration values."""
    return {
        "num_questions": 5,
        "difficulty": None,
        "question_types": ["multiple_choice", "true_false"],
    }
