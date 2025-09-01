# app/api/reflections.py
from datetime import date as date_cls
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Reflection

router = APIRouter()


class ReflectionIn(BaseModel):
    date: str | None = None  # ISO date, defaults to today
    mood: str
    energy_level: int | None = None
    note: str | None = None
    gratitude: str | None = None
    lessons_learned: str | None = None
    tomorrow_focus: str | None = None


@router.get("/", tags=["Reflections"])
def reflections_root():
    """Basic endpoint to verify Reflections API is wired up."""
    return {"status": "ok", "message": "Reflections API"}


@router.post("/", tags=["Reflections"])
def upsert_reflection(
    payload: ReflectionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update the user's reflection for a given date (default today)."""
    try:
        d = date_cls.fromisoformat(payload.date) if payload.date else date_cls.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Find existing reflection
    existing = (
        db.query(Reflection)
        .filter(Reflection.user_id == current_user.id, Reflection.date == d)
        .first()
    )

    if existing:
        existing.mood = payload.mood
        existing.energy_level = payload.energy_level
        existing.note = payload.note
        existing.gratitude = payload.gratitude
        existing.lessons_learned = payload.lessons_learned
        existing.tomorrow_focus = payload.tomorrow_focus
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return {"status": "updated", "id": str(existing.id), "date": str(existing.date)}

    # Create new
    ref = Reflection(
        user_id=current_user.id,
        date=d,
        mood=payload.mood,
        energy_level=payload.energy_level,
        note=payload.note,
        gratitude=payload.gratitude,
        lessons_learned=payload.lessons_learned,
        tomorrow_focus=payload.tomorrow_focus,
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return {"status": "created", "id": str(ref.id), "date": str(ref.date)}