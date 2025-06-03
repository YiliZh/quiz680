from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models import User, QuestionAttempt
from app.schemas import QuestionAttemptResponseSchema

router = APIRouter()

@router.get("/", response_model=List[QuestionAttemptResponseSchema])
def get_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all quiz attempts for current user"""
    return db.query(QuestionAttempt).filter(QuestionAttempt.user_id == current_user.id).all()

@router.get("/{attempt_id}", response_model=QuestionAttemptResponseSchema)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific quiz attempt"""
    attempt = db.query(QuestionAttempt).filter(
        QuestionAttempt.id == attempt_id,
        QuestionAttempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt 