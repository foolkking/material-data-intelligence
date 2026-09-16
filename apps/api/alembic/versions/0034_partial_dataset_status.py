"""Allow durable datasets to disclose independent partial admission.

Revision ID: 0034_partial_dataset_status
Revises: 0033_scientific_knowledge
"""

from alembic import op


revision = "0034_partial_dataset_status"
down_revision = "0033_scientific_knowledge"
branch_labels = None
depends_on = None


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
    with op.batch_alter_table("datasets", recreate="always") as batch:
        batch.drop_constraint("dataset_status", type_="check")
        batch.create_check_constraint(
            "dataset_status",
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
    with op.batch_alter_table("datasets", recreate="always") as batch:
        batch.drop_constraint("dataset_status", type_="check")
        batch.create_check_constraint(
            "dataset_status",
            "status in ('created', 'uploading', 'profile_ready', 'failed', 'archived')",
        )
