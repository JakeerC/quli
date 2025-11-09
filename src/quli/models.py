"""Pydantic models for quiz data structures."""

from enum import Enum

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    """Question type enumeration."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"


class Difficulty(str, Enum):
    """Difficulty level enumeration."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(BaseModel):
    """Model representing a single quiz question."""

    question_text: str = Field(..., description="The question text")
    question_type: QuestionType = Field(..., description="Type of question")
    options: list[str] = Field(..., description="List of answer options")
    correct_answer: str = Field(..., description="The correct answer")
    difficulty: Difficulty = Field(..., description="Difficulty level")
    explanation: str | None = Field(None, description="Explanation of the correct answer")

    def validate_options(self) -> bool:
        """Validate that options match question type."""
        if self.question_type == QuestionType.TRUE_FALSE:
            # Normalize for comparison
            options_set = {opt.strip() for opt in self.options}
            return len(self.options) == 2 and options_set == {"True", "False"}
        elif self.question_type == QuestionType.MULTIPLE_CHOICE:
            # Check that correct answer is in options (case-insensitive)
            options_lower = [opt.strip().lower() for opt in self.options]
            correct_lower = self.correct_answer.strip().lower()
            return len(self.options) >= 2 and (
                correct_lower in options_lower or self.correct_answer in self.options
            )
        return False


class QuizConfig(BaseModel):
    """Configuration model for quiz generation."""

    topic: str = Field(..., description="Topic for the quiz")
    num_questions: int = Field(default=5, ge=1, le=50, description="Number of questions")
    difficulty: Difficulty | None = Field(
        default=None, description="Difficulty level (None = mixed)"
    )
    question_types: list[QuestionType] = Field(
        default_factory=lambda: [QuestionType.MULTIPLE_CHOICE, QuestionType.TRUE_FALSE],
        description="Types of questions to include",
    )


class Quiz(BaseModel):
    """Model representing a complete quiz."""

    topic: str = Field(..., description="Quiz topic")
    questions: list[Question] = Field(..., description="List of questions")
    config: QuizConfig = Field(..., description="Configuration used to generate quiz")

    def __len__(self) -> int:
        """Return the number of questions."""
        return len(self.questions)


class UserAnswer(BaseModel):
    """Model representing a user's answer to a question."""

    question_index: int = Field(..., ge=0, description="Index of the question")
    answer: str = Field(..., description="User's selected answer")
    is_correct: bool = Field(..., description="Whether the answer is correct")
    time_taken: float | None = Field(None, description="Time taken to answer in seconds")


class QuizResult(BaseModel):
    """Model representing quiz results."""

    quiz: Quiz = Field(..., description="The quiz that was taken")
    answers: list[UserAnswer] = Field(..., description="User's answers")
    score: float = Field(..., description="Final score as percentage")
    total_questions: int = Field(..., description="Total number of questions")
    correct_answers: int = Field(..., description="Number of correct answers")
    time_taken: float | None = Field(None, description="Total time taken in seconds")

    @property
    def percentage(self) -> float:
        """Return score as percentage."""
        return self.score

