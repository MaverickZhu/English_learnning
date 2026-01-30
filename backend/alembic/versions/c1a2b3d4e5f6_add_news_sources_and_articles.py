"""add_news_sources_and_articles

Revision ID: c1a2b3d4e5f6
Revises: e32a1887daec
Create Date: 2026-01-31 01:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c1a2b3d4e5f6"
down_revision = "e32a1887daec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "news_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("site_url", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_sources_id"), "news_sources", ["id"], unique=False)
    op.create_index(op.f("ix_news_sources_name"), "news_sources", ["name"], unique=True)

    op.create_table(
        "news_articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["source_id"], ["news_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_articles_id"), "news_articles", ["id"], unique=False)
    op.create_index(op.f("ix_news_articles_source_id"), "news_articles", ["source_id"], unique=False)
    op.create_index(op.f("ix_news_articles_url"), "news_articles", ["url"], unique=True)
    op.create_index(op.f("ix_news_articles_content_hash"), "news_articles", ["content_hash"], unique=False)

    op.create_table(
        "news_ingest_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_ingest_jobs_id"), "news_ingest_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_news_ingest_jobs_status"), "news_ingest_jobs", ["status"], unique=False)

    op.add_column("words", sa.Column("source_id", sa.Integer(), nullable=True))
    op.add_column("words", sa.Column("article_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_words_source_id"), "words", ["source_id"], unique=False)
    op.create_index(op.f("ix_words_article_id"), "words", ["article_id"], unique=False)
    op.create_foreign_key("words_source_id_fkey", "words", "news_sources", ["source_id"], ["id"])
    op.create_foreign_key("words_article_id_fkey", "words", "news_articles", ["article_id"], ["id"])

    op.add_column("sentences", sa.Column("source_id", sa.Integer(), nullable=True))
    op.add_column("sentences", sa.Column("article_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_sentences_source_id"), "sentences", ["source_id"], unique=False)
    op.create_index(op.f("ix_sentences_article_id"), "sentences", ["article_id"], unique=False)
    op.create_foreign_key("sentences_source_id_fkey", "sentences", "news_sources", ["source_id"], ["id"])
    op.create_foreign_key("sentences_article_id_fkey", "sentences", "news_articles", ["article_id"], ["id"])

    op.add_column("passages", sa.Column("source_id", sa.Integer(), nullable=True))
    op.add_column("passages", sa.Column("article_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_passages_source_id"), "passages", ["source_id"], unique=False)
    op.create_index(op.f("ix_passages_article_id"), "passages", ["article_id"], unique=False)
    op.create_foreign_key("passages_source_id_fkey", "passages", "news_sources", ["source_id"], ["id"])
    op.create_foreign_key("passages_article_id_fkey", "passages", "news_articles", ["article_id"], ["id"])

    op.add_column("exercises", sa.Column("source_id", sa.Integer(), nullable=True))
    op.add_column("exercises", sa.Column("article_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_exercises_source_id"), "exercises", ["source_id"], unique=False)
    op.create_index(op.f("ix_exercises_article_id"), "exercises", ["article_id"], unique=False)
    op.create_foreign_key("exercises_source_id_fkey", "exercises", "news_sources", ["source_id"], ["id"])
    op.create_foreign_key("exercises_article_id_fkey", "exercises", "news_articles", ["article_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("exercises_article_id_fkey", "exercises", type_="foreignkey")
    op.drop_constraint("exercises_source_id_fkey", "exercises", type_="foreignkey")
    op.drop_index(op.f("ix_exercises_article_id"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_source_id"), table_name="exercises")
    op.drop_column("exercises", "article_id")
    op.drop_column("exercises", "source_id")

    op.drop_constraint("passages_article_id_fkey", "passages", type_="foreignkey")
    op.drop_constraint("passages_source_id_fkey", "passages", type_="foreignkey")
    op.drop_index(op.f("ix_passages_article_id"), table_name="passages")
    op.drop_index(op.f("ix_passages_source_id"), table_name="passages")
    op.drop_column("passages", "article_id")
    op.drop_column("passages", "source_id")

    op.drop_constraint("sentences_article_id_fkey", "sentences", type_="foreignkey")
    op.drop_constraint("sentences_source_id_fkey", "sentences", type_="foreignkey")
    op.drop_index(op.f("ix_sentences_article_id"), table_name="sentences")
    op.drop_index(op.f("ix_sentences_source_id"), table_name="sentences")
    op.drop_column("sentences", "article_id")
    op.drop_column("sentences", "source_id")

    op.drop_constraint("words_article_id_fkey", "words", type_="foreignkey")
    op.drop_constraint("words_source_id_fkey", "words", type_="foreignkey")
    op.drop_index(op.f("ix_words_article_id"), table_name="words")
    op.drop_index(op.f("ix_words_source_id"), table_name="words")
    op.drop_column("words", "article_id")
    op.drop_column("words", "source_id")

    op.drop_index(op.f("ix_news_ingest_jobs_status"), table_name="news_ingest_jobs")
    op.drop_index(op.f("ix_news_ingest_jobs_id"), table_name="news_ingest_jobs")
    op.drop_table("news_ingest_jobs")

    op.drop_index(op.f("ix_news_articles_content_hash"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_url"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_source_id"), table_name="news_articles")
    op.drop_index(op.f("ix_news_articles_id"), table_name="news_articles")
    op.drop_table("news_articles")

    op.drop_index(op.f("ix_news_sources_name"), table_name="news_sources")
    op.drop_index(op.f("ix_news_sources_id"), table_name="news_sources")
    op.drop_table("news_sources")
