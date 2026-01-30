"""add_fts_indexes

Revision ID: 4ca7b797f210
Revises: 26a4e7fc7012
Create Date: 2026-01-30 18:43:53.853759

"""
from alembic import op
import sqlalchemy as sa


revision = '4ca7b797f210'
down_revision = '26a4e7fc7012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS words_fts_idx
        ON words
        USING GIN (
            to_tsvector(
                'simple',
                coalesce("text", '') || ' ' || coalesce(meaning, '') || ' ' || coalesce(example, '')
            )
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS sentences_fts_idx
        ON sentences
        USING GIN (
            to_tsvector(
                'simple',
                coalesce("text", '') || ' ' || coalesce(meaning, '')
            )
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS passages_fts_idx
        ON passages
        USING GIN (
            to_tsvector(
                'simple',
                coalesce(title, '') || ' ' || coalesce(content, '') || ' ' || coalesce(summary, '')
            )
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS exercises_fts_idx
        ON exercises
        USING GIN (
            to_tsvector(
                'simple',
                coalesce(prompt, '') || ' ' || coalesce(answer, '') || ' ' || coalesce(explanation, '')
            )
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS exercises_fts_idx;")
    op.execute("DROP INDEX IF EXISTS passages_fts_idx;")
    op.execute("DROP INDEX IF EXISTS sentences_fts_idx;")
    op.execute("DROP INDEX IF EXISTS words_fts_idx;")
