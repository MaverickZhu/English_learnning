from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.crud import content
from app.crud.content import sentence_crud
from app.schemas.sentence import SentenceCreate, SentenceListResponse, SentenceOut, SentenceUpdate

router = APIRouter(prefix="/sentences")


@router.post("", response_model=SentenceOut)
def create_sentence(payload: SentenceCreate, db: Session = Depends(get_db)) -> SentenceOut:
    return content.create_sentence(db, payload.model_dump())


@router.get("", response_model=SentenceListResponse)
def list_sentences(
    skip: int = 0,
    limit: int = 20,
    level: str | None = None,
    tags: str | None = None,
    keyword: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> SentenceListResponse:
    items = content.list_sentences(
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
    total = content.count_sentences(db, level=level, tags=tags, keyword=keyword)
    next_cursor = items[-1].id if items else None
    return SentenceListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/{sentence_id}", response_model=SentenceOut)
def get_sentence(sentence_id: int, db: Session = Depends(get_db)) -> SentenceOut:
    db_obj = sentence_crud.get(db, sentence_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return db_obj


@router.put("/{sentence_id}", response_model=SentenceOut)
def update_sentence(
    sentence_id: int,
    payload: SentenceUpdate,
    db: Session = Depends(get_db),
) -> SentenceOut:
    db_obj = sentence_crud.get(db, sentence_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return content.update_sentence(db, db_obj, payload.model_dump(exclude_unset=True))


@router.delete("/{sentence_id}")
def delete_sentence(sentence_id: int, db: Session = Depends(get_db)) -> dict:
    db_obj = sentence_crud.get(db, sentence_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Sentence not found")
    sentence_crud.delete(db, sentence_id)
    return {"deleted": True}
