# app/api/messages.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Message, Friendship

router = APIRouter()


def _are_friends(db: Session, user_a: UUID, user_b: UUID) -> bool:
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.requester_id == user_a, Friendship.addressee_id == user_b),
            and_(Friendship.requester_id == user_b, Friendship.addressee_id == user_a),
        ),
        Friendship.status == "accepted",
    ).first()
    return friendship is not None


@router.get("/messages/with/{other_user_id}")
def get_conversation(
    other_user_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    before: Optional[str] = Query(None, description="ISO timestamp to paginate older messages"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch recent direct messages between current user and other_user_id, most recent first."""
    # Validate other user
    other = db.query(User).filter(User.id == other_user_id).first()
    if not other:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional: ensure they are friends (can relax if you want open DMs)
    if not _are_friends(db, current_user.id, other_user_id):
        raise HTTPException(status_code=403, detail="You can only message friends")

    q = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.recipient_id == current_user.id),
        )
    )

    if before:
        try:
            before_dt = datetime.fromisoformat(before)
            q = q.filter(Message.created_at < before_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid 'before' timestamp")

    items = q.order_by(Message.created_at.desc()).limit(limit).all()

    return [
        {
            "id": str(m.id),
            "sender_id": str(m.sender_id),
            "recipient_id": str(m.recipient_id),
            "content": m.content,
            "created_at": m.created_at.isoformat(),
            "read_at": m.read_at.isoformat() if m.read_at else None,
        }
        for m in items
    ]


@router.post("/messages/send")
def send_message(
    to: UUID,
    content: str = Query(..., min_length=1, max_length=4000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a direct message to a user."""
    if to == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")

    # Validate target user
    recipient = db.query(User).filter(User.id == to).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")

    # Optional: ensure they are friends
    if not _are_friends(db, current_user.id, to):
        raise HTTPException(status_code=403, detail="You can only message friends")

    msg = Message(sender_id=current_user.id, recipient_id=to, content=content.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return {
        "id": str(msg.id),
        "sender_id": str(msg.sender_id),
        "recipient_id": str(msg.recipient_id),
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }
