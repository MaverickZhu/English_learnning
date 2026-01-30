from pydantic import BaseModel, field_serializer

from app.schemas.common import LevelLiteral, TaggableModel


class SentenceBase(TaggableModel):
    text: str
    meaning: str
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class SentenceCreate(SentenceBase):
    pass


class SentenceUpdate(TaggableModel):
    text: str | None = None
    meaning: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class SentenceOut(SentenceBase):
    id: int
    tags: list[str]

    class Config:
        from_attributes = True

    @field_serializer("tags")
    def serialize_tags(self, tags):
        return [tag.name if hasattr(tag, "name") else tag for tag in tags or []]


class SentenceListResponse(BaseModel):
    total: int
    items: list[SentenceOut]
    next_cursor: int | None = None
