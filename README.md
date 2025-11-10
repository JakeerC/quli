# Quli - CLI Quiz App

A command-line quiz application powered by Gemini Flash 2.5 for generating quiz questions.

## Features

- Generate quiz questions on any topic using Gemini Flash 2.5
- Multiple choice and True/False question types
- Interactive arrow key navigation
- Two quiz modes: Interactive (question-by-question) and Batch (all at once)
- Minimal configuration by default, advanced options available
- Built with Pydantic for data validation
- Designed for easy scaling to Streamlit

## File responsibilities
- `cli.py`: Main entry point, configuration gathering, orchestration
- `ui/display.py`: Question and results display formatting
- `ui/input.py`: Answer input handling (interactive and simple fallback)
- `utils/selection.py`: Selection utilities (arrow keys, numbered options)
- `modes/interactive.py`: Interactive quiz mode (question-by-question with feedback)
- `modes/batch.py`: Batch quiz mode (all questions, then score)


## Installation

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### Basic Usage (Minimal Config)
```bash
uv run quli --topic "Python programming"
```

### Interactive Mode
```bash
uv run quli --topic "Python programming" --interactive
```

### Batch Mode
```bash
uv run quli --topic "Python programming" --batch
```

### Advanced Configuration
Run without arguments to access interactive configuration:
```bash
uv run quli
```

## Development

Run tests:
```bash
uv run pytest tests/
```

