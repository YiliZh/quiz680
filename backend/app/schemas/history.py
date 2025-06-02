from pydantic import BaseModel
from datetime import datetime

class QuizAttemptBase(BaseModel):
    question_id: int
    chosen_idx: int
    is_correct: bool

class QuizAttemptCreate(QuizAttemptBase):
    pass

class QuizAttempt(QuizAttemptBase):
    id: int
    user_id: int
    attempted_at: datetime

    class Config:
        from_attributes = True 