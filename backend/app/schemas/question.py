from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    question_text: str
    question_type: str  # multiple_choice, true_false, short_answer
    options: Optional[List[str]] = None
    correct_answer: str
    difficulty: str  # easy, medium, hard
    chapter_id: int

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    chosen_answer: str 