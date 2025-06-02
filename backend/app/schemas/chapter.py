from pydantic import BaseModel
from typing import Optional, List

class ChapterBase(BaseModel):
    chapter_no: int
    title: str
    content: str
    summary: Optional[str] = None
    keywords: Optional[str] = None
    upload_id: int

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    class Config:
        from_attributes = True 