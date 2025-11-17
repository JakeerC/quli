"""Quiz engine for managing quiz flow and scoring."""

import time

from quli_quiz.models import Question, Quiz, QuizResult, UserAnswer


class QuizEngine:
    """Engine for managing quiz flow and scoring."""

    def __init__(self, quiz: Quiz):
        """Initialize the engine with a quiz."""
        self.quiz = quiz
        self.answers: list[UserAnswer] = []
        self.start_time: float | None = None
        self.current_question_index = 0

    def start(self) -> None:
        """Start the quiz timer."""
        self.start_time = time.time()

    def submit_answer(self, answer: str, question_index: int | None = None) -> UserAnswer:
        """Submit an answer for a question."""
        if question_index is None:
            question_index = self.current_question_index

        if question_index >= len(self.quiz.questions):
            raise ValueError(f"Question index {question_index} is out of range")

        question = self.quiz.questions[question_index]
        is_correct = self._check_answer(question, answer)

        # Calculate the time taken to answer if quiz has started
        if self.start_time is not None:  # noqa: SIM108
            time_taken = time.time() - self.start_time
        else:
            time_taken = None

        user_answer = UserAnswer(
            question_index=question_index,
            answer=answer,
            is_correct=is_correct,
            time_taken=time_taken,
        )

        self.answers.append(user_answer)
        self.current_question_index += 1

        return user_answer

    def _check_answer(self, question: Question, answer: str) -> bool:
        """Check if the answer is correct."""
        # Normalize answers for comparison
        correct = question.correct_answer.strip().lower()
        user_answer = answer.strip().lower()

        # For multiple choice, check if answer matches or if it's an option index
        if question.question_type.value == "multiple_choice":
            # Check direct match
            if user_answer == correct:
                return True
            # Check if answer is an option letter (A, B, C, D)
            option_letters = ["a", "b", "c", "d"]
            if user_answer in option_letters:
                option_index = option_letters.index(user_answer)
                if option_index < len(question.options):
                    return question.options[option_index].strip().lower() == correct
        elif question.question_type.value == "true_false":
            # For true/false, check exact match
            return user_answer == correct

        return False

    def get_current_question(self) -> Question | None:
        """Get the current question."""
        if self.current_question_index >= len(self.quiz.questions):
            return None
        return self.quiz.questions[self.current_question_index]

    def is_complete(self) -> bool:
        """Check if the quiz is complete."""
        return self.current_question_index >= len(self.quiz.questions)

    def get_result(self) -> QuizResult:
        """Calculate and return quiz results."""
        if not self.is_complete():
            raise ValueError("Quiz is not complete yet")

        end_time = time.time()
        total_time = (end_time - self.start_time) if self.start_time else None

        correct_count = sum(1 for answer in self.answers if answer.is_correct)
        total_questions = len(self.quiz.questions)
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0.0

        return QuizResult(
            quiz=self.quiz,
            answers=self.answers,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_count,
            time_taken=total_time,
        )

    def get_question_by_index(self, index: int) -> Question:
        """Get a question by its index."""
        if index >= len(self.quiz.questions):
            raise ValueError(f"Question index {index} is out of range")
        return self.quiz.questions[index]
