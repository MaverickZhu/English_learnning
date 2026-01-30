from pydantic import BaseModel


class ExamConfigCreate(BaseModel):
    name: str
    duration_minutes: int = 30
    level: str | None = None
    distribution: dict


class ExamConfigOut(ExamConfigCreate):
    id: int

    class Config:
        from_attributes = True
