from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Friendship

router = APIRouter()

@router.post("/friends/request/{user_id}", tags=["Friends"])
def send_friend_request(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a friend request to another user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if target user exists
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if friendship already exists
    existing = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == user_id),
            and_(Friendship.requester_id == user_id, Friendship.addressee_id == current_user.id)
        )
    ).first()
    
    if existing:
        if existing.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends")
        elif existing.status == "pending":
            raise HTTPException(status_code=400, detail="Friend request already sent")
        elif existing.status == "blocked":
            raise HTTPException(status_code=400, detail="Cannot send friend request")
    
    # Create friend request
    friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=user_id,
        status="pending"
    )
    db.add(friendship)
    db.commit()
    
    return {"message": f"Friend request sent to {target_user.name}"}

@router.post("/friends/accept/{friendship_id}", tags=["Friends"])
def accept_friend_request(
    friendship_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a friend request"""
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friendship.status = "accepted"
    db.commit()
    
    requester = db.query(User).filter(User.id == friendship.requester_id).first()
    return {"message": f"You are now friends with {requester.name}"}

@router.post("/friends/reject/{friendship_id}", tags=["Friends"])
def reject_friend_request(
    friendship_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a friend request"""
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    db.delete(friendship)
    db.commit()
    
    return {"message": "Friend request rejected"}

@router.get("/friends", tags=["Friends"])
def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of current user's friends"""
    friendships = db.query(Friendship).filter(
        or_(
            Friendship.requester_id == current_user.id,
            Friendship.addressee_id == current_user.id
        ),
        Friendship.status == "accepted"
    ).all()
    
    friends = []
    for friendship in friendships:
        friend_id = friendship.addressee_id if friendship.requester_id == current_user.id else friendship.requester_id
        friend = db.query(User).filter(User.id == friend_id).first()
        if friend:
            friends.append({
                "id": str(friend.id),
                "name": friend.name,
                "email": friend.email,
                "avatar_url": friend.avatar_url,
                "level": friend.level,
                "xp": friend.xp,
                "profile": friend.profile
            })
    
    return friends

@router.get("/friends/requests", tags=["Friends"])
def get_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending friend requests (received)"""
    requests = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).all()
    
    result = []
    for request in requests:
        requester = db.query(User).filter(User.id == request.requester_id).first()
        if requester:
            result.append({
                "friendship_id": str(request.id),
                "requester": {
                    "id": str(requester.id),
                    "name": requester.name,
                    "email": requester.email,
                    "avatar_url": requester.avatar_url,
                    "level": requester.level,
                    "xp": requester.xp
                },
                "created_at": request.created_at.isoformat()
            })
    
    return result

@router.get("/users/search", tags=["Friends"])
def search_users(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search for users to add as friends"""
    users = db.query(User).filter(
        or_(
            User.name.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%")
        ),
        User.id != current_user.id
    ).limit(20).all()
    
    result = []
    for user in users:
        # Check friendship status
        friendship = db.query(Friendship).filter(
            or_(
                and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == user.id),
                and_(Friendship.requester_id == user.id, Friendship.addressee_id == current_user.id)
            )
        ).first()
        
        status = "none"
        if friendship:
            if friendship.status == "accepted":
                status = "friends"
            elif friendship.status == "pending":
                if friendship.requester_id == current_user.id:
                    status = "request_sent"
                else:
                    status = "request_received"
        
        result.append({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "level": user.level,
            "xp": user.xp,
            "friendship_status": status
        })
    
    return result

@router.delete("/friends/{friend_id}", tags=["Friends"])
def remove_friend(
    friend_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a friend"""
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == current_user.id, Friendship.addressee_id == friend_id),
            and_(Friendship.requester_id == friend_id, Friendship.addressee_id == current_user.id)
        ),
        Friendship.status == "accepted"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    db.delete(friendship)
    db.commit()
    
    return {"message": "Friend removed"}
