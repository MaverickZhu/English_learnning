from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud import content
from app.crud.content import exercise_crud
from app.schemas.exercise import ExerciseCreate, ExerciseListResponse, ExerciseOut, ExerciseUpdate

router = APIRouter(prefix="/exercises")


@router.post("", response_model=ExerciseOut)
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)) -> ExerciseOut:
    return content.create_exercise(db, payload.model_dump())


@router.get("", response_model=ExerciseListResponse)
def list_exercises(
    skip: int = 0,
    limit: int = 20,
    level: str | None = None,
    tags: str | None = None,
    keyword: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> ExerciseListResponse:
    items = content.list_exercises(
        db,
        skip=skip,
        limit=limit,
        level=level,
        tags=tags,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
        cursor_id=cursor_id,
    )
    total = content.count_exercises(db, level=level, tags=tags, keyword=keyword)
    next_cursor = items[-1].id if items else None
    return ExerciseListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/{exercise_id}", response_model=ExerciseOut)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)) -> ExerciseOut:
    db_obj = exercise_crud.get(db, exercise_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_obj


@router.put("/{exercise_id}", response_model=ExerciseOut)
def update_exercise(
    exercise_id: int,
    payload: ExerciseUpdate,
    db: Session = Depends(get_db),
) -> ExerciseOut:
    db_obj = exercise_crud.get(db, exercise_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return content.update_exercise(db, db_obj, payload.model_dump(exclude_unset=True))


@router.delete("/{exercise_id}")
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)) -> dict:
    db_obj = exercise_crud.get(db, exercise_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    exercise_crud.delete(db, exercise_id)
    return {"deleted": True}
