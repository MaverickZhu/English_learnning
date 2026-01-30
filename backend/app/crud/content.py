from typing import Iterable

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.exercise import Exercise
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.tag import Tag, exercise_tags, passage_tags, sentence_tags, word_tags
from app.models.word import Word

word_crud = CRUDBase(Word)
sentence_crud = CRUDBase(Sentence)
passage_crud = CRUDBase(Passage)
exercise_crud = CRUDBase(Exercise)

TAG_LINKS = {
    Word: (word_tags, "word_id"),
    Sentence: (sentence_tags, "sentence_id"),
    Passage: (passage_tags, "passage_id"),
    Exercise: (exercise_tags, "exercise_id"),
}


def _normalize_tags(tags: str | None) -> list[str]:
    if not tags:
        return []
    return [item.strip() for item in tags.split(",") if item.strip()]


def _apply_filters(query, model, level: str | None, tags: str | None, keyword: str | None, fields: Iterable):
    if level:
        query = query.filter(model.level == level)
    tag_list = _normalize_tags(tags)
    if tag_list:
        link_table, link_column = TAG_LINKS[model]
        tag_exists = (
            exists(
                select(1)
                .select_from(link_table.join(Tag, link_table.c.tag_id == Tag.id))
                .where(link_table.c[link_column] == model.id)
                .where(Tag.name.in_(tag_list))
            )
        )
        query = query.filter(tag_exists)
    if keyword:
        keyword_filters = [field.ilike(f"%{keyword}%") for field in fields]
        vector = func.to_tsvector("simple", func.concat_ws(" ", *fields))
        ts_query = func.plainto_tsquery("simple", keyword)
        query = query.filter(or_(vector.op("@@")(ts_query), *keyword_filters))
    return query


def _apply_sort(query, sort_column, sort_order: str | None):
    if sort_order and sort_order.lower() == "desc":
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())


def _apply_cursor(query, model, cursor_id: int | None, sort_order: str | None):
    if cursor_id is None:
        return query
    if sort_order and sort_order.lower() == "desc":
        return query.filter(model.id < cursor_id)
    return query.filter(model.id > cursor_id)


def _resolve_tags(db: Session, tags: list[str] | None) -> list[Tag]:
    if not tags:
        return []
    unique_tags = {tag.strip().lower() for tag in tags if tag.strip()}
    if not unique_tags:
        return []
    existing = db.query(Tag).filter(Tag.name.in_(unique_tags)).all()
    existing_map = {tag.name: tag for tag in existing}
    resolved = list(existing)
    for name in unique_tags:
        if name not in existing_map:
            new_tag = Tag(name=name)
            db.add(new_tag)
            resolved.append(new_tag)
    db.flush()
    return resolved


def apply_tags(db: Session, model, item_id: int, tags: list[str], mode: str, commit: bool = True):
    db_obj = db.get(model, item_id)
    if db_obj is None:
        return None
    resolved = _resolve_tags(db, tags)
    if mode == "replace":
        db_obj.tags = resolved
    elif mode == "add":
        existing = {tag.name for tag in db_obj.tags}
        for tag in resolved:
            if tag.name not in existing:
                db_obj.tags.append(tag)
    elif mode == "remove":
        remove_set = {tag.name for tag in resolved}
        db_obj.tags = [tag for tag in db_obj.tags if tag.name not in remove_set]
    else:
        return None
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def create_word(db: Session, payload: dict, commit: bool = True):
    tags = _resolve_tags(db, payload.pop("tags", None))
    db_obj = Word(**payload)
    db_obj.tags = tags
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def update_word(db: Session, db_obj: Word, payload: dict, commit: bool = True):
    tags = payload.pop("tags", None)
    for field, value in payload.items():
        setattr(db_obj, field, value)
    if tags is not None:
        db_obj.tags = _resolve_tags(db, tags)
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def upsert_word(db: Session, payload: dict, commit: bool = True):
    existing = db.query(Word).filter(Word.text == payload.get("text")).first()
    if existing is None:
        return create_word(db, payload, commit=commit), True
    return update_word(db, existing, payload, commit=commit), False


def create_sentence(db: Session, payload: dict, commit: bool = True):
    tags = _resolve_tags(db, payload.pop("tags", None))
    db_obj = Sentence(**payload)
    db_obj.tags = tags
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def update_sentence(db: Session, db_obj: Sentence, payload: dict, commit: bool = True):
    tags = payload.pop("tags", None)
    for field, value in payload.items():
        setattr(db_obj, field, value)
    if tags is not None:
        db_obj.tags = _resolve_tags(db, tags)
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def upsert_sentence(db: Session, payload: dict, commit: bool = True):
    existing = db.query(Sentence).filter(Sentence.text == payload.get("text")).first()
    if existing is None:
        return create_sentence(db, payload, commit=commit), True
    return update_sentence(db, existing, payload, commit=commit), False


def create_passage(db: Session, payload: dict, commit: bool = True):
    tags = _resolve_tags(db, payload.pop("tags", None))
    db_obj = Passage(**payload)
    db_obj.tags = tags
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def update_passage(db: Session, db_obj: Passage, payload: dict, commit: bool = True):
    tags = payload.pop("tags", None)
    for field, value in payload.items():
        setattr(db_obj, field, value)
    if tags is not None:
        db_obj.tags = _resolve_tags(db, tags)
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def upsert_passage(db: Session, payload: dict, commit: bool = True):
    existing = db.query(Passage).filter(Passage.title == payload.get("title")).first()
    if existing is None:
        return create_passage(db, payload, commit=commit), True
    return update_passage(db, existing, payload, commit=commit), False


