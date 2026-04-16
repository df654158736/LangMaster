# LangMaster Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a LangChain/LangGraph teaching web app with scenario-driven knowledge cards and simulated interview mode.

**Architecture:** Python FastAPI backend with SQLite database serves knowledge points, progress tracking, and interview logic via REST API. Next.js frontend with Tailwind CSS renders the card wall, detail pages, interview flow, and dashboard. MVP uses localStorage-generated UUID for user identity.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, pytest | Next.js 14 (App Router), TypeScript, Tailwind CSS

---

## File Structure

```
langsurpervisor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, router mounting
│   │   ├── database.py          # SQLAlchemy engine, session, Base
│   │   ├── models.py            # ORM models: KnowledgePoint, UserProgress, InterviewSession
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── points.py        # GET /api/points, GET /api/points/:id
│   │   │   ├── progress.py      # GET/PUT /api/progress
│   │   │   ├── interview.py     # POST /api/interview/start, answer, report, history
│   │   │   └── stats.py         # GET /api/stats/dashboard, weak-points
│   │   └── seed.py              # Seed data: 30+ LangChain/LangGraph knowledge points
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Test DB fixtures
│   │   ├── test_points.py
│   │   ├── test_progress.py
│   │   ├── test_interview.py
│   │   └── test_stats.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout + Navbar
│   │   │   ├── page.tsx             # Dashboard (home)
│   │   │   ├── learn/
│   │   │   │   ├── page.tsx         # Card wall (all levels)
│   │   │   │   └── [id]/page.tsx    # Knowledge point detail
│   │   │   ├── interview/
│   │   │   │   ├── setup/page.tsx   # Interview config
│   │   │   │   ├── session/page.tsx # Active interview
│   │   │   │   └── report/page.tsx  # Interview report
│   │   │   └── profile/page.tsx     # User profile + history
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── KnowledgeCard.tsx    # Card in wall view
│   │   │   ├── FilterBar.tsx        # Category + sort controls
│   │   │   ├── CodeBlock.tsx        # Syntax-highlighted code with copy
│   │   │   ├── InterviewQuestion.tsx # Single question in interview flow
│   │   │   ├── SelfRating.tsx       # 3-option self-evaluation
│   │   │   └── StatsCard.tsx        # Dashboard stat card
│   │   └── lib/
│   │       ├── api.ts               # API client (fetch wrapper)
│   │       ├── user.ts              # localStorage UUID management
│   │       └── types.ts             # Shared TypeScript types
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.ts
└── README.md
```

---

### Task 1: Backend Project Setup

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/database.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create requirements.txt**

```txt
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
pytest==8.3.0
httpx==0.27.0
```

- [ ] **Step 2: Create database module**

Create `backend/app/__init__.py` (empty file).

Create `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./langmaster.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 3: Create FastAPI app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LangMaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Install dependencies and verify**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- [ ] **Step 5: Run server and verify health endpoint**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
# In another terminal:
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git init
echo "venv/\n__pycache__/\n*.db\n.superpowers/\nnode_modules/\n.next/" > .gitignore
git add backend/requirements.txt backend/app/__init__.py backend/app/database.py backend/app/main.py .gitignore
git commit -m "feat: backend project setup with FastAPI and SQLite"
```

---

### Task 2: Database Models

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`

- [ ] **Step 1: Create ORM models**

Create `backend/app/models.py`:

```python
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
```

- [ ] **Step 2: Create Pydantic schemas**

Create `backend/app/schemas.py`:

```python
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
```

- [ ] **Step 3: Verify models load without errors**

```bash
cd backend
python -c "from app.models import KnowledgePoint, UserProgress, InterviewSession; print('Models OK')"
python -c "from app.schemas import KnowledgePointOut, InterviewConfig; print('Schemas OK')"
```

Expected: Both print OK.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models.py backend/app/schemas.py
git commit -m "feat: add database models and Pydantic schemas"
```

---

### Task 3: Test Fixtures

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create test fixtures**

Create `backend/tests/__init__.py` (empty file).

Create `backend/tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import KnowledgePoint

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_points(db):
    points = [
        KnowledgePoint(
            id=1,
            title="ChatPromptTemplate",
            category="Prompt",
            level="basic",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要构建带变量的提示词模板时",
            code_example='from langchain_core.prompts import ChatPromptTemplate\n\nprompt = ChatPromptTemplate.from_messages([\n    ("system", "你是一个{role}专家"),\n    ("human", "{question}"),\n])\nmessages = prompt.invoke({"role": "Python", "question": "如何使用列表推导式？"})',
            key_points=["支持 system/human/ai 消息类型", "变量用 {name} 占位", "是 LCEL 链的标准起点"],
            common_mistakes=["混淆 PromptTemplate 和 ChatPromptTemplate", "忘记消息类型元组格式"],
            related_point_ids=[2, 3],
            tags=["langchain", "prompt", "基础"],
            sort_order=1,
        ),
        KnowledgePoint(
            id=2,
            title="RunnableSequence",
            category="Chain",
            level="basic",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要将多个步骤串联为一个处理管道时",
            code_example='from langchain_core.prompts import ChatPromptTemplate\nfrom langchain_openai import ChatOpenAI\nfrom langchain_core.output_parsers import StrOutputParser\n\nchain = ChatPromptTemplate.from_template("讲一个关于{topic}的笑话") | ChatOpenAI() | StrOutputParser()\nresult = chain.invoke({"topic": "程序员"})',
            key_points=["用 | 管道符串联", "每个组件实现 Runnable 接口", "支持 invoke/ainvoke/stream"],
            common_mistakes=["组件输入输出类型不匹配", "忘记最后加 OutputParser"],
            related_point_ids=[1],
            tags=["langchain", "chain", "LCEL", "基础"],
            sort_order=2,
        ),
        KnowledgePoint(
            id=3,
            title="StateGraph",
            category="Graph",
            level="intermediate",
            interview_heat=3,
            dev_utility=3,
            scenario="当你需要构建有状态的多步骤 Agent 工作流时",
            code_example='from langgraph.graph import StateGraph, START, END\nfrom typing import TypedDict\n\nclass State(TypedDict):\n    messages: list[str]\n    count: int\n\ndef node_a(state: State) -> dict:\n    return {"messages": state["messages"] + ["hello from A"], "count": state["count"] + 1}\n\ngraph = StateGraph(State)\ngraph.add_node("a", node_a)\ngraph.add_edge(START, "a")\ngraph.add_edge("a", END)\napp = graph.compile()\nresult = app.invoke({"messages": [], "count": 0})',
            key_points=["State 用 TypedDict 定义", "add_node 注册节点函数", "add_edge 定义流转"],
            common_mistakes=["忘记 compile()", "State 字段类型不一致"],
            related_point_ids=[],
            tags=["langgraph", "graph", "进阶"],
            sort_order=10,
        ),
    ]
    db.add_all(points)
    db.commit()
    return points
```

- [ ] **Step 2: Verify fixtures work**

```bash
cd backend
python -m pytest tests/ --co -q
```

Expected: Shows collected test items (0 tests, no errors).

- [ ] **Step 3: Commit**

```bash
git add backend/tests/
git commit -m "feat: add test fixtures with sample knowledge points"
```

---

### Task 4: Knowledge Points API

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/points.py`
- Create: `backend/tests/test_points.py`
- Modify: `backend/app/main.py` (add router)

- [ ] **Step 1: Write failing tests**

Create `backend/app/routers/__init__.py` (empty file).

Create `backend/tests/test_points.py`:

```python
def test_list_points_returns_all(client, sample_points):
    resp = client.get("/api/points")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_list_points_filter_by_category(client, sample_points):
    resp = client.get("/api/points?category=Prompt")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "ChatPromptTemplate"


def test_list_points_filter_by_level(client, sample_points):
    resp = client.get("/api/points?level=basic")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


def test_list_points_sort_by_interview_heat(client, sample_points):
    resp = client.get("/api/points?sort=interview_heat")
    assert resp.status_code == 200
    data = resp.json()
    # All have heat=3, so sort is stable by sort_order
    assert data[0]["title"] == "ChatPromptTemplate"


