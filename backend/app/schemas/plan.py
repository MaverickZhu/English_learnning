from pydantic import BaseModel


class StudyPlanCreate(BaseModel):
    user_id: int
    title: str
    daily_target: int = 10
    start_date: str | None = None
    end_date: str | None = None
    is_active: bool = True


class StudyPlanOut(StudyPlanCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True


class StudyPlanListResponse(BaseModel):
    items: list[StudyPlanOut]
