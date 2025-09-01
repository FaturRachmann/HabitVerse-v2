# app/api/posts.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import Body
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Post, PostLike, PostComment, Follow

router = APIRouter()


@router.post("/posts")
async def create_post(
    content: Optional[str] = Body(default=None),
    image_url: Optional[str] = Body(default=None),
    is_public: bool = Body(default=True),
    challenge_id: Optional[str] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        user_id=current_user.id,
        content=content,
        image_url=image_url,
        is_public=is_public,
        challenge_id=challenge_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"id": str(post.id)}


@router.get("/posts/feed")
async def get_feed(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # following ids
    following_rows = db.query(Follow.followed_id).filter(Follow.follower_id == current_user.id).all()
    following_ids = [row[0] for row in following_rows]

    # fetch posts: from following OR public
    q = (
        db.query(Post)
        .filter(or_(Post.user_id.in_(following_ids), Post.is_public == True))
        .order_by(desc(Post.created_at))
        .limit(limit)
        .all()
    )

    # serialize with counts and basic author info
    result = []
    for p in q:
        like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        comment_count = db.query(PostComment).filter(PostComment.post_id == p.id).count()
        you_liked = (
            db.query(PostLike)
            .filter(PostLike.post_id == p.id, PostLike.user_id == current_user.id)
            .first()
            is not None
        )
        author = db.query(User).filter(User.id == p.user_id).first()
        result.append({
            "id": str(p.id),
            "user": {
                "id": str(author.id),
                "name": author.name,
                "avatar_url": author.avatar_url,
            },
            "content": p.content,
            "image_url": p.image_url,
            "is_public": p.is_public,
            "created_at": p.created_at.isoformat(),
            "like_count": like_count,
            "comment_count": comment_count,
            "you_liked": you_liked,
        })
    return result


@router.get("/posts/user/{user_id}")
async def get_user_posts(
    user_id: str,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # If viewing someone else, only show public posts; if self, show all
    is_self = str(current_user.id) == str(user_id)
    q = db.query(Post).filter(Post.user_id == user_id)
    if not is_self:
        q = q.filter(Post.is_public == True)
    posts = q.order_by(desc(Post.created_at)).limit(limit).all()

    author = db.query(User).filter(User.id == user_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="User not found")

    result = []
    for p in posts:
        like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        comment_count = db.query(PostComment).filter(PostComment.post_id == p.id).count()
        you_liked = (
            db.query(PostLike)
            .filter(PostLike.post_id == p.id, PostLike.user_id == current_user.id)
            .first()
            is not None
        )
        result.append({
            "id": str(p.id),
            "user": {
                "id": str(author.id),
                "name": author.name,
                "avatar_url": author.avatar_url,
            },
            "content": p.content,
            "image_url": p.image_url,
            "is_public": p.is_public,
            "created_at": p.created_at.isoformat(),
            "like_count": like_count,
            "comment_count": comment_count,
            "you_liked": you_liked,
        })
    return result
@router.get("/posts/me")
async def get_my_posts(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(Post)
        .filter(Post.user_id == current_user.id)
        .order_by(desc(Post.created_at))
        .limit(limit)
        .all()
    )

    result = []
    for p in q:
        like_count = db.query(PostLike).filter(PostLike.post_id == p.id).count()
        comment_count = db.query(PostComment).filter(PostComment.post_id == p.id).count()
        you_liked = (
            db.query(PostLike)
            .filter(PostLike.post_id == p.id, PostLike.user_id == current_user.id)
            .first()
            is not None
        )
        result.append({
            "id": str(p.id),
            "user": {
                "id": str(current_user.id),
                "name": current_user.name,
                "avatar_url": current_user.avatar_url,
            },
            "content": p.content,
            "image_url": p.image_url,
            "is_public": p.is_public,
            "created_at": p.created_at.isoformat(),
            "like_count": like_count,
            "comment_count": comment_count,
            "you_liked": you_liked,
        })
    return result


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    exists = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id).first()
    if exists:
        return {"status": "ok"}
    like = PostLike(post_id=post_id, user_id=current_user.id)
    db.add(like)
    db.commit()
    return {"status": "ok"}


@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == current_user.id).first()
    if like:
        db.delete(like)
        db.commit()
    return {"status": "ok"}


@router.get("/posts/{post_id}/comments")
async def list_comments(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = (
        db.query(PostComment)
        .filter(PostComment.post_id == post_id)
        .order_by(PostComment.created_at.asc())
        .all()
    )
    users = {u.id: u for u in db.query(User).filter(User.id.in_({c.user_id for c in comments})).all()}
    return [
        {
            "id": str(c.id),
            "user": {
                "id": str(c.user_id),
                "name": users[c.user_id].name if c.user_id in users else "User",
                "avatar_url": users[c.user_id].avatar_url if c.user_id in users else None,
            },
            "parent_id": str(c.parent_id) if c.parent_id else None,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]


@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: str,
    content: str = Body(...),
    parent_id: Optional[str] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comment = PostComment(post_id=post_id, user_id=current_user.id, content=content, parent_id=parent_id)
    db.add(comment)
    db.commit()
    return {"status": "ok"}
