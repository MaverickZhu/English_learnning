import random

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.mock_exam import MockExam


def _pick_by_distribution(db: Session, level: str | None, distribution: dict) -> list[int]:
    ids: list[int] = []
    for exercise_type, count in distribution.items():
        if count <= 0:
            continue
        query = db.query(Exercise).filter(Exercise.exercise_type == exercise_type)
        if level:
            query = query.filter(Exercise.level == level)
        picked = [item.id for item in query.order_by(func.random()).limit(count).all()]
        ids.extend(picked)
    total_needed = sum(max(0, int(value)) for value in distribution.values())
    if len(ids) < total_needed:
        remaining = total_needed - len(ids)
        query = db.query(Exercise)
        if level:
            query = query.filter(Exercise.level == level)
        if ids:
            query = query.filter(~Exercise.id.in_(ids))
        extra = [item.id for item in query.order_by(func.random()).limit(remaining).all()]
        ids.extend(extra)
    random.shuffle(ids)
    return ids


def generate_exam(
    db: Session,
    user_id: int,
    title: str,
    duration_minutes: int,
    level: str | None,
    limit: int,
    distribution: dict | None = None,
) -> MockExam:
    if distribution:
        ids = _pick_by_distribution(db, level, distribution)
    else:
        query = db.query(Exercise)
        if level:
            query = query.filter(Exercise.level == level)
        ids = [item.id for item in query.order_by(func.random()).limit(limit).all()]
    exam = MockExam(
        user_id=user_id,
        title=title,
        duration_minutes=duration_minutes,
        exercise_ids=ids,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_exam(db: Session, exam_id: int) -> MockExam | None:
    return db.get(MockExam, exam_id)
