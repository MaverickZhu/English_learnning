from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

word_tags = Table(
    "word_tags",
    Base.metadata,
    Column("word_id", ForeignKey("words.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

sentence_tags = Table(
    "sentence_tags",
    Base.metadata,
    Column("sentence_id", ForeignKey("sentences.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

passage_tags = Table(
    "passage_tags",
    Base.metadata,
    Column("passage_id", ForeignKey("passages.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

exercise_tags = Table(
    "exercise_tags",
    Base.metadata,
    Column("exercise_id", ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    words = relationship("Word", secondary=word_tags, back_populates="tags")
    sentences = relationship("Sentence", secondary=sentence_tags, back_populates="tags")
    passages = relationship("Passage", secondary=passage_tags, back_populates="tags")
    exercises = relationship("Exercise", secondary=exercise_tags, back_populates="tags")
