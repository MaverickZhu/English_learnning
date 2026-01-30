from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.exercise import Exercise
from app.schemas.practice import (
    PracticeBatchScoreRequest,
    PracticeBatchScoreResponse,
    PracticeGenerateRequest,
    PracticeGenerateResponse,
    PracticeScoreRequest,
    PracticeScoreResponse,
)

router = APIRouter(prefix="/practice")


def _normalize_answer(value: str | list[str]) -> str:
    if isinstance(value, list):
        value = " ".join(value)
    return " ".join(value.strip().lower().split())


def _score(exercise: Exercise, answer: str | list[str]) -> PracticeScoreResponse:
    expected = _normalize_answer(exercise.answer)
    actual = _normalize_answer(answer)
    return PracticeScoreResponse(
        correct=actual == expected,
        expected=exercise.answer,
        explanation=exercise.explanation,
    )


@router.post("/generate", response_model=PracticeGenerateResponse)
def generate(payload: PracticeGenerateRequest, db: Session = Depends(get_db)) -> PracticeGenerateResponse:
    if payload.limit <= 0 or payload.limit > 50:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 50")
    query = db.query(Exercise)
    if payload.exercise_type:
        query = query.filter(Exercise.exercise_type == payload.exercise_type)
    if payload.level:
        query = query.filter(Exercise.level == payload.level)
    items = query.order_by(func.random()).limit(payload.limit).all()
    return PracticeGenerateResponse(items=items)


@router.post("/score", response_model=PracticeScoreResponse)
def score(payload: PracticeScoreRequest, db: Session = Depends(get_db)) -> PracticeScoreResponse:
    exercise = db.get(Exercise, payload.exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return _score(exercise, payload.answer)


@router.post("/score/batch", response_model=PracticeBatchScoreResponse)
def score_batch(payload: PracticeBatchScoreRequest, db: Session = Depends(get_db)) -> PracticeBatchScoreResponse:
    results: list[PracticeScoreResponse] = []
    for item in payload.items:
        exercise = db.get(Exercise, item.exercise_id)
        if exercise is None:
            raise HTTPException(status_code=404, detail="Exercise not found")
        results.append(_score(exercise, item.answer))
    return PracticeBatchScoreResponse(results=results)
