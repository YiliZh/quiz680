from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models import Question, QuestionAttempt
from app.schemas import QuestionCreateSchema, QuestionResponseSchema, AnswerSubmitSchema, QuestionAttemptResponseSchema
from app.services.quiz import generate_questions

router = APIRouter()

@router.get("/{chapter_id}/questions", response_model=List[QuestionResponseSchema])
def get_questions(chapter_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")
    return questions

@router.post("/{chapter_id}/questions", response_model=List[QuestionResponseSchema])
async def create_questions(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Generate questions for a chapter"""
    # ... existing code ...

@router.post("/{question_id}/answer", response_model=QuestionAttemptResponseSchema)
async def submit_answer(
    question_id: int,
    answer: AnswerSubmitSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit an answer to a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    is_correct = answer.chosen_answer == question.correct_answer
    attempt = QuestionAttempt(
        user_id=current_user.id,
        question_id=question_id,
        chosen_answer=answer.chosen_answer,
        is_correct=is_correct
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return {
        "id": attempt.id,
        "user_id": attempt.user_id,
        "question_id": attempt.question_id,
        "chosen_answer": attempt.chosen_answer,
        "is_correct": attempt.is_correct,
        "attempted_at": attempt.attempted_at
    } 