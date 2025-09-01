# app/services/gamification.py
from sqlalchemy.orm import Session
from app.db.models import User, Badge, UserBadge
from datetime import datetime

class GamificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def award_xp(self, user: User, xp_amount: int, reason: str = ""):
        """Award XP to user and update level"""
        # Ensure the user instance is attached to this session
        user = self.db.merge(user, load=True)
        
        # Safe arithmetic in case of None
        user.xp = (user.xp or 0) + int(xp_amount)
        
        # Calculate new level
        old_level = user.level or 1
        new_level = self._calculate_level(user.xp)
        user.level = new_level
        
        # Check for level up
        if new_level > old_level:
            self._handle_level_up(user, new_level)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "xp_awarded": xp_amount,
            "total_xp": user.xp,
            "level": user.level,
            "leveled_up": new_level > old_level
        }
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        if xp < 100:
            return 1
        elif xp < 300:
            return 2
        elif xp < 600:
            return 3
        elif xp < 1000:
            return 4
        else:
            return 5 + ((xp - 1000) // 500)
    
    def _handle_level_up(self, user: User, new_level: int):
        """Handle level up rewards and notifications"""
        # This could trigger notifications, unlock features, etc.
        pass
    
    def check_and_award_badges(self, user: User, context: dict):
        """Check if user earned any new badges"""
        # This would contain logic to check various badge requirements
        # For now, just a placeholder
        pass
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top users by XP"""
        users = self.db.query(User).order_by(User.xp.desc()).limit(limit).all()
        
        leaderboard = []
        for i, user in enumerate(users, 1):
            leaderboard.append({
                "rank": i,
                "name": user.name,
                "xp": user.xp,
                "level": user.level
            })
        
        return leaderboard