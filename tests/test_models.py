"""Tests for Pydantic models."""

import pytest

from quli_quiz.models import Difficulty, Question, QuestionType, Quiz, QuizConfig, QuizResult, UserAnswer


def test_question_validation():
    """Test question validation."""
    # Valid multiple choice question
    question = Question(
        question_text="What is 2+2?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=["3", "4", "5", "6"],
        correct_answer="4",
        difficulty=Difficulty.EASY,
    )
    assert question.validate_options()

    # Valid true/false question
    question = Question(
        question_text="Python is a programming language.",
        question_type=QuestionType.TRUE_FALSE,
        options=["True", "False"],
        correct_answer="True",
        difficulty=Difficulty.EASY,
    )
    assert question.validate_options()

    # Invalid true/false (wrong options)
    question = Question(
        question_text="Test",
        question_type=QuestionType.TRUE_FALSE,
        options=["Yes", "No"],
        correct_answer="Yes",
        difficulty=Difficulty.EASY,
    )
    assert not question.validate_options()


def test_quiz_config():
    """Test quiz configuration."""
    config = QuizConfig(topic="Python")
    assert config.topic == "Python"
    assert config.num_questions == 5
    assert config.difficulty is None
    assert len(config.question_types) == 2

    config = QuizConfig(
        topic="Math",
        num_questions=10,
        difficulty=Difficulty.HARD,
        question_types=[QuestionType.MULTIPLE_CHOICE],
    )
    assert config.num_questions == 10
    assert config.difficulty == Difficulty.HARD
    assert len(config.question_types) == 1


def test_quiz():
    """Test quiz model."""
    config = QuizConfig(topic="Test")
    questions = [
        Question(
            question_text="Q1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["A", "B", "C", "D"],
            correct_answer="A",
            difficulty=Difficulty.EASY,
        )
    ]
    quiz = Quiz(topic="Test", questions=questions, config=config)
    assert len(quiz) == 1
    assert quiz.topic == "Test"


def test_quiz_result():
    """Test quiz result calculation."""
    config = QuizConfig(topic="Test")
    questions = [
        Question(
            question_text="Q1",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["A", "B"],
            correct_answer="A",
            difficulty=Difficulty.EASY,
        ),
        Question(
            question_text="Q2",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["A", "B"],
            correct_answer="B",
            difficulty=Difficulty.EASY,
        ),
    ]
    quiz = Quiz(topic="Test", questions=questions, config=config)

    answers = [
        UserAnswer(question_index=0, answer="A", is_correct=True),
        UserAnswer(question_index=1, answer="A", is_correct=False),
    ]

    result = QuizResult(
        quiz=quiz,
        answers=answers,
        score=50.0,
        total_questions=2,
        correct_answers=1,
    )

    assert result.score == 50.0
    assert result.percentage == 50.0
    assert result.correct_answers == 1
    assert result.total_questions == 2

