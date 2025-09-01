# app/api/leaderboard.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_leaderboard():
    """Return a simple mock leaderboard list."""
    data = [
        {"user": "Ayu", "level": 7, "xp": 1450, "streak": 21},
        {"user": "Bima", "level": 6, "xp": 1200, "streak": 18},
        {"user": "Citra", "level": 5, "xp": 860, "streak": 12},
        {"user": "Deni", "level": 4, "xp": 610, "streak": 9},
    ]
    return {"items": data}
