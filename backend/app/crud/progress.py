from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.study_record import StudyRecord


def create_record(db: Session, payload: dict) -> StudyRecord:
    record = StudyRecord(**payload)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_records(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[StudyRecord]:
    return (
        db.query(StudyRecord)
        .filter(StudyRecord.user_id == user_id)
        .order_by(StudyRecord.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def summary(db: Session, user_id: int, days: int) -> dict:
    since = datetime.utcnow() - timedelta(days=days)
    query = db.query(StudyRecord).filter(StudyRecord.user_id == user_id).filter(StudyRecord.created_at >= since)
    total = query.count()
    correct = query.filter(StudyRecord.correct.is_(True)).count()
    total_time = (
        db.query(func.coalesce(func.sum(StudyRecord.time_spent_seconds), 0))
        .filter(StudyRecord.user_id == user_id)
        .filter(StudyRecord.created_at >= since)
        .scalar()
    )
    accuracy = (correct / total) if total > 0 else 0.0
    return {
        "total_records": total,
        "correct_count": correct,
        "accuracy": round(accuracy, 4),
        "total_time_seconds": int(total_time or 0),
    }
