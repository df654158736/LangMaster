from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterviewSession, KnowledgePoint, UserProgress
from app.schemas import DashboardStats, WeakPoint

router = APIRouter(prefix="/api/stats", tags=["stats"])


def get_user_id(x_user_id: str | None = Header(None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header required")
    return x_user_id


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    total_points = db.query(KnowledgePoint).count()
    progress_list = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

    mastered_count = sum(1 for p in progress_list if p.mastery == "mastered")
    weak_count = sum(1 for p in progress_list if p.mastery in ("partial", "not_started") and p.review_count > 0)

    interview_count = (
        db.query(InterviewSession).filter(InterviewSession.user_id == user_id).count()
    )

    last_session = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
        .first()
    )
    last_score_percent = None
    if last_session and last_session.results:
        total = len(last_session.results)
        if total > 0:
            last_score_percent = round(last_session.total_mastered / total * 100, 1)

    return DashboardStats(
        total_points=total_points,
        mastered_count=mastered_count,
        interview_count=interview_count,
        weak_count=weak_count,
        last_score_percent=last_score_percent,
    )


@router.get("/weak-points", response_model=list[WeakPoint])
def weak_points(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    progress_list = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.mastery.in_(["partial", "not_started"]),
            UserProgress.review_count > 0,
        )
        .all()
    )
    result = []
    for p in progress_list:
        point = db.query(KnowledgePoint).filter(KnowledgePoint.id == p.point_id).first()
        if point:
            result.append(
                WeakPoint(
                    point_id=p.point_id,
                    title=point.title,
                    mastery=p.mastery,
                    category=point.category,
                    level=point.level,
                )
            )
    return result
