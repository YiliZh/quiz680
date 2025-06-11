from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class QuestionAttemptDetail(BaseModel):
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None

class ExamSessionBase(BaseModel):
    chapter_id: int
    score: int
    total_questions: int
    duration: Optional[int] = None

class ExamSessionCreate(ExamSessionBase):
    pass

class ExamSession(ExamSessionBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExamSessionWithDetails(ExamSession):
    chapter_title: str
    book_title: str
    performance_percentage: float
    attempts: List[QuestionAttemptDetail]

class ReviewRecommendation(BaseModel):
    id: int
    question_text: str
    chapter_title: str
    book_title: str
    last_reviewed_at: Optional[datetime] = None
    next_review_at: datetime
    review_stage: int
    days_until_review: int

    class Config:
        from_attributes = True 