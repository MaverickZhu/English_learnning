import hashlib
import time

from sqlalchemy.orm import Session

from app.crud import content
from app.crud.news import create_article, get_article_by_url, get_or_create_source, update_article
from app.models.exercise import Exercise
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.word import Word
from app.services.ai_generator import generate_learning_content
from app.services.news_extractor import ArticleContent, extract_article
from app.services.news_fetcher import DEFAULT_SOURCES, NewsSourceConfig, fetch_top_article_urls


def _hash_text(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sanitize_level(level: str | None) -> str | None:
    if not level:
        return None
    return level.strip().upper()


def _has_generated_items(db: Session, article_id: int) -> bool:
    if db.query(Passage).filter(Passage.article_id == article_id).first() is not None:
        return True
    if db.query(Word).filter(Word.article_id == article_id).first() is not None:
        return True
    if db.query(Sentence).filter(Sentence.article_id == article_id).first() is not None:
        return True
    if db.query(Exercise).filter(Exercise.article_id == article_id).first() is not None:
        return True
    return False


def ingest_sources(db: Session, limit_per_source: int = 5) -> dict:
    summary = {
        "sources": 0,
        "articles_fetched": 0,
        "articles_ingested": 0,
        "items_created": {"words": 0, "sentences": 0, "passages": 0, "exercises": 0},
        "source_errors": [],
        "article_errors": [],
    }
    for source in DEFAULT_SOURCES:
        summary["sources"] += 1
        _ingest_source(db, source, limit_per_source, summary)
        if limit_per_source <= 1 and summary["articles_ingested"] >= 1:
            break
    return summary


def _ingest_source(db: Session, source: NewsSourceConfig, limit_per_source: int, summary: dict) -> None:
    source_row = get_or_create_source(db, source.name, source.site_url)
    try:
        urls = fetch_top_article_urls(source, limit=limit_per_source)
    except Exception as exc:
        summary["source_errors"].append({"source": source.name, "error": str(exc)})
        return
    summary["articles_fetched"] += len(urls)
    for url in urls:
        existing = get_article_by_url(db, url)
        if existing is not None and _has_generated_items(db, existing.id):
            continue
        try:
            article_row = existing
            article = None
            if article_row is None or not (article_row.content or article_row.summary or article_row.title):
                article = extract_article(url)
                content_hash = _hash_text(article.content or article.summary or article.title)
                if article_row is None:
                    article_row = create_article(
                        db,
                        {
                            "source_id": source_row.id,
                            "url": article.url,
                            "title": article.title,
                            "summary": article.summary,
                            "content": article.content,
                            "image_url": article.image_url,
                            "content_hash": content_hash,
                            "published_at": article.published_at,
                        },
                    )
                else:
                    update_article(
                        db,
                        article_row,
                        {
                            "title": article.title,
                            "summary": article.summary,
                            "content": article.content,
                            "image_url": article.image_url,
                            "content_hash": content_hash,
                            "published_at": article.published_at,
                        },
                    )
            else:
                article = ArticleContent(
                    url=article_row.url,
                    title=article_row.title,
                    summary=article_row.summary,
                    content=article_row.content,
                    image_url=article_row.image_url,
                    published_at=article_row.published_at,
                )

            generated = generate_learning_content(article.title, article.summary, article.content)
            level = _sanitize_level(generated.level) or "A2"

            passage_payload = generated.passage or {}
            if passage_payload.get("content"):
                passage = content.create_passage(
                    db,
                    {
                        "title": passage_payload.get("title") or article.title,
                        "content": passage_payload.get("content"),
                        "summary": passage_payload.get("summary") or article.summary,
                        "image_url": article.image_url,
                        "level": level,
                        "tags": generated.tags,
                        "source_id": source_row.id,
                        "article_id": article_row.id,
                    },
                    commit=True,
                )
                if passage:
                    summary["items_created"]["passages"] += 1

            for item in generated.words:
                payload = {
                    "text": item.get("text"),
                    "meaning": item.get("meaning"),
                    "example": item.get("example"),
                    "level": _sanitize_level(item.get("level")) or level,
                    "tags": item.get("tags") or generated.tags,
                    "source_id": source_row.id,
                    "article_id": article_row.id,
                }
                if payload["text"] and payload["meaning"]:
                    content.create_word(db, payload, commit=True)
                    summary["items_created"]["words"] += 1

            for item in generated.sentences:
                payload = {
                    "text": item.get("text"),
                    "meaning": item.get("meaning"),
                    "level": _sanitize_level(item.get("level")) or level,
                    "tags": item.get("tags") or generated.tags,
                    "source_id": source_row.id,
                    "article_id": article_row.id,
                }
                if payload["text"] and payload["meaning"]:
                    content.create_sentence(db, payload, commit=True)
                    summary["items_created"]["sentences"] += 1

            for item in generated.exercises:
                options = item.get("options")
                if options and not isinstance(options, list):
                    options = [opt.strip() for opt in str(options).split(",") if opt.strip()]
                payload = {
                    "exercise_type": item.get("exercise_type") or "cloze",
                    "prompt": item.get("prompt"),
                    "options": options,
                    "answer": item.get("answer"),
                    "explanation": item.get("explanation"),
                    "level": _sanitize_level(item.get("level")) or level,
                    "tags": item.get("tags") or generated.tags,
                    "source_id": source_row.id,
                    "article_id": article_row.id,
                }
                if payload["prompt"] and payload["answer"]:
                    content.create_exercise(db, payload, commit=True)
                    summary["items_created"]["exercises"] += 1

            summary["articles_ingested"] += 1
        except Exception as exc:
            summary["article_errors"].append({"url": url, "error": str(exc)})
            continue
        finally:
            time.sleep(3.2)
