from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

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
    completed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExamSessionWithDetails(ExamSession):
    chapter_title: str
    book_title: str
    performance_percentage: float
    attempts: List[dict]  # Will contain question details and user's answers 