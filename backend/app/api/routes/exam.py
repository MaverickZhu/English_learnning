from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.crud.exam import generate_exam, get_exam
from app.crud.exam_config import create_config, get_config_by_name, list_configs
from app.crud.exam_result import create_result, list_results
from app.crud.mistake import record_mistake
from app.models.exercise import Exercise
from app.schemas.exam import ExamAnswerDetail, ExamGenerateRequest, ExamOut, ExamSubmitRequest, ExamSubmitResponse
from app.schemas.exam_config import ExamConfigCreate, ExamConfigOut
from app.schemas.exam_result import ExamResultListResponse, ExamResultOut

router = APIRouter(prefix="/exam")


@router.post("/generate", response_model=ExamOut)
def generate(
    payload: ExamGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ExamOut:
    if payload.limit <= 0 or payload.limit > 200:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 200")
    if payload.duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="duration_minutes must be > 0")
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    distribution = None
    if payload.config_name:
        config = get_config_by_name(db, payload.config_name)
        if config is None:
            raise HTTPException(status_code=404, detail="Exam config not found")
        distribution = config.distribution
        if not isinstance(distribution, dict) or not distribution:
            raise HTTPException(status_code=400, detail="Exam config distribution invalid")
        if sum(int(value) for value in distribution.values()) <= 0:
            raise HTTPException(status_code=400, detail="Exam config distribution invalid")
        if not payload.level and config.level:
            payload.level = config.level
        if payload.duration_minutes == 30 and config.duration_minutes:
            payload.duration_minutes = config.duration_minutes
    return generate_exam(
        db,
        user_id=payload.user_id,
        title=payload.title,
        duration_minutes=payload.duration_minutes,
        level=payload.level,
        limit=payload.limit,
        distribution=distribution,
    )


@router.post("/submit", response_model=ExamSubmitResponse)
def submit(
    payload: ExamSubmitRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ExamSubmitResponse:
    exam = get_exam(db, payload.exam_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    if exam.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    exercises = db.query(Exercise).filter(Exercise.id.in_(exam.exercise_ids)).all()
    answers_map = payload.answers
    correct = 0
    total = len(exercises)
    details: list[ExamAnswerDetail] = []
    for exercise in exercises:
        expected = exercise.answer.strip().lower()
        given = answers_map.get(exercise.id)
        if given is None:
            details.append(
                ExamAnswerDetail(
                    exercise_id=exercise.id,
                    given=None,
                    correct=False,
                    expected=exercise.answer,
                    explanation=exercise.explanation,
                )
            )
            record_mistake(
                db,
                {
                    "user_id": exam.user_id,
                    "content_type": "exercise",
                    "content_id": exercise.id,
                    "correct": False,
                },
            )
            continue
        if isinstance(given, list):
            given_text = " ".join(given).strip().lower()
        else:
            given_text = str(given).strip().lower()
        if given_text == expected:
            correct += 1
            details.append(
                ExamAnswerDetail(
                    exercise_id=exercise.id,
                    given=given_text,
                    correct=True,
                    expected=exercise.answer,
                    explanation=exercise.explanation,
                )
            )
        else:
            details.append(
                ExamAnswerDetail(
                    exercise_id=exercise.id,
                    given=given_text,
                    correct=False,
                    expected=exercise.answer,
                    explanation=exercise.explanation,
                )
            )
            record_mistake(
                db,
                {
                    "user_id": exam.user_id,
                    "content_type": "exercise",
                    "content_id": exercise.id,
                    "correct": False,
                },
            )
    score = int((correct / total) * 100) if total > 0 else 0
    create_result(
        db,
        {
            "exam_id": exam.id,
            "user_id": exam.user_id,
            "total": total,
            "correct": correct,
            "score": score,
            "answers": {str(k): v for k, v in answers_map.items()},
        },
    )
    return ExamSubmitResponse(total=total, correct=correct, score=score, details=details)


@router.get("/results", response_model=ExamResultListResponse)
def results(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ExamResultListResponse:
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    items = list_results(db, user_id=current_user.id, skip=skip, limit=limit)
    return ExamResultListResponse(items=items)


@router.post("/config", response_model=ExamConfigOut)
def create_exam_config(payload: ExamConfigCreate, db: Session = Depends(get_db)) -> ExamConfigOut:
    if payload.duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="duration_minutes must be > 0")
    if not payload.distribution:
        raise HTTPException(status_code=400, detail="distribution is required")
    if sum(int(value) for value in payload.distribution.values()) <= 0:
        raise HTTPException(status_code=400, detail="distribution must have positive counts")
    return create_config(db, payload.model_dump())


@router.get("/configs", response_model=list[ExamConfigOut])
def list_exam_configs(db: Session = Depends(get_db)) -> list[ExamConfigOut]:
    return list_configs(db)


@router.get("/config/{name}", response_model=ExamConfigOut)
def get_exam_config(name: str, db: Session = Depends(get_db)) -> ExamConfigOut:
    config = get_config_by_name(db, name)
    if config is None:
        raise HTTPException(status_code=404, detail="Exam config not found")
    return config
