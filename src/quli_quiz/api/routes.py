from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from quli_quiz.api import models, schemas
from quli_quiz.api.database import get_db
from quli_quiz.generator import QuizGenerator
from quli_quiz.models import Difficulty, Question, QuestionType, Quiz, QuizConfig, UserAnswer

router = APIRouter()


@router.post("/quizzes/", response_model=schemas.QuizRead)
def create_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db)):  # noqa: B008
    # Initialize generator
    try:
        generator = QuizGenerator()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    # Generate quiz
    try:
        generated_quiz = generator.generate_quiz(quiz.config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}") from e

    # Create QuizModel
    db_quiz = models.QuizModel(
        topic=generated_quiz.topic,
        config=generated_quiz.config.model_dump(),
    )
    db.add(db_quiz)
    db.flush()  # Flush to get ID

    # Save questions and link them
    db_questions = []
    for q in generated_quiz.questions:
        # Create QuestionModel
        db_q = models.QuestionModel(
            question_text=q.question_text,
            question_type=q.question_type.value,
            options=q.options,
            correct_answer=q.correct_answer,
            difficulty=q.difficulty.value,
            explanation=q.explanation,
        )
        db.add(db_q)
        db.flush()  # Get ID

        # Link to quiz
        link = models.QuizQuestionLink(quiz_id=db_quiz.id, question_id=db_q.id)
        db.add(link)

        # Add to list for response
        # We need to manually construct the Pydantic model from the DB model to match the schema
        # or rely on the relationship if we commit and refresh.
        # However, the relationship returns QuizQuestionLink objects, not QuestionModel objects directly
        # in the way Pydantic expects for `questions: list[Question]`.
        # The schema QuizRead expects `questions: list[Question]`.
        # But `db_quiz.questions` is a list of `QuizQuestionLink`.
        # We need to fix the response model or the schema.

        # Actually, let's fix the schema to handle this or construct the response manually.
        # For now, let's just append the Pydantic question object we already have,
        # but we need the ID.
        q_read = schemas.QuestionRead(id=db_q.id, **q.model_dump())
        db_questions.append(q_read)

    db.commit()
    db.refresh(db_quiz)

    # Construct response manually to avoid relationship mapping issues for now
    return schemas.QuizRead(
        id=db_quiz.id, topic=db_quiz.topic, questions=db_questions, config=quiz.config
    )


def check_answer(question: models.QuestionModel, answer: str) -> bool:
    """Check if the answer is correct (logic from engine.py)."""
    # Normalize answers for comparison
    correct = question.correct_answer.strip().lower()
    user_answer = answer.strip().lower()

    # For multiple choice, check if answer matches or if it's an option index
    if question.question_type == "multiple_choice":
        # Check direct match
        if user_answer == correct:
            return True
        # Check if answer is an option letter (A, B, C, D)
        option_letters = ["a", "b", "c", "d"]
        if user_answer in option_letters:
            option_index = option_letters.index(user_answer)
            if option_index < len(question.options):
                return question.options[option_index].strip().lower() == correct
    elif question.question_type == "true_false":
        # For true/false, check exact match
        return user_answer == correct

    return False


@router.post("/quizzes/{quiz_id}/submit", response_model=schemas.QuizResultRead)
def submit_quiz(quiz_id: int, submission: schemas.QuizSubmission, db: Session = Depends(get_db)):  # noqa: B008
    quiz = db.query(models.QuizModel).filter(models.QuizModel.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get questions (assuming order is stable/consistent with what client saw)
    # Ideally we should sort by ID or something deterministic
    # quiz.questions is a list of QuizQuestionLink
    quiz_links = sorted(quiz.questions, key=lambda x: x.question_id)

    if not quiz_links:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    correct_count = 0
    total_questions = len(quiz_links)
    user_answers_db = []

    for ans in submission.answers:
        if ans.question_index < 0 or ans.question_index >= total_questions:
            continue

        link = quiz_links[ans.question_index]
        question = link.question

        # Check answer
        is_correct = check_answer(question, ans.answer)
        if is_correct:
            correct_count += 1

        user_answers_db.append(
            {
                "question_index": ans.question_index,
                "answer": ans.answer,
                "is_correct": is_correct,
                "time_taken": ans.time_taken,
            }
        )

    score = (correct_count / total_questions * 100) if total_questions > 0 else 0.0

    # Create Result
    db_result = models.QuizResultModel(
        quiz_id=quiz_id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_count,
        time_taken=sum(a["time_taken"] or 0 for a in user_answers_db),
    )
    db.add(db_result)
    db.flush()

    # Add answers
    for ans_data in user_answers_db:
        db_ans = models.UserAnswerModel(result_id=db_result.id, **ans_data)
        db.add(db_ans)

    db.commit()
    db.refresh(db_result)

    # Reconstruct Quiz Pydantic object
    quiz_questions = []
    # Sort links by question_id (same as we did for checking)
    sorted_links = sorted(quiz.questions, key=lambda x: x.question_id)
    for link in sorted_links:
        q = link.question
        quiz_questions.append(
            Question(
                question_text=q.question_text,
                question_type=QuestionType(q.question_type),
                options=q.options,
                correct_answer=q.correct_answer,
                difficulty=Difficulty(q.difficulty),
                explanation=q.explanation,
            )
        )

    pydantic_quiz = Quiz(
        topic=quiz.topic, questions=quiz_questions, config=QuizConfig(**quiz.config)
    )

    # Reconstruct UserAnswers
    pydantic_answers = []
    for ans in db_result.answers:
        pydantic_answers.append(
            UserAnswer(
                question_index=ans.question_index,
                answer=ans.answer,
                is_correct=ans.is_correct,
                time_taken=ans.time_taken,
            )
        )

    return schemas.QuizResultRead(
        id=db_result.id,
        quiz=pydantic_quiz,
        answers=pydantic_answers,
        score=db_result.score,
        total_questions=db_result.total_questions,
        correct_answers=db_result.correct_answers,
        time_taken=db_result.time_taken,
    )
