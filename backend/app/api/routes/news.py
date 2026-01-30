from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.deps import admin_auth, get_db
from app.crud.news import create_job, get_latest_job
from app.schemas.news import NewsIngestJobOut, NewsIngestRequest
from app.services.news_tasks import run_ingest_job

router = APIRouter(prefix="/admin/news", dependencies=[Depends(admin_auth)])


@router.post("/ingest", response_model=NewsIngestJobOut)
def ingest_news(
    payload: NewsIngestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> NewsIngestJobOut:
    job = create_job(db, status="queued")
    background_tasks.add_task(run_ingest_job, payload.limit_per_source, job.id)
    return job


@router.get("/status", response_model=NewsIngestJobOut | None)
def ingest_status(db: Session = Depends(get_db)) -> NewsIngestJobOut | None:
    return get_latest_job(db)
