from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tag import passage_tags


class Passage(Base):
    __tablename__ = "passages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("news_sources.id"), nullable=True, index=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("news_articles.id"), nullable=True, index=True)
    tags = relationship("Tag", secondary=passage_tags, back_populates="passages")
