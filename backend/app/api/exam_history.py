from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_user
from app.models import User, ExamSession, ReviewRecommendation, Question, Chapter, Upload
from app.schemas.exam_session import ExamSessionWithDetails
from app.schemas.review_recommendation import ReviewRecommendationWithQuestion

router = APIRouter()

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
        session_dict["performance_percentage"] = (session.score / session.total_questions) * 100
        
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
    now = datetime.utcnow()
    recommendations = (
        db.query(ReviewRecommendation)
        .filter(
            ReviewRecommendation.user_id == current_user.id,
            ReviewRecommendation.next_review_at <= now
        )
        .all()
    )
    
    result = []
    for rec in recommendations:
        question = db.query(Question).filter(Question.id == rec.question_id).first()
        chapter = db.query(Chapter).filter(Chapter.id == question.chapter_id).first()
        upload = db.query(Upload).filter(Upload.id == chapter.upload_id).first()
        
        rec_dict = rec.__dict__
        rec_dict["question_text"] = question.q_text
        rec_dict["chapter_title"] = chapter.title
        rec_dict["book_title"] = upload.filename
        rec_dict["days_until_review"] = (rec.next_review_at - now).days
        
        result.append(ReviewRecommendationWithQuestion(**rec_dict))
    
    return result

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