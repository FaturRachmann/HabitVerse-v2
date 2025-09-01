# app/schemas/habit.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional
from app.db.models import HabitCategory, HabitFrequency, LogStatus, Mood
from uuid import UUID

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: HabitCategory = HabitCategory.OTHER
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_count: int = 1
    reminder_time: Optional[str] = None
    color: str = "#3B82F6"

class HabitCreate(HabitBase):
    pass

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[HabitCategory] = None
    frequency: Optional[HabitFrequency] = None
    target_count: Optional[int] = None
    reminder_time: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class HabitResponse(HabitBase):
    id: UUID
    user_id: UUID
    current_streak: int
    best_streak: int
    total_completions: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)

class HabitLogBase(BaseModel):
    status: LogStatus = LogStatus.COMPLETED
    count: int = 1
    mood: Optional[Mood] = None
    note: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    date: Optional[date] = None

class HabitLogUpdate(BaseModel):
    status: Optional[LogStatus] = None
    count: Optional[int] = None
    mood: Optional[Mood] = None
    note: Optional[str] = None

class HabitLogResponse(HabitLogBase):
    id: UUID
    habit_id: UUID
    date: date
    created_at: datetime
    updated_at: datetime
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)

class HabitAnalytics(BaseModel):
    total_days: int
    completed_days: int
    completion_rate: float
    current_streak: int
    best_streak: int
    total_completions: int