def test_list_points_sort_by_dev_utility(client, sample_points):
    resp = client.get("/api/points?sort=dev_utility")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_point_detail(client, sample_points):
    resp = client.get("/api/points/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "ChatPromptTemplate"
    assert "code_example" in data
    assert len(data["key_points"]) == 3


def test_get_point_not_found(client, sample_points):
    resp = client.get("/api/points/999")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
python -m pytest tests/test_points.py -v
```

Expected: FAIL (no route registered).

- [ ] **Step 3: Implement points router**

Create `backend/app/routers/points.py`:

```python
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
```

- [ ] **Step 4: Mount router in main.py**

Add to `backend/app/main.py` after the CORS middleware block:

```python
from app.routers import points

app.include_router(points.router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
python -m pytest tests/test_points.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/ backend/tests/test_points.py backend/app/main.py
git commit -m "feat: add knowledge points API with filtering and sorting"
```

---

### Task 5: User Progress API

**Files:**
- Create: `backend/app/routers/progress.py`
- Create: `backend/tests/test_progress.py`
- Modify: `backend/app/main.py` (add router)

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_progress.py`:

```python
USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_get_progress_empty(client, sample_points):
    resp = client.get("/api/progress", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


def test_update_mastery(client, sample_points):
    resp = client.put(
        "/api/progress/1",
        json={"mastery": "mastered"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["mastery"] == "mastered"
    assert resp.json()["review_count"] == 1


def test_update_mastery_increments_review_count(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    assert resp.json()["review_count"] == 2


def test_get_progress_after_update(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    resp = client.get("/api/progress", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["point_id"] == 1
    assert data[0]["mastery"] == "mastered"


def test_toggle_favorite(client, sample_points):
    resp = client.put(
        "/api/progress/1/favorite",
        json={"is_favorite": True},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True


def test_toggle_favorite_off(client, sample_points):
    client.put("/api/progress/1/favorite", json={"is_favorite": True}, headers=HEADERS)
    resp = client.put("/api/progress/1/favorite", json={"is_favorite": False}, headers=HEADERS)
    assert resp.json()["is_favorite"] is False


def test_progress_requires_user_id(client, sample_points):
    resp = client.get("/api/progress")
    assert resp.status_code == 400
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
python -m pytest tests/test_progress.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement progress router**

Create `backend/app/routers/progress.py`:

```python
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
        progress = UserProgress(user_id=user_id, point_id=point_id)
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
```

- [ ] **Step 4: Mount router in main.py**

Add to `backend/app/main.py`:

```python
from app.routers import points, progress

app.include_router(points.router)
app.include_router(progress.router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
python -m pytest tests/test_progress.py -v
```

Expected: All 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/progress.py backend/tests/test_progress.py backend/app/main.py
git commit -m "feat: add user progress API with mastery and favorites"
```

---

### Task 6: Interview API

**Files:**
- Create: `backend/app/routers/interview.py`
- Create: `backend/tests/test_interview.py`
- Modify: `backend/app/main.py` (add router)

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_interview.py`:

```python
USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_start_interview_random(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["questions"]) == 2


def test_start_interview_filter_by_category(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"categories": ["Prompt"], "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 1
    assert data["questions"][0]["category"] == "Prompt"


def test_start_interview_filter_by_level(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"levels": ["basic"], "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 2


def test_start_interview_filter_by_heat(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"min_heat": 3, "count": 10, "strategy": "random"},
        headers=HEADERS,
    )
    data = resp.json()
    assert len(data["questions"]) == 3  # all have heat=3


def test_submit_answer(client, sample_points):
    start = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "random"},
        headers=HEADERS,
    )
    session_id = start.json()["session_id"]
    resp = client.post(
        f"/api/interview/{session_id}/answer",
        json={"point_id": 1, "self_score": "mastered"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()["results_count"] == 1


def test_get_report(client, sample_points):
    start = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "random"},
        headers=HEADERS,
    )
    session_id = start.json()["session_id"]
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 1, "self_score": "mastered"}, headers=HEADERS)
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 2, "self_score": "partial"}, headers=HEADERS)
    client.post(f"/api/interview/{session_id}/answer", json={"point_id": 3, "self_score": "unfamiliar"}, headers=HEADERS)

    resp = client.get(f"/api/interview/{session_id}/report", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_mastered"] == 1
    assert data["total_partial"] == 1
    assert data["total_unfamiliar"] == 1


def test_get_history(client, sample_points):
    client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    resp = client.get("/api/interview/history", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_start_interview_sequential(client, sample_points):
    resp = client.post(
        "/api/interview/start",
        json={"count": 3, "strategy": "sequential"},
        headers=HEADERS,
    )
    data = resp.json()
    orders = [q["sort_order"] for q in data["questions"]]
    assert orders == sorted(orders)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
python -m pytest tests/test_interview.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement interview router**

Create `backend/app/routers/interview.py`:

```python
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
        progress = UserProgress(user_id=user_id, point_id=answer.point_id)
        db.add(progress)

    mastery_map = {"mastered": "mastered", "partial": "partial", "unfamiliar": "not_started"}
    progress.mastery = mastery_map.get(answer.self_score, progress.mastery)
    progress.last_reviewed_at = datetime.utcnow()
    progress.review_count += 1

    db.commit()
    return {"status": "ok", "results_count": len(results)}


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
```

- [ ] **Step 4: Mount router in main.py**

Update `backend/app/main.py` imports:

```python
from app.routers import points, progress, interview

app.include_router(points.router)
app.include_router(progress.router)
app.include_router(interview.router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
python -m pytest tests/test_interview.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/interview.py backend/tests/test_interview.py backend/app/main.py
git commit -m "feat: add interview API with start, answer, report, history"
```

---

### Task 7: Stats API

**Files:**
- Create: `backend/app/routers/stats.py`
- Create: `backend/tests/test_stats.py`
- Modify: `backend/app/main.py` (add router)

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_stats.py`:

```python
USER_ID = "test-user-uuid"
HEADERS = {"X-User-Id": USER_ID}


def test_dashboard_empty(client, sample_points):
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_points"] == 3
    assert data["mastered_count"] == 0
    assert data["interview_count"] == 0
    assert data["weak_count"] == 0
    assert data["last_score_percent"] is None


def test_dashboard_with_progress(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    client.put("/api/progress/2", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    data = resp.json()
    assert data["mastered_count"] == 1
    assert data["weak_count"] == 1  # partial counts as weak


def test_dashboard_with_interview(client, sample_points):
    client.post(
        "/api/interview/start",
        json={"count": 2, "strategy": "random"},
        headers=HEADERS,
    )
    resp = client.get("/api/stats/dashboard", headers=HEADERS)
    assert resp.json()["interview_count"] == 1


def test_weak_points_empty(client, sample_points):
    resp = client.get("/api/stats/weak-points", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


def test_weak_points_returns_partial_and_not_started_reviewed(client, sample_points):
    client.put("/api/progress/1", json={"mastery": "mastered"}, headers=HEADERS)
    client.put("/api/progress/2", json={"mastery": "partial"}, headers=HEADERS)
    resp = client.get("/api/stats/weak-points", headers=HEADERS)
    data = resp.json()
    assert len(data) == 1
    assert data[0]["point_id"] == 2
    assert data[0]["mastery"] == "partial"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
python -m pytest tests/test_stats.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement stats router**

Create `backend/app/routers/stats.py`:

```python
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
```

- [ ] **Step 4: Mount router in main.py**

Update `backend/app/main.py` imports:

```python
from app.routers import points, progress, interview, stats

app.include_router(points.router)
app.include_router(progress.router)
app.include_router(interview.router)
app.include_router(stats.router)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
python -m pytest tests/test_stats.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 6: Run all backend tests**

```bash
cd backend
python -m pytest tests/ -v
```

Expected: All tests PASS (points: 7, progress: 7, interview: 8, stats: 5 = 27 total).

- [ ] **Step 7: Commit**

```bash
git add backend/app/routers/stats.py backend/tests/test_stats.py backend/app/main.py
git commit -m "feat: add stats API with dashboard and weak-points"
```

---

### Task 8: Seed Data

**Files:**
- Create: `backend/app/seed.py`
- Modify: `backend/app/main.py` (add seed on startup)

- [ ] **Step 1: Create seed data with 30 knowledge points**

Create `backend/app/seed.py`:

```python
from sqlalchemy.orm import Session

from app.models import KnowledgePoint

SEED_DATA = [
    # === BASIC: LangChain ===
    {
        "id": 1,
        "title": "ChatPromptTemplate",
        "category": "Prompt",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建带变量的提示词模板，将系统消息、用户消息组合成结构化 prompt 发送给 LLM 时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}专家"),
    ("human", "{question}"),
])
messages = prompt.invoke({"role": "Python", "question": "如何使用列表推导式？"})
print(messages)""",
        "key_points": [
            "支持 system/human/ai/placeholder 四种消息类型",
            "变量用 {variable_name} 占位，invoke 时传入字典",
            "是 LCEL 链的标准起点，可用 | 管道符串联后续步骤",
        ],
        "common_mistakes": [
            "混淆 PromptTemplate（生成字符串）和 ChatPromptTemplate（生成消息列表）",
            "忘记 from_messages 中使用 (role, content) 元组格式",
        ],
        "related_point_ids": [2, 3, 4],
        "tags": ["langchain", "prompt", "基础"],
        "sort_order": 1,
    },
    {
        "id": 2,
        "title": "MessagesPlaceholder",
        "category": "Prompt",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在 prompt 模板中动态插入一段历史对话消息列表时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
messages = prompt.invoke({
    "history": [("human", "你好"), ("ai", "你好！有什么可以帮你的？")],
    "input": "介绍一下 Python",
})""",
        "key_points": [
            "用于在模板中插入动态数量的历史消息",
            "variable_name 对应 invoke 字典中的 key",
            "常与 Memory 配合实现多轮对话",
        ],
        "common_mistakes": [
            "忘记将 history 作为消息列表传入（传了字符串）",
            "optional=False 时不传 history 会报错",
        ],
        "related_point_ids": [1, 12],
        "tags": ["langchain", "prompt", "memory", "基础"],
        "sort_order": 2,
    },
    {
        "id": 3,
        "title": "StrOutputParser",
        "category": "Output",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要从 LLM 的 AIMessage 响应中提取纯文本字符串时",
        "code_example": """from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("用一句话解释{concept}")
    | ChatOpenAI()
    | StrOutputParser()
)
result = chain.invoke({"concept": "递归"})
print(result)  # 纯字符串，不再是 AIMessage 对象""",
        "key_points": [
            "将 AIMessage 对象转为纯字符串",
            "是最常用的 OutputParser，几乎每条链都会用到",
            "放在 LCEL 链末尾，用 | 连接",
        ],
        "common_mistakes": [
            "不加 StrOutputParser 直接使用链，拿到的是 AIMessage 对象而非字符串",
            "对需要结构化输出的场景误用 StrOutputParser（应该用 PydanticOutputParser）",
        ],
        "related_point_ids": [1, 4, 5],
        "tags": ["langchain", "output", "LCEL", "基础"],
        "sort_order": 3,
    },
    {
        "id": 4,
        "title": "PydanticOutputParser",
        "category": "Output",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要 LLM 返回结构化数据（如 JSON 对象）并自动校验格式时",
        "code_example": """from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class Joke(BaseModel):
    setup: str = Field(description="笑话的开头")
    punchline: str = Field(description="笑话的结尾")

parser = PydanticOutputParser(pydantic_object=Joke)
prompt = ChatPromptTemplate.from_template(
    "讲一个关于{topic}的笑话。\\n{format_instructions}"
)
# parser.get_format_instructions() 返回 JSON schema 提示
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | model | parser
result = chain.invoke({"topic": "程序员"})
print(result.setup, result.punchline)""",
        "key_points": [
            "用 Pydantic BaseModel 定义输出结构",
            "get_format_instructions() 生成格式说明注入 prompt",
            "自动解析 + 校验 LLM 输出，返回 Pydantic 对象",
        ],
        "common_mistakes": [
            "忘记在 prompt 中注入 format_instructions",
            "Field description 写得不清楚导致 LLM 输出格式不对",
        ],
        "related_point_ids": [3, 1],
        "tags": ["langchain", "output", "structured", "基础"],
        "sort_order": 4,
    },
    {
        "id": 5,
        "title": "RunnableSequence (LCEL管道)",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要将多个处理步骤（prompt → model → parser）串联为一个可执行管道时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 用 | 管道符构建 RunnableSequence
chain = (
    ChatPromptTemplate.from_template("翻译成英文：{text}")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

# 三种调用方式
result = chain.invoke({"text": "你好世界"})        # 同步
result = await chain.ainvoke({"text": "你好世界"})  # 异步
async for chunk in chain.astream({"text": "你好世界"}):  # 流式
    print(chunk, end="")""",
        "key_points": [
            "| 管道符是 LCEL 的核心语法，创建 RunnableSequence",
            "每个组件实现 Runnable 接口（invoke/ainvoke/stream/astream）",
            "前一个组件的输出自动作为下一个组件的输入",
        ],
        "common_mistakes": [
            "管道中组件的输入输出类型不匹配（如 parser 期望 AIMessage 但收到 str）",
            "在需要异步的环境中使用 invoke 而非 ainvoke",
        ],
        "related_point_ids": [1, 3, 6],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 5,
    },
    {
        "id": 6,
        "title": "ChatModel 调用",
        "category": "Model",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要直接调用 LLM（如 OpenAI、Anthropic）进行对话时",
        "code_example": """from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

# OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Anthropic
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# 直接调用
response = llm.invoke([
    SystemMessage(content="你是一个翻译助手"),
    HumanMessage(content="翻译：Hello World"),
])
print(response.content)""",
        "key_points": [
            "ChatOpenAI/ChatAnthropic 等是统一的 ChatModel 接口",
            "输入是 Message 列表，输出是 AIMessage",
            "temperature=0 表示确定性输出，适合需要一致结果的场景",
        ],
        "common_mistakes": [
            "忘记设置 API key 环境变量",
            "混淆 ChatOpenAI（Chat Model）和 OpenAI（旧版 LLM 接口）",
        ],
        "related_point_ids": [1, 5],
        "tags": ["langchain", "model", "基础"],
        "sort_order": 6,
    },
    {
        "id": 7,
        "title": "RunnableParallel",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要将输入同时分发给多个处理链并合并结果时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

chain = RunnableParallel(
    summary=ChatPromptTemplate.from_template("总结：{text}") | model | StrOutputParser(),
    translation=ChatPromptTemplate.from_template("翻译成英文：{text}") | model | StrOutputParser(),
)
result = chain.invoke({"text": "LangChain 是一个用于构建 LLM 应用的框架"})
print(result["summary"])
print(result["translation"])""",
        "key_points": [
            "多个链并行执行，提高效率",
            "结果以字典形式返回，key 对应每个分支的名称",
            "也可用 dict 语法简写：{\"a\": chain_a, \"b\": chain_b}",
        ],
        "common_mistakes": [
            "所有分支必须接受相同的输入格式",
            "并行分支之间不能有依赖关系",
        ],
        "related_point_ids": [5],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 7,
    },
    {
        "id": 8,
        "title": "RunnableLambda",
        "category": "Chain",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要在 LCEL 链中插入自定义的 Python 函数作为处理步骤时",
        "code_example": """from langchain_core.runnables import RunnableLambda

def add_prefix(text: str) -> str:
    return f"[重要] {text}"

def word_count(text: str) -> dict:
    return {"text": text, "count": len(text.split())}

# 方式1：显式包装
chain = RunnableLambda(add_prefix) | RunnableLambda(word_count)

# 方式2：用 @chain 装饰器（推荐）
from langchain_core.runnables import chain as chain_decorator

@chain_decorator
def my_step(input: str) -> str:
    return input.upper()

result = chain.invoke("hello world")""",
        "key_points": [
            "将普通 Python 函数转为 Runnable，可加入 LCEL 管道",
            "函数签名决定输入输出类型",
            "@chain 装饰器是更优雅的写法",
        ],
        "common_mistakes": [
            "函数返回类型与下一个组件期望的输入类型不匹配",
            "在 Lambda 中做了耗时操作但没有用异步版本",
        ],
        "related_point_ids": [5, 7],
        "tags": ["langchain", "LCEL", "chain", "基础"],
        "sort_order": 8,
    },
    # === BASIC: LangGraph ===
    {
        "id": 9,
        "title": "StateGraph 基本概念",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建有状态的、多步骤的 Agent 工作流时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. 定义状态
class State(TypedDict):
    messages: list[str]
    count: int

# 2. 定义节点（普通函数）
def greet(state: State) -> dict:
    return {
        "messages": state["messages"] + ["Hello!"],
        "count": state["count"] + 1,
    }

# 3. 构建图
graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)

# 4. 编译并运行
app = graph.compile()
result = app.invoke({"messages": [], "count": 0})
print(result)  # {"messages": ["Hello!"], "count": 1}""",
        "key_points": [
            "State 用 TypedDict 定义，是贯穿所有节点的共享状态",
            "节点是普通函数，接收 State 返回部分更新",
            "必须 compile() 后才能 invoke()",
        ],
        "common_mistakes": [
            "忘记调用 compile()",
            "节点函数返回完整 State 而非部分更新字典",
            "没有连接 START → 第一个节点",
        ],
        "related_point_ids": [10, 11],
        "tags": ["langgraph", "graph", "state", "基础"],
        "sort_order": 9,
    },
    {
        "id": 10,
        "title": "State 与 Annotation",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要定义图的状态结构，特别是需要对列表字段做追加操作而非覆盖时",
        "code_example": """from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add

# 用 Annotated + reducer 定义追加行为
class State(TypedDict):
    messages: Annotated[list[str], add]  # add = 列表追加
    count: int                            # 普通字段 = 覆盖

def node_a(state: State) -> dict:
    return {"messages": ["from A"], "count": 1}  # messages 会追加，count 会覆盖

def node_b(state: State) -> dict:
    return {"messages": ["from B"], "count": 2}

graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", END)
app = graph.compile()
result = app.invoke({"messages": [], "count": 0})
print(result)  # {"messages": ["from A", "from B"], "count": 2}""",
        "key_points": [
            "Annotated[type, reducer] 定义字段的合并策略",
            "operator.add 对列表做追加，对数字做累加",
            "没有 Annotation 的字段默认是覆盖行为",
        ],
        "common_mistakes": [
            "对 messages 不加 Annotated[..., add]，导致后面节点覆盖前面的消息",
            "reducer 函数签名不对（需要接收两个参数并返回合并结果）",
        ],
        "related_point_ids": [9, 11],
        "tags": ["langgraph", "state", "annotation", "基础"],
        "sort_order": 10,
    },
    {
        "id": 11,
        "title": "Node 与 Edge",
        "category": "Graph",
        "level": "basic",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在图中定义多个处理节点并指定它们之间的执行顺序时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    value: str

def step1(state: State) -> dict:
    return {"value": state["value"] + " -> step1"}

def step2(state: State) -> dict:
    return {"value": state["value"] + " -> step2"}

graph = StateGraph(State)
# 添加节点
graph.add_node("step1", step1)
graph.add_node("step2", step2)
# 添加边（定义顺序）
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", END)

app = graph.compile()
result = app.invoke({"value": "start"})
print(result["value"])  # "start -> step1 -> step2" """,
        "key_points": [
            "add_node(name, func) 注册节点",
            "add_edge(from, to) 定义节点间的固定连接",
            "START 和 END 是内置的特殊节点",
        ],
        "common_mistakes": [
            "节点名称拼写不一致（add_node 和 add_edge 中的名称不匹配）",
            "形成了死循环没有通往 END 的路径",
        ],
        "related_point_ids": [9, 10, 15],
        "tags": ["langgraph", "graph", "基础"],
        "sort_order": 11,
    },
    # === INTERMEDIATE: LangChain ===
    {
        "id": 12,
        "title": "ConversationBufferMemory",
        "category": "Memory",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要让 LLM 记住之前的对话内容实现多轮对话时",
        "code_example": """from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

memory = ConversationBufferMemory(return_messages=True)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = (
    RunnablePassthrough.assign(history=lambda _: memory.load_memory_variables({})["history"])
    | prompt
    | ChatOpenAI()
    | StrOutputParser()
)

# 对话
response = chain.invoke({"input": "我叫小明"})
memory.save_context({"input": "我叫小明"}, {"output": response})
response = chain.invoke({"input": "我叫什么？"})  # 能记住""",
        "key_points": [
            "return_messages=True 让 memory 返回消息对象而非字符串",
            "需要手动 save_context 保存每轮对话",
            "在 LangGraph 中推荐用 Checkpointing 替代 Memory",
        ],
        "common_mistakes": [
            "忘记 save_context 导致 LLM '失忆'",
            "在高并发场景使用 BufferMemory（不是线程安全的）",
        ],
        "related_point_ids": [2, 18],
        "tags": ["langchain", "memory", "进阶"],
        "sort_order": 12,
    },
    {
        "id": 13,
        "title": "Document Loaders",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要从文件（PDF/TXT/CSV）、网页或数据库中加载文档用于 RAG 时",
        "code_example": """from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    WebBaseLoader,
)

# 加载文本文件
docs = TextLoader("data.txt").load()

# 加载 PDF
docs = PyPDFLoader("report.pdf").load()

# 加载网页
docs = WebBaseLoader("https://example.com").load()

# 每个 Document 有 page_content 和 metadata
for doc in docs:
    print(doc.page_content[:100])
    print(doc.metadata)""",
        "key_points": [
            "所有 Loader 都有统一的 .load() 接口，返回 Document 列表",
            "Document 包含 page_content（文本）和 metadata（来源信息）",
            "是 RAG 管道的第一步：加载 → 切分 → 嵌入 → 检索",
        ],
        "common_mistakes": [
            "忘记安装对应的依赖包（如 pypdf、beautifulsoup4）",
            "对大文件直接 load() 导致内存溢出（应该用 lazy_load()）",
        ],
        "related_point_ids": [14, 15, 16],
        "tags": ["langchain", "RAG", "retrieval", "进阶"],
        "sort_order": 13,
    },
    {
        "id": 14,
        "title": "Text Splitters",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要将长文档切分为适合嵌入和检索的小块时",
        "code_example": """from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\\n\\n", "\\n", "。", "，", " ", ""],
)

text = "这是一段很长的文本..." * 100
chunks = splitter.split_text(text)
print(f"切分为 {len(chunks)} 个块")

# 也可以直接对 Document 列表操作
from langchain_community.document_loaders import TextLoader
docs = TextLoader("data.txt").load()
split_docs = splitter.split_documents(docs)""",
        "key_points": [
            "RecursiveCharacterTextSplitter 是最常用的切分器",
            "chunk_size 控制每块大小，chunk_overlap 控制重叠",
            "separators 按优先级尝试，先按段落分，再按句子分",
        ],
        "common_mistakes": [
            "chunk_size 设太大导致检索不精确，设太小丢失上下文",
            "忘记设 chunk_overlap 导致跨块信息丢失",
        ],
        "related_point_ids": [13, 15, 16],
        "tags": ["langchain", "RAG", "retrieval", "进阶"],
        "sort_order": 14,
    },
    {
        "id": 15,
        "title": "Embeddings + Vector Store",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要将文档块转为向量并存储到向量数据库以支持语义检索时",
        "code_example": """from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 准备嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. 从文档创建向量库
from langchain_text_splitters import RecursiveCharacterTextSplitter
texts = ["LangChain 是一个框架", "LangGraph 用于构建 Agent", "RAG 是检索增强生成"]
vectorstore = FAISS.from_texts(texts, embeddings)

# 3. 相似性搜索
results = vectorstore.similarity_search("什么是 Agent？", k=2)
for doc in results:
    print(doc.page_content)

# 4. 转为 Retriever 用于链
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})""",
        "key_points": [
            "Embeddings 将文本转为向量，VectorStore 存储和检索向量",
            "FAISS 适合本地开发，生产可用 Pinecone/Chroma/Weaviate",
            "as_retriever() 将向量库转为 Retriever 接口，可加入 LCEL 链",
        ],
        "common_mistakes": [
            "嵌入模型和查询用了不同的模型导致检索效果差",
            "k 值设太大导致上下文过长超出 LLM 窗口",
        ],
        "related_point_ids": [13, 14, 16],
        "tags": ["langchain", "RAG", "embeddings", "vector", "进阶"],
        "sort_order": 15,
    },
    {
        "id": 16,
        "title": "RAG 完整链",
        "category": "Retrieval",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要构建完整的检索增强生成管道，让 LLM 基于你的文档回答问题时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 假设 vectorstore 已创建
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_template(
    \"\"\"基于以下上下文回答问题。如果上下文中没有相关信息，说"我不确定"。

上下文：{context}

问题：{question}\"\"\"
)

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | ChatOpenAI()
    | StrOutputParser()
)

answer = rag_chain.invoke("LangGraph 是什么？")""",
        "key_points": [
            "RAG = Retriever + Prompt + LLM，是最常见的 LLM 应用模式",
            "RunnablePassthrough() 将用户输入直接传递到 question",
            "retriever | format_docs 将检索结果格式化为上下文字符串",
        ],
        "common_mistakes": [
            "prompt 中没有明确告诉 LLM '基于上下文回答'导致幻觉",
            "format_docs 中没有分隔文档导致上下文混乱",
        ],
        "related_point_ids": [13, 14, 15, 5],
        "tags": ["langchain", "RAG", "进阶"],
        "sort_order": 16,
    },
    {
        "id": 17,
        "title": "Tools 定义与绑定",
        "category": "Tools",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要让 LLM 调用外部函数（如搜索、计算、API调用）时",
        "code_example": """from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search(query: str) -> str:
    \"\"\"搜索互联网获取最新信息\"\"\"
    return f"搜索结果：关于 {query} 的最新信息..."

@tool
def calculator(expression: str) -> str:
    \"\"\"计算数学表达式\"\"\"
    return str(eval(expression))

# 将工具绑定到模型
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([search, calculator])

# 模型会决定是否调用工具
response = llm_with_tools.invoke("2024年奥运会在哪里举办？")
print(response.tool_calls)  # [{"name": "search", "args": {...}}]""",
        "key_points": [
            "@tool 装饰器将函数转为 Tool，docstring 作为工具描述",
            "bind_tools() 让 LLM 知道可用工具，但不自动执行",
            "LLM 返回 tool_calls 列表，需要你自己执行并返回结果",
        ],
        "common_mistakes": [
            "tool 的 docstring 写得不清楚导致 LLM 不知道何时调用",
            "以为 bind_tools 会自动执行工具（需要配合 Agent 或手动执行）",
        ],
        "related_point_ids": [18, 19],
        "tags": ["langchain", "tools", "agent", "进阶"],
        "sort_order": 17,
    },
    {
        "id": 18,
        "title": "create_react_agent",
        "category": "Agent",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要快速创建一个能自主决定使用工具的 ReAct Agent 时",
        "code_example": """from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    \"\"\"获取城市天气\"\"\"
    return f"{city}今天晴，25°C"

@tool
def search(query: str) -> str:
    \"\"\"搜索信息\"\"\"
    return f"搜索结果：{query}"

llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[get_weather, search])

# Agent 自动决定用哪个工具
result = agent.invoke({
    "messages": [("human", "北京今天天气怎么样？")]
})
print(result["messages"][-1].content)""",
        "key_points": [
            "create_react_agent 是 LangGraph 提供的预构建 Agent",
            "Agent 自动循环：思考 → 选择工具 → 执行 → 观察 → 继续/结束",
            "底层是 LangGraph 的 StateGraph，可自定义扩展",
        ],
        "common_mistakes": [
            "tools 列表为空（Agent 没有工具可用）",
            "工具太多导致 LLM 选择混乱（建议 5-10 个以内）",
        ],
        "related_point_ids": [17, 9, 19],
        "tags": ["langchain", "langgraph", "agent", "进阶"],
        "sort_order": 18,
    },
    {
        "id": 19,
        "title": "Callbacks",
        "category": "Chain",
        "level": "intermediate",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要监控链的执行过程（日志、token计数、延迟追踪）时",
        "code_example": """from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

class MyCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM 开始调用，prompt 长度: {len(prompts[0])}")

    def on_llm_end(self, response, **kwargs):
        print(f"LLM 结束，token 使用: {response.llm_output}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"Chain 开始: {serialized.get('name', 'unknown')}")

llm = ChatOpenAI(callbacks=[MyCallback()])
result = llm.invoke("你好")

# 也可以在 invoke 时传入
result = llm.invoke("你好", config={"callbacks": [MyCallback()]})""",
        "key_points": [
            "继承 BaseCallbackHandler 实现需要的钩子方法",
            "可在构造时或 invoke 时传入 callbacks",
            "常用于日志、监控、token 计费",
        ],
        "common_mistakes": [
            "在 callback 中做耗时操作阻塞主流程",
            "忘记异步场景需要用 AsyncCallbackHandler",
        ],
        "related_point_ids": [5, 6],
        "tags": ["langchain", "callbacks", "monitoring", "进阶"],
        "sort_order": 19,
    },
    # === INTERMEDIATE: LangGraph ===
    {
        "id": 20,
        "title": "Conditional Edges",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要根据状态动态决定下一步执行哪个节点时（条件分支）",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    input: str
    category: str

def classify(state: State) -> dict:
    if "天气" in state["input"]:
        return {"category": "weather"}
    return {"category": "general"}

def handle_weather(state: State) -> dict:
    return {"input": f"天气查询：{state['input']}"}

def handle_general(state: State) -> dict:
    return {"input": f"通用回答：{state['input']}"}

def route(state: State) -> str:
    if state["category"] == "weather":
        return "weather"
    return "general"

graph = StateGraph(State)
graph.add_node("classify", classify)
graph.add_node("weather", handle_weather)
graph.add_node("general", handle_general)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route, {"weather": "weather", "general": "general"})
graph.add_edge("weather", END)
graph.add_edge("general", END)

app = graph.compile()""",
        "key_points": [
            "add_conditional_edges(source, func, mapping) 实现条件路由",
            "路由函数接收 State，返回字符串 key",
            "mapping 字典将返回值映射到目标节点名称",
        ],
        "common_mistakes": [
            "路由函数返回值不在 mapping 字典中导致运行时报错",
            "忘记为所有分支都连接到 END（或下一个节点）",
        ],
        "related_point_ids": [9, 11, 21],
        "tags": ["langgraph", "graph", "routing", "进阶"],
        "sort_order": 20,
    },
    {
        "id": 21,
        "title": "Checkpointing (持久化状态)",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 3,
        "dev_utility": 3,
        "scenario": "当你需要保存图的执行状态，支持暂停/恢复、多轮对话记忆或故障恢复时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]

def chat(state: State) -> dict:
    last_msg = state["messages"][-1]
    return {"messages": [f"回复：{last_msg}"]}

graph = StateGraph(State)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# 添加 checkpointer
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# 用 thread_id 区分不同对话
config = {"configurable": {"thread_id": "user-123"}}

result = app.invoke({"messages": ["你好"]}, config=config)
result = app.invoke({"messages": ["我叫小明"]}, config=config)
# messages 会累积：["你好", "回复：你好", "我叫小明", "回复：我叫小明"]""",
        "key_points": [
            "compile(checkpointer=...) 启用状态持久化",
            "MemorySaver 存内存（开发用），SqliteSaver/PostgresSaver 存数据库（生产用）",
            "thread_id 区分不同会话/用户的状态",
        ],
        "common_mistakes": [
            "忘记传 config 中的 thread_id 导致所有用户共享状态",
            "开发用 MemorySaver 但部署到生产（重启后状态丢失）",
        ],
        "related_point_ids": [9, 10, 22],
        "tags": ["langgraph", "checkpoint", "memory", "进阶"],
        "sort_order": 21,
    },
    {
        "id": 22,
        "title": "Human-in-the-loop",
        "category": "Graph",
        "level": "intermediate",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要在 Agent 执行过程中暂停等待人工审批或输入时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

class State(TypedDict):
    query: str
    plan: str
    approved: bool
    result: str

def make_plan(state: State) -> dict:
    return {"plan": f"计划处理: {state['query']}"}

def execute(state: State) -> dict:
    return {"result": f"执行完成: {state['plan']}"}

graph = StateGraph(State)
graph.add_node("plan", make_plan)
graph.add_node("execute", execute)
graph.add_edge(START, "plan")
graph.add_edge("plan", "execute")  # interrupt_before 会在这里暂停
graph.add_edge("execute", END)

app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["execute"],  # 在 execute 前暂停
)

config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"query": "删除所有数据", "approved": False, "plan": "", "result": ""}, config=config)
print(result["plan"])  # 展示计划给用户

