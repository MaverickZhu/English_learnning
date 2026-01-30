from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.study_record import StudyRecord


def mastery_summary(db: Session, user_id: int, content_type: str | None, days: int) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    query = db.query(StudyRecord).filter(StudyRecord.user_id == user_id).filter(StudyRecord.created_at >= since)
    if content_type:
        query = query.filter(StudyRecord.content_type == content_type)
    grouped = (
        query.with_entities(
            StudyRecord.content_type,
            func.count(StudyRecord.id),
            func.sum(func.case((StudyRecord.correct.is_(True), 1), else_=0)),
        )
        .group_by(StudyRecord.content_type)
        .all()
    )
    results = []
    for ctype, total, correct in grouped:
        total = int(total or 0)
        correct = int(correct or 0)
        accuracy = (correct / total) if total > 0 else 0.0
        mastery = min(1.0, max(0.0, accuracy))
        results.append(
            {
                "content_type": ctype,
                "total": total,
                "correct": correct,
                "accuracy": round(accuracy, 4),
                "mastery_score": round(mastery, 4),
            }
        )
    return results
