from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.review import create_reminder, list_reminders, mark_done
from app.schemas.review import ReviewReminderCreate, ReviewReminderListResponse, ReviewReminderOut

router = APIRouter(prefix="/review")


@router.post("/reminder", response_model=ReviewReminderOut)
def create(
    payload: ReviewReminderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReviewReminderOut:
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return create_reminder(db, payload.model_dump())


@router.get("/reminders", response_model=ReviewReminderListResponse)
def list_all(
    user_id: int,
    status: str | None = None,
    before: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReviewReminderListResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ReviewReminderListResponse(
        items=list_reminders(db, user_id=user_id, status=status, before=before, skip=skip, limit=limit)
    )


@router.post("/reminders/{reminder_id}/done", response_model=ReviewReminderOut)
def done(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReviewReminderOut:
    reminder = mark_done(db, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if reminder.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return reminder