# 用户审批后，更新状态并继续
app.update_state(config, {"approved": True})
result = app.invoke(None, config=config)  # 从暂停点继续""",
        "key_points": [
            "interrupt_before/interrupt_after 指定暂停点",
            "需要 checkpointer 才能暂停和恢复",
            "update_state() 注入人工输入后 invoke(None) 继续执行",
        ],
        "common_mistakes": [
            "没有配置 checkpointer 就使用 interrupt（会报错）",
            "invoke(None) 时忘记传 config 导致找不到暂停的状态",
        ],
        "related_point_ids": [21, 9],
        "tags": ["langgraph", "human-in-the-loop", "interrupt", "进阶"],
        "sort_order": 22,
    },
    # === ADVANCED: LangChain ===
    {
        "id": 23,
        "title": "Streaming (流式输出)",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要让 LLM 的回答逐字逐句显示（打字机效果）而非等待完整响应时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("写一首关于{topic}的诗")
    | ChatOpenAI(model="gpt-4o-mini")
    | StrOutputParser()
)

# 方式1：stream（同步流式）
for chunk in chain.stream({"topic": "春天"}):
    print(chunk, end="", flush=True)

# 方式2：astream（异步流式）
async for chunk in chain.astream({"topic": "春天"}):
    print(chunk, end="", flush=True)

