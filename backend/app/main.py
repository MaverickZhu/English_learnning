from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.storage import ensure_buckets
from app.core.scheduler import schedule_daily_job, start_scheduler
from app.services.news_tasks import run_ingest_job


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.on_event("startup")
    def _startup() -> None:
        ensure_buckets()
        if settings.news_ingest_enabled:
            start_scheduler()
            schedule_daily_job(run_ingest_job, settings.news_ingest_hour, settings.news_ingest_minute)

    return app


app = create_app()
