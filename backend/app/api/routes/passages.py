from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud import content
from app.crud.content import passage_crud
from app.schemas.passage import PassageCreate, PassageListResponse, PassageOut, PassageUpdate

router = APIRouter(prefix="/passages")


@router.post("", response_model=PassageOut)
def create_passage(payload: PassageCreate, db: Session = Depends(get_db)) -> PassageOut:
    return content.create_passage(db, payload.model_dump())


@router.get("", response_model=PassageListResponse)
def list_passages(
    skip: int = 0,
    limit: int = 20,
    level: str | None = None,
    tags: str | None = None,
    keyword: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> PassageListResponse:
    items = content.list_passages(
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
    total = content.count_passages(db, level=level, tags=tags, keyword=keyword)
    next_cursor = items[-1].id if items else None
    return PassageListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/{passage_id}", response_model=PassageOut)
def get_passage(passage_id: int, db: Session = Depends(get_db)) -> PassageOut:
    db_obj = passage_crud.get(db, passage_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    return db_obj


@router.put("/{passage_id}", response_model=PassageOut)
def update_passage(
    passage_id: int,
    payload: PassageUpdate,
    db: Session = Depends(get_db),
) -> PassageOut:
    db_obj = passage_crud.get(db, passage_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    return content.update_passage(db, db_obj, payload.model_dump(exclude_unset=True))


@router.delete("/{passage_id}")
def delete_passage(passage_id: int, db: Session = Depends(get_db)) -> dict:
    db_obj = passage_crud.get(db, passage_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    passage_crud.delete(db, passage_id)
    return {"deleted": True}
