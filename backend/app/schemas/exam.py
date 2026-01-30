from datetime import datetime

from pydantic import BaseModel


class ExamGenerateRequest(BaseModel):
    user_id: int
    title: str
    duration_minutes: int = 30
    level: str | None = None
    limit: int = 20
    config_name: str | None = None


class ExamOut(BaseModel):
    id: int
    user_id: int
    title: str
    duration_minutes: int
    exercise_ids: list[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ExamAnswerDetail(BaseModel):
    exercise_id: int
    given: str | None = None
    correct: bool
    expected: str
    explanation: str | None = None


class ExamSubmitRequest(BaseModel):
    exam_id: int
    answers: dict[int, str | list[str]]


class ExamSubmitResponse(BaseModel):
    total: int
    correct: int
    score: int
    details: list[ExamAnswerDetail]
