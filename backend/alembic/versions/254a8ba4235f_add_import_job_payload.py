"""add_import_job_payload

Revision ID: 254a8ba4235f
Revises: 36151d9de9f9
Create Date: 2026-01-30 19:06:08.646502

"""
from alembic import op
import sqlalchemy as sa


revision = '254a8ba4235f'
down_revision = '36151d9de9f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("import_jobs", sa.Column("payload", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("import_jobs", "payload")
