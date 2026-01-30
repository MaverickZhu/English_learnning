from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.exercise import Exercise
from app.models.news_article import NewsArticle
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.word import Word
from app.schemas.news import NewsLearningOut

router = APIRouter(prefix="/news")

_ALLOWED_LEVELS = {"A1", "A2", "B1", "B2", "C1"}
_EXERCISE_TYPE_MAP = {
    "multiple_choice": "image_choice",
    "fill_in_the_blank": "cloze",
}


def _normalize_level(value: str | None) -> str | None:
    if not value:
        return None
    return value if value in _ALLOWED_LEVELS else None


def _normalize_exercise_type(value: str | None) -> str | None:
    if not value:
        return None
    if value in {"image_choice", "listening_choice", "sentence_order", "cloze"}:
        return value
    return _EXERCISE_TYPE_MAP.get(value)


@router.get("/latest", response_model=NewsLearningOut)
def latest_news_learning(db: Session = Depends(get_db)) -> NewsLearningOut:
    passage = (
        db.query(Passage)
        .filter(Passage.article_id.isnot(None))
        .order_by(Passage.id.desc())
        .first()
    )
    if passage is None or passage.article_id is None:
        raise HTTPException(status_code=404, detail="No news learning content found")

    article = db.get(NewsArticle, passage.article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    words = (
        db.query(Word)
        .filter(Word.article_id == passage.article_id)
        .order_by(Word.id.asc())
        .limit(20)
        .all()
    )
    sentences = (
        db.query(Sentence)
        .filter(Sentence.article_id == passage.article_id)
        .order_by(Sentence.id.asc())
        .limit(10)
        .all()
    )
    exercises = (
        db.query(Exercise)
        .filter(Exercise.article_id == passage.article_id)
        .order_by(Exercise.id.asc())
        .limit(10)
        .all()
    )

    passage.level = _normalize_level(passage.level)
    for item in words:
        item.level = _normalize_level(item.level)
    for item in sentences:
        item.level = _normalize_level(item.level)
    for item in exercises:
        item.level = _normalize_level(item.level)
        item.exercise_type = _normalize_exercise_type(item.exercise_type)

    return NewsLearningOut(
        article=article,
        passage=passage,
        words=words,
        sentences=sentences,
        exercises=exercises,
    )
