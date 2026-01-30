from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, item_id: int) -> ModelType | None:
        return db.get(self.model, item_id)

    def list(self, db: Session, skip: int = 0, limit: int = 20) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(self.model).count()

    def create(self, db: Session, obj_in: dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, item_id: int) -> None:
        db_obj = self.get(db, item_id)
        if db_obj is None:
            return None
        db.delete(db_obj)
        db.commit()
        return None
