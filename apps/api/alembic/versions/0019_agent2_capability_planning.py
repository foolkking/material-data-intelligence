"""Agent 2.0 deterministic capability resolution and planning evidence."""

from alembic import op
import sqlalchemy as sa


revision = "0019_agent2_capability_planning"
down_revision = "0018_agent2_orchestration_decisions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint(
            "ck_rt_status",
            "status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')",
        )
    op.create_table(
        "research_capability_resolutions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("contract_version", sa.String(length=32), nullable=False),
        sa.Column("requirement_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("resolution_json", sa.JSON(), nullable=False),
        sa.Column("registry_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("resolver_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["research_turn_id"], ["research_turns.id"], name="fk_rcr_turn", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_research_capability_resolutions"),
        sa.UniqueConstraint("research_turn_id", name="uq_research_capability_resolutions_turn"),
    )
    op.create_index("idx_research_capability_resolutions_fingerprint", "research_capability_resolutions", ["registry_fingerprint"])

    op.create_table(
        "research_capability_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("capability_resolution_id", sa.Uuid(), nullable=False),
        sa.Column("contract_version", sa.String(length=32), nullable=False),
        sa.Column("plan_json", sa.JSON(), nullable=False),
        sa.Column("input_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("planner_mode", sa.String(length=16), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("provider_request_id", sa.String(length=128), nullable=True),
        sa.Column("repair_attempted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["research_turn_id"], ["research_turns.id"], name="fk_rcp_turn", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["capability_resolution_id"], ["research_capability_resolutions.id"], name="fk_rcp_resolution", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_research_capability_plans"),
        sa.UniqueConstraint("research_turn_id", name="uq_research_capability_plans_turn"),
        sa.CheckConstraint("planner_mode in ('DETERMINISTIC', 'LLM')", name="ck_rcp_planner_mode"),
        sa.CheckConstraint("validation_status = 'VALIDATED'", name="ck_rcp_validation"),
    )
    op.create_index("idx_research_capability_plans_resolution", "research_capability_plans", ["capability_resolution_id"])
    op.create_index("idx_research_capability_plans_fingerprint", "research_capability_plans", ["input_fingerprint"])


def downgrade() -> None:
    op.drop_index("idx_research_capability_plans_fingerprint", table_name="research_capability_plans")
    op.drop_index("idx_research_capability_plans_resolution", table_name="research_capability_plans")
    op.drop_table("research_capability_plans")
    op.drop_index("idx_research_capability_resolutions_fingerprint", table_name="research_capability_resolutions")
    op.drop_table("research_capability_resolutions")
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint(
            "ck_rt_status",
            "status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')",
        )
