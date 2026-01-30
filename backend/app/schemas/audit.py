from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    action: str
    entity_type: str | None = None
    entity_id: int | None = None
    payload: dict | None = None
    created_at: str

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    total: int
    items: list[AuditLogOut]
    next_cursor: int | None = None
