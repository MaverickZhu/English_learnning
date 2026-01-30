from sqlalchemy.orm import Session

from app.models.news_article import NewsArticle
from app.models.news_ingest_job import NewsIngestJob
from app.models.news_source import NewsSource


def get_or_create_source(db: Session, name: str, site_url: str) -> NewsSource:
    existing = db.query(NewsSource).filter(NewsSource.name == name).first()
    if existing is not None:
        return existing
    source = NewsSource(name=name, site_url=site_url)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def get_article_by_url(db: Session, url: str) -> NewsArticle | None:
    return db.query(NewsArticle).filter(NewsArticle.url == url).first()


def create_article(db: Session, payload: dict, commit: bool = True) -> NewsArticle:
    article = NewsArticle(**payload)
    db.add(article)
    if commit:
        db.commit()
        db.refresh(article)
    else:
        db.flush()
    return article


def update_article(db: Session, article: NewsArticle, payload: dict) -> NewsArticle:
    for field, value in payload.items():
        setattr(article, field, value)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def create_job(db: Session, status: str) -> NewsIngestJob:
    job = NewsIngestJob(status=status)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_job(db: Session, job: NewsIngestJob, payload: dict) -> NewsIngestJob:
    for field, value in payload.items():
        setattr(job, field, value)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_latest_job(db: Session) -> NewsIngestJob | None:
    return db.query(NewsIngestJob).order_by(NewsIngestJob.id.desc()).first()
