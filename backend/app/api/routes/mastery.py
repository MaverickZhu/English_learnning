from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.mastery import mastery_summary
from app.schemas.mastery import MasterySummaryRequest, MasterySummaryResponse

router = APIRouter(prefix="/mastery")


@router.post("/summary", response_model=MasterySummaryResponse)
def summary(
    payload: MasterySummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> MasterySummaryResponse:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return MasterySummaryResponse(
        items=mastery_summary(db, user_id=current_user.id, content_type=payload.content_type, days=payload.days)
    )
