from pydantic import BaseModel


class MasterySummaryRequest(BaseModel):
    user_id: int
    content_type: str | None = None
    days: int = 30


class MasterySummaryItem(BaseModel):
    content_type: str
    total: int
    correct: int
    accuracy: float
    mastery_score: float


class MasterySummaryResponse(BaseModel):
    items: list[MasterySummaryItem]
