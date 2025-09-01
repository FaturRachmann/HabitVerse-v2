# app/schemas/reflection.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional
from app.db.models import Mood

class ReflectionBase(BaseModel):
    mood: Mood
    energy_level: Optional[int] = None  # 1-5 scale
    note: Optional[str] = None
    gratitude: Optional[str] = None
    lessons_learned: Optional[str] = None
    tomorrow_focus: Optional[str] = None

class ReflectionCreate(ReflectionBase):
    date: Optional[date] = None

class ReflectionUpdate(BaseModel):
    mood: Optional[Mood] = None
    energy_level: Optional[int] = None
    note: Optional[str] = None
    gratitude: Optional[str] = None
    lessons_learned: Optional[str] = None
    tomorrow_focus: Optional[str] = None

class ReflectionResponse(ReflectionBase):
    id: str
    user_id: str
    date: date
    created_at: datetime
    updated_at: datetime
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)