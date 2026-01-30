from pydantic import BaseModel, field_serializer

from app.schemas.common import LevelLiteral, TaggableModel


class WordBase(TaggableModel):
    text: str
    meaning: str
    example: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class WordCreate(WordBase):
    pass


class WordUpdate(TaggableModel):
    text: str | None = None
    meaning: str | None = None
    example: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class WordOut(WordBase):
    id: int
    tags: list[str]

    class Config:
        from_attributes = True

    @field_serializer("tags")
    def serialize_tags(self, tags):
        return [tag.name if hasattr(tag, "name") else tag for tag in tags or []]


class WordListResponse(BaseModel):
    total: int
    items: list[WordOut]
    next_cursor: int | None = None
