from pydantic import BaseModel


class ExamResultOut(BaseModel):
    id: int
    exam_id: int
    user_id: int
    total: int
    correct: int
    score: int
    answers: dict
    created_at: str

    class Config:
        from_attributes = True


class ExamResultListResponse(BaseModel):
    items: list[ExamResultOut]
