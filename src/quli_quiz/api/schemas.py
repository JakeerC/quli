from pydantic import BaseModel, ConfigDict

from quli_quiz.models import Question, Quiz, QuizConfig, QuizResult, UserAnswer


class QuestionCreate(Question):
    """Schema for creating a question."""

    pass


class QuestionRead(Question):
    """Schema for reading a question."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class QuizCreate(BaseModel):
    """Schema for creating a quiz."""

    topic: str
    config: QuizConfig


class QuizRead(Quiz):
    """Schema for reading a quiz."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserAnswerCreate(UserAnswer):
    """Schema for submitting an answer."""

    pass


class UserAnswerSubmit(BaseModel):
    """Schema for submitting an answer without correctness check."""

    question_index: int
    answer: str
    time_taken: float | None = None


class QuizSubmission(BaseModel):
    """Schema for submitting a complete quiz."""

    answers: list[UserAnswerSubmit]


class QuizResultRead(QuizResult):
    """Schema for reading quiz results."""

    id: int

    model_config = ConfigDict(from_attributes=True)
