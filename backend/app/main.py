from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import points, progress, interview, stats

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LangMaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(points.router)
app.include_router(progress.router)
app.include_router(interview.router)
app.include_router(stats.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
