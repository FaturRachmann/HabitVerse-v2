# app/api/habits.py
from typing import List, Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Habit, HabitLog, LogStatus
from app.schemas.habit import HabitCreate, HabitUpdate, HabitResponse, HabitLogCreate, HabitLogResponse
from app.services.habit_service import HabitService
from app.services.gamification import GamificationService

router = APIRouter()

@router.get("", response_model=List[HabitResponse])
@router.get("/", response_model=List[HabitResponse])
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's habits"""
    habits = db.query(Habit).filter(
        Habit.user_id == current_user.id,
        Habit.is_active == True
    ).all()
    
    return [HabitResponse.model_validate(habit) for habit in habits]

@router.post("", response_model=HabitResponse)
@router.post("/", response_model=HabitResponse)
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new habit"""
    db_habit = Habit(
        user_id=current_user.id,
        **habit_data.dict()
    )
    
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    
    return HabitResponse.model_validate(db_habit)

@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    return HabitResponse.model_validate(habit)

@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: UUID,
    habit_update: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update habit"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Update fields
    update_data = habit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    habit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(habit)
    
    return HabitResponse.model_validate(habit)

@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete habit (soft delete)"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    habit.is_active = False
    habit.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Habit deleted successfully"}

@router.post("/{habit_id}/log", response_model=HabitLogResponse)
async def log_habit(
    habit_id: UUID,
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log habit completion"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Check if already logged today
    log_date = log_data.date or date.today()
    existing_log = db.query(HabitLog).filter(
        and_(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == current_user.id,
            HabitLog.date == log_date
        )
    ).first()
    
    if existing_log:
        # Update existing log
        update_data = log_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(existing_log, field, value)
        
        existing_log.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_log)
        log = existing_log
    else:
        # Create new log
        db_log = HabitLog(
            habit_id=habit_id,
            user_id=current_user.id,
            date=log_date,
            **log_data.dict(exclude={"date"})
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        log = db_log
    
    # Update habit statistics if completed
    if log_data.status == LogStatus.COMPLETED:
        habit_service = HabitService(db)
        habit_service.update_habit_progress(habit, log_date)
        
        # Ensure the current user is attached before awarding XP
        current_user = db.merge(current_user, load=True)
        # Award XP
        gamification = GamificationService(db)
        gamification.award_xp(current_user, 10, "habit_completion")
    
    return HabitLogResponse.model_validate(log)

@router.get("/{habit_id}/logs", response_model=List[HabitLogResponse])
async def get_habit_logs(
    habit_id: UUID,
    days: Optional[int] = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get habit logs"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Get logs for specified period
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)
    
    logs = db.query(HabitLog).filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= start_date
    ).order_by(HabitLog.date.desc()).all()
    
    return [HabitLogResponse.model_validate(log) for log in logs]

@router.get("/stats/heatmap")
async def get_heatmap(
    days: int = 180,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aggregate per-day completion counts for all user's habits for a calendar heatmap.
    Returns: [{"date": "YYYY-MM-DD", "count": int}]
    """
    from datetime import timedelta
    from sqlalchemy import func

    start_date = date.today() - timedelta(days=days)

    # Sum 'completed' logs across all habits owned by the user per day
    q = (
        db.query(HabitLog.date.label("d"), func.sum(HabitLog.count).label("c"))
        .join(Habit, Habit.id == HabitLog.habit_id)
        .filter(
            Habit.user_id == current_user.id,
            HabitLog.date >= start_date,
            HabitLog.status == LogStatus.COMPLETED,
        )
        .group_by(HabitLog.date)
        .order_by(HabitLog.date.asc())
    )

    rows = q.all()
    data = [{"date": d.strftime("%Y-%m-%d"), "count": int(c or 0)} for d, c in rows]
    return {"days": days, "data": data}
