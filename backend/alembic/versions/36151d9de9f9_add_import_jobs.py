"""add_import_jobs

Revision ID: 36151d9de9f9
Revises: 2a8cd74838a9
Create Date: 2026-01-30 19:04:36.798346

"""
from alembic import op
import sqlalchemy as sa


revision = '36151d9de9f9'
down_revision = '2a8cd74838a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("atomic", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("filename", sa.String(length=256), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
        sa.Column("error_summary", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_import_jobs_id"), "import_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_import_jobs_status"), "import_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_import_jobs_entity_type"), "import_jobs", ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_import_jobs_entity_type"), table_name="import_jobs")
    op.drop_index(op.f("ix_import_jobs_status"), table_name="import_jobs")
    op.drop_index(op.f("ix_import_jobs_id"), table_name="import_jobs")
    op.drop_table("import_jobs")
