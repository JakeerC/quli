from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from quli_quiz.api.database import Base


class QuestionModel(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, index=True)
    question_type = Column(String)
    options = Column(JSON)  # Store list of strings as JSON
    correct_answer = Column(String)
    difficulty = Column(String)
    explanation = Column(String, nullable=True)

    quizzes = relationship("QuizQuestionLink", back_populates="question")


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    config = Column(JSON)  # Store QuizConfig as JSON

    questions = relationship("QuizQuestionLink", back_populates="quiz")
    results = relationship("QuizResultModel", back_populates="quiz")


class QuizQuestionLink(Base):
    __tablename__ = "quiz_question_links"

    quiz_id = Column(Integer, ForeignKey("quizzes.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), primary_key=True)

    quiz = relationship("QuizModel", back_populates="questions")
    question = relationship("QuestionModel", back_populates="quizzes")


class UserAnswerModel(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("quiz_results.id"))
    question_index = Column(Integer)
    answer = Column(String)
    is_correct = Column(Boolean)
    time_taken = Column(Float, nullable=True)

    result = relationship("QuizResultModel", back_populates="answers")


class QuizResultModel(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    score = Column(Float)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    time_taken = Column(Float, nullable=True)

    quiz = relationship("QuizModel", back_populates="results")
    answers = relationship("UserAnswerModel", back_populates="result")
