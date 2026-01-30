from sqlalchemy import ForeignKey, JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tag import exercise_tags


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exercise_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("news_sources.id"), nullable=True, index=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("news_articles.id"), nullable=True, index=True)
    tags = relationship("Tag", secondary=exercise_tags, back_populates="exercises")
