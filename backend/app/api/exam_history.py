from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.core.deps import get_db, get_current_user
from app.models import User, ExamSession, ReviewRecommendation, Question, Chapter, Upload, QuestionAttempt
from app.schemas.exam_session import ExamSessionWithDetails, ExamSessionCreate
from app.schemas.review_recommendation import ReviewRecommendationWithQuestion

router = APIRouter()

logger = logging.getLogger(__name__)

class ReviewRecommendationBatchCreate(BaseModel):
    exam_session_id: int
    question_ids: List[int]

@router.get("/history", response_model=List[ExamSessionWithDetails])
def get_exam_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """Get user's exam history with details"""
    exam_sessions = (
        db.query(ExamSession)
        .filter(ExamSession.user_id == current_user.id)
        .order_by(ExamSession.completed_at.desc())
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
        
        # Safely calculate performance percentage
        try:
            total_questions = float(session.total_questions or 0)
            score = float(session.score or 0)
            logger.info(f"Converted values - score: {score}, total_questions: {total_questions}")
            
            if total_questions <= 0:
                logger.warning(f"Session {session.id}: total_questions is {total_questions}, setting performance to 0.0")
                session_dict["performance_percentage"] = 0.0
            else:
                performance = (score / total_questions) * 100
                logger.info(f"Session {session.id}: Calculated performance: {performance}%")
                session_dict["performance_percentage"] = performance
                
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.error(f"Error calculating performance percentage for session {session.id}: {str(e)}")
            logger.error(f"Problematic values - score: {session.score}, total_questions: {session.total_questions}")
            session_dict["performance_percentage"] = 0.0
        
        # Get attempts for this session
        attempts = []
        for attempt in session.attempts:
            question = db.query(Question).filter(Question.id == attempt.question_id).first()
            attempts.append({
                "question_text": question.q_text,
                "user_answer": attempt.chosen_answer,
                "correct_answer": question.correct_answer,
                "is_correct": attempt.is_correct,
                "explanation": question.explanation
            })
        session_dict["attempts"] = attempts
        
        result.append(ExamSessionWithDetails(**session_dict))
    
    return result

@router.get("/review-recommendations", response_model=List[ReviewRecommendationWithQuestion])
def get_review_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's review recommendations based on Ebbinghaus Forgetting Curve"""
    now = datetime.utcnow().replace(tzinfo=None)  # Make it timezone-naive
    recommendations = (
        db.query(ReviewRecommendation)
        .filter(
            ReviewRecommendation.user_id == current_user.id
        )
        .all()
    )
    
    result = []
    for rec in recommendations:
        question = db.query(Question).filter(Question.id == rec.question_id).first()
        chapter = db.query(Chapter).filter(Chapter.id == question.chapter_id).first()
        upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
        
        rec_dict = rec.__dict__
        rec_dict["question_text"] = question.question_text
        rec_dict["chapter_title"] = chapter.title
        rec_dict["book_title"] = upload.filename
        # Ensure next_review_at is timezone-naive before subtraction
        next_review = rec.next_review_at.replace(tzinfo=None) if rec.next_review_at.tzinfo else rec.next_review_at
        rec_dict["days_until_review"] = (next_review - now).days
        
        result.append(ReviewRecommendationWithQuestion(**rec_dict))
    
    return result


@router.get("/history/{session_id}", response_model=ExamSessionWithDetails)
def get_exam_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            "question_text": question.q_text,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a review recommendation as completed and schedule next review"""
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
    
    now = datetime.utcnow()
    recommendation.last_reviewed_at = now
    
    # Update review stage and schedule next review
    if recommendation.review_stage < 4:
        recommendation.review_stage += 1
    
    # Calculate next review date based on stage
    review_intervals = {
        1: 1,    # 1 day
        2: 7,    # 7 days
        3: 16,   # 16 days
        4: 35    # 35 days
    }
    
    recommendation.next_review_at = now + timedelta(days=review_intervals[recommendation.review_stage])
    
    db.commit()
    return {"message": "Review completed successfully"}

@router.post("/sessions", response_model=ExamSessionWithDetails)
def create_exam_session(
    exam_data: ExamSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
            "question_text": question.q_text,
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
    current_user: User = Depends(get_current_user)
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
    now = datetime.utcnow()
    
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
        rec_dict["days_until_review"] = (rec.next_review_at - now).days
        
        result.append(ReviewRecommendationWithQuestion(**rec_dict))
    
    return result 