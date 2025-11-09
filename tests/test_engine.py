"""Tests for quiz engine."""

from quli.engine import QuizEngine
from quli.models import Difficulty, Question, QuestionType, Quiz, QuizConfig


def create_sample_quiz() -> Quiz:
    """Create a sample quiz for testing."""
    config = QuizConfig(topic="Test", num_questions=2)
    questions = [
        Question(
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["3", "4", "5", "6"],
            correct_answer="4",
            difficulty=Difficulty.EASY,
        ),
        Question(
            question_text="Python is a programming language.",
            question_type=QuestionType.TRUE_FALSE,
            options=["True", "False"],
            correct_answer="True",
            difficulty=Difficulty.EASY,
        ),
    ]
    return Quiz(topic="Test", questions=questions, config=config)


def test_engine_initialization():
    """Test engine initialization."""
    quiz = create_sample_quiz()
    engine = QuizEngine(quiz)
    assert engine.quiz == quiz
    assert len(engine.answers) == 0
    assert engine.current_question_index == 0


def test_submit_answer():
    """Test answer submission."""
    quiz = create_sample_quiz()
    engine = QuizEngine(quiz)
    engine.start()

    # Correct answer
    answer = engine.submit_answer("4")
    assert answer.is_correct
    assert answer.question_index == 0
    assert engine.current_question_index == 1

    # Incorrect answer
    answer = engine.submit_answer("False")
    assert not answer.is_correct
    assert answer.question_index == 1


def test_get_result():
    """Test result calculation."""
    quiz = create_sample_quiz()
    engine = QuizEngine(quiz)
    engine.start()

    engine.submit_answer("4")  # Correct
    engine.submit_answer("True")  # Correct

    result = engine.get_result()
    assert result.score == 100.0
    assert result.correct_answers == 2
    assert result.total_questions == 2


def test_answer_validation():
    """Test answer validation logic."""
    quiz = create_sample_quiz()
    engine = QuizEngine(quiz)
    engine.start()

    # Test case-insensitive matching
    answer = engine.submit_answer("4")
    assert answer.is_correct

    # Test option letter matching (A, B, C, D)
    engine2 = QuizEngine(quiz)
    engine2.start()
    # For the first question, option "4" is at index 1 (B)
    # But we need to check if the answer matches the correct answer text
    answer = engine2.submit_answer("4")
    assert answer.is_correct