# 方式3：astream_events（获取中间步骤事件）
async for event in chain.astream_events({"topic": "春天"}, version="v2"):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")""",
        "key_points": [
            "stream/astream 获取最终输出的流式 chunk",
            "astream_events 可获取链中每个步骤的事件（调试利器）",
            "流式输出对用户体验至关重要，生产环境必备",
        ],
        "common_mistakes": [
            "在 FastAPI 中用 stream 而不是 astream（阻塞事件循环）",
            "流式输出时忘记 flush 导致输出积攒",
        ],
        "related_point_ids": [5, 6],
        "tags": ["langchain", "streaming", "高级"],
        "sort_order": 23,
    },
    {
        "id": 24,
        "title": "Custom Runnable",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要创建一个完全自定义的 Runnable 组件加入 LCEL 链，且需要支持流式/异步时",
        "code_example": """from langchain_core.runnables import RunnableGenerator
from typing import Iterator

# 方式1：RunnableGenerator（最简单）
def streaming_transform(chunks: Iterator[str]) -> Iterator[str]:
    buffer = ""
    for chunk in chunks:
        buffer += chunk
        if "。" in buffer:
            parts = buffer.split("。")
            for part in parts[:-1]:
                yield part + "。\\n"
            buffer = parts[-1]
    if buffer:
        yield buffer

transform = RunnableGenerator(streaming_transform)

# 方式2：继承 Runnable（完全控制）
from langchain_core.runnables import Runnable, RunnableConfig

class MyRunnable(Runnable):
    def invoke(self, input, config: RunnableConfig | None = None):
        return input.upper()

    async def ainvoke(self, input, config: RunnableConfig | None = None):
        return input.upper()

chain = some_chain | transform  # 加入管道""",
        "key_points": [
            "RunnableGenerator 适合流式转换场景",
            "继承 Runnable 需实现 invoke，可选 ainvoke/stream/astream",
            "自定义 Runnable 自动获得 batch/abatch 等能力",
        ],
        "common_mistakes": [
            "只实现 invoke 不实现 ainvoke，在异步环境中阻塞",
            "流式处理时没有正确处理 chunk 边界",
        ],
        "related_point_ids": [5, 8, 23],
        "tags": ["langchain", "LCEL", "custom", "高级"],
        "sort_order": 24,
    },
    {
        "id": 25,
        "title": "Batch 批处理",
        "category": "Chain",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要同时处理多个输入以提高吞吐量时",
        "code_example": """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

chain = (
    ChatPromptTemplate.from_template("用一句话解释{concept}")
    | ChatOpenAI()
    | StrOutputParser()
)

# 批量调用
results = chain.batch([
    {"concept": "递归"},
    {"concept": "闭包"},
    {"concept": "多态"},
], config={"max_concurrency": 3})

# 异步批量
results = await chain.abatch([
    {"concept": "递归"},
    {"concept": "闭包"},
])

for r in results:
    print(r)""",
        "key_points": [
            "batch/abatch 接受输入列表，返回结果列表",
            "max_concurrency 控制最大并发数",
            "比循环调用 invoke 更高效（并发执行）",
        ],
        "common_mistakes": [
            "不设 max_concurrency 导致触发 API 限流",
            "batch 列表太大导致内存压力",
        ],
        "related_point_ids": [5, 23],
        "tags": ["langchain", "batch", "性能", "高级"],
        "sort_order": 25,
    },
    # === ADVANCED: LangGraph ===
    {
        "id": 26,
        "title": "Multi-Agent 协作",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 3,
        "dev_utility": 2,
        "scenario": "当你需要多个 Agent 协作完成复杂任务（如一个负责研究，一个负责写作）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]
    task: str

llm = ChatOpenAI()

def researcher(state: State) -> dict:
    # 研究 Agent：收集信息
    response = llm.invoke(f"研究以下主题并列出要点：{state['task']}")
    return {"messages": [f"[研究员] {response.content}"]}

def writer(state: State) -> dict:
    # 写作 Agent：基于研究结果撰写
    context = "\\n".join(state["messages"])
    response = llm.invoke(f"基于以下研究写一篇文章：\\n{context}")
    return {"messages": [f"[写手] {response.content}"]}

def reviewer(state: State) -> dict:
    # 审稿 Agent：检查质量
    context = "\\n".join(state["messages"])
    response = llm.invoke(f"审查以下内容并给出修改建议：\\n{context}")
    return {"messages": [f"[审稿] {response.content}"]}

graph = StateGraph(State)
graph.add_node("researcher", researcher)
graph.add_node("writer", writer)
graph.add_node("reviewer", reviewer)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "writer")
graph.add_edge("writer", "reviewer")
graph.add_edge("reviewer", END)

