import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.report import recommendations, summary, trend, trend_by_type
from app.schemas.report import (
    ReportRecommendationRequest,
    ReportRecommendationResponse,
    ReportSummaryRequest,
    ReportSummaryResponse,
    ReportTrendByTypeRequest,
    ReportTrendByTypeResponse,
    ReportTrendRequest,
    ReportTrendResponse,
)

router = APIRouter(prefix="/reports")


@router.post("/summary", response_model=ReportSummaryResponse)
def report_summary(
    payload: ReportSummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReportSummaryResponse:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ReportSummaryResponse(**summary(db, user_id=current_user.id, days=payload.days))


@router.post("/summary/export")
def export_summary(
    payload: ReportSummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = summary(db, user_id=current_user.id, days=payload.days)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["study_total", data["study_total"]])
    writer.writerow(["study_accuracy", data["study_accuracy"]])
    writer.writerow(["exam_total", data["exam_total"]])
    writer.writerow(["exam_avg_score", data["exam_avg_score"]])
    writer.writerow([])
    writer.writerow(["by_type"])
    writer.writerow(["content_type", "total", "correct", "accuracy"])
    for item in data["by_type"]:
        writer.writerow([item["content_type"], item["total"], item["correct"], item["accuracy"]])
    writer.writerow([])
    writer.writerow(["by_exercise_type"])
    writer.writerow(["exercise_type", "total", "correct", "accuracy"])
    for item in data["by_exercise_type"]:
        writer.writerow([item["content_type"], item["total"], item["correct"], item["accuracy"]])
    writer.writerow([])
    writer.writerow(["by_level"])
    writer.writerow(["level", "total", "correct", "accuracy"])
    for item in data["by_level"]:
        writer.writerow([item["level"], item["total"], item["correct"], item["accuracy"]])
    writer.writerow([])
    writer.writerow(["weak_items"])
    writer.writerow(["content_type", "content_id", "wrong_count"])
    for item in data["weak_items"]:
        writer.writerow([item["content_type"], item["content_id"], item["wrong_count"]])
    writer.writerow([])
    writer.writerow(["suggestions"])
    for suggestion in data["suggestions"]:
        writer.writerow([suggestion])
    writer.writerow([])
    writer.writerow(["raw_json"])
    writer.writerow([json.dumps(data, ensure_ascii=False)])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/summary/export.json")
def export_summary_json(
    payload: ReportSummaryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Response:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = summary(db, user_id=current_user.id, days=payload.days)
    return Response(content=json.dumps(data, ensure_ascii=False), media_type="application/json")


@router.post("/trend", response_model=ReportTrendResponse)
def report_trend(
    payload: ReportTrendRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReportTrendResponse:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ReportTrendResponse(items=trend(db, user_id=current_user.id, days=payload.days))


@router.post("/trend/by-type", response_model=ReportTrendByTypeResponse)
def report_trend_by_type(
    payload: ReportTrendByTypeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReportTrendByTypeResponse:
    if payload.days <= 0 or payload.days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ReportTrendByTypeResponse(items=trend_by_type(db, user_id=current_user.id, days=payload.days))


@router.post("/recommendations", response_model=ReportRecommendationResponse)
def report_recommendations(
    payload: ReportRecommendationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ReportRecommendationResponse:
    if payload.limit <= 0 or payload.limit > 50:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 50")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ReportRecommendationResponse(items=recommendations(db, user_id=current_user.id, limit=payload.limit))
