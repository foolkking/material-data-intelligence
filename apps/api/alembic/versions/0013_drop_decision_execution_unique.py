"""Rebuild capability executions without the accidental decision-only unique index."""

from alembic import op
import sqlalchemy as sa


revision = "0013_drop_decision_execution_unique"
down_revision = "0012_reusable_planning_execution_bindings"
branch_labels = None
depends_on = None


def _table() -> sa.Table:
    metadata = sa.MetaData()
    return sa.Table(
        "capability_planning_executions",
        metadata,
        sa.Column("id", sa.String(96), primary_key=True),
        sa.Column("decision_id", sa.String(96), sa.ForeignKey("capability_planning_decisions.id"), nullable=False),
        sa.Column("intent_id", sa.String(96), sa.ForeignKey("analysis_intents.id"), nullable=False),
        sa.Column("plan_id", sa.String(96), sa.ForeignKey("analysis_plans.id"), nullable=False, unique=True),
        sa.Column("job_id", sa.String(64), sa.ForeignKey("jobs.id"), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("decision_id", "intent_id", "plan_id", "job_id", name="uq_capability_planning_execution"),
    )


def upgrade() -> None:
    if "capability_planning_executions" not in sa.inspect(op.get_bind()).get_table_names():
        return
    # copy_from supplies an explicit SQLite rebuild definition, which removes
    # the historical column-level unique index while retaining all rows.
    with op.batch_alter_table(
        "capability_planning_executions", recreate="always", copy_from=_table()
    ):
        pass
    op.create_index(
        "idx_capability_executions_intent",
        "capability_planning_executions",
        ["intent_id"],
    )


def downgrade() -> None:
    if "capability_planning_executions" not in sa.inspect(op.get_bind()).get_table_names():
        return
    with op.batch_alter_table(
        "capability_planning_executions", recreate="always", copy_from=_table()
    ) as batch:
        batch.create_unique_constraint("uq_capability_decision_execution_legacy", ["decision_id"])
    op.create_index(
        "idx_capability_executions_intent",
        "capability_planning_executions",
        ["intent_id"],
    )
