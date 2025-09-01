# app/api/challenges.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import (
    User,
    Challenge,
    ChallengeMember,
    Community,
    CommunityMember,
    Friendship,
    FriendshipStatus,
)

router = APIRouter()

@router.get("/", tags=["Challenges"])
def challenges_root():
    """Basic endpoint to verify Challenges API is wired up."""
    return {"status": "ok", "message": "Challenges API"}

# -------------------------
# Community Endpoints (MVP)
# -------------------------

@router.post("/communities", tags=["Communities"])
def create_community(
    name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: create_community called with params: name={name}")
    if db.query(Community).filter(Community.name == name).first():
        raise HTTPException(status_code=400, detail="Community name already exists")

    comm = Community(name=name, description=description, owner_id=current_user.id)
    db.add(comm)
    db.commit()
    db.refresh(comm)

    # Owner becomes admin member
    member = CommunityMember(community_id=comm.id, user_id=current_user.id, role="admin")
    db.add(member)
    db.commit()

    return {
        "id": str(comm.id),
        "name": comm.name,
        "description": comm.description,
        "owner_id": str(comm.owner_id),
        "created_at": comm.created_at,
    }

@router.get("/communities", tags=["Communities"])
def list_communities(
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: list_communities called with params: q={q}")
    query = db.query(Community)
    if q:
        like = f"%{q}%"
        query = query.filter(Community.name.like(like))
    rows = query.order_by(Community.created_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "owner_id": str(r.owner_id),
        }
        for r in rows
    ]

@router.post("/communities/{community_id}/join", tags=["Communities"])
def join_community(
    community_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: join_community called with params: community_id={community_id}")
    comm = db.query(Community).filter(Community.id == community_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Community not found")

    exists = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.id,
    ).first()
    if exists:
        return {"message": "Already a member"}

    m = CommunityMember(community_id=community_id, user_id=current_user.id, role="member")
    db.add(m)
    db.commit()
    return {"message": "Joined community"}

@router.post("/communities/{community_id}/leave", tags=["Communities"])
def leave_community(
    community_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: leave_community called with params: community_id={community_id}")
    m = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.id,
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Membership not found")

    db.delete(m)
    db.commit()
    return {"message": "Left community"}

@router.get("/communities/{community_id}/members", tags=["Communities"])
def community_members(
    community_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: community_members called with params: community_id={community_id}")
    comm = db.query(Community).filter(Community.id == community_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Community not found")

    members = db.query(CommunityMember).filter(CommunityMember.community_id == community_id).all()
    return [
        {
            "id": str(m.id),
            "user_id": str(m.user_id),
            "role": m.role,
            "joined_at": m.joined_at,
        }
        for m in members
    ]

@router.get("/user/communities", tags=["Communities"])
def get_user_communities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: get_user_communities called")
    """Get communities where the current user is a member"""
    communities = db.query(Community).join(CommunityMember).filter(
        CommunityMember.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": str(community.id),
            "name": community.name,
            "description": community.description
        }
        for community in communities
    ]

# ---------------------------------
# Challenges under a Community (MVP)
# ---------------------------------

@router.post("/create", tags=["Challenges"])
def create_challenge(
    name: str,
    start_date: date,
    end_date: date,
    description: Optional[str] = None,
    reward_xp: int = 50,
    is_public: bool = False,
    max_members: Optional[int] = None,
    community_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: create_challenge called with params: name={name}, is_public={is_public}")
    
    # Only check membership for private challenges
    if community_id and not is_public:
        membership = db.query(CommunityMember).filter(
            CommunityMember.community_id == community_id,
            CommunityMember.user_id == current_user.id,
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Join the community first")
    
    ch = Challenge(
        name=name,
        description=description,
        category="community" if community_id else "public",
        start_date=start_date,
        end_date=end_date,
        reward_xp=reward_xp,
        community_id=community_id,
        is_public=is_public,
        max_members=max_members,
        owner_id=current_user.id,  # Set owner
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    
    return {
        "id": str(ch.id),
        "name": ch.name,
        "community_id": str(ch.community_id) if ch.community_id else None,
        "is_public": ch.is_public,
        "max_members": ch.max_members,
        "owner_id": str(ch.owner_id),
    }

@router.put("/{challenge_id}/edit", tags=["Challenges"])
def edit_challenge(
    challenge_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    reward_xp: Optional[int] = None,
    is_public: Optional[bool] = None,
    max_members: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: edit_challenge called for challenge_id={challenge_id}")
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if user is owner
    if challenge.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only challenge owner can edit")
    
    # Update fields if provided
    if name is not None:
        challenge.name = name
    if description is not None:
        challenge.description = description
    if start_date is not None:
        challenge.start_date = start_date
    if end_date is not None:
        challenge.end_date = end_date
    if reward_xp is not None:
        challenge.reward_xp = reward_xp
    if is_public is not None:
        challenge.is_public = is_public
    if max_members is not None:
        challenge.max_members = max_members
    
    challenge.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(challenge)
    
    return {
        "id": str(challenge.id),
        "name": challenge.name,
        "description": challenge.description,
        "start_date": challenge.start_date.isoformat(),
        "end_date": challenge.end_date.isoformat(),
        "reward_xp": challenge.reward_xp,
        "is_public": challenge.is_public,
        "max_members": challenge.max_members,
        "owner_id": str(challenge.owner_id),
    }

@router.get("/{challenge_id}/details", tags=["Challenges"])
def get_challenge_details(
    challenge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: get_challenge_details called for challenge_id={challenge_id}")
    
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if user is member
    is_member = db.query(ChallengeMember).filter(
        ChallengeMember.challenge_id == challenge_id,
        ChallengeMember.user_id == current_user.id
    ).first() is not None
    
    # Check if user is owner
    is_owner = challenge.owner_id == current_user.id
    
    return {
        "id": str(challenge.id),
        "name": challenge.name,
        "description": challenge.description,
        "start_date": challenge.start_date.isoformat(),
        "end_date": challenge.end_date.isoformat(),
        "reward_xp": challenge.reward_xp,
        "is_public": challenge.is_public,
        "max_members": challenge.max_members,
        "member_count": challenge.member_count,
        "owner_id": str(challenge.owner_id),
        "is_owner": is_owner,
        "is_member": is_member,
        "is_ongoing": challenge.is_ongoing,
        "community_id": str(challenge.community_id) if challenge.community_id else None,
    }

@router.get("/", tags=["Challenges"])
def list_challenges(
    public: Optional[bool] = None,
    community_id: Optional[UUID] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: list_challenges called with params: public={public}, community_id={community_id}, q={q}")
    qy = db.query(Challenge)
    if public is not None:
        qy = qy.filter(Challenge.is_public == public)
    if community_id is not None:
        qy = qy.filter(Challenge.community_id == community_id)
    if q:
        like = f"%{q}%"
        qy = qy.filter(Challenge.name.like(like))
    rows = qy.order_by(Challenge.created_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "name": r.name,
            "description": r.description,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "reward_xp": r.reward_xp,
            "community_id": str(r.community_id) if r.community_id else None,
            "is_public": r.is_public,
            "max_members": r.max_members,
            "member_count": r.member_count,
        }
        for r in rows
    ]

@router.post("/{challenge_id}/invite/{user_id}", tags=["Challenges"])
def invite_user_to_challenge(
    challenge_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: invite_user_to_challenge called with params: challenge_id={challenge_id}, user_id={user_id}")
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # If community-bound, inviter must be a member
    if ch.community_id:
        membership = db.query(CommunityMember).filter(
            CommunityMember.community_id == ch.community_id,
            CommunityMember.user_id == current_user.id,
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Only community members can invite")

    exists = db.query(ChallengeMember).filter(
        ChallengeMember.challenge_id == challenge_id,
        ChallengeMember.user_id == user_id,
    ).first()
    if exists:
        return {"message": "User already in challenge"}

    # Enforce max_members if set
    if ch.max_members is not None and ch.member_count >= ch.max_members:
        raise HTTPException(status_code=400, detail="Challenge is full")

    cm = ChallengeMember(challenge_id=challenge_id, user_id=user_id)
    db.add(cm)
    db.commit()
    return {"message": "User invited/added"}

@router.post("/{challenge_id}/join", tags=["Challenges"])
def join_challenge(
    challenge_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: join_challenge called with params: challenge_id={challenge_id}")
    """Allow the current user to join a challenge.
    Rules:
    - If the challenge is community-bound and not public: must be a community member.
    - If public: anyone can join.
    - Respect max_members if set.
    """
    ch = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    # Membership rule
    if ch.community_id and not ch.is_public:
        membership = db.query(CommunityMember).filter(
            CommunityMember.community_id == ch.community_id,
            CommunityMember.user_id == current_user.id,
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="Join the community first")

    # Already in challenge
    exists = db.query(ChallengeMember).filter(
        ChallengeMember.challenge_id == challenge_id,
        ChallengeMember.user_id == current_user.id,
    ).first()
    if exists:
        return {"message": "Already joined"}

    # Enforce max_members if set
    if ch.max_members is not None and ch.member_count >= ch.max_members:
        raise HTTPException(status_code=400, detail="Challenge is full")

    cm = ChallengeMember(challenge_id=challenge_id, user_id=current_user.id)
    db.add(cm)
    db.commit()
    return {"message": "Joined challenge"}

# ----------------------
# Friendship Endpoints
# ----------------------

@router.post("/friends/requests", tags=["Friends"])
def send_friend_request(
    addressee_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: send_friend_request called with params: addressee_id={addressee_id}")
    if addressee_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot friend yourself")

    # Existing relationship?
    existing = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == addressee_id))
        | ((Friendship.requester_id == addressee_id) & (Friendship.addressee_id == current_user.id))
    ).first()
    if existing and existing.status == FriendshipStatus.ACCEPTED:
        return {"message": "Already friends"}
    if existing and existing.status == FriendshipStatus.PENDING:
        return {"message": "Request already pending"}

    req = Friendship(requester_id=current_user.id, addressee_id=addressee_id, status=FriendshipStatus.PENDING)
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"id": str(req.id), "status": req.status}

@router.post("/friends/requests/{request_id}/accept", tags=["Friends"])
def accept_friend_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: accept_friend_request called with params: request_id={request_id}")
    req = db.query(Friendship).filter(Friendship.id == request_id).first()
    if not req or req.addressee_id != current_user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = FriendshipStatus.ACCEPTED
    req.responded_at = datetime.utcnow()
    db.commit()
    return {"message": "Friend request accepted"}

@router.post("/friends/requests/{request_id}/decline", tags=["Friends"])
def decline_friend_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: decline_friend_request called with params: request_id={request_id}")
    req = db.query(Friendship).filter(Friendship.id == request_id).first()
    if not req or req.addressee_id != current_user.id:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = FriendshipStatus.DECLINED
    req.responded_at = datetime.utcnow()
    db.commit()
    return {"message": "Friend request declined"}

@router.get("/friends", tags=["Friends"])
def list_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: list_friends called")
    rows = db.query(Friendship).filter(
        (Friendship.status == FriendshipStatus.ACCEPTED)
        & ((Friendship.requester_id == current_user.id) | (Friendship.addressee_id == current_user.id))
    ).all()
    def other_id(r: Friendship):
        return r.addressee_id if r.requester_id == current_user.id else r.requester_id
    return [{"friend_user_id": str(other_id(r)), "since": r.responded_at} for r in rows]

@router.get("/friends/requests", tags=["Friends"])
def list_friend_requests(
    incoming: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: list_friend_requests called with params: incoming={incoming}")
    q = db.query(Friendship).filter(Friendship.status == FriendshipStatus.PENDING)
    if incoming:
        q = q.filter(Friendship.addressee_id == current_user.id)
    else:
        q = q.filter(Friendship.requester_id == current_user.id)
    rows = q.order_by(Friendship.created_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "requester_id": str(r.requester_id),
            "addressee_id": str(r.addressee_id),
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in rows
    ]

# ----------------------
# User Profile (MVP)
# ----------------------

@router.post("/me/profile", tags=["Users"])
def update_profile(
    profile: Optional[str] = None,
    avatar_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"DEBUG: update_profile called with params: profile={profile}, avatar_url={avatar_url}")
    current_user.profile = profile if profile is not None else current_user.profile
    current_user.avatar_url = avatar_url if avatar_url is not None else current_user.avatar_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "profile": current_user.profile,
    }