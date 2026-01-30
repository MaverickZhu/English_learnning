from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.wrong_item import WrongItem


def record_mistake(db: Session, payload: dict) -> WrongItem:
    user_id = payload["user_id"]
    content_type = payload["content_type"]
    content_id = payload["content_id"]
    correct = payload["correct"]
    item = (
        db.query(WrongItem)
        .filter(
            and_(
                WrongItem.user_id == user_id,
                WrongItem.content_type == content_type,
                WrongItem.content_id == content_id,
            )
        )
        .first()
    )
    if item is None and not correct:
        item = WrongItem(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            wrong_count=1,
            last_wrong_at=datetime.utcnow(),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    if item is None and correct:
        return WrongItem(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            wrong_count=0,
            last_wrong_at=datetime.utcnow(),
        )
    if not correct:
        item.wrong_count += 1
        item.last_wrong_at = datetime.utcnow()
    else:
        item.wrong_count = max(0, item.wrong_count - 1)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_mistakes(
    db: Session, user_id: int, content_type: str | None = None, skip: int = 0, limit: int = 20
) -> list[WrongItem]:
    query = db.query(WrongItem).filter(WrongItem.user_id == user_id)
    if content_type:
        query = query.filter(WrongItem.content_type == content_type)
    return (
        query.order_by(WrongItem.wrong_count.desc(), WrongItem.last_wrong_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
