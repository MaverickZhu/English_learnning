from datetime import datetime

from sqlalchemy.orm import Session

from app.models.review_reminder import ReviewReminder


def create_reminder(db: Session, payload: dict) -> ReviewReminder:
    reminder = ReviewReminder(**payload)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def list_reminders(
    db: Session,
    user_id: int,
    status: str | None = None,
    before: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[ReviewReminder]:
    query = db.query(ReviewReminder).filter(ReviewReminder.user_id == user_id)
    if status:
        query = query.filter(ReviewReminder.status == status)
    if before:
        query = query.filter(ReviewReminder.next_review_at <= datetime.fromisoformat(before))
    return query.order_by(ReviewReminder.next_review_at.asc()).offset(skip).limit(limit).all()


def mark_done(db: Session, reminder_id: int) -> ReviewReminder | None:
    reminder = db.get(ReviewReminder, reminder_id)
    if reminder is None:
        return None
    reminder.status = "done"
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder
