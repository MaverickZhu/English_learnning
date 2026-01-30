from pydantic import BaseModel, field_serializer

from app.schemas.common import LevelLiteral, TaggableModel


class PassageBase(TaggableModel):
    title: str
    content: str
    summary: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class PassageCreate(PassageBase):
    pass


class PassageUpdate(TaggableModel):
    title: str | None = None
    content: str | None = None
    summary: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    level: LevelLiteral | None = None


class PassageOut(PassageBase):
    id: int
    tags: list[str]

    class Config:
        from_attributes = True

    @field_serializer("tags")
    def serialize_tags(self, tags):
        return [tag.name if hasattr(tag, "name") else tag for tag in tags or []]


class PassageListResponse(BaseModel):
    total: int
    items: list[PassageOut]
    next_cursor: int | None = None
