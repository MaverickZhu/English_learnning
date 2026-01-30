"""add_admin_audit_logs

Revision ID: 2a8cd74838a9
Revises: 2949b4e213af
Create Date: 2026-01-30 18:55:33.254925

"""
from alembic import op
import sqlalchemy as sa


revision = '2a8cd74838a9'
down_revision = '2949b4e213af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_audit_logs_id"), "admin_audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_action"), "admin_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_entity_type"), "admin_audit_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_admin_audit_logs_entity_id"), "admin_audit_logs", ["entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_audit_logs_entity_id"), table_name="admin_audit_logs")
    op.drop_index(op.f("ix_admin_audit_logs_entity_type"), table_name="admin_audit_logs")
    op.drop_index(op.f("ix_admin_audit_logs_action"), table_name="admin_audit_logs")
    op.drop_index(op.f("ix_admin_audit_logs_id"), table_name="admin_audit_logs")
    op.drop_table("admin_audit_logs")
