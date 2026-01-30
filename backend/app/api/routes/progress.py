from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.progress import create_record, list_records, summary
from app.schemas.progress import (
    ProgressHistoryResponse,
    ProgressSummaryRequest,
    ProgressSummaryResponse,
    StudyRecordCreate,
    StudyRecordOut,
)

router = APIRouter(prefix="/progress")


@router.post("/record", response_model=StudyRecordOut)
def record(
    payload: StudyRecordCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudyRecordOut:
    if payload.time_spent_seconds is not None and payload.time_spent_seconds < 0:
        raise HTTPException(status_code=400, detail="time_spent_seconds must be >= 0")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return create_record(db, payload.model_dump())


@router.get("/history", response_model=ProgressHistoryResponse)
def history(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProgressHistoryResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    items = list_records(db, user_id=user_id, skip=skip, limit=limit)
    return ProgressHistoryResponse(items=items)


@router.post("/summary", response_model=ProgressSummaryResponse)
def progress_summary(
    payload: ProgressSummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProgressSummaryResponse:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ProgressSummaryResponse(**summary(db, user_id=current_user.id, days=payload.days))
