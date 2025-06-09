from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ReviewRecommendationBase(BaseModel):
    question_id: int
    review_stage: int = 1

class ReviewRecommendationCreate(ReviewRecommendationBase):
    pass

class ReviewRecommendation(ReviewRecommendationBase):
    id: int
    user_id: int
    last_reviewed_at: Optional[datetime]
    next_review_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReviewRecommendationWithQuestion(ReviewRecommendation):
    question_text: str
    chapter_title: str
    book_title: str
    days_until_review: int 