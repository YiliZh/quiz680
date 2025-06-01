from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models import User, Chapter, Upload
from app.schemas import Chapter as ChapterSchema

router = APIRouter()

@router.get("/{upload_id}/chapters", response_model=List[ChapterSchema])
def get_chapters(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chapters for a specific upload"""
    # Verify upload belongs to user
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return db.query(Chapter).filter(Chapter.upload_id == upload_id).all()

@router.get("/{chapter_id}", response_model=ChapterSchema)
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chapter"""
    chapter = db.query(Chapter).join(Upload).filter(
        Chapter.id == chapter_id,
        Upload.user_id == current_user.id
    ).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter 