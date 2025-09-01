# app/routes/challenges.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def challenges_home(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    html = f"""
    <html>
      <head><title>Challenges - HabitVerse</title></head>
      <body style=\"font-family: Arial; max-width: 720px; margin: 40px auto;\">
        <h1>Challenges</h1>
        <p>Hi {current_user.name}, challenges UI is coming soon.</p>
        <a href=\"/dashboard\">Back to Dashboard</a>
      </body>
    </html>
    """
    return HTMLResponse(content=html)