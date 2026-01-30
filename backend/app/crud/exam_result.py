from sqlalchemy.orm import Session

from app.models.exam_result import ExamResult


def create_result(db: Session, payload: dict) -> ExamResult:
    result = ExamResult(**payload)
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def list_results(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[ExamResult]:
    return (
        db.query(ExamResult)
        .filter(ExamResult.user_id == user_id)
        .order_by(ExamResult.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
