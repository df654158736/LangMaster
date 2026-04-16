from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import KnowledgePoint
from app.schemas import KnowledgePointBrief, KnowledgePointOut

router = APIRouter(prefix="/api/points", tags=["points"])

SORT_COLUMNS = {
    "interview_heat": KnowledgePoint.interview_heat,
    "dev_utility": KnowledgePoint.dev_utility,
    "sort_order": KnowledgePoint.sort_order,
}


@router.get("", response_model=list[KnowledgePointBrief])
def list_points(
    category: str | None = None,
    level: str | None = None,
    sort: str = "sort_order",
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgePoint)
    if category:
        query = query.filter(KnowledgePoint.category == category)
    if level:
        query = query.filter(KnowledgePoint.level == level)
    sort_col = SORT_COLUMNS.get(sort, KnowledgePoint.sort_order)
    if sort in ("interview_heat", "dev_utility"):
        query = query.order_by(desc(sort_col), KnowledgePoint.sort_order)
    else:
        query = query.order_by(sort_col)
    return query.all()


@router.get("/{point_id}", response_model=KnowledgePointOut)
def get_point(point_id: int, db: Session = Depends(get_db)):
    point = db.query(KnowledgePoint).filter(KnowledgePoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="Knowledge point not found")
    return point
