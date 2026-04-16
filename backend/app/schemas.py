from datetime import datetime

from pydantic import BaseModel


# --- Knowledge Point ---

class KnowledgePointOut(BaseModel):
    id: int
    title: str
    category: str
    level: str
    interview_heat: int
    dev_utility: int
    scenario: str
    code_example: str
    key_points: list[str]
    common_mistakes: list[str]
    related_point_ids: list[int]
    tags: list[str]
    sort_order: int

    model_config = {"from_attributes": True}


class KnowledgePointBrief(BaseModel):
    """Card wall view — no code_example or common_mistakes."""
    id: int
    title: str
    category: str
    level: str
    interview_heat: int
    dev_utility: int
    scenario: str
    tags: list[str]
    sort_order: int

    model_config = {"from_attributes": True}


# --- User Progress ---

class UserProgressOut(BaseModel):
    point_id: int
    mastery: str
    last_reviewed_at: datetime | None
    review_count: int
    is_favorite: bool

    model_config = {"from_attributes": True}


class UserProgressUpdate(BaseModel):
    mastery: str  # not_started / partial / mastered


class FavoriteToggle(BaseModel):
    is_favorite: bool


# --- Interview ---

class InterviewConfig(BaseModel):
    categories: list[str] | None = None  # None = all
    levels: list[str] | None = None
    min_heat: int = 1  # 1-3, filter interview_heat >= this
    count: int = 10
    strategy: str = "smart"  # smart / random / sequential


class InterviewAnswer(BaseModel):
    point_id: int
    self_score: str  # mastered / partial / unfamiliar


class InterviewStartOut(BaseModel):
    session_id: int
    questions: list[KnowledgePointOut]


class InterviewReportOut(BaseModel):
    id: int
    config: dict
    results: list[dict]
    total_mastered: int
    total_partial: int
    total_unfamiliar: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Stats ---

class DashboardStats(BaseModel):
    total_points: int
    mastered_count: int
    interview_count: int
    weak_count: int
    last_score_percent: float | None


class WeakPoint(BaseModel):
    point_id: int
    title: str
    mastery: str
    category: str
    level: str
