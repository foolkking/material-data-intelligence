"""Allow durable datasets to disclose independent partial admission.

Revision ID: 0034_partial_dataset_status
Revises: 0033_scientific_knowledge
"""

from alembic import op
import sqlalchemy as sa


revision = "0034_partial_dataset_status"
down_revision = "0033_scientific_knowledge"
branch_labels = None
depends_on = None


def _dataset_status_constraint_name(bind: sa.engine.Connection) -> str | None:
    for constraint in sa.inspect(bind).get_check_constraints("datasets"):
        expression = "".join((constraint.get("sqltext") or "").lower().split())
        if expression.startswith("statusin("):
            name = constraint.get("name")
            return str(name) if name else None
    return None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        # PostgreSQL preserves the explicit constraint name from the
        # foundation migration.  Alembic batch reflection can synthesize a
        # naming-convention alias and then fail to find the real constraint.
        op.execute("ALTER TABLE datasets DROP CONSTRAINT IF EXISTS dataset_status")
        op.create_check_constraint(
            "dataset_status",
            "datasets",
            "status in ('created', 'uploading', 'profile_ready', 'partially_ready', 'failed', 'archived')",
        )
        return
    existing_constraint = _dataset_status_constraint_name(bind)
    with op.batch_alter_table("datasets", recreate="always") as batch:
        if existing_constraint is not None:
            batch.drop_constraint(op.f(existing_constraint), type_="check")
        batch.create_check_constraint(
            op.f("dataset_status"),
            "status in ('created', 'uploading', 'profile_ready', 'partially_ready', 'failed', 'archived')",
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE datasets DROP CONSTRAINT IF EXISTS dataset_status")
        op.create_check_constraint(
            "dataset_status",
            "datasets",
            "status in ('created', 'uploading', 'profile_ready', 'failed', 'archived')",
        )
        return
    existing_constraint = _dataset_status_constraint_name(bind)
    with op.batch_alter_table("datasets", recreate="always") as batch:
        if existing_constraint is not None:
            batch.drop_constraint(op.f(existing_constraint), type_="check")
        batch.create_check_constraint(
            op.f("dataset_status"),
            "status in ('created', 'uploading', 'profile_ready', 'failed', 'archived')",
        )
