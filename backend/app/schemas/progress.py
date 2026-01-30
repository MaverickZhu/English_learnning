from pydantic import BaseModel


class StudyRecordCreate(BaseModel):
    user_id: int
    content_type: str
    content_id: int
    score: int | None = None
    correct: bool | None = None
    time_spent_seconds: int | None = None


class StudyRecordOut(StudyRecordCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True


class ProgressSummaryRequest(BaseModel):
    user_id: int
    days: int = 7


class ProgressSummaryResponse(BaseModel):
    total_records: int
    correct_count: int
    accuracy: float
    total_time_seconds: int


class ProgressHistoryResponse(BaseModel):
    items: list[StudyRecordOut]
