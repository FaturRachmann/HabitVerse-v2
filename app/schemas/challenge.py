# app/schemas/challenge.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from app.db.models import HabitCategory

class ChallengeBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: HabitCategory = HabitCategory.OTHER
    start_date: date
    end_date: date
    reward_xp: int = 50
    reward_badge: Optional[str] = None
    max_members: Optional[int] = None

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[HabitCategory] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reward_xp: Optional[int] = None
    reward_badge: Optional[str] = None
    max_members: Optional[int] = None
    is_active: Optional[bool] = None

class ChallengeMemberResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    progress: float
    completed_days: int
    total_days: int
    joined_at: datetime
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)

class ChallengeResponse(ChallengeBase):
    id: str
    is_active: bool
    member_count: int
    is_ongoing: bool
    created_at: datetime
    updated_at: datetime
    members: Optional[List[ChallengeMemberResponse]] = None
    
    # Pydantic v2 ORM mode
    model_config = ConfigDict(from_attributes=True)
