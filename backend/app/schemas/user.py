from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBaseSchema(BaseModel):
    email: str
    username: str

class UserCreateSchema(UserBaseSchema):
    password: str

class UserSchema(UserBaseSchema):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 