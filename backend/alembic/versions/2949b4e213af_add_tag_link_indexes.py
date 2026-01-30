"""add_tag_link_indexes

Revision ID: 2949b4e213af
Revises: 4ca7b797f210
Create Date: 2026-01-30 18:45:08.532893

"""
from alembic import op
import sqlalchemy as sa


revision = '2949b4e213af'
down_revision = '4ca7b797f210'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("idx_word_tags_tag_id", "word_tags", ["tag_id"], unique=False)
    op.create_index("idx_word_tags_word_id", "word_tags", ["word_id"], unique=False)
    op.create_index("idx_sentence_tags_tag_id", "sentence_tags", ["tag_id"], unique=False)
    op.create_index("idx_sentence_tags_sentence_id", "sentence_tags", ["sentence_id"], unique=False)
    op.create_index("idx_passage_tags_tag_id", "passage_tags", ["tag_id"], unique=False)
    op.create_index("idx_passage_tags_passage_id", "passage_tags", ["passage_id"], unique=False)
    op.create_index("idx_exercise_tags_tag_id", "exercise_tags", ["tag_id"], unique=False)
    op.create_index("idx_exercise_tags_exercise_id", "exercise_tags", ["exercise_id"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_exercise_tags_exercise_id", table_name="exercise_tags")
    op.drop_index("idx_exercise_tags_tag_id", table_name="exercise_tags")
    op.drop_index("idx_passage_tags_passage_id", table_name="passage_tags")
    op.drop_index("idx_passage_tags_tag_id", table_name="passage_tags")
    op.drop_index("idx_sentence_tags_sentence_id", table_name="sentence_tags")
    op.drop_index("idx_sentence_tags_tag_id", table_name="sentence_tags")
    op.drop_index("idx_word_tags_word_id", table_name="word_tags")
    op.drop_index("idx_word_tags_tag_id", table_name="word_tags")
