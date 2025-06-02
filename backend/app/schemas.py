from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class UploadBase(BaseModel):
    filename: str

class UploadCreate(UploadBase):
    pass

class Upload(UploadBase):
    id: int
    user_id: int
    file_path: str
    uploaded_at: datetime
    class Config:
        orm_mode = True

class ChapterBase(BaseModel):
    chapter_no: int
    title: str
    summary: str

class ChapterCreate(ChapterBase):
    upload_id: int

class Chapter(ChapterBase):
    id: int
    upload_id: int
    class Config:
        orm_mode = True

class TagBase(BaseModel):
    name: str
    slug: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    class Config:
        orm_mode = True

class ChapterTagBase(BaseModel):
    chapter_id: int
    tag_id: int

class ChapterTagCreate(ChapterTagBase):
    pass

class ChapterTag(ChapterTagBase):
    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    q_text: str
    options: List[str]
    answer_key: int
    explanation: str

class QuestionCreate(QuestionBase):
    chapter_id: int

class Question(QuestionBase):
    id: int
    chapter_id: int
    class Config:
        orm_mode = True

class QuizAttemptBase(BaseModel):
    user_id: int
    question_id: int
    chosen_idx: int
    is_correct: bool

class QuizAttemptCreate(QuizAttemptBase):
    pass

class QuizAttempt(QuizAttemptBase):
    id: int
    attempted_at: datetime
    class Config:
        orm_mode = True 