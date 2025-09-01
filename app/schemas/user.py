# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    xp: int
    level: int
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str