from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import QuizAttempt
from app.schemas import QuizAttempt as QuizAttemptSchema

router = APIRouter()

@router.get("/attempts", response_model=List[QuizAttemptSchema])
def get_attempts(db: Session = Depends(get_db)):
    attempts = db.query(QuizAttempt).all()
    return attempts

@router.get("/attempts/{attempt_id}", response_model=QuizAttemptSchema)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt 