from typing import Literal

from pydantic import BaseModel, field_serializer

from app.schemas.common import LevelLiteral, TaggableModel

ExerciseType = Literal["image_choice", "listening_choice", "sentence_order", "cloze"]


class ExerciseBase(TaggableModel):
    exercise_type: ExerciseType
    prompt: str
    options: list[str] | None = None
    answer: str
    explanation: str | None = None
    level: LevelLiteral | None = None


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(TaggableModel):
    exercise_type: ExerciseType | None = None
    prompt: str | None = None
    options: list[str] | None = None
    answer: str | None = None
    explanation: str | None = None
    level: LevelLiteral | None = None


class ExerciseOut(ExerciseBase):
    id: int
    tags: list[str]

    class Config:
        from_attributes = True

    @field_serializer("tags")
    def serialize_tags(self, tags):
        return [tag.name if hasattr(tag, "name") else tag for tag in tags or []]


class ExerciseListResponse(BaseModel):
    total: int
    items: list[ExerciseOut]
    next_cursor: int | None = None
