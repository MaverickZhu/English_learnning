from pydantic import BaseModel


class ImportJobOut(BaseModel):
    id: int
    status: str
    entity_type: str
    mode: str
    atomic: bool
    filename: str | None = None
    summary: dict | None = None
    error_summary: dict | None = None
    error_details: dict | None = None
    created_at: str
    updated_at: str | None = None
    finished_at: str | None = None

    class Config:
        from_attributes = True


class ImportJobListResponse(BaseModel):
    total: int
    items: list[ImportJobOut]
    next_cursor: int | None = None
