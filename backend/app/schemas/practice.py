from pydantic import BaseModel

from app.schemas.exercise import ExerciseOut


class PracticeGenerateRequest(BaseModel):
    exercise_type: str | None = None
    level: str | None = None
    limit: int = 10


class PracticeGenerateResponse(BaseModel):
    items: list[ExerciseOut]


class PracticeScoreRequest(BaseModel):
    exercise_id: int
    answer: str | list[str]


class PracticeScoreResponse(BaseModel):
    correct: bool
    expected: str
    explanation: str | None = None


class PracticeBatchScoreRequest(BaseModel):
    items: list[PracticeScoreRequest]


class PracticeBatchScoreResponse(BaseModel):
    results: list[PracticeScoreResponse]
