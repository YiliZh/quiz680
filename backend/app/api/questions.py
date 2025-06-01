from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import Question, QuizAttempt
from app.schemas import Question as QuestionSchema, QuizAttempt as QuizAttemptSchema

router = APIRouter()

@router.get("/{chapter_id}/questions", response_model=List[QuestionSchema])
def get_questions(chapter_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")
    return questions

@router.post("/{question_id}/answer", response_model=QuizAttemptSchema)
def submit_answer(question_id: int, chosen_idx: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    is_correct = chosen_idx == question.answer_key
    attempt = QuizAttempt(user_id=1, question_id=question_id, chosen_idx=chosen_idx, is_correct=is_correct)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt 