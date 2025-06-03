from pydantic import BaseModel
from datetime import datetime

class QuestionAttemptBase(BaseModel):
    question_id: int
    chosen_answer: str
    is_correct: bool

class QuestionAttemptCreate(QuestionAttemptBase):
    pass

class QuestionAttemptResponse(QuestionAttemptBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 