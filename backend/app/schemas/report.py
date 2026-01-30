from pydantic import BaseModel


class ReportSummaryRequest(BaseModel):
    user_id: int
    days: int = 30


class ReportTypeStat(BaseModel):
    content_type: str
    total: int
    correct: int
    accuracy: float


class ReportSummaryResponse(BaseModel):
    study_total: int
    study_accuracy: float
    exam_total: int
    exam_avg_score: float
    weak_items: list[dict]
    by_type: list[ReportTypeStat]
    by_exercise_type: list[ReportTypeStat]
    suggestions: list[str]
    by_level: list[dict]


class ReportTrendRequest(BaseModel):
    user_id: int
    days: int = 30


class ReportTrendItem(BaseModel):
    date: str
    total: int
    correct: int
    accuracy: float


class ReportTrendResponse(BaseModel):
    items: list[ReportTrendItem]


class ReportTrendByTypeRequest(BaseModel):
    user_id: int
    days: int = 30


class ReportTrendByTypeItem(BaseModel):
    date: str
    content_type: str
    total: int
    correct: int
    accuracy: float


class ReportTrendByTypeResponse(BaseModel):
    items: list[ReportTrendByTypeItem]


class ReportRecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10


class ReportRecommendationItem(BaseModel):
    content_type: str
    content_id: int
    reason: str
    preview: str | None = None
    link: str | None = None


class ReportRecommendationResponse(BaseModel):
    items: list[ReportRecommendationItem]