app = graph.compile()
result = app.invoke({"messages": [], "task": "AI Agent 的发展趋势"})""",
        "key_points": [
            "每个 Agent 是图中的一个节点，共享 State 通信",
            "Agent 之间通过 State 中的 messages 传递信息",
            "可用条件边实现更复杂的协作模式（如循环审稿直到通过）",
        ],
        "common_mistakes": [
            "Agent 之间信息传递不充分，后续 Agent 缺少上下文",
            "循环协作没有设退出条件导致无限循环",
        ],
        "related_point_ids": [9, 20, 27],
        "tags": ["langgraph", "multi-agent", "高级"],
        "sort_order": 26,
    },
    {
        "id": 27,
        "title": "Subgraphs (子图)",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要将复杂图拆分为可复用的模块，或在图中嵌套另一个图时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 子图：处理订单
class OrderState(TypedDict):
    order_id: str
    status: str

def validate(state: OrderState) -> dict:
    return {"status": "validated"}

def process(state: OrderState) -> dict:
    return {"status": "processed"}

order_graph = StateGraph(OrderState)
order_graph.add_node("validate", validate)
order_graph.add_node("process", process)
order_graph.add_edge(START, "validate")
order_graph.add_edge("validate", "process")
order_graph.add_edge("process", END)
order_subgraph = order_graph.compile()

# 主图
class MainState(TypedDict):
    order_id: str
    status: str
    result: str

def prepare(state: MainState) -> dict:
    return {"result": "准备中"}

def finalize(state: MainState) -> dict:
    return {"result": f"订单 {state['order_id']} 完成，状态: {state['status']}"}

main_graph = StateGraph(MainState)
main_graph.add_node("prepare", prepare)
main_graph.add_node("order", order_subgraph)  # 嵌入子图
main_graph.add_node("finalize", finalize)
main_graph.add_edge(START, "prepare")
main_graph.add_edge("prepare", "order")
main_graph.add_edge("order", "finalize")
main_graph.add_edge("finalize", END)

app = main_graph.compile()""",
        "key_points": [
            "子图是独立的 compiled graph，作为节点嵌入父图",
            "父图和子图通过共享的 State 字段通信",
            "子图内部的节点对父图透明，实现封装",
        ],
        "common_mistakes": [
            "父图和子图的 State 没有重叠字段导致无法通信",
            "子图内部的 checkpointer 和父图冲突",
        ],
        "related_point_ids": [9, 26, 28],
        "tags": ["langgraph", "subgraph", "模块化", "高级"],
        "sort_order": 27,
    },
    {
        "id": 28,
        "title": "Dynamic Breakpoints",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 1,
        "dev_utility": 2,
        "scenario": "当你需要在运行时根据条件动态决定是否暂停执行（而非编译时固定暂停点）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from typing import TypedDict

class State(TypedDict):
    input: str
    risk_level: str
    result: str

def analyze(state: State) -> dict:
    if "删除" in state["input"] or "drop" in state["input"].lower():
        return {"risk_level": "high"}
    return {"risk_level": "low"}

def execute(state: State) -> dict:
    # 动态中断：高风险操作需要人工确认
    if state["risk_level"] == "high":
        raise NodeInterrupt(
            f"高风险操作检测到: {state['input']}，需要人工确认"
        )
    return {"result": f"已执行: {state['input']}"}

graph = StateGraph(State)
graph.add_node("analyze", analyze)
graph.add_node("execute", execute)
graph.add_edge(START, "analyze")
graph.add_edge("analyze", "execute")
graph.add_edge("execute", END)

app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"input": "删除所有用户数据", "risk_level": "", "result": ""}, config=config)
# 高风险 → NodeInterrupt 触发 → 暂停

# 人工确认后继续
app.update_state(config, {"risk_level": "low"})  # 降级风险
result = app.invoke(None, config=config)""",
        "key_points": [
            "raise NodeInterrupt(reason) 在节点内部动态触发暂停",
            "比 interrupt_before/after 更灵活，可基于运行时条件判断",
            "同样需要 checkpointer 支持暂停/恢复",
        ],
        "common_mistakes": [
            "NodeInterrupt 后忘记 update_state 就调用 invoke(None)，会再次触发中断",
            "没有 checkpointer 时 raise NodeInterrupt 会直接报错",
        ],
        "related_point_ids": [22, 21],
        "tags": ["langgraph", "interrupt", "dynamic", "高级"],
        "sort_order": 28,
    },
    {
        "id": 29,
        "title": "Command 模式",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 2,
        "scenario": "当你需要在节点内部同时更新状态和控制路由（跳转到指定节点）时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict

class State(TypedDict):
    input: str
    stage: str

def router_node(state: State) -> Command:
    if "紧急" in state["input"]:
        return Command(
            update={"stage": "urgent"},
            goto="urgent_handler",  # 直接跳转
        )
    return Command(
        update={"stage": "normal"},
        goto="normal_handler",
    )

def urgent_handler(state: State) -> dict:
    return {"input": f"[紧急处理] {state['input']}"}

def normal_handler(state: State) -> dict:
    return {"input": f"[常规处理] {state['input']}"}

graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("urgent_handler", urgent_handler)
graph.add_node("normal_handler", normal_handler)
graph.add_edge(START, "router")
# 不需要 add_conditional_edges，Command.goto 已处理路由
graph.add_edge("urgent_handler", END)
graph.add_edge("normal_handler", END)

app = graph.compile()""",
        "key_points": [
            "Command(update=..., goto=...) 同时更新状态和控制流转",
            "比 conditional_edges 更灵活，路由逻辑在节点内部",
            "goto 可以是单个节点名或节点名列表（并行分发）",
        ],
        "common_mistakes": [
            "返回 Command 的节点不能同时有 add_conditional_edges",
            "goto 指向不存在的节点名",
        ],
        "related_point_ids": [20, 9],
        "tags": ["langgraph", "command", "routing", "高级"],
        "sort_order": 29,
    },
    {
        "id": 30,
        "title": "LangGraph Streaming",
        "category": "Graph",
        "level": "advanced",
        "interview_heat": 2,
        "dev_utility": 3,
        "scenario": "当你需要实时获取图执行过程中每个节点的状态更新和 LLM 输出流时",
        "code_example": """from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from operator import add

class State(TypedDict):
    messages: Annotated[list[str], add]

def node_a(state: State) -> dict:
    return {"messages": ["A done"]}

def node_b(state: State) -> dict:
    return {"messages": ["B done"]}

graph = StateGraph(State)
graph.add_node("a", node_a)
graph.add_node("b", node_b)
graph.add_edge(START, "a")
graph.add_edge("a", "b")
graph.add_edge("b", END)
app = graph.compile()

# stream_mode="updates" — 每个节点完成后发送更新
for event in app.stream({"messages": []}, stream_mode="updates"):
    print(event)
    # {"a": {"messages": ["A done"]}}
    # {"b": {"messages": ["B done"]}}

# stream_mode="values" — 每步发送完整状态
for event in app.stream({"messages": []}, stream_mode="values"):
    print(event)

# 多种模式同时使用
for mode, event in app.stream({"messages": []}, stream_mode=["updates", "values"]):
    print(f"[{mode}] {event}")""",
        "key_points": [
            "stream_mode='updates' 只返回每步的增量更新",
            "stream_mode='values' 返回每步后的完整状态",
            "可同时传多个 stream_mode 获取不同粒度的事件",
        ],
        "common_mistakes": [
            "混淆 updates 和 values 模式导致解析错误",
            "在异步环境用 stream 而非 astream",
        ],
        "related_point_ids": [23, 9],
        "tags": ["langgraph", "streaming", "高级"],
        "sort_order": 30,
    },
]


def seed_database(db):
    """Seed database with knowledge points if empty."""
    if db.query(KnowledgePoint).count() > 0:
        return
    for data in SEED_DATA:
        point = KnowledgePoint(**data)
        db.add(point)
    db.commit()
```

- [ ] **Step 2: Add seed call on startup in main.py**

Add to `backend/app/main.py` after `Base.metadata.create_all(bind=engine)`:

```python
from app.database import Base, engine, SessionLocal
from app.seed import seed_database

Base.metadata.create_all(bind=engine)

# Seed data on startup
db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()
```

- [ ] **Step 3: Verify seed data loads**

```bash
cd backend
rm -f langmaster.db
python -c "
from app.main import app
from app.database import SessionLocal
from app.models import KnowledgePoint
db = SessionLocal()
count = db.query(KnowledgePoint).count()
print(f'Seeded {count} knowledge points')
db.close()
"
```

Expected: `Seeded 30 knowledge points`

- [ ] **Step 4: Run all backend tests**

```bash
cd backend
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/seed.py backend/app/main.py
git commit -m "feat: add 30 LangChain/LangGraph knowledge points seed data"
```

---

### Task 9: Frontend Project Setup

**Files:**
- Create: `frontend/` (Next.js project)
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/user.ts`

- [ ] **Step 1: Create Next.js project**

```bash
cd /home/zxxy/repository/langsurpervisor
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias --use-npm
```

Accept defaults for all prompts.

- [ ] **Step 2: Create shared types**

Create `frontend/src/lib/types.ts`:

```typescript
export interface KnowledgePointBrief {
  id: number;
  title: string;
  category: string;
  level: string;
  interview_heat: number;
  dev_utility: number;
  scenario: string;
  tags: string[];
  sort_order: number;
}

export interface KnowledgePoint extends KnowledgePointBrief {
  code_example: string;
  key_points: string[];
  common_mistakes: string[];
  related_point_ids: number[];
}

export interface UserProgress {
  point_id: number;
  mastery: "not_started" | "partial" | "mastered";
  last_reviewed_at: string | null;
  review_count: number;
  is_favorite: boolean;
}

export interface InterviewConfig {
  categories?: string[];
  levels?: string[];
  min_heat?: number;
  count: number;
  strategy: "smart" | "random" | "sequential";
}

export interface InterviewStartResult {
  session_id: number;
  questions: KnowledgePoint[];
}

export interface InterviewReport {
  id: number;
  config: Record<string, unknown>;
  results: { point_id: number; self_score: string }[];
  total_mastered: number;
  total_partial: number;
  total_unfamiliar: number;
  created_at: string;
}

export interface DashboardStats {
  total_points: number;
  mastered_count: number;
  interview_count: number;
  weak_count: number;
  last_score_percent: number | null;
}

export interface WeakPoint {
  point_id: number;
  title: string;
  mastery: string;
  category: string;
  level: string;
}
```

- [ ] **Step 3: Create user identity module**

Create `frontend/src/lib/user.ts`:

```typescript
const USER_ID_KEY = "langmaster_user_id";

export function getUserId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}
```

- [ ] **Step 4: Create API client**

Create `frontend/src/lib/api.ts`:

```typescript
import type {
  KnowledgePointBrief,
  KnowledgePoint,
  UserProgress,
  InterviewConfig,
  InterviewStartResult,
  InterviewReport,
  DashboardStats,
  WeakPoint,
} from "./types";
import { getUserId } from "./user";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": getUserId(),
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Knowledge Points
export function getPoints(params?: {
  category?: string;
  level?: string;
  sort?: string;
}): Promise<KnowledgePointBrief[]> {
  const search = new URLSearchParams();
  if (params?.category) search.set("category", params.category);
  if (params?.level) search.set("level", params.level);
  if (params?.sort) search.set("sort", params.sort);
  const qs = search.toString();
  return fetchAPI(`/api/points${qs ? `?${qs}` : ""}`);
}

export function getPoint(id: number): Promise<KnowledgePoint> {
  return fetchAPI(`/api/points/${id}`);
}

// Progress
export function getProgress(): Promise<UserProgress[]> {
  return fetchAPI("/api/progress");
}

export function updateMastery(
  pointId: number,
  mastery: string
): Promise<UserProgress> {
  return fetchAPI(`/api/progress/${pointId}`, {
    method: "PUT",
    body: JSON.stringify({ mastery }),
  });
}

export function toggleFavorite(
  pointId: number,
  isFavorite: boolean
): Promise<UserProgress> {
  return fetchAPI(`/api/progress/${pointId}/favorite`, {
    method: "PUT",
    body: JSON.stringify({ is_favorite: isFavorite }),
  });
}

// Interview
export function startInterview(
  config: InterviewConfig
): Promise<InterviewStartResult> {
  return fetchAPI("/api/interview/start", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

export function submitAnswer(
  sessionId: number,
  pointId: number,
  selfScore: string
): Promise<{ status: string; results_count: number }> {
  return fetchAPI(`/api/interview/${sessionId}/answer`, {
    method: "POST",
    body: JSON.stringify({ point_id: pointId, self_score: selfScore }),
  });
}

export function getReport(sessionId: number): Promise<InterviewReport> {
  return fetchAPI(`/api/interview/${sessionId}/report`);
}

export function getInterviewHistory(): Promise<InterviewReport[]> {
  return fetchAPI("/api/interview/history");
}

// Stats
export function getDashboardStats(): Promise<DashboardStats> {
  return fetchAPI("/api/stats/dashboard");
}

export function getWeakPoints(): Promise<WeakPoint[]> {
  return fetchAPI("/api/stats/weak-points");
}
```

