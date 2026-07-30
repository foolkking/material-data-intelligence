from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_phase10l2_capability"
down_revision = "0003_phase10l1_intents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "capability_eligibility_resolutions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("resolution_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id"), nullable=False),
        sa.Column("profile_id", sa.String(length=64), nullable=False),
        sa.Column("profile_semantic_hash", sa.String(length=128), nullable=False),
        sa.Column("registry_snapshot_id", sa.String(length=96), nullable=False),
        sa.Column("registry_snapshot_hash", sa.String(length=64), nullable=False),
        sa.Column("resolver_version", sa.String(length=32), nullable=False),
        sa.Column("resolution_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_capability_resolutions_intent", "capability_eligibility_resolutions", ["intent_id"])

    op.create_table(
        "capability_planning_decisions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("decision_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id"), nullable=False),
        sa.Column("resolution_id", sa.String(length=96), sa.ForeignKey("capability_eligibility_resolutions.id"), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_contract_version", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("repair_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("decision_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "outcome in ('PLAN_READY', 'NEEDS_CLARIFICATION', 'UNSUPPORTED', 'CAPABILITY_MISMATCH', 'VALIDATION_FAILED')",
            name="capability_planning_decision_outcome",
        ),
        sa.CheckConstraint("repair_count >= 0 and repair_count <= 1", name="capability_planning_repair_count"),
    )
    op.create_index("idx_capability_decisions_intent", "capability_planning_decisions", ["intent_id"])
    op.create_index("idx_capability_decisions_resolution", "capability_planning_decisions", ["resolution_id"])

    op.create_table(
        "capability_planning_executions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("decision_id", sa.String(length=96), sa.ForeignKey("capability_planning_decisions.id"), nullable=False, unique=True),
        sa.Column("intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False, unique=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("decision_id", "intent_id", "plan_id", "job_id", name="uq_capability_planning_execution"),
    )
    op.create_index("idx_capability_executions_intent", "capability_planning_executions", ["intent_id"])


def downgrade() -> None:
    op.drop_index("idx_capability_executions_intent", table_name="capability_planning_executions")
    op.drop_table("capability_planning_executions")
    op.drop_index("idx_capability_decisions_resolution", table_name="capability_planning_decisions")
    op.drop_index("idx_capability_decisions_intent", table_name="capability_planning_decisions")
    op.drop_table("capability_planning_decisions")
    op.drop_index("idx_capability_resolutions_intent", table_name="capability_eligibility_resolutions")
    op.drop_table("capability_eligibility_resolutions")
