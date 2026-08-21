"""Allow one immutable intent/decision contract to back multiple runs."""

from alembic import op
import sqlalchemy as sa


revision = "0012_reusable_planning_execution_bindings"
down_revision = "0011_reversible_run_archive_projection"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "capability_planning_executions" not in sa.inspect(op.get_bind()).get_table_names():
        return
    # The old schema accidentally made decision_id unique.  A decision is a
    # validated reusable contract; each plan/job execution remains unique.
    with op.batch_alter_table("capability_planning_executions", recreate="always") as batch:
        batch.alter_column("decision_id", existing_type=sa.String(length=96), unique=False)


def downgrade() -> None:
    if "capability_planning_executions" not in sa.inspect(op.get_bind()).get_table_names():
        return
    # Downgrade is only valid when the table contains at most one execution per
    # decision.  Alembic will surface a database constraint error otherwise.
    with op.batch_alter_table("capability_planning_executions", recreate="always") as batch:
        batch.alter_column("decision_id", existing_type=sa.String(length=96), unique=True)
