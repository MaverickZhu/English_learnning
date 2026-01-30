from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud import content
from app.crud.content import word_crud
from app.schemas.word import WordCreate, WordListResponse, WordOut, WordUpdate

router = APIRouter(prefix="/words")


@router.post("", response_model=WordOut)
def create_word(payload: WordCreate, db: Session = Depends(get_db)) -> WordOut:
    return content.create_word(db, payload.model_dump())


@router.get("", response_model=WordListResponse)
def list_words(
    skip: int = 0,
    limit: int = 20,
    level: str | None = None,
    tags: str | None = None,
    keyword: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> WordListResponse:
    items = content.list_words(
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
    total = content.count_words(db, level=level, tags=tags, keyword=keyword)
    next_cursor = items[-1].id if items else None
    return WordListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/{word_id}", response_model=WordOut)
def get_word(word_id: int, db: Session = Depends(get_db)) -> WordOut:
    db_obj = word_crud.get(db, word_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return db_obj


@router.put("/{word_id}", response_model=WordOut)
def update_word(
    word_id: int,
    payload: WordUpdate,
    db: Session = Depends(get_db),
) -> WordOut:
    db_obj = word_crud.get(db, word_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return content.update_word(db, db_obj, payload.model_dump(exclude_unset=True))


@router.delete("/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)) -> dict:
    db_obj = word_crud.get(db, word_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Word not found")
    word_crud.delete(db, word_id)
    return {"deleted": True}
