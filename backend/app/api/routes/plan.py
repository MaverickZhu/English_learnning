from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.plan import activate_plan, create_plan, get_active_plan, list_plans
from app.schemas.plan import StudyPlanCreate, StudyPlanListResponse, StudyPlanOut

router = APIRouter(prefix="/plans")


@router.post("", response_model=StudyPlanOut)
def create(
    payload: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudyPlanOut:
    if payload.daily_target <= 0:
        raise HTTPException(status_code=400, detail="daily_target must be > 0")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return create_plan(db, payload.model_dump())


@router.get("", response_model=StudyPlanListResponse)
def list_all(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudyPlanListResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return StudyPlanListResponse(items=list_plans(db, user_id))


@router.post("/{plan_id}/activate", response_model=StudyPlanOut)
def activate(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudyPlanOut:
    plan = activate_plan(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return plan


@router.get("/active", response_model=StudyPlanOut)
def get_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> StudyPlanOut:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    plan = get_active_plan(db, user_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Active plan not found")
    return plan
