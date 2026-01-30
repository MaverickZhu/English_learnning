from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.mistake import list_mistakes, record_mistake
from app.schemas.mistake import MistakeItemOut, MistakeListResponse, MistakeRecordRequest

router = APIRouter(prefix="/mistakes")


@router.post("/record", response_model=MistakeItemOut)
def record(
    payload: MistakeRecordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MistakeItemOut:
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return record_mistake(db, payload.model_dump())


@router.get("", response_model=MistakeListResponse)
def list_all(
    user_id: int,
    content_type: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MistakeListResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    items = list_mistakes(db, user_id=user_id, content_type=content_type, skip=skip, limit=limit)
    return MistakeListResponse(items=items)
