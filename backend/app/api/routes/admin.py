import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import presign_get_url, upload_bytes
from app.core.database import SessionLocal
from app.core.deps import admin_auth, get_db
from app.crud import content
from app.models.audit_log import AdminAuditLog
from app.models.exercise import Exercise
from app.models.import_job import ImportJob
from app.models.passage import Passage
from app.models.sentence import Sentence
from app.models.word import Word
from app.schemas.admin import (
    BulkActionResult,
    BulkDeleteRequest,
    BulkDeleteResult,
    BulkError,
    BulkErrorSummary,
    BulkExerciseRequest,
    BulkPassageRequest,
    BulkResult,
    BulkSentenceRequest,
    BulkTagAssignRequest,
    BulkValidateRequest,
    BulkValidateResult,
    ImportExecuteRequest,
    BulkWordRequest,
    TagAssignRequest,
)
from app.schemas.exercise import ExerciseCreate
from app.schemas.import_job import ImportJobListResponse, ImportJobOut
from app.schemas.passage import PassageCreate
from app.schemas.sentence import SentenceCreate
from app.schemas.word import WordCreate
from app.utils.import_utils import apply_mapping, parse_file

router = APIRouter(prefix="/admin", dependencies=[Depends(admin_auth)])

MODEL_MAP = {
    "word": Word,
    "sentence": Sentence,
    "passage": Passage,
    "exercise": Exercise,
}


def _summarize_errors(errors: list[BulkError]) -> list[BulkErrorSummary]:
    buckets: dict[tuple[str, str], int] = {}
    for error in errors:
        key = (error.field, error.message)
        buckets[key] = buckets.get(key, 0) + 1
    return [BulkErrorSummary(field=field, message=message, count=count) for (field, message), count in buckets.items()]


def _log_action(
    db: Session,
    action: str,
    payload: dict,
    entity_type: str | None = None,
    entity_id: int | None = None,
    commit: bool = True,
) -> None:
    entry = AdminAuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
    )
    db.add(entry)
    if commit:
        db.commit()
    else:
        db.flush()


@router.post("/words/bulk", response_model=BulkResult)
def bulk_words(payload: BulkWordRequest, db: Session = Depends(get_db)) -> BulkResult:
    created = updated = skipped = 0
    errors: list[BulkError] = []
    has_errors = False
    seen_keys: set[str] = set()
    for index, item in enumerate(payload.items):
        try:
            data = WordCreate.model_validate(item).model_dump()
        except ValidationError as exc:
            skipped += 1
            has_errors = True
            for err in exc.errors():
                field = ".".join(str(part) for part in err.get("loc", []))
                errors.append(
                    BulkError(index=index, field=field or "item", message=err.get("msg", "Invalid value"))
                )
            continue
        key = data.get("text")
        if key in seen_keys:
            skipped += 1
            has_errors = True
            errors.append(BulkError(index=index, field="text", message="Duplicate item in payload"))
            continue
        seen_keys.add(key)
        if payload.mode == "insert_only":
            existing = db.query(Word).filter(Word.text == key).first()
            if existing is not None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="text", message="Already exists"))
                continue
            content.create_word(db, data, commit=not payload.atomic)
            created += 1
        elif payload.mode == "update_only":
            existing = db.query(Word).filter(Word.text == key).first()
            if existing is None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="text", message="Not found for update"))
                continue
            content.update_word(db, existing, data, commit=not payload.atomic)
            updated += 1
        else:
            _, is_created = content.upsert_word(db, data, commit=not payload.atomic)
            if is_created:
                created += 1
            else:
                updated += 1
    if payload.atomic:
        if has_errors:
            db.rollback()
            created = updated = 0
            skipped = len(payload.items)
        else:
            db.commit()
    _log_action(
        db,
        action="bulk_words",
        payload={
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "mode": payload.mode,
            "atomic": payload.atomic,
            "error_summary": _summarize_errors(errors),
        },
        entity_type="word",
        commit=True,
    )
    return BulkResult(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/sentences/bulk", response_model=BulkResult)
def bulk_sentences(payload: BulkSentenceRequest, db: Session = Depends(get_db)) -> BulkResult:
    created = updated = skipped = 0
    errors: list[BulkError] = []
    has_errors = False
    seen_keys: set[str] = set()
    for index, item in enumerate(payload.items):
        try:
            data = SentenceCreate.model_validate(item).model_dump()
        except ValidationError as exc:
            skipped += 1
            has_errors = True
            for err in exc.errors():
                field = ".".join(str(part) for part in err.get("loc", []))
                errors.append(
                    BulkError(index=index, field=field or "item", message=err.get("msg", "Invalid value"))
                )
            continue
        key = data.get("text")
        if key in seen_keys:
            skipped += 1
            has_errors = True
            errors.append(BulkError(index=index, field="text", message="Duplicate item in payload"))
            continue
        seen_keys.add(key)
        if payload.mode == "insert_only":
            existing = db.query(Sentence).filter(Sentence.text == key).first()
            if existing is not None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="text", message="Already exists"))
                continue
            content.create_sentence(db, data, commit=not payload.atomic)
            created += 1
        elif payload.mode == "update_only":
            existing = db.query(Sentence).filter(Sentence.text == key).first()
            if existing is None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="text", message="Not found for update"))
                continue
            content.update_sentence(db, existing, data, commit=not payload.atomic)
            updated += 1
        else:
            _, is_created = content.upsert_sentence(db, data, commit=not payload.atomic)
            if is_created:
                created += 1
            else:
                updated += 1
    if payload.atomic:
        if has_errors:
            db.rollback()
            created = updated = 0
            skipped = len(payload.items)
        else:
            db.commit()
    _log_action(
        db,
        action="bulk_sentences",
        payload={
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "mode": payload.mode,
            "atomic": payload.atomic,
            "error_summary": _summarize_errors(errors),
        },
        entity_type="sentence",
        commit=True,
    )
    return BulkResult(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/passages/bulk", response_model=BulkResult)
def bulk_passages(payload: BulkPassageRequest, db: Session = Depends(get_db)) -> BulkResult:
    created = updated = skipped = 0
    errors: list[BulkError] = []
    has_errors = False
    seen_keys: set[str] = set()
    for index, item in enumerate(payload.items):
        try:
            data = PassageCreate.model_validate(item).model_dump()
        except ValidationError as exc:
            skipped += 1
            has_errors = True
            for err in exc.errors():
                field = ".".join(str(part) for part in err.get("loc", []))
                errors.append(
                    BulkError(index=index, field=field or "item", message=err.get("msg", "Invalid value"))
                )
            continue
        key = data.get("title")
        if key in seen_keys:
            skipped += 1
            has_errors = True
            errors.append(BulkError(index=index, field="title", message="Duplicate item in payload"))
            continue
        seen_keys.add(key)
        if payload.mode == "insert_only":
            existing = db.query(Passage).filter(Passage.title == key).first()
            if existing is not None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="title", message="Already exists"))
                continue
            content.create_passage(db, data, commit=not payload.atomic)
            created += 1
        elif payload.mode == "update_only":
            existing = db.query(Passage).filter(Passage.title == key).first()
            if existing is None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="title", message="Not found for update"))
                continue
            content.update_passage(db, existing, data, commit=not payload.atomic)
            updated += 1
        else:
            _, is_created = content.upsert_passage(db, data, commit=not payload.atomic)
            if is_created:
                created += 1
            else:
                updated += 1
    if payload.atomic:
        if has_errors:
            db.rollback()
            created = updated = 0
            skipped = len(payload.items)
        else:
            db.commit()
    _log_action(
        db,
        action="bulk_passages",
        payload={
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "mode": payload.mode,
            "atomic": payload.atomic,
            "error_summary": _summarize_errors(errors),
        },
        entity_type="passage",
        commit=True,
    )
    return BulkResult(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/exercises/bulk", response_model=BulkResult)
def bulk_exercises(payload: BulkExerciseRequest, db: Session = Depends(get_db)) -> BulkResult:
    created = updated = skipped = 0
    errors: list[BulkError] = []
    has_errors = False
    seen_keys: set[tuple[str, str]] = set()
    for index, item in enumerate(payload.items):
        try:
            data = ExerciseCreate.model_validate(item).model_dump()
        except ValidationError as exc:
            skipped += 1
            has_errors = True
            for err in exc.errors():
                field = ".".join(str(part) for part in err.get("loc", []))
                errors.append(
                    BulkError(index=index, field=field or "item", message=err.get("msg", "Invalid value"))
                )
            continue
        key = (data.get("exercise_type"), data.get("prompt"))
        if key in seen_keys:
            skipped += 1
            has_errors = True
            errors.append(BulkError(index=index, field="prompt", message="Duplicate item in payload"))
            continue
        seen_keys.add(key)
        if payload.mode == "insert_only":
            existing = (
                db.query(Exercise)
                .filter(Exercise.exercise_type == key[0])
                .filter(Exercise.prompt == key[1])
                .first()
            )
            if existing is not None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="prompt", message="Already exists"))
                continue
            content.create_exercise(db, data, commit=not payload.atomic)
            created += 1
        elif payload.mode == "update_only":
            existing = (
                db.query(Exercise)
                .filter(Exercise.exercise_type == key[0])
                .filter(Exercise.prompt == key[1])
                .first()
            )
            if existing is None:
                skipped += 1
                has_errors = True
                errors.append(BulkError(index=index, field="prompt", message="Not found for update"))
                continue
            content.update_exercise(db, existing, data, commit=not payload.atomic)
            updated += 1
        else:
            _, is_created = content.upsert_exercise(db, data, commit=not payload.atomic)
            if is_created:
                created += 1
            else:
                updated += 1
    if payload.atomic:
        if has_errors:
            db.rollback()
            created = updated = 0
            skipped = len(payload.items)
        else:
            db.commit()
    _log_action(
        db,
        action="bulk_exercises",
        payload={
            "created": created,
            "updated": updated,
            "skipped": skipped,
            "mode": payload.mode,
            "atomic": payload.atomic,
            "error_summary": _summarize_errors(errors),
        },
        entity_type="exercise",
        commit=True,
    )
    return BulkResult(
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/tags/assign")
def assign_tags(payload: TagAssignRequest, db: Session = Depends(get_db)) -> dict:
    model = MODEL_MAP.get(payload.entity_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    result = content.apply_tags(db, model, payload.entity_id, payload.tags, payload.mode)
    if result is None:
        raise HTTPException(status_code=404, detail="Target not found or invalid mode")
    _log_action(
        db,
        action="assign_tags",
        payload=payload.model_dump(),
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        commit=True,
    )
    return {"updated": True}


@router.post("/tags/bulk-assign", response_model=BulkActionResult)
def bulk_assign_tags(payload: BulkTagAssignRequest, db: Session = Depends(get_db)) -> BulkActionResult:
    updated = skipped = 0
    errors: list[BulkError] = []
    has_errors = False
    model = MODEL_MAP.get(payload.entity_type)
    if model is None:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    for index, item in enumerate(payload.items):
        result = content.apply_tags(db, model, item.entity_id, item.tags, item.mode, commit=not payload.atomic)
        if result is None:
            skipped += 1
            has_errors = True
            errors.append(BulkError(index=index, field="entity_id", message="Target not found or invalid mode"))
            continue
        updated += 1
    if payload.atomic:
        if has_errors:
            db.rollback()
            updated = 0
            skipped = len(payload.items)
        else:
            db.commit()
    _log_action(
        db,
        action="bulk_assign_tags",
        payload={"updated": updated, "skipped": skipped, "entity_type": payload.entity_type},
        entity_type=payload.entity_type,
        commit=True,
    )
    return BulkActionResult(
        updated=updated,
        skipped=skipped,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/words/bulk-delete", response_model=BulkDeleteResult)
def bulk_delete_words(payload: BulkDeleteRequest, db: Session = Depends(get_db)) -> BulkDeleteResult:
    ids = set(payload.ids)
    if not ids:
        return BulkDeleteResult(deleted=0, missing=[])
    existing_ids = {item[0] for item in db.query(Word.id).filter(Word.id.in_(ids)).all()}
    missing = sorted(ids - existing_ids)
    if payload.atomic and missing:
        return BulkDeleteResult(deleted=0, missing=missing)
    deleted = db.query(Word).filter(Word.id.in_(existing_ids)).delete(synchronize_session=False)
    db.commit()
    _log_action(
        db,
        action="bulk_delete_words",
        payload={"deleted": deleted, "missing": missing, "atomic": payload.atomic},
        entity_type="word",
        commit=True,
    )
    return BulkDeleteResult(deleted=deleted, missing=missing)


@router.post("/sentences/bulk-delete", response_model=BulkDeleteResult)
def bulk_delete_sentences(payload: BulkDeleteRequest, db: Session = Depends(get_db)) -> BulkDeleteResult:
    ids = set(payload.ids)
    if not ids:
        return BulkDeleteResult(deleted=0, missing=[])
    existing_ids = {item[0] for item in db.query(Sentence.id).filter(Sentence.id.in_(ids)).all()}
    missing = sorted(ids - existing_ids)
    if payload.atomic and missing:
        return BulkDeleteResult(deleted=0, missing=missing)
    deleted = db.query(Sentence).filter(Sentence.id.in_(existing_ids)).delete(synchronize_session=False)
    db.commit()
    _log_action(
        db,
        action="bulk_delete_sentences",
        payload={"deleted": deleted, "missing": missing, "atomic": payload.atomic},
        entity_type="sentence",
        commit=True,
    )
    return BulkDeleteResult(deleted=deleted, missing=missing)


@router.post("/passages/bulk-delete", response_model=BulkDeleteResult)
def bulk_delete_passages(payload: BulkDeleteRequest, db: Session = Depends(get_db)) -> BulkDeleteResult:
    ids = set(payload.ids)
    if not ids:
        return BulkDeleteResult(deleted=0, missing=[])
    existing_ids = {item[0] for item in db.query(Passage.id).filter(Passage.id.in_(ids)).all()}
    missing = sorted(ids - existing_ids)
    if payload.atomic and missing:
        return BulkDeleteResult(deleted=0, missing=missing)
    deleted = db.query(Passage).filter(Passage.id.in_(existing_ids)).delete(synchronize_session=False)
    db.commit()
    _log_action(
        db,
        action="bulk_delete_passages",
        payload={"deleted": deleted, "missing": missing, "atomic": payload.atomic},
        entity_type="passage",
        commit=True,
    )
    return BulkDeleteResult(deleted=deleted, missing=missing)


@router.post("/exercises/bulk-delete", response_model=BulkDeleteResult)
def bulk_delete_exercises(payload: BulkDeleteRequest, db: Session = Depends(get_db)) -> BulkDeleteResult:
    ids = set(payload.ids)
    if not ids:
        return BulkDeleteResult(deleted=0, missing=[])
    existing_ids = {item[0] for item in db.query(Exercise.id).filter(Exercise.id.in_(ids)).all()}
    missing = sorted(ids - existing_ids)
    if payload.atomic and missing:
        return BulkDeleteResult(deleted=0, missing=missing)
    deleted = db.query(Exercise).filter(Exercise.id.in_(existing_ids)).delete(synchronize_session=False)
    db.commit()
    _log_action(
        db,
        action="bulk_delete_exercises",
        payload={"deleted": deleted, "missing": missing, "atomic": payload.atomic},
        entity_type="exercise",
        commit=True,
    )
    return BulkDeleteResult(deleted=deleted, missing=missing)


@router.post("/import/validate", response_model=BulkValidateResult)
def validate_import(payload: BulkValidateRequest) -> BulkValidateResult:
    errors: list[BulkError] = []
    schema_map = {
        "word": WordCreate,
        "sentence": SentenceCreate,
        "passage": PassageCreate,
        "exercise": ExerciseCreate,
    }
    schema = schema_map.get(payload.entity_type)
    if schema is None:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    for index, item in enumerate(payload.items):
        try:
            schema.model_validate(item)
        except ValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(part) for part in err.get("loc", []))
                errors.append(BulkError(index=index, field=field or "item", message=err.get("msg", "Invalid value")))
    return BulkValidateResult(
        valid=len(errors) == 0,
        errors=errors,
        error_summary=_summarize_errors(errors),
    )


@router.post("/import/execute", response_model=BulkResult)
def execute_import(payload: ImportExecuteRequest, db: Session = Depends(get_db)) -> BulkResult:
    return _execute_import_internal(payload, db)


@router.post("/import/upload", response_model=BulkResult)
def import_upload(
    entity_type: str = Form(...),
    mode: str = Form("upsert"),
    atomic: bool = Form(False),
    mapping: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BulkResult:
    try:
        raw = file.file.read()
        if len(raw) > settings.max_import_bytes:
            raise HTTPException(status_code=413, detail="File too large")
        content = raw.decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to read file") from exc
    try:
        items = parse_file(file.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    mapping_dict = None
    if mapping:
        try:
            mapping_dict = json.loads(mapping)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid mapping JSON") from exc
    items = apply_mapping(items, mapping_dict)
    payload = ImportExecuteRequest(entity_type=entity_type, items=items, mode=mode, atomic=atomic)
    return execute_import(payload, db)


@router.get("/import/template")
def import_template(entity_type: str) -> dict:
    templates = {
        "word": {
            "columns": ["text", "meaning", "example", "audio_url", "image_url", "level", "tags"],
            "example": {
                "text": "focus",
                "meaning": "the center of interest",
                "level": "A2",
                "tags": "learning,attention",
            },
        },
        "sentence": {
            "columns": ["text", "meaning", "audio_url", "image_url", "level", "tags"],
            "example": {
                "text": "The train arrives at 8:30 every morning.",
                "meaning": "The train comes at the same time each morning.",
                "level": "A1",
                "tags": "travel,routine",
            },
        },
        "passage": {
            "columns": ["title", "content", "summary", "audio_url", "image_url", "level", "tags"],
            "example": {
                "title": "A Morning Routine",
                "content": "Lena wakes up at 6:30 and makes a cup of tea.",
                "level": "A2",
                "tags": "routine,lifestyle",
            },
        },
        "exercise": {
            "columns": ["exercise_type", "prompt", "options", "answer", "explanation", "level", "tags"],
            "example": {
                "exercise_type": "cloze",
                "prompt": "Complete the sentence: We need a more ____ workflow.",
                "options": "efficient,fragile,silent,distant",
                "answer": "efficient",
                "level": "B1",
                "tags": "vocabulary,cloze",
            },
        },
    }
    template = templates.get(entity_type)
    if template is None:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    return template


def _execute_import_internal(payload: ImportExecuteRequest, db: Session) -> BulkResult:
    if payload.entity_type == "word":
        return bulk_words(BulkWordRequest(items=payload.items, mode=payload.mode, atomic=payload.atomic), db)
    if payload.entity_type == "sentence":
        return bulk_sentences(BulkSentenceRequest(items=payload.items, mode=payload.mode, atomic=payload.atomic), db)
    if payload.entity_type == "passage":
        return bulk_passages(BulkPassageRequest(items=payload.items, mode=payload.mode, atomic=payload.atomic), db)
    if payload.entity_type == "exercise":
        return bulk_exercises(BulkExerciseRequest(items=payload.items, mode=payload.mode, atomic=payload.atomic), db)
    raise HTTPException(status_code=400, detail="Invalid entity type")


def _process_import_job(job_id: int, payload: ImportExecuteRequest, filename: str | None) -> None:
    db = SessionLocal()
    try:
        job = db.get(ImportJob, job_id)
        if job is None:
            return
        if job.status == "cancelled":
            return
        job.status = "running"
        db.add(job)
        db.commit()
        result = _execute_import_internal(payload, db)
        job.status = "success"
        job.summary = {"created": result.created, "updated": result.updated, "skipped": result.skipped}
        job.error_summary = [item.model_dump() for item in result.error_summary]
        job.error_details = [item.model_dump() for item in result.errors[:200]]
        job.finished_at = datetime.utcnow()
        db.add(job)
        db.commit()
        _log_action(
            db,
            action="import_async",
            payload={"job_id": job_id, "filename": filename, "summary": job.summary},
            entity_type=payload.entity_type,
            commit=True,
        )
    except Exception as exc:
        job = db.get(ImportJob, job_id)
        if job is not None:
            job.status = "failed"
            job.summary = {"error": str(exc)}
            job.finished_at = datetime.utcnow()
            db.add(job)
            db.commit()
    finally:
        db.close()


@router.post("/import/async-upload", response_model=ImportJobOut)
def import_async_upload(
    background_tasks: BackgroundTasks,
    entity_type: str = Form(...),
    mode: str = Form("upsert"),
    atomic: bool = Form(False),
    mapping: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> ImportJobOut:
    try:
        raw = file.file.read()
        if len(raw) > settings.max_import_bytes:
            raise HTTPException(status_code=413, detail="File too large")
        content = raw.decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to read file") from exc
    try:
        items = parse_file(file.filename or "", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    mapping_dict = None
    if mapping:
        try:
            mapping_dict = json.loads(mapping)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid mapping JSON") from exc
    items = apply_mapping(items, mapping_dict)
    payload = ImportExecuteRequest(entity_type=entity_type, items=items, mode=mode, atomic=atomic)
    job = ImportJob(
        status="queued",
        entity_type=entity_type,
        mode=mode,
        atomic=atomic,
        filename=file.filename,
        payload=payload.model_dump(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(_process_import_job, job.id, payload, file.filename)
    return job


@router.get("/import/jobs", response_model=ImportJobListResponse)
def list_import_jobs(
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    entity_type: str | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> ImportJobListResponse:
    query = db.query(ImportJob)
    if status:
        query = query.filter(ImportJob.status == status)
    if entity_type:
        query = query.filter(ImportJob.entity_type == entity_type)
    if start_at:
        try:
            query = query.filter(ImportJob.created_at >= datetime.fromisoformat(start_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid start_at format") from exc
    if end_at:
        try:
            query = query.filter(ImportJob.created_at <= datetime.fromisoformat(end_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid end_at format") from exc
    total = query.count()
    if cursor_id is not None:
        query = query.filter(ImportJob.id < cursor_id)
    query = query.order_by(ImportJob.id.desc())
    items = query.offset(skip).limit(limit).all()
    next_cursor = items[-1].id if items else None
    return ImportJobListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/import/jobs/{job_id}", response_model=ImportJobOut)
def get_import_job(job_id: int, db: Session = Depends(get_db)) -> ImportJobOut:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/import/jobs/{job_id}/export")
def export_import_job(job_id: int, db: Session = Depends(get_db)) -> dict:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "entity_type": job.entity_type,
        "mode": job.mode,
        "atomic": job.atomic,
        "summary": job.summary,
        "error_summary": job.error_summary,
        "error_details": job.error_details,
    }


@router.post("/import/jobs/{job_id}/retry", response_model=ImportJobOut)
def retry_import_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ImportJobOut:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.payload:
        raise HTTPException(status_code=400, detail="No payload available for retry")
    payload = ImportExecuteRequest(**job.payload)
    new_job = ImportJob(
        status="queued",
        entity_type=job.entity_type,
        mode=job.mode,
        atomic=job.atomic,
        filename=job.filename,
        payload=job.payload,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    background_tasks.add_task(_process_import_job, new_job.id, payload, job.filename)
    _log_action(
        db,
        action="import_retry",
        payload={"from_job_id": job.id, "new_job_id": new_job.id},
        entity_type=job.entity_type,
        commit=True,
    )
    return new_job


@router.get("/import/jobs/{job_id}/errors")
def get_import_job_errors(
    job_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> dict:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    details = job.error_details or []
    paged = details[skip : skip + limit]
    return {
        "job_id": job.id,
        "status": job.status,
        "error_summary": job.error_summary or [],
        "error_details": paged,
        "total": len(details),
        "next_offset": skip + limit if skip + limit < len(details) else None,
    }


@router.get("/import/jobs/{job_id}/export.csv")
def export_import_job_csv(job_id: int, db: Session = Depends(get_db)) -> Response:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["job_id", "status", "entity_type", "mode", "atomic"])
    writer.writerow([job.id, job.status, job.entity_type, job.mode, job.atomic])
    writer.writerow([])
    writer.writerow(["summary"])
    writer.writerow([json.dumps(job.summary or {}, ensure_ascii=False)])
    writer.writerow([])
    writer.writerow(["error_summary"])
    writer.writerow([json.dumps(job.error_summary or [], ensure_ascii=False)])
    writer.writerow([])
    writer.writerow(["error_details"])
    writer.writerow(["index", "field", "message"])
    for item in job.error_details or []:
        writer.writerow([item.get("index"), item.get("field"), item.get("message")])
    return Response(content=output.getvalue(), media_type="text/csv")


@router.post("/import/jobs/{job_id}/cancel", response_model=ImportJobOut)
def cancel_import_job(job_id: int, db: Session = Depends(get_db)) -> ImportJobOut:
    job = db.get(ImportJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in {"success", "failed"}:
        raise HTTPException(status_code=400, detail="Job already finished")
    job.status = "cancelled"
    db.add(job)
    db.commit()
    _log_action(
        db,
        action="import_cancel",
        payload={"job_id": job.id},
        entity_type=job.entity_type,
        commit=True,
    )
    return job


@router.post("/media/upload")
async def upload_media(kind: str = Form(...), file: UploadFile = File(...)) -> dict:
    if kind not in {"image", "audio"}:
        raise HTTPException(status_code=400, detail="Unsupported media kind")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    bucket, object_name = upload_bytes(kind, data, file.content_type, file.filename)
    url = presign_get_url(kind, object_name)
    return {
        "bucket": bucket,
        "object_name": object_name,
        "url": url,
        "content_type": file.content_type,
    }


@router.get("/media/presign")
def presign_media_url(kind: str, object_name: str) -> dict:
    if kind not in {"image", "audio"}:
        raise HTTPException(status_code=400, detail="Unsupported media kind")
    url = presign_get_url(kind, object_name)
    return {"url": url}