def create_exercise(db: Session, payload: dict, commit: bool = True):
    tags = _resolve_tags(db, payload.pop("tags", None))
    db_obj = Exercise(**payload)
    db_obj.tags = tags
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def update_exercise(db: Session, db_obj: Exercise, payload: dict, commit: bool = True):
    tags = payload.pop("tags", None)
    for field, value in payload.items():
        setattr(db_obj, field, value)
    if tags is not None:
        db_obj.tags = _resolve_tags(db, tags)
    db.add(db_obj)
    if commit:
        db.commit()
        db.refresh(db_obj)
    else:
        db.flush()
    return db_obj


def upsert_exercise(db: Session, payload: dict, commit: bool = True):
    existing = (
        db.query(Exercise)
        .filter(Exercise.exercise_type == payload.get("exercise_type"))
        .filter(Exercise.prompt == payload.get("prompt"))
        .first()
    )
    if existing is None:
        return create_exercise(db, payload, commit=commit), True
    return update_exercise(db, existing, payload, commit=commit), False


def list_words(
    db: Session,
    skip: int,
    limit: int,
    level: str | None,
    tags: str | None,
    keyword: str | None,
    sort_by: str | None,
    sort_order: str | None,
    cursor_id: int | None,
):
    query = db.query(Word)
    query = _apply_filters(query, Word, level, tags, keyword, [Word.text, Word.meaning, Word.example])
    if cursor_id is not None:
        query = _apply_cursor(query, Word, cursor_id, sort_order)
        sort_by = "id"
    sort_map = {"id": Word.id, "text": Word.text, "level": Word.level}
    sort_column = sort_map.get(sort_by or "id", Word.id)
    query = _apply_sort(query, sort_column, sort_order)
    return query.offset(skip).limit(limit).all()


def list_sentences(
    db: Session,
    skip: int,
    limit: int,
    level: str | None,
    tags: str | None,
    keyword: str | None,
    sort_by: str | None,
    sort_order: str | None,
    cursor_id: int | None,
):
    query = db.query(Sentence)
    query = _apply_filters(query, Sentence, level, tags, keyword, [Sentence.text, Sentence.meaning])
    if cursor_id is not None:
        query = _apply_cursor(query, Sentence, cursor_id, sort_order)
        sort_by = "id"
    sort_map = {"id": Sentence.id, "level": Sentence.level}
    sort_column = sort_map.get(sort_by or "id", Sentence.id)
    query = _apply_sort(query, sort_column, sort_order)
    return query.offset(skip).limit(limit).all()


def list_passages(
    db: Session,
    skip: int,
    limit: int,
    level: str | None,
    tags: str | None,
    keyword: str | None,
    sort_by: str | None,
    sort_order: str | None,
    cursor_id: int | None,
):
    query = db.query(Passage)
    query = _apply_filters(query, Passage, level, tags, keyword, [Passage.title, Passage.content, Passage.summary])
    if cursor_id is not None:
        query = _apply_cursor(query, Passage, cursor_id, sort_order)
        sort_by = "id"
    sort_map = {"id": Passage.id, "title": Passage.title, "level": Passage.level}
    sort_column = sort_map.get(sort_by or "id", Passage.id)
    query = _apply_sort(query, sort_column, sort_order)
    return query.offset(skip).limit(limit).all()


def list_exercises(
    db: Session,
    skip: int,
    limit: int,
    level: str | None,
    tags: str | None,
    keyword: str | None,
    sort_by: str | None,
    sort_order: str | None,
    cursor_id: int | None,
):
    query = db.query(Exercise)
    query = _apply_filters(query, Exercise, level, tags, keyword, [Exercise.prompt, Exercise.answer, Exercise.explanation])
    if cursor_id is not None:
        query = _apply_cursor(query, Exercise, cursor_id, sort_order)
        sort_by = "id"
    sort_map = {"id": Exercise.id, "type": Exercise.exercise_type, "level": Exercise.level}
    sort_column = sort_map.get(sort_by or "id", Exercise.id)
    query = _apply_sort(query, sort_column, sort_order)
    return query.offset(skip).limit(limit).all()


def count_words(db: Session, level: str | None, tags: str | None, keyword: str | None) -> int:
    query = db.query(Word)
    query = _apply_filters(query, Word, level, tags, keyword, [Word.text, Word.meaning, Word.example])
    return query.count()


def count_sentences(db: Session, level: str | None, tags: str | None, keyword: str | None) -> int:
    query = db.query(Sentence)
    query = _apply_filters(query, Sentence, level, tags, keyword, [Sentence.text, Sentence.meaning])
    return query.count()


def count_passages(db: Session, level: str | None, tags: str | None, keyword: str | None) -> int:
    query = db.query(Passage)
    query = _apply_filters(query, Passage, level, tags, keyword, [Passage.title, Passage.content, Passage.summary])
    return query.count()


def count_exercises(db: Session, level: str | None, tags: str | None, keyword: str | None) -> int:
    query = db.query(Exercise)
    query = _apply_filters(query, Exercise, level, tags, keyword, [Exercise.prompt, Exercise.answer, Exercise.explanation])
    return query.count()
