from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class QuestionAttemptBaseSchema(BaseModel):
    question_id: int
    chosen_answer: str
    is_correct: bool

class QuestionAttemptCreateSchema(QuestionAttemptBaseSchema):
    pass

class QuestionAttemptResponseSchema(QuestionAttemptBaseSchema):
    id: int
    user_id: int
    attempted_at: datetime

    class Config:
        from_attributes = True 