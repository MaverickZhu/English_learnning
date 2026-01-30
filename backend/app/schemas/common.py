from typing import Literal

from pydantic import BaseModel, field_validator

LevelLiteral = Literal["A1", "A2", "B1", "B2", "C1"]


class TaggableModel(BaseModel):
    tags: list[str] | None = None

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value):
        if value is None:
            return value
        cleaned = []
        for item in value:
            if isinstance(item, str):
                tag = item.strip()
            elif isinstance(item, dict) and "name" in item:
                tag = str(item["name"]).strip()
            elif hasattr(item, "name"):
                tag = str(item.name).strip()
            else:
                raise ValueError("Tag must be a string")
            if not tag:
                raise ValueError("Tag cannot be empty")
            if len(tag) > 32:
                raise ValueError("Tag length must be <= 32")
            cleaned.append(tag)
        if len(cleaned) > 20:
            raise ValueError("Tag count must be <= 20")
        return cleaned


class Pagination(BaseModel):
    total: int
    items: list
