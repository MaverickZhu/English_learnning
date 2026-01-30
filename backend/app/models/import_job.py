from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    atomic: Mapped[bool] = mapped_column(nullable=False, default=False)
    filename: Mapped[str | None] = mapped_column(String(256), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    finished_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
