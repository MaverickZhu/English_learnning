from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tag import word_tags


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    meaning: Mapped[str] = mapped_column(Text, nullable=False)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("news_sources.id"), nullable=True, index=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("news_articles.id"), nullable=True, index=True)
    tags = relationship("Tag", secondary=word_tags, back_populates="words")
