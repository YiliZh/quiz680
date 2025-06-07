from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChapterBaseSchema(BaseModel):
    chapter_no: int
    title: str
    content: str
    summary: Optional[str] = None
    keywords: Optional[str] = None
    upload_id: int
    has_questions: bool = False

class ChapterCreateSchema(ChapterBaseSchema):
    pass

class ChapterSchema(ChapterBaseSchema):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()
        if data.get('updated_at'):
            data['updated_at'] = data['updated_at'].isoformat()
        return data 