from pydantic import BaseModel
from datetime import datetime

class AttemptBase(BaseModel):
    question_id: int
    chosen_idx: int
    is_correct: bool

class AttemptCreate(AttemptBase):
    pass

class Attempt(AttemptBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 