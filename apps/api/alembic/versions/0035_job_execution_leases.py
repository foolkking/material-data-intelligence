"""Add one durable Job execution ownership authority.

Revision ID: 0035_job_execution_leases
Revises: 0034_partial_dataset_status
"""

from alembic import op
import sqlalchemy as sa


revision = "0035_job_execution_leases"
down_revision = "0034_partial_dataset_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("jobs") as batch:
        batch.add_column(sa.Column("execution_owner", sa.String(length=160), nullable=True))
        batch.add_column(
            sa.Column(
                "execution_attempt",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch.add_column(sa.Column("lease_claimed_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("lease_renewed_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("cancel_requested_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("cancel_acknowledged_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("terminal_at", sa.DateTime(timezone=True), nullable=True))
        batch.create_check_constraint(
            "job_execution_attempt_non_negative",
            "execution_attempt >= 0",
        )
    op.create_index(
        "idx_jobs_execution_lease",
        "jobs",
        ["status", "lease_expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_execution_lease", table_name="jobs")
    with op.batch_alter_table("jobs") as batch:
        batch.drop_constraint("job_execution_attempt_non_negative", type_="check")
        batch.drop_column("terminal_at")
        batch.drop_column("cancel_acknowledged_at")
        batch.drop_column("cancel_requested_at")
        batch.drop_column("lease_expires_at")
        batch.drop_column("lease_renewed_at")
        batch.drop_column("lease_claimed_at")
        batch.drop_column("execution_attempt")
        batch.drop_column("execution_owner")
