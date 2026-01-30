"""add_import_job_error_details

Revision ID: 8410bd99e233
Revises: 254a8ba4235f
Create Date: 2026-01-30 19:08:49.779579

"""
from alembic import op
import sqlalchemy as sa


revision = '8410bd99e233'
down_revision = '254a8ba4235f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("import_jobs", sa.Column("error_details", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("import_jobs", "error_details")
