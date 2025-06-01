from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.db import get_db
from app.models import Chapter
from app.schemas import Chapter as ChapterSchema

router = APIRouter()

@router.get("/{upload_id}/chapters", response_model=List[ChapterSchema])
def get_chapters(upload_id: int, db: Session = Depends(get_db)):
    chapters = db.query(Chapter).filter(Chapter.upload_id == upload_id).all()
    if not chapters:
        raise HTTPException(status_code=404, detail="Chapters not found")
    return chapters

@router.get("/{chapter_id}", response_model=ChapterSchema)
def get_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter 