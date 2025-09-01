# app/services/habit_service.py
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.models import Habit, HabitLog, LogStatus

class HabitService:
    def __init__(self, db: Session):
        self.db = db
    
    def update_habit_progress(self, habit: Habit, completion_date: date):
        """Update habit progress statistics"""
        # Update total completions
        habit.total_completions += 1
        
        # Update streak
        self._update_streak(habit, completion_date)
        
        # Update timestamp
        from datetime import datetime
        habit.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def _update_streak(self, habit: Habit, completion_date: date):
        """Calculate and update habit streak"""
        yesterday = completion_date - timedelta(days=1)
        
        # Check if there was a completion yesterday
        yesterday_log = self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit.id,
            HabitLog.date == yesterday,
            HabitLog.status == LogStatus.COMPLETED
        ).first()
        
        if yesterday_log:
            # Continue streak
            habit.current_streak += 1
        else:
            # New streak starts
            habit.current_streak = 1
        
        # Update best streak
        habit.best_streak = max(habit.best_streak, habit.current_streak)
    
    def get_habit_analytics(self, habit: Habit, days: int = 30) -> dict:
        """Get habit analytics data"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get all logs in period
        logs = self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit.id,
            HabitLog.date >= start_date,
            HabitLog.date <= end_date
        ).all()
        
        # Calculate statistics
        total_days = days
        completed_days = len([log for log in logs if log.status == LogStatus.COMPLETED])
        completion_rate = (completed_days / total_days) * 100 if total_days > 0 else 0
        
        return {
            "total_days": total_days,
            "completed_days": completed_days,
            "completion_rate": round(completion_rate, 1),
            "current_streak": habit.current_streak,
            "best_streak": habit.best_streak,
            "total_completions": habit.total_completions
        }

