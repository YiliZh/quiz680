from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadBaseSchema(BaseModel):
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None

class UploadCreateSchema(UploadBaseSchema):
    pass

class UploadSchema(UploadBaseSchema):
    id: int
    user_id: int
    status: str
    file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 