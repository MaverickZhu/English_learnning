from sqlalchemy import Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ExamConfig(Base):
    __tablename__ = "exam_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    distribution: Mapped[dict] = mapped_column(JSON, nullable=False)
