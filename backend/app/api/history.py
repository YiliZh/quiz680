from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models import User, Attempt
from app.schemas import Attempt as AttemptSchema

router = APIRouter()

@router.get("/", response_model=List[AttemptSchema])
def get_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all quiz attempts for current user"""
    return db.query(Attempt).filter(Attempt.user_id == current_user.id).all()

@router.get("/{attempt_id}", response_model=AttemptSchema)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific quiz attempt"""
    attempt = db.query(Attempt).filter(
        Attempt.id == attempt_id,
        Attempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt 