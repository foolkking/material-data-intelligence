"""Allow the immutable Agent 2 result projection lifecycle state."""

from alembic import op


revision = "0021_agent2_scientific_result_projection"
down_revision = "0020_agent2_execution_integration"
branch_labels = None
depends_on = None


_STATUSES = "'RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'CANCELING', 'RESULT_PENDING', 'RESULT_READY', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED'"


def upgrade() -> None:
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint("ck_rt_status", f"status in ({_STATUSES})")


def downgrade() -> None:
    with op.batch_alter_table("research_turns") as batch:
        batch.drop_constraint("ck_rt_status", type_="check")
        batch.create_check_constraint(
            "ck_rt_status",
            "status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'CANCELING', 'RESULT_PENDING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')",
        )
