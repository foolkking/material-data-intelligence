"""Create durable research sessions and messages."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_product_research_sessions"
down_revision = "0009_product_research_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=True),
        sa.Column("mode", sa.String(length=32), nullable=False, server_default="auto"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_sessions_project_created", "sessions", ["project_id", "created_at"])
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("session_id", sa.String(length=64), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content_summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role in ('user', 'system', 'agent')", name="message_role"),
    )
    op.create_index("idx_messages_session_created", "messages", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_messages_session_created", table_name="messages")
    op.drop_table("messages")
    op.drop_index("idx_sessions_project_created", table_name="sessions")
    op.drop_table("sessions")