- [ ] **Step 5: Verify frontend dev server starts**

```bash
cd frontend
npm run dev
```

Expected: Next.js dev server starts on http://localhost:3000.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: frontend project setup with Next.js, types, API client"
```

---

### Task 10: Navbar Component + Root Layout

**Files:**
- Create: `frontend/src/components/Navbar.tsx`
- Modify: `frontend/src/app/layout.tsx`
- Modify: `frontend/src/app/globals.css`

- [ ] **Step 1: Create Navbar component**

Create `frontend/src/components/Navbar.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "首页" },
  { href: "/learn", label: "学习路径" },
  { href: "/interview/setup", label: "模拟面试" },
  { href: "/profile", label: "个人中心" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link href="/" className="text-lg font-bold text-gray-900">
          LangMaster
        </Link>
        <div className="flex gap-6">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`text-sm font-medium ${
                  isActive
                    ? "text-blue-600"
                    : "text-gray-500 hover:text-gray-900"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
```

- [ ] **Step 2: Update root layout**

Replace `frontend/src/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LangMaster - LangChain/LangGraph 教学",
  description: "通过场景驱动的知识卡片和模拟面试掌握 LangChain 和 LangGraph",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={`${inter.className} bg-gray-50 text-gray-900`}>
        <Navbar />
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Clean up globals.css**

Replace `frontend/src/app/globals.css` with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 4: Verify Navbar renders**

```bash
cd frontend
npm run dev
# Open http://localhost:3000 — should see Navbar with 4 links
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Navbar.tsx frontend/src/app/layout.tsx frontend/src/app/globals.css
git commit -m "feat: add Navbar component and root layout"
```

---

### Task 11: Shared Components (StatsCard, CodeBlock, FilterBar)

**Files:**
- Create: `frontend/src/components/StatsCard.tsx`
- Create: `frontend/src/components/CodeBlock.tsx`
- Create: `frontend/src/components/FilterBar.tsx`

- [ ] **Step 1: Create StatsCard**

Create `frontend/src/components/StatsCard.tsx`:

```tsx
interface StatsCardProps {
  value: string | number;
  label: string;
  color: "blue" | "green" | "yellow" | "pink";
}

const COLOR_MAP = {
  blue: "bg-blue-50 text-blue-800",
  green: "bg-green-50 text-green-800",
  yellow: "bg-amber-50 text-amber-800",
  pink: "bg-pink-50 text-pink-800",
};

export default function StatsCard({ value, label, color }: StatsCardProps) {
  return (
    <div className={`rounded-lg p-4 text-center ${COLOR_MAP[color]}`}>
      <div className="text-3xl font-bold">{value}</div>
      <div className="mt-1 text-xs text-gray-500">{label}</div>
    </div>
  );
}
```

- [ ] **Step 2: Create CodeBlock**

Create `frontend/src/components/CodeBlock.tsx`:

```tsx
"use client";

import { useState } from "react";

interface CodeBlockProps {
  code: string;
}

export default function CodeBlock({ code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <button
        onClick={handleCopy}
        className="absolute right-3 top-3 rounded bg-gray-700 px-2 py-1 text-xs text-gray-300 hover:bg-gray-600"
      >
        {copied ? "已复制" : "复制"}
      </button>
      <pre className="overflow-x-auto rounded-lg bg-gray-900 p-4 text-sm leading-relaxed text-gray-100">
        <code>{code}</code>
      </pre>
    </div>
  );
}
```

- [ ] **Step 3: Create FilterBar**

Create `frontend/src/components/FilterBar.tsx`:

```tsx
"use client";

interface FilterBarProps {
  categories: string[];
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
}

const SORT_OPTIONS = [
  { value: "sort_order", label: "学习路径" },
  { value: "interview_heat", label: "面试热度" },
  { value: "dev_utility", label: "开发实用度" },
];

export default function FilterBar({
  categories,
  selectedCategory,
  onCategoryChange,
  sortBy,
  onSortChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex gap-2">
        <button
          onClick={() => onCategoryChange(null)}
          className={`rounded-full px-3 py-1 text-sm ${
            selectedCategory === null
              ? "bg-blue-500 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          全部
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onCategoryChange(cat)}
            className={`rounded-full px-3 py-1 text-sm ${
              selectedCategory === cat
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="ml-auto flex items-center gap-2 text-xs text-gray-500">
        <span>排序：</span>
        {SORT_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onSortChange(opt.value)}
            className={`${
              sortBy === opt.value
                ? "font-semibold text-blue-600"
                : "hover:text-gray-900"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/StatsCard.tsx frontend/src/components/CodeBlock.tsx frontend/src/components/FilterBar.tsx
git commit -m "feat: add StatsCard, CodeBlock, FilterBar shared components"
```

---

### Task 12: Knowledge Card Component + Learn Page (Card Wall)

**Files:**
- Create: `frontend/src/components/KnowledgeCard.tsx`
- Create: `frontend/src/app/learn/page.tsx`

- [ ] **Step 1: Create KnowledgeCard component**

Create `frontend/src/components/KnowledgeCard.tsx`:

```tsx
import Link from "next/link";
import type { KnowledgePointBrief, UserProgress } from "@/lib/types";

interface KnowledgeCardProps {
  point: KnowledgePointBrief;
  progress?: UserProgress;
}

const HEAT_DISPLAY = ["", "🔥", "🔥🔥", "🔥🔥🔥"];
const UTILITY_DISPLAY = ["", "⭐", "⭐⭐", "⭐⭐⭐"];

const MASTERY_STYLES: Record<string, { border: string; badge: string; label: string }> = {
  mastered: {
    border: "border-green-300",
    badge: "bg-green-100 text-green-700",
    label: "已掌握",
  },
  partial: {
    border: "border-amber-300",
    badge: "bg-amber-100 text-amber-700",
    label: "部分掌握",
  },
  not_started: {
    border: "border-gray-200",
    badge: "bg-gray-100 text-gray-500",
    label: "未学习",
  },
};

export default function KnowledgeCard({ point, progress }: KnowledgeCardProps) {
  const mastery = progress?.mastery || "not_started";
  const styles = MASTERY_STYLES[mastery];

  return (
    <Link href={`/learn/${point.id}`}>
      <div
        className={`relative rounded-xl border p-4 transition-shadow hover:shadow-md ${styles.border} ${
          mastery === "not_started" && !progress ? "opacity-70" : ""
        }`}
      >
        <span
          className={`absolute right-2 top-2 rounded-full px-2 py-0.5 text-xs ${styles.badge}`}
        >
          {styles.label}
        </span>
        <div className="mb-2 flex gap-2 text-xs">
          <span className="text-red-500">{HEAT_DISPLAY[point.interview_heat]}</span>
          <span className="text-gray-400">{UTILITY_DISPLAY[point.dev_utility]}</span>
        </div>
        <h4 className="mb-1 text-sm font-semibold text-gray-900">{point.title}</h4>
        <p className="line-clamp-2 text-xs text-gray-500">{point.scenario}</p>
        <div className="mt-3 flex flex-wrap gap-1">
          {point.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </Link>
  );
}
```

- [ ] **Step 2: Create Learn page (card wall)**

Create `frontend/src/app/learn/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { getPoints, getProgress } from "@/lib/api";
import type { KnowledgePointBrief, UserProgress } from "@/lib/types";
import KnowledgeCard from "@/components/KnowledgeCard";
import FilterBar from "@/components/FilterBar";

const LEVEL_TABS = [
  { value: null, label: "全部" },
  { value: "basic", label: "基础" },
  { value: "intermediate", label: "进阶" },
  { value: "advanced", label: "高级" },
];

export default function LearnPage() {
  const [points, setPoints] = useState<KnowledgePointBrief[]>([]);
  const [progressMap, setProgressMap] = useState<Record<number, UserProgress>>({});
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState("sort_order");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [pts, prog] = await Promise.all([
        getPoints({
          category: selectedCategory || undefined,
          level: selectedLevel || undefined,
          sort: sortBy,
        }),
        getProgress(),
      ]);
      setPoints(pts);
      const map: Record<number, UserProgress> = {};
      for (const p of prog) {
        map[p.point_id] = p;
      }
      setProgressMap(map);
      setLoading(false);
    }
    load();
  }, [selectedCategory, selectedLevel, sortBy]);

  const categories = [...new Set(points.map((p) => p.category))];

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">学习路径</h1>
      <p className="mb-6 text-sm text-gray-500">
        按场景学习 LangChain 和 LangGraph 的核心知识点
      </p>

      {/* Level tabs */}
      <div className="mb-4 flex gap-2">
        {LEVEL_TABS.map((tab) => (
          <button
            key={tab.label}
            onClick={() => setSelectedLevel(tab.value)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              selectedLevel === tab.value
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <FilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        sortBy={sortBy}
        onSortChange={setSortBy}
      />

      {loading ? (
        <div className="mt-12 text-center text-gray-400">加载中...</div>
      ) : (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {points.map((point) => (
            <KnowledgeCard
              key={point.id}
              point={point}
              progress={progressMap[point.id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Verify card wall renders**

Start both backend and frontend:

```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
# Open http://localhost:3000/learn
```

Expected: 30 knowledge cards displayed with filters and sort controls.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/KnowledgeCard.tsx frontend/src/app/learn/page.tsx
git commit -m "feat: add knowledge card wall with filtering and sorting"
```

---

### Task 13: Knowledge Point Detail Page

**Files:**
- Create: `frontend/src/app/learn/[id]/page.tsx`

- [ ] **Step 1: Create detail page**

Create `frontend/src/app/learn/[id]/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getPoint, getProgress, updateMastery, toggleFavorite } from "@/lib/api";
import type { KnowledgePoint, UserProgress } from "@/lib/types";
import CodeBlock from "@/components/CodeBlock";
import Link from "next/link";

const HEAT_DISPLAY = ["", "🔥", "🔥🔥", "🔥🔥🔥"];
const UTILITY_DISPLAY = ["", "⭐", "⭐⭐", "⭐⭐⭐"];
const LEVEL_LABELS: Record<string, string> = {
  basic: "基础",
  intermediate: "进阶",
  advanced: "高级",
};

const MASTERY_OPTIONS = [
  { value: "not_started", label: "未学习", color: "bg-gray-100 text-gray-600" },
  { value: "partial", label: "部分掌握", color: "bg-amber-100 text-amber-700" },
  { value: "mastered", label: "已掌握", color: "bg-green-100 text-green-700" },
];

export default function PointDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const [point, setPoint] = useState<KnowledgePoint | null>(null);
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [pt, allProgress] = await Promise.all([getPoint(id), getProgress()]);
      setPoint(pt);
      setProgress(allProgress.find((p) => p.point_id === id) || null);
      setLoading(false);
    }
    load();
  }, [id]);

  const handleMastery = async (mastery: string) => {
    const updated = await updateMastery(id, mastery);
    setProgress(updated);
  };

  const handleFavorite = async () => {
    const updated = await toggleFavorite(id, !progress?.is_favorite);
    setProgress(updated);
  };

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!point) {
    return <div className="mt-12 text-center text-gray-400">知识点不存在</div>;
  }

  const currentMastery = progress?.mastery || "not_started";

  return (
    <div className="mx-auto max-w-3xl">
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="mb-4 text-sm text-gray-500 hover:text-gray-900"
      >
        ← 返回
      </button>

      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <h1 className="text-2xl font-bold">{point.title}</h1>
            <span className="rounded-full bg-blue-100 px-3 py-0.5 text-xs text-blue-700">
              {LEVEL_LABELS[point.level] || point.level}
            </span>
          </div>
          <div className="flex gap-4 text-sm text-gray-500">
            <span>面试热度：{HEAT_DISPLAY[point.interview_heat]}</span>
            <span>开发实用度：{UTILITY_DISPLAY[point.dev_utility]}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleFavorite}
            className={`rounded-lg border px-3 py-1.5 text-sm ${
              progress?.is_favorite
                ? "border-amber-300 bg-amber-50 text-amber-600"
                : "border-gray-200 text-gray-500 hover:bg-gray-50"
            }`}
          >
            {progress?.is_favorite ? "★ 已收藏" : "☆ 收藏"}
          </button>
        </div>
      </div>

      {/* Scenario */}
      <div className="mb-6 rounded-r-lg border-l-4 border-blue-500 bg-blue-50 px-5 py-4">
        <div className="mb-1 font-semibold text-blue-800">💡 使用场景</div>
        <div className="text-gray-700">{point.scenario}</div>
      </div>

      {/* Code */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">📝 代码示例</h3>
        <CodeBlock code={point.code_example} />
      </div>

      {/* Key Points */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">🎯 核心要点</h3>
        <div className="space-y-2">
          {point.key_points.map((kp, i) => (
            <div key={i} className="flex gap-2 text-sm">
              <span className="font-bold text-green-500">✓</span>
              <span>{kp}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Common Mistakes */}
      <div className="mb-6">
        <h3 className="mb-2 font-semibold text-gray-800">⚠️ 常见误区</h3>
        <div className="rounded-lg bg-red-50 p-4">
          {point.common_mistakes.map((cm, i) => (
            <div key={i} className="flex gap-2 text-sm">
              <span className="text-red-500">✗</span>
              <span>{cm}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Related Points */}
      {point.related_point_ids.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-2 font-semibold text-gray-800">🔗 关联知识点</h3>
          <div className="flex flex-wrap gap-2">
            {point.related_point_ids.map((rid) => (
              <Link
                key={rid}
                href={`/learn/${rid}`}
                className="rounded-lg bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
              >
                #{rid}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Mastery Control */}
      <div className="rounded-lg border bg-white p-4">
        <h3 className="mb-3 text-sm font-semibold text-gray-600">标记掌握程度</h3>
        <div className="flex gap-2">
          {MASTERY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => handleMastery(opt.value)}
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                currentMastery === opt.value
                  ? opt.color + " ring-2 ring-offset-1"
                  : "bg-gray-50 text-gray-500 hover:bg-gray-100"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify detail page renders**

```bash
# With backend running on :8000 and frontend on :3000
# Open http://localhost:3000/learn/1
```

Expected: Full detail page for ChatPromptTemplate with scenario, code, key points, mistakes, related points, and mastery control.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/learn/[id]/page.tsx
git commit -m "feat: add knowledge point detail page with mastery control"
```

---

### Task 14: Interview Setup Page

**Files:**
- Create: `frontend/src/app/interview/setup/page.tsx`

- [ ] **Step 1: Create interview setup page**

Create `frontend/src/app/interview/setup/page.tsx`:

```tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { startInterview } from "@/lib/api";

const CATEGORIES = [
  { value: "Prompt", label: "Prompt" },
  { value: "Output", label: "Output" },
  { value: "Chain", label: "Chain" },
  { value: "Model", label: "Model" },
  { value: "Memory", label: "Memory" },
  { value: "Retrieval", label: "Retrieval" },
  { value: "Tools", label: "Tools" },
  { value: "Agent", label: "Agent" },
  { value: "Graph", label: "Graph" },
];

const LEVELS = [
  { value: "basic", label: "基础" },
  { value: "intermediate", label: "进阶" },
  { value: "advanced", label: "高级" },
];

const STRATEGIES = [
  { value: "smart", label: "智能优先", desc: "优先出你不熟的题" },
  { value: "random", label: "随机", desc: "完全随机抽取" },
  { value: "sequential", label: "顺序", desc: "按学习路径顺序" },
];

const COUNT_OPTIONS = [5, 10, 15, 20];

export default function InterviewSetupPage() {
  const router = useRouter();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedLevels, setSelectedLevels] = useState<string[]>([]);
  const [heatFilter, setHeatFilter] = useState(1);
  const [count, setCount] = useState(10);
  const [strategy, setStrategy] = useState("smart");
  const [starting, setStarting] = useState(false);

  const toggleCategory = (cat: string) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  };

  const toggleLevel = (level: string) => {
    setSelectedLevels((prev) =>
      prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]
    );
  };

  const handleStart = async () => {
    setStarting(true);
    const result = await startInterview({
      categories: selectedCategories.length > 0 ? selectedCategories : undefined,
      levels: selectedLevels.length > 0 ? selectedLevels : undefined,
      min_heat: heatFilter,
      count,
      strategy: strategy as "smart" | "random" | "sequential",
    });
    // Store session data in sessionStorage for the session page
    sessionStorage.setItem("interview_session", JSON.stringify(result));
    router.push("/interview/session");
  };

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-2xl font-bold">模拟面试</h1>
      <p className="mb-8 text-sm text-gray-500">配置面试参数，开始模拟</p>

      {/* Categories */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          题目范围
        </h3>
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => toggleCategory(cat.value)}
              className={`rounded-full px-3 py-1 text-sm ${
                selectedCategories.includes(cat.value)
                  ? "bg-blue-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {cat.label}
            </button>
          ))}
          {selectedCategories.length > 0 && (
            <button
              onClick={() => setSelectedCategories([])}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              清除
            </button>
          )}
        </div>
        {selectedCategories.length === 0 && (
          <p className="mt-1 text-xs text-gray-400">未选择 = 全部分类</p>
        )}
      </div>

      {/* Levels */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          难度
        </h3>
        <div className="flex gap-2">
          {LEVELS.map((level) => (
            <button
              key={level.value}
              onClick={() => toggleLevel(level.value)}
              className={`rounded-lg px-4 py-2 text-sm ${
                selectedLevels.includes(level.value)
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {level.label}
            </button>
          ))}
        </div>
        {selectedLevels.length === 0 && (
          <p className="mt-1 text-xs text-gray-400">未选择 = 全部难度</p>
        )}
      </div>

      {/* Heat filter */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          面试热度筛选
        </h3>
        <div className="flex gap-2">
          {[1, 2, 3].map((h) => (
            <button
              key={h}
              onClick={() => setHeatFilter(h)}
              className={`rounded-lg px-4 py-2 text-sm ${
                heatFilter === h
                  ? "bg-red-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {h === 1 ? "全部" : h === 2 ? "🔥🔥 中频以上" : "🔥🔥🔥 仅高频"}
            </button>
          ))}
        </div>
      </div>

      {/* Count */}
      <div className="mb-6">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          题数
        </h3>
        <div className="flex gap-2">
          {COUNT_OPTIONS.map((n) => (
            <button
              key={n}
              onClick={() => setCount(n)}
              className={`rounded-lg px-4 py-2 text-sm ${
                count === n
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {n} 题
            </button>
          ))}
        </div>
      </div>

      {/* Strategy */}
      <div className="mb-8">
        <h3 className="mb-2 text-sm font-semibold uppercase text-gray-500">
          出题策略
        </h3>
        <div className="flex gap-3">
          {STRATEGIES.map((s) => (
            <button
              key={s.value}
              onClick={() => setStrategy(s.value)}
              className={`flex-1 rounded-lg border-2 p-3 text-center ${
                strategy === s.value
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="text-sm font-semibold">{s.label}</div>
              <div className="text-xs text-gray-500">{s.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Start button */}
      <button
        onClick={handleStart}
        disabled={starting}
        className="w-full rounded-lg bg-purple-600 py-3 text-lg font-semibold text-white hover:bg-purple-700 disabled:opacity-50"
      >
        {starting ? "正在生成题目..." : "开始面试"}
      </button>
    </div>
  );
}
```

- [ ] **Step 2: Verify setup page renders**

```bash
# Open http://localhost:3000/interview/setup
```

Expected: Interview configuration page with category, level, heat, count, strategy options.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/interview/setup/page.tsx
git commit -m "feat: add interview setup page with config options"
```

---

### Task 15: Interview Session Page

**Files:**
- Create: `frontend/src/components/InterviewQuestion.tsx`
- Create: `frontend/src/components/SelfRating.tsx`
- Create: `frontend/src/app/interview/session/page.tsx`

- [ ] **Step 1: Create SelfRating component**

Create `frontend/src/components/SelfRating.tsx`:

```tsx
interface SelfRatingProps {
  onRate: (score: "mastered" | "partial" | "unfamiliar") => void;
}

const RATINGS = [
  {
    value: "mastered" as const,
    label: "完全掌握",
    color: "bg-green-500 hover:bg-green-600",
    desc: "能流畅讲出使用场景和代码",
  },
  {
    value: "partial" as const,
    label: "部分掌握",
    color: "bg-amber-500 hover:bg-amber-600",
    desc: "知道概念但代码细节不确定",
  },
  {
    value: "unfamiliar" as const,
    label: "不熟悉",
    color: "bg-red-500 hover:bg-red-600",
    desc: "完全不记得或没学过",
  },
];

export default function SelfRating({ onRate }: SelfRatingProps) {
  return (
    <div className="mt-6 rounded-lg border-2 border-dashed border-gray-300 p-6">
      <h3 className="mb-4 text-center text-sm font-semibold text-gray-600">
        自评一下你的掌握程度
      </h3>
      <div className="flex gap-3">
        {RATINGS.map((r) => (
          <button
            key={r.value}
            onClick={() => onRate(r.value)}
            className={`flex-1 rounded-lg px-4 py-3 text-white ${r.color}`}
          >
            <div className="text-sm font-semibold">{r.label}</div>
            <div className="mt-1 text-xs opacity-80">{r.desc}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Create InterviewQuestion component**

Create `frontend/src/components/InterviewQuestion.tsx`:

```tsx
"use client";

import { useState } from "react";
import type { KnowledgePoint } from "@/lib/types";
import CodeBlock from "./CodeBlock";
import SelfRating from "./SelfRating";

interface InterviewQuestionProps {
  point: KnowledgePoint;
  index: number;
  total: number;
  onRate: (score: "mastered" | "partial" | "unfamiliar") => void;
}

export default function InterviewQuestion({
  point,
  index,
  total,
  onRate,
}: InterviewQuestionProps) {
  const [revealed, setRevealed] = useState(false);

  return (
    <div className="mx-auto max-w-3xl">
      {/* Progress */}
      <div className="mb-6 flex items-center justify-between">
        <span className="text-sm text-gray-500">
          第 {index + 1} / {total} 题
        </span>
        <div className="h-2 flex-1 mx-4 rounded-full bg-gray-200">
          <div
            className="h-2 rounded-full bg-blue-500 transition-all"
            style={{ width: `${((index + 1) / total) * 100}%` }}
          />
        </div>
      </div>

      {/* Scenario (always visible) */}
      <div className="mb-6 rounded-r-lg border-l-4 border-purple-500 bg-purple-50 px-5 py-4">
        <div className="mb-1 text-xs font-semibold uppercase text-purple-600">
          面试题
        </div>
        <div className="text-lg font-medium text-gray-800">
          {point.scenario}，你会使用什么？请说明用法和关键注意事项。
        </div>
      </div>

      {/* Hint: title */}
      <div className="mb-4 text-center text-sm text-gray-400">
        提示：{point.category} 分类 · {point.level === "basic" ? "基础" : point.level === "intermediate" ? "进阶" : "高级"}
      </div>

      {!revealed ? (
        <div className="text-center">
          <p className="mb-4 text-sm text-gray-500">
            先在心中组织你的答案，准备好后点击查看参考答案
          </p>
          <button
            onClick={() => setRevealed(true)}
            className="rounded-lg bg-blue-600 px-8 py-3 text-white hover:bg-blue-700"
          >
            查看答案
          </button>
        </div>
      ) : (
        <div>
          <h2 className="mb-4 text-xl font-bold">{point.title}</h2>

          {/* Code */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">📝 参考代码</h3>
            <CodeBlock code={point.code_example} />
          </div>

          {/* Key Points */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">🎯 核心要点</h3>
            <div className="space-y-1">
              {point.key_points.map((kp, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="font-bold text-green-500">✓</span>
                  <span>{kp}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Common Mistakes */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm font-semibold text-gray-600">⚠️ 常见误区</h3>
            <div className="rounded-lg bg-red-50 p-3">
              {point.common_mistakes.map((cm, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="text-red-500">✗</span>
                  <span>{cm}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Self rating */}
          <SelfRating onRate={onRate} />
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Create interview session page**

Create `frontend/src/app/interview/session/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { submitAnswer } from "@/lib/api";
import type { InterviewStartResult } from "@/lib/types";
import InterviewQuestion from "@/components/InterviewQuestion";

export default function InterviewSessionPage() {
  const router = useRouter();
  const [session, setSession] = useState<InterviewStartResult | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const stored = sessionStorage.getItem("interview_session");
    if (!stored) {
      router.push("/interview/setup");
      return;
    }
    setSession(JSON.parse(stored));
  }, [router]);

  if (!session) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  const currentQuestion = session.questions[currentIndex];

  if (!currentQuestion) {
    // All questions answered — redirect to report
    sessionStorage.setItem("interview_session_id", String(session.session_id));
    router.push("/interview/report");
    return null;
  }

  const handleRate = async (score: "mastered" | "partial" | "unfamiliar") => {
    await submitAnswer(session.session_id, currentQuestion.id, score);
    setCurrentIndex((prev) => prev + 1);
  };

  return (
    <InterviewQuestion
      point={currentQuestion}
      index={currentIndex}
      total={session.questions.length}
      onRate={handleRate}
    />
  );
}
```

- [ ] **Step 4: Verify interview flow works**

```bash
# Open http://localhost:3000/interview/setup
# Configure and start interview
# Should navigate to /interview/session with questions
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/InterviewQuestion.tsx frontend/src/components/SelfRating.tsx frontend/src/app/interview/session/page.tsx
git commit -m "feat: add interview session page with question flow and self-rating"
```

---

### Task 16: Interview Report Page

**Files:**
- Create: `frontend/src/app/interview/report/page.tsx`

- [ ] **Step 1: Create report page**

Create `frontend/src/app/interview/report/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getReport } from "@/lib/api";
import type { InterviewReport } from "@/lib/types";

export default function InterviewReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const sessionId = sessionStorage.getItem("interview_session_id");
    if (!sessionId) {
      router.push("/interview/setup");
      return;
    }
    async function load() {
      const data = await getReport(Number(sessionId));
      setReport(data);
      setLoading(false);
    }
    load();
  }, [router]);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!report) return null;

  const total = report.results.length;
  const scorePercent =
    total > 0 ? Math.round((report.total_mastered / total) * 100) : 0;

  const weakPoints = report.results.filter(
    (r) => r.self_score === "unfamiliar" || r.self_score === "partial"
  );

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-2 text-2xl font-bold">面试报告</h1>
      <p className="mb-8 text-sm text-gray-500">
        {new Date(report.created_at).toLocaleString("zh-CN")}
      </p>

      {/* Score summary */}
      <div className="mb-8 flex justify-center gap-8">
        <div className="text-center">
          <div className="text-4xl font-bold text-green-500">
            {report.total_mastered}
          </div>
          <div className="text-sm text-gray-500">完全掌握</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-amber-500">
            {report.total_partial}
          </div>
          <div className="text-sm text-gray-500">部分掌握</div>
        </div>
        <div className="text-center">
          <div className="text-4xl font-bold text-red-500">
            {report.total_unfamiliar}
          </div>
          <div className="text-sm text-gray-500">不熟悉</div>
        </div>
      </div>

      {/* Score bar */}
      <div className="mb-8 text-center">
        <div className="text-5xl font-bold text-gray-900">{scorePercent}%</div>
        <div className="text-sm text-gray-500">掌握率</div>
      </div>

      {/* Weak points */}
      {weakPoints.length > 0 && (
        <div className="mb-8 rounded-lg bg-amber-50 p-4">
          <h3 className="mb-2 font-semibold text-amber-800">
            建议重点复习
          </h3>
          <div className="space-y-2">
            {weakPoints.map((wp) => (
              <Link
                key={wp.point_id}
                href={`/learn/${wp.point_id}`}
                className="flex items-center justify-between rounded-lg bg-white px-3 py-2 text-sm hover:bg-gray-50"
              >
                <span>知识点 #{wp.point_id}</span>
                <span
                  className={
                    wp.self_score === "unfamiliar"
                      ? "text-red-500"
                      : "text-amber-500"
                  }
                >
                  {wp.self_score === "unfamiliar" ? "不熟悉" : "部分掌握"}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Link
          href="/interview/setup"
          className="flex-1 rounded-lg bg-purple-600 py-3 text-center text-white hover:bg-purple-700"
        >
          再来一次
        </Link>
        <Link
          href="/learn"
          className="flex-1 rounded-lg bg-gray-200 py-3 text-center text-gray-700 hover:bg-gray-300"
        >
          去学习
        </Link>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify full interview flow**

```bash
# Complete a full interview flow:
# 1. /interview/setup → configure → start
# 2. /interview/session → answer all questions
# 3. /interview/report → see results
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/interview/report/page.tsx
git commit -m "feat: add interview report page with score summary"
```

---

### Task 17: Dashboard (Home Page)

**Files:**
- Modify: `frontend/src/app/page.tsx`

- [ ] **Step 1: Create dashboard page**

Replace `frontend/src/app/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getDashboardStats, getWeakPoints } from "@/lib/api";
import type { DashboardStats, WeakPoint } from "@/lib/types";
import StatsCard from "@/components/StatsCard";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weakPoints, setWeakPoints] = useState<WeakPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, wp] = await Promise.all([getDashboardStats(), getWeakPoints()]);
      setStats(s);
      setWeakPoints(wp);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!stats) return null;

  return (
    <div>
      <h1 className="mb-2 text-2xl font-bold">LangMaster</h1>
      <p className="mb-8 text-sm text-gray-500">
        场景驱动学习 LangChain & LangGraph
      </p>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatsCard
          value={`${stats.mastered_count}/${stats.total_points}`}
          label="已掌握知识点"
          color="blue"
        />
        <StatsCard
          value={stats.interview_count}
          label="模拟面试次数"
          color="green"
        />
        <StatsCard
          value={stats.weak_count}
          label="待复习（薄弱）"
          color="yellow"
        />
        <StatsCard
          value={
            stats.last_score_percent !== null
              ? `${stats.last_score_percent}%`
              : "-"
          }
          label="最近面试得分"
          color="pink"
        />
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Weak points */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">
            📌 推荐复习
          </h3>
          {weakPoints.length === 0 ? (
            <p className="text-sm text-gray-400">暂无薄弱知识点</p>
          ) : (
            <div className="space-y-2">
              {weakPoints.slice(0, 5).map((wp) => (
                <Link
                  key={wp.point_id}
                  href={`/learn/${wp.point_id}`}
                  className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm hover:bg-gray-100"
                >
                  <span>{wp.title}</span>
                  <span
                    className={
                      wp.mastery === "not_started"
                        ? "text-red-500"
                        : "text-amber-500"
                    }
                  >
                    {wp.mastery === "not_started" ? "不熟悉" : "部分掌握"}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="rounded-lg border bg-white p-4">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">
            🚀 快捷入口
          </h3>
          <div className="space-y-2">
            <Link
              href="/learn"
              className="block rounded-lg bg-blue-500 py-3 text-center text-sm font-semibold text-white hover:bg-blue-600"
            >
              开始学习
            </Link>
            <Link
              href="/interview/setup"
              className="block rounded-lg bg-purple-500 py-3 text-center text-sm font-semibold text-white hover:bg-purple-600"
            >
              模拟面试
            </Link>
            <Link
              href="/profile"
              className="block rounded-lg bg-gray-200 py-3 text-center text-sm font-semibold text-gray-700 hover:bg-gray-300"
            >
              个人中心
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify dashboard**

```bash
# Open http://localhost:3000
```

Expected: Dashboard with stats cards, recommended review, and quick action buttons.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/page.tsx
git commit -m "feat: add dashboard home page with stats and quick actions"
```

---

### Task 18: Profile Page

**Files:**
- Create: `frontend/src/app/profile/page.tsx`

- [ ] **Step 1: Create profile page**

Create `frontend/src/app/profile/page.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getProgress,
  getInterviewHistory,
  getDashboardStats,
} from "@/lib/api";
import type { UserProgress, InterviewReport, DashboardStats } from "@/lib/types";

export default function ProfilePage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [progress, setProgress] = useState<UserProgress[]>([]);
  const [history, setHistory] = useState<InterviewReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [s, p, h] = await Promise.all([
        getDashboardStats(),
        getProgress(),
        getInterviewHistory(),
      ]);
      setStats(s);
      setProgress(p);
      setHistory(h);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="mt-12 text-center text-gray-400">加载中...</div>;
  }

  if (!stats) return null;

  const favorites = progress.filter((p) => p.is_favorite);
  const mastered = progress.filter((p) => p.mastery === "mastered");
  const partial = progress.filter((p) => p.mastery === "partial");

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-6 text-2xl font-bold">个人中心</h1>

      {/* Stats summary */}
      <div className="mb-8 grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-green-50 p-4 text-center">
          <div className="text-3xl font-bold text-green-700">{mastered.length}</div>
          <div className="text-xs text-gray-500">已掌握</div>
        </div>
        <div className="rounded-lg bg-amber-50 p-4 text-center">
          <div className="text-3xl font-bold text-amber-700">{partial.length}</div>
          <div className="text-xs text-gray-500">部分掌握</div>
        </div>
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <div className="text-3xl font-bold text-blue-700">{stats.total_points}</div>
          <div className="text-xs text-gray-500">总知识点</div>
        </div>
      </div>

      {/* Favorites */}
      <div className="mb-8">
        <h2 className="mb-3 text-lg font-semibold">⭐ 收藏的知识点</h2>
        {favorites.length === 0 ? (
          <p className="text-sm text-gray-400">暂无收藏</p>
        ) : (
          <div className="space-y-2">
            {favorites.map((f) => (
              <Link
                key={f.point_id}
                href={`/learn/${f.point_id}`}
                className="block rounded-lg border px-4 py-2 text-sm hover:bg-gray-50"
              >
                知识点 #{f.point_id}
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Interview history */}
      <div>
        <h2 className="mb-3 text-lg font-semibold">📝 面试历史</h2>
        {history.length === 0 ? (
          <p className="text-sm text-gray-400">暂无面试记录</p>
        ) : (
          <div className="space-y-2">
            {history.map((h) => {
              const total = h.results.length;
              const percent =
                total > 0 ? Math.round((h.total_mastered / total) * 100) : 0;
              return (
                <div
                  key={h.id}
                  className="flex items-center justify-between rounded-lg border px-4 py-3"
                >
                  <div>
                    <div className="text-sm font-medium">
                      {total} 题 · 掌握率 {percent}%
                    </div>
                    <div className="text-xs text-gray-400">
                      {new Date(h.created_at).toLocaleString("zh-CN")}
                    </div>
                  </div>
                  <div className="flex gap-3 text-sm">
                    <span className="text-green-500">
                      ✓ {h.total_mastered}
                    </span>
                    <span className="text-amber-500">
                      ~ {h.total_partial}
                    </span>
                    <span className="text-red-500">
                      ✗ {h.total_unfamiliar}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Verify profile page**

```bash
# Open http://localhost:3000/profile
```

Expected: Profile page with stats, favorites list, and interview history.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/profile/page.tsx
git commit -m "feat: add profile page with favorites and interview history"
```

---

### Task 19: End-to-End Verification

**Files:** None (testing only)

- [ ] **Step 1: Run all backend tests**

```bash
cd backend
python -m pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 2: Start both servers and verify all pages**

```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Verify each page:
- `http://localhost:3000` — Dashboard with stats
- `http://localhost:3000/learn` — 30 cards with filters
- `http://localhost:3000/learn/1` — ChatPromptTemplate detail
- `http://localhost:3000/interview/setup` — Interview config
- Complete a full interview → report page
- `http://localhost:3000/profile` — Stats and history

- [ ] **Step 3: Run frontend type check**

```bash
cd frontend
npx tsc --noEmit
```

Expected: No type errors.

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete LangMaster MVP — knowledge cards + interview mode"
```
