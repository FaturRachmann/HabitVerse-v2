# app/api/quotes.py
from fastapi import APIRouter
from datetime import date

router = APIRouter()

QUOTES = [
    {"text": "Small daily improvements are the key to staggering long-term results.", "author": "James Clear"},
    {"text": "We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "author": "Will Durant"},
    {"text": "Motivation is what gets you started. Habit is what keeps you going.", "author": "Jim Rohn"},
    {"text": "Do the best you can until you know better. Then when you know better, do better.", "author": "Maya Angelou"},
]

@router.get("/today")
def quote_of_the_day():
    """Return a quote of the day (deterministic by date)."""
    idx = date.today().toordinal() % len(QUOTES)
    q = QUOTES[idx]
    return {"date": str(date.today()), "quote": q["text"], "author": q["author"]}
