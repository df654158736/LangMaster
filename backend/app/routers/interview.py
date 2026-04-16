import random
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InterviewSession, KnowledgePoint, UserProgress
from app.schemas import (
    InterviewAnswer,
    InterviewConfig,
    InterviewReportOut,
    InterviewStartOut,
    KnowledgePointOut,
)

router = APIRouter(prefix="/api/interview", tags=["interview"])


def get_user_id(x_user_id: str | None = Header(None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header required")
    return x_user_id


@router.post("/start", response_model=InterviewStartOut)
def start_interview(
    config: InterviewConfig,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgePoint)
    if config.categories:
        query = query.filter(KnowledgePoint.category.in_(config.categories))
    if config.levels:
        query = query.filter(KnowledgePoint.level.in_(config.levels))
    if config.min_heat > 1:
        query = query.filter(KnowledgePoint.interview_heat >= config.min_heat)

    candidates = query.all()

    if config.strategy == "smart":
        progress_map = {}
        for p in db.query(UserProgress).filter(UserProgress.user_id == user_id).all():
            progress_map[p.point_id] = p

        def sort_key(pt):
            prog = progress_map.get(pt.id)
            if not prog or prog.mastery == "not_started":
                return (0, datetime.min)
            if prog.mastery == "partial":
                return (1, prog.last_reviewed_at or datetime.min)
            return (2, prog.last_reviewed_at or datetime.min)

        candidates.sort(key=sort_key)
    elif config.strategy == "sequential":
        candidates.sort(key=lambda pt: pt.sort_order)
    else:
        random.shuffle(candidates)

    questions = candidates[: config.count]

    session = InterviewSession(
        user_id=user_id,
        config=config.model_dump(),
        results=[],
        total_mastered=0,
        total_partial=0,
        total_unfamiliar=0,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return InterviewStartOut(
        session_id=session.id,
        questions=[KnowledgePointOut.model_validate(q) for q in questions],
    )


@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    answer: InterviewAnswer,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    results = list(session.results or [])
    results.append({"point_id": answer.point_id, "self_score": answer.self_score})
    session.results = results

    score_map = {"mastered": "total_mastered", "partial": "total_partial", "unfamiliar": "total_unfamiliar"}
    field = score_map.get(answer.self_score)
    if field:
        setattr(session, field, getattr(session, field) + 1)

    # Also update UserProgress
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.point_id == answer.point_id)
        .first()
    )
    if not progress:
        progress = UserProgress(
            user_id=user_id,
            point_id=answer.point_id,
            mastery="not_started",
            review_count=0,
            is_favorite=False,
        )
        db.add(progress)

    mastery_map = {"mastered": "mastered", "partial": "partial", "unfamiliar": "not_started"}
    progress.mastery = mastery_map.get(answer.self_score, progress.mastery)
    progress.last_reviewed_at = datetime.utcnow()
    progress.review_count += 1

    db.commit()
    return {"status": "ok", "results_count": len(results)}


@router.get("/history", response_model=list[InterviewReportOut])
def get_history(
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )


@router.get("/{session_id}/report", response_model=InterviewReportOut)
def get_report(
    session_id: int,
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    session = (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
