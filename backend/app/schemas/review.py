from pydantic import BaseModel


class ReviewReminderCreate(BaseModel):
    user_id: int
    content_type: str
    content_id: int
    next_review_at: str


class ReviewReminderOut(ReviewReminderCreate):
    id: int
    status: str
    created_at: str
    updated_at: str | None = None

    class Config:
        from_attributes = True


class ReviewReminderListResponse(BaseModel):
    items: list[ReviewReminderOut]
