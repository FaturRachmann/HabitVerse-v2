# app/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db, init_db
from app.core.security import get_current_user_optional
from app.db.models import User

# Import routers
from app.api import auth, habits, challenges, reflections, quotes, leaderboard, friends, posts, uploads, users as users_api
from app.api import messages as messages_api
from app.routes import (
    dashboard,
    auth as auth_routes,
    habits as habit_routes,
    challenges as challenge_routes,
    community as community_routes,
    coach as coach_routes,
    profile as profile_routes,
    users as users_routes,
    dm as dm_routes,
    friends as friends_routes,
)

# Create FastAPI app
app = FastAPI(
    title="HabitVerse",
    description="A gamified habit tracker built with FastAPI",
    version="1.0.0",
    redirect_slashes=False
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Add template globals
@app.on_event("startup")
async def setup_template_globals():
    """Add global functions to Jinja2 templates and init DB."""
    # Initialize DB tables (dev convenience)
    init_db()
    
    # Debug: Print registered routes
    print("DEBUG: Registered routes:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            print(f"  {route.methods} {route.path}")

    def format_date(date_obj):
        """Format date for templates"""
        if not date_obj:
            return ""
        return date_obj.strftime("%B %d, %Y")

    def format_streak(count):
        """Format streak count with emoji"""
        if count == 0:
            return "No streak 😞"
        elif count == 1:
            return "1 day 🔥"
        else:
            return f"{count} days 🔥🔥"

    def calculate_progress_percent(current, target):
        """Calculate progress percentage"""
        if target == 0:
            return 0
        return min(100, (current / target) * 100)

    # Add functions to template environment
    templates.env.globals["format_date"] = format_date
    templates.env.globals["format_streak"] = format_streak
    templates.env.globals["calculate_progress_percent"] = calculate_progress_percent

# Web Routes (HTML pages) - Register FIRST to avoid conflicts
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth Pages"])
app.include_router(habit_routes.router, prefix="/habits", tags=["Habit Pages"])
app.include_router(challenge_routes.router, prefix="/challenges", tags=["Challenge Pages"])
app.include_router(community_routes.router, prefix="", tags=["Community Page"])
app.include_router(coach_routes.router, prefix="", tags=["Coach Page"])
app.include_router(profile_routes.router, prefix="", tags=["Profile Page"])
app.include_router(dm_routes.router, prefix="", tags=["DM Page"])
app.include_router(friends_routes.router, prefix="", tags=["Friends Page"])
app.include_router(users_routes.router, prefix="", tags=["Users Page"])

# API Routes - Register AFTER web routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(habits.router, prefix="/api/habits", tags=["Habits"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["Challenges"])
app.include_router(reflections.router, prefix="/api/reflections", tags=["Reflections"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["Quotes"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(friends.router, prefix="/api", tags=["Friends"])
app.include_router(posts.router, prefix="/api", tags=["Posts"])
app.include_router(uploads.router, prefix="/api", tags=["Uploads"])
app.include_router(users_api.router, prefix="/api", tags=["Users"])
app.include_router(messages_api.router, prefix="/api", tags=["Messages"])

# Root route - redirect to dashboard or login
@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Homepage - redirect to dashboard if logged in, otherwise login page"""

    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)

    return RedirectResponse(url="/auth/login", status_code=302)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for deployment monitoring"""
    return {"status": "healthy", "version": "1.0.0"}

# 404 handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Simple 404 response while templates are incomplete"""
    return HTMLResponse("<h1>404 Not Found</h1>", status_code=404)

# 500 handler
@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Simple 500 response while templates are incomplete"""
    return HTMLResponse(f"<h1>Server Error</h1><pre>{str(exc)}</pre>", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )