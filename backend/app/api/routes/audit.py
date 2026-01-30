from datetime import datetime
import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.deps import admin_auth, get_db
from app.models.audit_log import AdminAuditLog
from app.schemas.audit import AuditLogListResponse

router = APIRouter(prefix="/admin/audit", dependencies=[Depends(admin_auth)])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    skip: int = 0,
    limit: int = 20,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    cursor_id: int | None = None,
    db: Session = Depends(get_db),
) -> AuditLogListResponse:
    query = db.query(AdminAuditLog)
    if action:
        query = query.filter(AdminAuditLog.action == action)
    if entity_type:
        query = query.filter(AdminAuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AdminAuditLog.entity_id == entity_id)
    if start_at:
        try:
            query = query.filter(AdminAuditLog.created_at >= datetime.fromisoformat(start_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid start_at format") from exc
    if end_at:
        try:
            query = query.filter(AdminAuditLog.created_at <= datetime.fromisoformat(end_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid end_at format") from exc
    total = query.count()
    if cursor_id is not None:
        query = query.filter(AdminAuditLog.id < cursor_id)
    sort_map = {
        "id": AdminAuditLog.id,
        "created_at": AdminAuditLog.created_at,
        "action": AdminAuditLog.action,
    }
    sort_column = sort_map.get(sort_by or "id", AdminAuditLog.id)
    if sort_order and sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    items = query.offset(skip).limit(limit).all()
    next_cursor = items[-1].id if items else None
    return AuditLogListResponse(total=total, items=items, next_cursor=next_cursor)


@router.get("/export")
def export_audit_logs(
    limit: int = 1000,
    offset: int = 0,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    start_at: str | None = None,
    end_at: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    db: Session = Depends(get_db),
) -> Response:
    query = db.query(AdminAuditLog)
    if action:
        query = query.filter(AdminAuditLog.action == action)
    if entity_type:
        query = query.filter(AdminAuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AdminAuditLog.entity_id == entity_id)
    if start_at:
        try:
            query = query.filter(AdminAuditLog.created_at >= datetime.fromisoformat(start_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid start_at format") from exc
    if end_at:
        try:
            query = query.filter(AdminAuditLog.created_at <= datetime.fromisoformat(end_at))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid end_at format") from exc
    sort_map = {
        "id": AdminAuditLog.id,
        "created_at": AdminAuditLog.created_at,
        "action": AdminAuditLog.action,
    }
    sort_column = sort_map.get(sort_by or "id", AdminAuditLog.id)
    if sort_order and sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    items = query.offset(offset).limit(limit).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "action", "entity_type", "entity_id", "created_at", "payload"])
    for item in items:
        writer.writerow(
            [
                item.id,
                item.action,
                item.entity_type or "",
                item.entity_id or "",
                item.created_at.isoformat() if item.created_at else "",
                json.dumps(item.payload, ensure_ascii=False) if item.payload else "",
            ]
        )
    return Response(content=output.getvalue(), media_type="text/csv")
