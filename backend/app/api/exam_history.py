from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import logging

from ..database import get_db
from ..models import ExamSession, Question, Chapter, Upload, User, ReviewRecommendation
from ..schemas.exam_session import (
    ExamSessionWithDetails,
    ExamSessionCreate,
    ReviewRecommendation as ReviewRecommendationSchema
)
from ..schemas.review_recommendation import ReviewRecommendationWithQuestion
from ..core.deps import get_current_user
from ..models.user import User as UserModel

router = APIRouter()

logger = logging.getLogger(__name__)

class ReviewRecommendationBatchCreate(BaseModel):
    exam_session_id: int
    question_ids: List[int]

class QuestionReviewDetail(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[List[str]]
    correct_answer: str
    explanation: Optional[str]
    chapter_title: str
    book_title: str

@router.get("/history", response_model=dict)
def get_exam_history(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get user's exam history with details"""
    # Get total count
    total = db.query(ExamSession).filter(ExamSession.user_id == current_user.id).count()
    
    exam_sessions = (
        db.query(ExamSession)
        .filter(ExamSession.user_id == current_user.id)
        .order_by(ExamSession.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for session in exam_sessions:
        chapter = db.query(Chapter).filter(Chapter.id == session.chapter_id).first()
        upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
        
        session_dict = session.__dict__
        session_dict["chapter_title"] = chapter.title
        session_dict["book_title"] = upload.filename
        
        # Add detailed logging for debugging
        logger.info(f"Processing exam session {session.id}:")
        logger.info(f"Raw values - score: {session.score} (type: {type(session.score)}), total_questions: {session.total_questions} (type: {type(session.total_questions)})")
        logger.info(f"Session completed_at: {session.completed_at}")
        
        # Safely calculate performance percentage
        try:
            performance_percentage = (session.score / session.total_questions) * 100
            logger.info(f"Calculated performance: {performance_percentage}%")
        except (ZeroDivisionError, TypeError) as e:
            logger.error(f"Error calculating performance: {str(e)}")
            performance_percentage = 0.0
        
        session_dict["performance_percentage"] = performance_percentage
        
        # Get attempts for this session
        attempts = []
        for attempt in session.attempts:
            question = db.query(Question).filter(Question.id == attempt.question_id).first()
            attempts.append({
                "question_text": question.question_text,
                "user_answer": attempt.chosen_answer,
                "correct_answer": question.correct_answer,
                "is_correct": attempt.is_correct,
                "explanation": question.explanation
            })
        session_dict["attempts"] = attempts
        result.append(ExamSessionWithDetails(**session_dict))
    
    return {
        "items": result,
        "total": total
    }

@router.get("/review-recommendations", response_model=dict)
def get_review_recommendations(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get review recommendations for the user"""
    # Get total count
    total = db.query(ReviewRecommendation).filter(ReviewRecommendation.user_id == current_user.id).count()
    
    recommendations = (
        db.query(ReviewRecommendation)
        .filter(ReviewRecommendation.user_id == current_user.id)
        .order_by(ReviewRecommendation.next_review_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    result = []
    for rec in recommendations:
        question = db.query(Question).filter(Question.id == rec.question_id).first()
        chapter = db.query(Chapter).filter(Chapter.id == question.chapter_id).first()
        upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
        
        # Make both datetimes timezone-aware
        now = datetime.now(timezone.utc)
        next_review = rec.next_review_at.replace(tzinfo=timezone.utc)
        days_until_review = (next_review - now).days
        
        result.append(ReviewRecommendationSchema(
            id=rec.id,
            question_text=question.question_text,
            chapter_title=chapter.title,
            book_title=upload.filename,
            last_reviewed_at=rec.last_reviewed_at,
            next_review_at=rec.next_review_at,
            review_stage=rec.review_stage,
            days_until_review=days_until_review
        ))
    
    return {
        "items": result,
        "total": total
    }

@router.get("/history/{session_id}", response_model=ExamSessionWithDetails)
def get_exam_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get details of a specific exam session"""
    exam_session = (
        db.query(ExamSession)
        .filter(
            ExamSession.id == session_id,
            ExamSession.user_id == current_user.id
        )
        .first()
    )
    
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    chapter = db.query(Chapter).filter(Chapter.id == exam_session.chapter_id).first()
    upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
    
    session_dict = exam_session.__dict__
    session_dict["chapter_title"] = chapter.title
    session_dict["book_title"] = upload.filename
    session_dict["performance_percentage"] = 0.0 if exam_session.total_questions == 0 else (exam_session.score / exam_session.total_questions) * 100
    
    # Get attempts for this session
    attempts = []
    for attempt in exam_session.attempts:
        question = db.query(Question).filter(Question.id == attempt.question_id).first()
        attempts.append({
            "question_text": question.question_text,
            "user_answer": attempt.chosen_answer,
            "correct_answer": question.correct_answer,
            "is_correct": attempt.is_correct,
            "explanation": question.explanation
        })
    session_dict["attempts"] = attempts
    
    return ExamSessionWithDetails(**session_dict) 

@router.post("/review-recommendations/{recommendation_id}/complete")
def complete_review(
    recommendation_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a review recommendation as completed"""
    recommendation = (
        db.query(ReviewRecommendation)
        .filter(
            ReviewRecommendation.id == recommendation_id,
            ReviewRecommendation.user_id == current_user.id
        )
        .first()
    )
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Review recommendation not found")
    
    # Update review stage and next review date
    recommendation.review_stage += 1
    recommendation.last_reviewed_at = datetime.utcnow()
    
    # Calculate next review date based on review stage
    if recommendation.review_stage == 1:
        recommendation.next_review_at = datetime.utcnow() + timedelta(days=1)
    elif recommendation.review_stage == 2:
        recommendation.next_review_at = datetime.utcnow() + timedelta(days=3)
    elif recommendation.review_stage == 3:
        recommendation.next_review_at = datetime.utcnow() + timedelta(days=7)
    elif recommendation.review_stage == 4:
        recommendation.next_review_at = datetime.utcnow() + timedelta(days=14)
    elif recommendation.review_stage == 5:
        recommendation.next_review_at = datetime.utcnow() + timedelta(days=30)
    else:
        # If review stage is beyond 5, mark as completed
        db.delete(recommendation)
    
    db.commit()
    return {"message": "Review completed successfully"}

@router.post("/review-recommendations/{recommendation_id}/skip")
def skip_review(
    recommendation_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Skip a review recommendation (mark as no need to review)"""
    recommendation = (
        db.query(ReviewRecommendation)
        .filter(
            ReviewRecommendation.id == recommendation_id,
            ReviewRecommendation.user_id == current_user.id
        )
        .first()
    )
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Review recommendation not found")
    
    # Delete the recommendation
    db.delete(recommendation)
    db.commit()
    
    return {"message": "Review skipped successfully"}

@router.post("/sessions", response_model=ExamSessionWithDetails)
def create_exam_session(
    exam_data: ExamSessionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new exam session when a quiz is completed"""
    # Create the exam session
    exam_session = ExamSession(
        user_id=current_user.id,
        chapter_id=exam_data.chapter_id,
        score=exam_data.score,
        total_questions=exam_data.total_questions,
        correct_answers=exam_data.score,  # score is the number of correct answers
        started_at=datetime.utcnow() - timedelta(seconds=exam_data.duration or 0),
        completed_at=datetime.utcnow()
    )
    
    db.add(exam_session)
    db.commit()
    db.refresh(exam_session)
    
    # Get the chapter and upload info for the response
    chapter = db.query(Chapter).filter(Chapter.id == exam_session.chapter_id).first()
    upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
    
    # Get the attempts for this session
    attempts = db.query(QuestionAttempt).filter(
        QuestionAttempt.user_id == current_user.id,
        QuestionAttempt.exam_session_id == exam_session.id
    ).all()
    
    # Prepare the response
    session_dict = exam_session.__dict__
    session_dict["chapter_title"] = chapter.title
    session_dict["book_title"] = upload.filename
    session_dict["performance_percentage"] = 0.0 if exam_session.total_questions == 0 else (exam_session.score / exam_session.total_questions) * 100
    
    # Add attempt details
    attempts_list = []
    for attempt in attempts:
        question = db.query(Question).filter(Question.id == attempt.question_id).first()
        attempts_list.append({
            "question_text": question.question_text,
            "user_answer": attempt.chosen_answer,
            "correct_answer": question.correct_answer,
            "is_correct": attempt.is_correct,
            "explanation": question.explanation
        })
    session_dict["attempts"] = attempts_list
    
    return ExamSessionWithDetails(**session_dict)

@router.post("/review-recommendations", response_model=List[ReviewRecommendationWithQuestion])
def create_review_recommendations(
    data: ReviewRecommendationBatchCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create review recommendations for failed questions"""
    # Verify exam session exists and belongs to user
    exam_session = (
        db.query(ExamSession)
        .filter(
            ExamSession.id == data.exam_session_id,
            ExamSession.user_id == current_user.id
        )
        .first()
    )
    
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    # Create review recommendations for each question
    recommendations = []
    now = datetime.now(timezone.utc)
    
    for question_id in data.question_ids:
        # Check if recommendation already exists
        existing = (
            db.query(ReviewRecommendation)
            .filter(
                ReviewRecommendation.user_id == current_user.id,
                ReviewRecommendation.question_id == question_id
            )
            .first()
        )
        
        if existing:
            # Update existing recommendation
            existing.last_reviewed_at = now
            existing.review_stage = 1  # Reset to first stage
            existing.next_review_at = now + timedelta(days=1)  # Review in 1 day
            recommendations.append(existing)
        else:
            # Create new recommendation
            recommendation = ReviewRecommendation(
                user_id=current_user.id,
                question_id=question_id,
                last_reviewed_at=now,
                next_review_at=now + timedelta(days=1),
                review_stage=1
            )
            db.add(recommendation)
            recommendations.append(recommendation)
    
    db.commit()
    
    # Prepare response with question details
    result = []
    for rec in recommendations:
        question = db.query(Question).filter(Question.id == rec.question_id).first()
        chapter = db.query(Chapter).filter(Chapter.id == question.chapter_id).first()
        upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
        
        rec_dict = rec.__dict__
        rec_dict["question_text"] = question.question_text
        rec_dict["chapter_title"] = chapter.title
        rec_dict["book_title"] = upload.filename
        
        # Make both datetimes timezone-aware
        next_review = rec.next_review_at.replace(tzinfo=timezone.utc)
        rec_dict["days_until_review"] = (next_review - now).days
        
        result.append(ReviewRecommendationWithQuestion(**rec_dict))
    
    return result 

@router.get("/review-recommendations/{recommendation_id}/question", response_model=QuestionReviewDetail)
def get_question_for_review(
    recommendation_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get question details for review"""
    recommendation = (
        db.query(ReviewRecommendation)
        .filter(
            ReviewRecommendation.id == recommendation_id,
            ReviewRecommendation.user_id == current_user.id
        )
        .first()
    )
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Review recommendation not found")
    
    question = db.query(Question).filter(Question.id == recommendation.question_id).first()
    chapter = db.query(Chapter).filter(Chapter.id == question.chapter_id).first()
    upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
    
    return QuestionReviewDetail(
        id=recommendation.id,
        question_text=question.question_text,
        question_type=question.question_type,
        options=question.options,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        chapter_title=chapter.title,
        book_title=upload.filename
    ) 