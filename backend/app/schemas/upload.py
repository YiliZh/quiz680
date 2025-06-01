from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadBase(BaseModel):
    filename: str
    title: str
    description: Optional[str] = None

class UploadCreate(UploadBase):
    pass

class Upload(UploadBase):
    id: int
    user_id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True 