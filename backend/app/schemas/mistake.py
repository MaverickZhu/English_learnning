from pydantic import BaseModel


class MistakeRecordRequest(BaseModel):
    user_id: int
    content_type: str
    content_id: int
    correct: bool


class MistakeItemOut(BaseModel):
    id: int
    user_id: int
    content_type: str
    content_id: int
    wrong_count: int
    last_wrong_at: str

    class Config:
        from_attributes = True


class MistakeListResponse(BaseModel):
    items: list[MistakeItemOut]
