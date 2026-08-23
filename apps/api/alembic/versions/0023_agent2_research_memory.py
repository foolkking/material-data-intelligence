"""Persist bounded, auditable Agent2 ResearchSession memory."""

from alembic import op
import sqlalchemy as sa


revision = "0023_agent2_research_memory"
down_revision = "0022_agent2_scientific_interpretation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_session_states",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.String(64), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("active_scope_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("active_selection_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pinned_object_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pinned_result_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("session_constraints_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("active_research_goal", sa.Text(), nullable=True),
        sa.Column("open_questions_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("version >= 1", name="ck_rss_version"),
    )
    op.create_table(
        "research_session_context_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("session_id", sa.String(64), sa.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("item_type", sa.String(32), nullable=False),
        sa.Column("scope", sa.String(16), nullable=False),
        sa.Column("ref_json", sa.JSON(), nullable=True),
        sa.Column("statement", sa.Text(), nullable=True),
        sa.Column("structured_constraint_json", sa.JSON(), nullable=True),
        sa.Column("source_message_id", sa.String(64), sa.ForeignKey("messages.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("explicitly_requested", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("scope in ('TURN', 'SESSION')", name="ck_rsci_scope"),
        sa.CheckConstraint("item_type in ('ACTIVE_SCOPE', 'ACTIVE_SELECTION', 'PINNED_OBJECT', 'PINNED_RESULT', 'SESSION_CONSTRAINT', 'RESEARCH_GOAL', 'OPEN_QUESTION', 'PRIOR_FINDING')", name="ck_rsci_item_type"),
    )
    op.create_index("idx_rsci_session_active", "research_session_context_items", ["session_id", "active", "item_type"])


def downgrade() -> None:
    op.drop_index("idx_rsci_session_active", table_name="research_session_context_items")
    op.drop_table("research_session_context_items")
    op.drop_table("research_session_states")
