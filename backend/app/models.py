from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # basic/intermediate/advanced
    interview_heat: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3
    dev_utility: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3
    scenario: Mapped[str] = mapped_column(Text, nullable=False)
    code_example: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[list] = mapped_column(JSON, nullable=False)
    common_mistakes: Mapped[list] = mapped_column(JSON, nullable=False)
    related_point_ids: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    point_id: Mapped[int] = mapped_column(Integer, nullable=False)
    mastery: Mapped[str] = mapped_column(String(20), default="not_started")  # not_started/partial/mastered
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    results: Mapped[list] = mapped_column(JSON, default=list)
    total_mastered: Mapped[int] = mapped_column(Integer, default=0)
    total_partial: Mapped[int] = mapped_column(Integer, default=0)
    total_unfamiliar: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
