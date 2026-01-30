from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class WrongItem(Base):
    __tablename__ = "wrong_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_wrong_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
