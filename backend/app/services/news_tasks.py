from datetime import datetime

from app.core.database import SessionLocal
from app.crud.news import create_job, update_job
from app.models.news_ingest_job import NewsIngestJob
from app.services.news_ingest import ingest_sources


def run_ingest_job(limit_per_source: int = 5, job_id: int | None = None) -> int:
    db = SessionLocal()
    job = None
    try:
        if job_id is None:
            job = create_job(db, status="queued")
            job_id = job.id
        else:
            job = db.get(NewsIngestJob, job_id)
        if job is None:
            return 0
        update_job(db, job, {"status": "running", "started_at": datetime.utcnow()})
        summary = ingest_sources(db, limit_per_source=limit_per_source)
        update_job(
            db,
            job,
            {"status": "success", "summary": summary, "finished_at": datetime.utcnow()},
        )
        return job_id
    except Exception as exc:
        if job is not None:
            update_job(db, job, {"status": "failed", "error": str(exc), "finished_at": datetime.utcnow()})
        return job_id or 0
    finally:
        db.close()
