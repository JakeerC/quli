# Quli - Quiz App

A quiz application powered by Gemini Flash 2.5 for generating quiz questions. Available as both a CLI tool and a Streamlit web interface.

## Table of Contents

- [Quli - Quiz App](#quli---quiz-app)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [CLI Styling and Accessibility](#cli-styling-and-accessibility)
    - [Themes](#themes)
    - [Symbols and Fonts](#symbols-and-fonts)
    - [Accessibility Notes](#accessibility-notes)
    - [Example](#example)
  - [File Responsibilities](#file-responsibilities)
  - [Folder structure](#folder-structure)
  - [Installation](#installation)
  - [Environment Variable Configuration](#environment-variable-configuration)
    - [Priority Order](#priority-order)
    - [Configuration Methods](#configuration-methods)
      - [1. System Environment Variables](#1-system-environment-variables)
      - [2. `.env` File (Project Root)](#2-env-file-project-root)
      - [3. `.zshenv` File (Zsh Users)](#3-zshenv-file-zsh-users)
      - [4. Standard Input (Piped)](#4-standard-input-piped)
      - [5. Interactive Prompting](#5-interactive-prompting)
      - [6. Custom Environment File (`--env-file`)](#6-custom-environment-file---env-file)
    - [Examples](#examples)
    - [Troubleshooting](#troubleshooting)
  - [Usage](#usage)
    - [Command-Line Options](#command-line-options)
    - [Basic Usage (Minimal Config)](#basic-usage-minimal-config)
    - [Interactive Mode](#interactive-mode)
    - [Batch Mode](#batch-mode)
    - [Advanced Configuration](#advanced-configuration)
    - [Answering Questions](#answering-questions)
    - [Examples](#examples-1)
  - [Streamlit Web Interface](#streamlit-web-interface)
    - [Launching the Streamlit App](#launching-the-streamlit-app)
    - [Streamlit Features](#streamlit-features)
    - [Streamlit vs CLI Comparison](#streamlit-vs-cli-comparison)
    - [Troubleshooting Streamlit](#troubleshooting-streamlit)
  - [Development](#development)

## Features

- Generate quiz questions on any topic using Gemini Flash 2.5
- Multiple choice and True/False question types
- Two quiz modes: Interactive (question-by-question) and Batch (all at once)
- **CLI Interface**: Terminal-based with arrow key navigation and configurable styling
- **Streamlit Web UI**: Modern web interface with visualizations and interactive charts
- Minimal configuration by default, advanced options available
- Built with Pydantic for data validation

## CLI Styling and Accessibility

Quli ships with configurable, accessible CLI styling. It uses Rich (already a dependency) and prompt-toolkit.

### Themes
- classic (default when color is available)
- high-contrast (better readability with strong colors)
- auto (chooses based on terminal capabilities)

Select with:

```bash
uv run quli --style auto        # or classic, high-contrast
```

### Symbols and Fonts
- Unicode symbols are used when supported by your terminal/locale.
- Nerd Font glyphs are used when available/preferred (e.g., JetBrains Mono Nerd Font). If unavailable, Quli falls back to Unicode or ASCII.

Overrides:

```bash
uv run quli --ascii                 # force ASCII-only symbols
uv run quli --unicode               # force Unicode symbols (if supported)
uv run quli --nerd-font             # prefer Nerd Font glyphs
uv run quli --no-nerd-font          # disable Nerd Font glyphs
```

Environment hints:
- Respect `NO_COLOR` (disables colors)
- Respect `TERM=dumb` (disables colors)
- Optional `NERD_FONT=1` to hint Nerd Font availability

### Accessibility Notes
- High-contrast theme emphasizes readability with minimal decoration.
- ASCII fallbacks ensure compatibility on limited environments.
- Unicode/nerd glyphs are only used when your terminal supports them.

### Example

```bash
uv run quli --style high-contrast --nerd-font
```

## File Responsibilities
- `cli.py`: CLI entry point, configuration gathering, orchestration
- `streamlit_app.py`: Streamlit web interface entry point
- `config.py`: Configuration management (API keys, environment variables, default settings)
- `models.py`: Pydantic data models (Question, Quiz, QuizConfig, UserAnswer, QuizResult)
- `generator.py`: Gemini API integration for quiz question generation
- `engine.py`: Quiz engine managing flow, scoring, answer validation, and timing
- `ui/display.py`: CLI question and results display formatting
- `ui/input.py`: CLI answer input handling (interactive and simple fallback)
- `ui/streamlit/`: Streamlit UI components (config, question, results, utils)
- `utils/selection.py`: Selection utilities (arrow keys, numbered options)
- `modes/interactive.py`: Interactive quiz mode (question-by-question with feedback)
- `modes/batch.py`: Batch quiz mode (all questions, then score)

## Folder structure
```
src/quli/
├── __init__.py
├── cli.py
├── streamlit_app.py          # Streamlit web interface
├── config.py
├── engine.py
├── generator.py
├── models.py
├── ui/
│   ├── __init__.py
│   ├── display.py (display_question, display_results)
│   ├── input.py (get_answer_interactive, get_answer_simple)
│   └── streamlit/            # Streamlit UI components
│       ├── __init__.py
│       ├── config.py         # Configuration UI
│       ├── question.py       # Question display components
│       ├── results.py        # Results and visualizations
│       └── utils.py          # Shared utilities
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

## Environment Variable Configuration

Quli supports flexible environment variable loading from multiple sources with a clear priority order. This allows you to configure the tool in a way that best fits your workflow.

### Priority Order

Environment variables are loaded in the following priority order (higher priority overrides lower):

1. **CLI arguments** (via `--env-file` option) - **Highest Priority**
2. **Standard input (stdin)**: piped or interactive entry
3. **`.zshenv` file** (if zsh is installed): checked in current directory first, then `~/.zshenv`
4. **`.env` file** (project root directory)
5. **System environment variables** (already set in your shell) - **Lowest Priority**

### Configuration Methods

#### 1. System Environment Variables

Set environment variables in your shell session:

```bash
export GEMINI_API_KEY="your-api-key-here"
```
```bash 
quli -t "Python"
```

#### 2. `.env` File (Project Root)

Create a `.env` file in your project root:

```bash
# .env
GEMINI_API_KEY=your-api-key-here
```

This is the traditional method and works automatically when you run Quli.

#### 3. `.zshenv` File (Zsh Users)

If you use zsh, Quli will automatically check for `.zshenv` files:

- **Current directory**: `./.zshenv` (checked first)
- **Home directory**: `~/.zshenv` (checked if current directory file doesn't exist)

Example `.zshenv` file:

```bash
# .zshenv
export GEMINI_API_KEY="your-api-key-here"
# Other environment variables
export CUSTOM_VAR="value"
```

**Note**: Quli only reads `.zshenv` files if zsh is installed on your system. If zsh is not available, this method is skipped.

#### 4. Standard Input (Piped)

Pipe environment variables from a file or command:

```bash
# From a file
cat .env | quli -t "Python"

# From echo
echo "GEMINI_API_KEY=your-key" | quli -t "Python"

# Multiple variables
cat <<EOF | quli -t "Python"
GEMINI_API_KEY=your-key
CUSTOM_VAR=value
EOF
```

**Supported formats:**
- `KEY=value`
- `export KEY=value`

#### 5. Interactive Prompting

If no environment variables are found and you're running Quli interactively (not piped), you'll be prompted to enter them:

```bash
quli -t "Python"
# If GEMINI_API_KEY is not set, you'll see:
# Enter environment variables (KEY=value format, one per line).
# Press Enter on empty line to finish, or Ctrl+D.
```

Enter variables one per line:
```
GEMINI_API_KEY=your-api-key-here
CUSTOM_VAR=value

# Press Enter on empty line to finish
```

#### 6. Custom Environment File (`--env-file`)

Specify a custom environment file path:

```bash
quli --env-file /path/to/custom.env -t "Python"
```

The file should be in standard `.env` format (KEY=value pairs).

### Examples

**Using .zshenv (automatic for zsh users):**
```bash
# Create .zshenv in your project directory
echo 'export GEMINI_API_KEY="your-key"' > .zshenv
quli -t "Python"  # Automatically loads from .zshenv
```

**Piping from stdin:**
```bash
echo "GEMINI_API_KEY=test-key" | quli -t "Test Quiz"
```

**Interactive entry:**
```bash
quli -t "Python"
# When prompted, enter:
# GEMINI_API_KEY=your-key
# [Press Enter on empty line]
```

**Using custom env file:**
```bash
quli --env-file ~/.config/quli.env -t "Python"
```

**Combining methods (priority example):**
```bash
# .env has: GEMINI_API_KEY=env-key
# stdin has: GEMINI_API_KEY=stdin-key
echo "GEMINI_API_KEY=stdin-key" | quli -t "Python"
# Result: Uses stdin-key (stdin overrides .env)
```

### Troubleshooting

**Environment variable not found:**
- Check that the variable is set in at least one of the supported sources
- Verify the variable name is correct (case-sensitive)
- For `.zshenv`, ensure zsh is installed (`which zsh`)
- Try using `--env-file` to explicitly specify a file

**`.zshenv` not being read:**
- Verify zsh is installed: `which zsh` or `zsh --version`
- Check file exists: `ls -la .zshenv` or `ls -la ~/.zshenv`
- Ensure file has correct format (KEY=value or export KEY=value)

**Interactive prompt not appearing:**
- Interactive prompts only appear when stdin is a TTY (not piped)
- If you're piping input, variables should be in the piped data
- Check that `GEMINI_API_KEY` is actually missing: `echo $GEMINI_API_KEY`

**Variable format issues:**
- Use `KEY=value` format (no spaces around =)
- For values with spaces, use quotes: `KEY="value with spaces"`
- Comments start with `#`
- Empty lines are ignored

## Usage

### Command-Line Options

| Option          | Short | Description                                                             |
| --------------- | ----- | ----------------------------------------------------------------------- |
| `--topic`       | `-t`  | Topic for the quiz (e.g., "Python programming")                         |
| `--interactive` | `-i`  | Run in interactive mode (question-by-question with immediate feedback)  |
| `--batch`       | `-b`  | Run in batch mode (answer all questions, then see results)              |
| `--advanced`    | `-a`  | Use advanced configuration (customize difficulty, question types, etc.) |
| `--env-file`    | `-e`  | Path to custom environment file (.env format) to load                   |

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

## Streamlit Web Interface

Quli includes a modern web-based interface built with Streamlit, providing an intuitive alternative to the CLI with visual feedback and interactive charts.

### Launching the Streamlit App

After installing dependencies, launch the web interface:

```bash
streamlit run src/quli/streamlit_app.py
```

Or use the convenience script (if configured):

```bash
uv run quli-streamlit
```

The app will open in your default web browser, typically at `http://localhost:8501`.

### Streamlit Features

**Configuration Sidebar:**
- Enter quiz topic
- Select number of questions (1-50)
- Choose difficulty level (Mixed, Easy, Medium, Hard)
- Select question types (Both, Multiple Choice only, True/False only)
- Choose quiz mode (Interactive or Batch)

**Interactive Quiz Taking:**
- Progress bar showing completion status
- Visual question display with difficulty indicators
- Radio button selection for answers
- Immediate feedback in Interactive mode (with explanations)
- Navigation buttons to move between questions

**Results & Visualizations:**
- **Score Overview**: Gauge chart showing your percentage score
- **Difficulty Breakdown**: Bar chart showing performance by difficulty level
- **Time Analysis**: Time spent per question (if available)
- **Question Review**: Expandable sections for each question with:
  - Your answer vs. correct answer
  - Explanations
  - Time taken per question

**UI/UX Enhancements:**
- Color-coded feedback (green for correct, red for incorrect)
- Progress tracking throughout the quiz
- Responsive layout that works on different screen sizes
- Easy navigation with Previous/Next buttons
- Option to start a new quiz after completion

### Streamlit vs CLI Comparison

| Feature                 | CLI                    | Streamlit UI                                         |
| ----------------------- | ---------------------- | ---------------------------------------------------- |
| Quiz Generation         | ✅                      | ✅                                                    |
| Interactive Mode        | ✅                      | ✅                                                    |
| Batch Mode              | ✅                      | ✅                                                    |
| Configuration Options   | ✅                      | ✅                                                    |
| Visual Feedback         | Text-based             | Visual with colors                                   |
| Charts & Visualizations | ❌                      | ✅ (Score gauge, difficulty breakdown, time analysis) |
| Question Review         | Table format           | Expandable sections                                  |
| Arrow Key Navigation    | ✅                      | ❌ (Uses radio buttons)                               |
| Terminal Integration    | ✅                      | ❌                                                    |
| Accessibility           | High (themes, symbols) | Good (web standards)                                 |

**When to use CLI:**
- Terminal-based workflows
- Scripting and automation
- Quick quizzes without opening a browser
- Prefer keyboard navigation

**When to use Streamlit:**
- Visual learners who benefit from charts
- Sharing quizzes with others (web-based)
- Detailed performance analysis
- Prefer mouse/touch interaction

### Troubleshooting Streamlit

**App won't start:**
- Ensure Streamlit is installed: `uv sync`
- Check that you're in the project root directory
- Verify your Python environment is activated

**API Key errors:**
- Make sure `GEMINI_API_KEY` is set in your environment or `.env` file
- Restart the Streamlit app after setting the key

**Visualizations not showing:**
- Ensure Plotly is installed: `uv sync`
- Check browser console for JavaScript errors
- Try refreshing the page

**Session state issues:**
- Use the "Start New Quiz" button to reset state
- Refresh the browser if the app becomes unresponsive

## Development

Run tests:
```bash
uv run pytest tests/
```

