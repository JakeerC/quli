from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from quli_quiz.api.database import Base, get_db
from quli_quiz.api.main import app
from quli_quiz.models import Difficulty, Question, QuestionType, Quiz, QuizConfig

# Setup in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_module(module):
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    Base.metadata.drop_all(bind=engine)


@patch("quli_quiz.api.routes.QuizGenerator")
def test_create_quiz(mock_generator_cls):
    # Setup mock
    mock_generator = MagicMock()
    mock_generator_cls.return_value = mock_generator

    mock_quiz = Quiz(
        topic="Math",
        config=QuizConfig(topic="Math", num_questions=1),
        questions=[
            Question(
                question_text="1+1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["1", "2", "3", "4"],
                correct_answer="2",
                difficulty=Difficulty.EASY,
            )
        ],
    )
    mock_generator.generate_quiz.return_value = mock_quiz

    response = client.post(
        "/quizzes/",
        json={
            "topic": "Math",
            "config": {
                "topic": "Math",
                "num_questions": 1,
                "difficulty": "easy",
                "question_types": ["multiple_choice"],
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Math"
    assert data["id"] is not None
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question_text"] == "1+1?"


@patch("quli_quiz.api.routes.QuizGenerator")
def test_submit_quiz(mock_generator_cls):
    # Reuse create logic to get a quiz ID
    # (Or we could refactor to share setup, but copying for simplicity here)
    mock_generator = MagicMock()
    mock_generator_cls.return_value = mock_generator

    mock_quiz = Quiz(
        topic="Math",
        config=QuizConfig(topic="Math", num_questions=1),
        questions=[
            Question(
                question_text="1+1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=["1", "2", "3", "4"],
                correct_answer="2",
                difficulty=Difficulty.EASY,
            )
        ],
    )
    mock_generator.generate_quiz.return_value = mock_quiz

    # Create quiz
    create_response = client.post(
        "/quizzes/",
        json={
            "topic": "Math",
            "config": {
                "topic": "Math",
                "num_questions": 1,
                "difficulty": "easy",
                "question_types": ["multiple_choice"],
            },
        },
    )
    quiz_id = create_response.json()["id"]

    # Submit correct answer
    response = client.post(
        f"/quizzes/{quiz_id}/submit",
        json={"answers": [{"question_index": 0, "answer": "2", "time_taken": 5.0}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 100.0
    assert data["correct_answers"] == 1

    # Submit incorrect answer
    response = client.post(
        f"/quizzes/{quiz_id}/submit",
        json={"answers": [{"question_index": 0, "answer": "3", "time_taken": 2.0}]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 0.0
    assert data["correct_answers"] == 0
