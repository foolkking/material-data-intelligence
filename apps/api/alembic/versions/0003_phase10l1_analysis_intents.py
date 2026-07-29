from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_phase10l1_intents"
down_revision = "0002_phase8b_plans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_intents",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("profile_id", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=16), nullable=False),
        sa.Column("intent_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("parent_intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id"), nullable=True),
        sa.Column("clarification_round", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("intent_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("outcome in ('READY', 'NEEDS_CLARIFICATION', 'UNSUPPORTED')", name="analysis_intent_outcome"),
        sa.CheckConstraint("clarification_round >= 0 and clarification_round <= 1", name="analysis_intent_round"),
    )
    op.create_index("idx_analysis_intents_dataset_created", "analysis_intents", ["dataset_id", "created_at"])
    op.create_index("idx_analysis_intents_parent", "analysis_intents", ["parent_intent_id"])

    op.create_table(
        "analysis_intent_executions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False, unique=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("intent_id", "plan_id", "job_id", name="uq_intent_execution_binding"),
    )
    op.create_index("idx_intent_executions_intent", "analysis_intent_executions", ["intent_id"])


def downgrade() -> None:
    op.drop_index("idx_intent_executions_intent", table_name="analysis_intent_executions")
    op.drop_table("analysis_intent_executions")
    op.drop_index("idx_analysis_intents_parent", table_name="analysis_intents")
    op.drop_index("idx_analysis_intents_dataset_created", table_name="analysis_intents")
    op.drop_table("analysis_intents")
