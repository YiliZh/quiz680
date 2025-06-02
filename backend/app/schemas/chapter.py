from pydantic import BaseModel
from typing import Optional, List

class ChapterBase(BaseModel):
    chapter_no: int
    title: str
    summary: str
    upload_id: int

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    class Config:
        from_attributes = True 