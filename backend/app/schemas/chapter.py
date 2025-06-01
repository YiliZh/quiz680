from pydantic import BaseModel
from typing import Optional, List

class ChapterBase(BaseModel):
    title: str
    content: str
    upload_id: int
    page_number: int
    keywords: Optional[List[str]] = None

class ChapterCreate(ChapterBase):
    pass

class Chapter(ChapterBase):
    id: int

    class Config:
        from_attributes = True 