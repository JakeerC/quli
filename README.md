# Quli - CLI Quiz App

A command-line quiz application powered by Gemini Flash 2.5 for generating quiz questions.

## Table of Contents

- [Quli - CLI Quiz App](#quli---cli-quiz-app)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [File Responsibilities](#file-responsibilities)
  - [Folder structure](#folder-structure)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Command-Line Options](#command-line-options)
    - [Basic Usage (Minimal Config)](#basic-usage-minimal-config)
    - [Interactive Mode](#interactive-mode)
    - [Batch Mode](#batch-mode)
    - [Advanced Configuration](#advanced-configuration)
    - [Answering Questions](#answering-questions)
    - [Examples](#examples)
  - [Development](#development)

## Features

- Generate quiz questions on any topic using Gemini Flash 2.5
- Multiple choice and True/False question types
- Interactive arrow key navigation
- Two quiz modes: Interactive (question-by-question) and Batch (all at once)
- Minimal configuration by default, advanced options available
- Built with Pydantic for data validation
- Designed for easy scaling to Streamlit

## File Responsibilities
- `cli.py`: Main entry point, configuration gathering, orchestration
- `config.py`: Configuration management (API keys, environment variables, default settings)
- `models.py`: Pydantic data models (Question, Quiz, QuizConfig, UserAnswer, QuizResult)
- `generator.py`: Gemini API integration for quiz question generation
- `engine.py`: Quiz engine managing flow, scoring, answer validation, and timing
- `ui/display.py`: Question and results display formatting
- `ui/input.py`: Answer input handling (interactive and simple fallback)
- `utils/selection.py`: Selection utilities (arrow keys, numbered options)
- `modes/interactive.py`: Interactive quiz mode (question-by-question with feedback)
- `modes/batch.py`: Batch quiz mode (all questions, then score)

## Folder structure
```
src/quli/
├── __init__.py
├── cli.py
├── config.py
├── engine.py
├── generator.py
├── models.py
├── ui/
│   ├── __init__.py
│   ├── display.py (display_question, display_results)
│   └── input.py (get_answer_interactive, get_answer_simple)
├── utils/
│   ├── __init__.py
│   └── selection.py (select_option, select_with_arrows)
└── modes/
    ├── __init__.py
    ├── interactive.py (run_interactive_mode)
    └── batch.py (run_batch_mode)
```

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

### Command-Line Options

| Option          | Short | Description                                                             |
| --------------- | ----- | ----------------------------------------------------------------------- |
| `--topic`       | `-t`  | Topic for the quiz (e.g., "Python programming")                         |
| `--interactive` | `-i`  | Run in interactive mode (question-by-question with immediate feedback)  |
| `--batch`       | `-b`  | Run in batch mode (answer all questions, then see results)              |
| `--advanced`    | `-a`  | Use advanced configuration (customize difficulty, question types, etc.) |

**Note:** If no topic is provided, the app will prompt for advanced configuration interactively.

### Basic Usage (Minimal Config)

The simplest way to run a quiz is to provide just a topic. By default, this runs in interactive mode with 5 questions:

```bash
uv run quli --topic "Python programming"
```

This will:
- Generate 5 questions about Python programming
- Include both multiple choice and true/false questions
- Use mixed difficulty levels
- Show immediate feedback after each answer

### Interactive Mode

Interactive mode shows one question at a time with immediate feedback after each answer:

```bash
uv run quli --topic "Python programming" --interactive
```

**What to expect:**
- Questions are displayed one at a time
- After answering, you'll see if you were correct or incorrect
- The correct answer is shown if you got it wrong
- Explanations are displayed when available
- Press Enter to continue to the next question
- Final results are shown at the end

**Example flow:**
```
Question 1/5: What is the output of print(2 + 2)?
A) 3
B) 4
C) 5
D) 6

[Use arrow keys to select, Enter to confirm]
✓ Correct!

Press Enter to continue
```

### Batch Mode

Batch mode lets you answer all questions first, then shows your results at the end:

```bash
uv run quli --topic "Python programming" --batch
```

**What to expect:**
- All questions are displayed sequentially
- You answer each question without immediate feedback
- After answering all questions, you'll see:
  - Your final score (percentage)
  - Number of correct answers
  - Total time taken
  - Review of all questions with your answers and correct answers

**Use case:** Best for timed quizzes or when you want to answer all questions before seeing results.

### Advanced Configuration

Run without arguments or use the `--advanced` flag to access interactive configuration:

```bash
uv run quli
# or
uv run quli --advanced
```

**Configuration options:**
- **Topic:** Enter any topic for your quiz
- **Number of questions:** Choose how many questions (default: 5)
- **Difficulty level:** Easy, Medium, Hard, or Mixed (default)
- **Question types:** Multiple Choice only, True/False only, or Both (default)

**Example:**
```bash
uv run quli --advanced --topic "Machine Learning" --interactive
```

### Answering Questions

**Multiple Choice Questions:**
- Use **arrow keys** (↑/↓) to navigate between options
- Press **Enter** to confirm your selection
- Or type the option letter (A, B, C, D) and press Enter
- If arrow keys don't work, you'll be prompted to type the option number

**True/False Questions:**
- Use **arrow keys** (↑/↓) to select True or False
- Press **Enter** to confirm
- Or type "True" or "False" directly

**Keyboard Shortcuts:**
- `Ctrl+C`: Cancel the quiz at any time
- `Enter`: Confirm selection or continue to next question
- `↑/↓`: Navigate options (in interactive input mode)

### Examples

**Quick quiz on a specific topic:**
```bash
uv run quli -t "JavaScript"
```

**Hard difficulty quiz with 10 questions:**
```bash
uv run quli -a -t "Data Structures" -i
# Then select: 10 questions, Hard difficulty
```

**Batch mode for timed practice:**
```bash
uv run quli -t "Algorithms" -b
```

**True/False only quiz:**
```bash
uv run quli -a -t "History"
# Then select: True/False only
```

## Development

Run tests:
```bash
uv run pytest tests/
```

