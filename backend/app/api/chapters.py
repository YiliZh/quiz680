from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.deps import get_db, get_current_user
from app.models import User, Chapter, Upload, Question
from app.schemas import ChapterSchema, QuestionResponseSchema
from app.services.question_generator import QuestionGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/uploads/{upload_id}/chapters", response_model=List[ChapterSchema])
def get_chapters(
    upload_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all chapters for a specific upload with pagination.
    """
    logger.info(f"Fetching chapters for upload {upload_id} (page {page}, size {page_size}) for user {current_user.id}")
    
    try:
        # First verify the upload belongs to the user
        upload = db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.user_id == current_user.id
        ).first()
        
        if not upload:
            logger.warning(f"Upload {upload_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Get total count for pagination
        total = db.query(Chapter).filter(Chapter.upload_id == upload_id).count()
        logger.debug(f"Total chapters found: {total}")
        
        # Get paginated chapters
        chapters = db.query(Chapter).filter(
            Chapter.upload_id == upload_id
        ).order_by(Chapter.chapter_no).offset((page - 1) * page_size).limit(page_size).all()
        
        logger.info(f"Successfully fetched {len(chapters)} chapters for upload {upload_id}")
        logger.debug(f"Chapters: {[{'id': c.id, 'title': c.title, 'chapter_no': c.chapter_no} for c in chapters]}")
        
        return chapters
        
    except Exception as e:
        logger.error(f"Error fetching chapters for upload {upload_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{chapter_id}", response_model=ChapterSchema)
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific chapter by ID"""
    logger.info(f"Fetching chapter {chapter_id} for user {current_user.id}")
    
    try:
        # Log the query parameters
        logger.debug(f"Query parameters - chapter_id: {chapter_id}, user_id: {current_user.id}")
        
        # First check if the chapter exists
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            logger.warning(f"Chapter {chapter_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Then verify ownership through the upload
        upload = db.query(Upload).filter(
            Upload.id == chapter.upload_id,
            Upload.user_id == current_user.id
        ).first()
        
        if not upload:
            logger.warning(f"Upload {chapter.upload_id} not found or not owned by user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )
        
        # Log successful fetch
        logger.info(f"Successfully fetched chapter {chapter_id}")
        logger.debug(f"Chapter details - id: {chapter.id}, title: {chapter.title}, chapter_no: {chapter.chapter_no}")
        
        return chapter
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the full error details
        logger.error(f"Error fetching chapter {chapter_id}: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        
        # Raise a more detailed error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching chapter: {str(e)}"
        )

@router.get("/{chapter_id}/questions", response_model=List[QuestionResponseSchema])
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

@router.post("/{chapter_id}/generate-questions", response_model=List[QuestionResponseSchema])
async def generate_questions(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    num_questions: int = Query(5, ge=1, le=20)
):
    """Generate questions for a specific chapter"""
    logger.info(f"Generating {num_questions} questions for chapter {chapter_id}")
    
    try:
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
        
        # Initialize question generator
        generator = QuestionGenerator()
        
        # Generate questions
        questions = generator.generate_questions(chapter, num_questions)
        
        # Save questions to database
        db_questions = []
        for question in questions:
            db_question = Question(
                question_text=question.question_text,
                question_type=question.question_type,
                options=question.options,
                correct_answer=question.correct_answer,
                difficulty=question.difficulty,
                chapter_id=chapter_id
            )
            db.add(db_question)
            db_questions.append(db_question)
        
        db.commit()
        
        # Refresh questions to get their IDs
        for question in db_questions:
            db.refresh(question)
        
        logger.info(f"Successfully generated and saved {len(db_questions)} questions for chapter {chapter_id}")
        return db_questions
        
    except Exception as e:
        logger.error(f"Error generating questions for chapter {chapter_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating questions"
        ) 