from datetime import datetime

from pydantic import BaseModel

from app.schemas.exercise import ExerciseOut
from app.schemas.passage import PassageOut
from app.schemas.sentence import SentenceOut
from app.schemas.word import WordOut


class NewsSourceOut(BaseModel):
    id: int
    name: str
    site_url: str

    class Config:
        from_attributes = True


class NewsArticleOut(BaseModel):
    id: int
    source_id: int
    url: str
    title: str
    summary: str | None = None
    content: str | None = None
    image_url: str | None = None
    content_hash: str | None = None
    published_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class NewsIngestRequest(BaseModel):
    limit_per_source: int = 5


class NewsIngestSummary(BaseModel):
    sources: int
    articles_fetched: int
    articles_ingested: int
    items_created: dict


class NewsIngestJobOut(BaseModel):
    id: int
    status: str
    summary: dict | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None

    class Config:
        from_attributes = True


class NewsLearningOut(BaseModel):
    article: NewsArticleOut
    passage: PassageOut
    words: list[WordOut]
    sentences: list[SentenceOut]
    exercises: list[ExerciseOut]

    class Config:
        from_attributes = True
