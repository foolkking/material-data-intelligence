"""Agent 2.0 execution bridge and deterministic execution summaries."""

from alembic import op
import sqlalchemy as sa


revision = "0020_agent2_execution_integration"
down_revision = "0019_agent2_capability_planning"
branch_labels = None
depends_on = None


_STATUSES = "'RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'CANCELING', 'RESULT_PENDING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED'"


def upgrade() -> None:
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint("ck_rt_status", f"status in ({_STATUSES})")
        batch.create_unique_constraint("uq_research_turns_job_id", ["job_id"])

    op.create_table(
        "research_execution_summaries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=False),
        sa.Column("contract_version", sa.String(length=32), nullable=False),
        sa.Column("execution_outcome", sa.String(length=32), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("source_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("projector_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["research_turn_id"], ["research_turns.id"], name="fk_res_turn", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], name="fk_res_job", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_research_execution_summaries"),
        sa.UniqueConstraint("research_turn_id", name="uq_research_execution_summaries_turn"),
        sa.UniqueConstraint("job_id", name="uq_research_execution_summaries_job"),
        sa.CheckConstraint("execution_outcome in ('SUCCESS', 'PARTIAL', 'FAILED', 'CANCELED')", name="ck_res_execution_outcome"),
    )
    op.create_index("idx_research_execution_summaries_turn", "research_execution_summaries", ["research_turn_id"])
    op.create_index("idx_research_execution_summaries_job", "research_execution_summaries", ["job_id"])


def downgrade() -> None:
    op.drop_index("idx_research_execution_summaries_job", table_name="research_execution_summaries")
    op.drop_index("idx_research_execution_summaries_turn", table_name="research_execution_summaries")
    op.drop_table("research_execution_summaries")
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("uq_research_turns_job_id", type_="unique")
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint(
            "ck_rt_status",
            "status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')",
        )
