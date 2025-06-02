from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.deps import get_db, get_current_user
from app.models import User, Chapter, Upload, Question
from app.schemas import Chapter, QuestionResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/by-upload/{upload_id}", response_model=List[Chapter])
def get_upload_chapters(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all chapters for a specific upload"""
    logger.info(f"Fetching chapters for upload {upload_id}")
    
    # Verify upload belongs to user
    upload = db.query(Upload).filter(
        Upload.id == upload_id,
        Upload.user_id == current_user.id
    ).first()
    if not upload:
        logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    chapters = db.query(Chapter).filter(Chapter.upload_id == upload_id).all()
    logger.info(f"Found {len(chapters)} chapters for upload {upload_id}")
    return chapters

@router.get("/{chapter_id}", response_model=Chapter)
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chapter"""
    logger.info(f"Fetching chapter {chapter_id}")
    
    chapter = db.query(Chapter).join(Upload).filter(
        Chapter.id == chapter_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not chapter:
        logger.warning(f"Chapter {chapter_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    logger.info(f"Successfully retrieved chapter {chapter_id}")
    return chapter

@router.get("/{chapter_id}/questions", response_model=List[QuestionResponse])
def get_chapter_questions(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all questions for a specific chapter"""
    logger.info(f"Fetching questions for chapter {chapter_id}")
    
    # Get the chapter and verify ownership
    chapter = db.query(Chapter).join(Upload).filter(
        Chapter.id == chapter_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not chapter:
        logger.warning(f"Chapter {chapter_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    # Get questions
    questions = db.query(Question).filter(Question.chapter_id == chapter_id).all()
    logger.info(f"Found {len(questions)} questions for chapter {chapter_id}")
    
    return questions

@router.post("/{chapter_id}/generate-questions")
async def generate_questions(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate questions for a chapter"""
    logger.info(f"Generating questions for chapter {chapter_id}")
    
    # Get the chapter and verify ownership
    chapter = db.query(Chapter).join(Upload).filter(
        Chapter.id == chapter_id,
        Upload.user_id == current_user.id
    ).first()
    
    if not chapter:
        logger.warning(f"Chapter {chapter_id} not found for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )
    
    try:
        # TODO: Implement question generation logic
        # For now, return a placeholder
        return {"message": "Question generation not implemented yet"}
        
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        ) 