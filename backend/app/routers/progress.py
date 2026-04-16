from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserProgress
from app.schemas import FavoriteToggle, UserProgressOut, UserProgressUpdate

router = APIRouter(prefix="/api/progress", tags=["progress"])


def get_user_id(x_user_id: str | None = Header(None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header required")
    return x_user_id


@router.get("", response_model=list[UserProgressOut])
def get_progress(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    return db.query(UserProgress).filter(UserProgress.user_id == user_id).all()


def _get_or_create_progress(db: Session, user_id: str, point_id: int) -> UserProgress:
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.point_id == point_id)
        .first()
    )
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            point_id=point_id,
            mastery="not_started",
            review_count=0,
            is_favorite=False,
        )
        db.add(progress)
    return progress


@router.put("/{point_id}", response_model=UserProgressOut)
def update_mastery(
    point_id: int,
    body: UserProgressUpdate,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    progress = _get_or_create_progress(db, user_id, point_id)
    progress.mastery = body.mastery
    progress.last_reviewed_at = datetime.utcnow()
    progress.review_count += 1
    db.commit()
    db.refresh(progress)
    return progress


@router.put("/{point_id}/favorite", response_model=UserProgressOut)
def toggle_favorite(
    point_id: int,
    body: FavoriteToggle,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    progress = _get_or_create_progress(db, user_id, point_id)
    progress.is_favorite = body.is_favorite
    db.commit()
    db.refresh(progress)
    return progress
