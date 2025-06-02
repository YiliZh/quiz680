from pydantic import BaseModel
from typing import List, Optional

class QuestionBase(BaseModel):
    q_text: str
    options: List[str]
    answer_key: int
    explanation: str
    chapter_id: int

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: int

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    chosen_idx: int 