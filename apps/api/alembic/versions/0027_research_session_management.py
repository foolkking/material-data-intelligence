"""Add non-scientific organization and recoverable lifecycle to research sessions."""

from alembic import op
import sqlalchemy as sa


revision = "0027_research_session_management"
down_revision = "0026_scientific_object_trash_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("title_override", sa.String(length=200), nullable=True))
        batch.add_column(
            sa.Column(
                "is_pinned",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch.add_column(sa.Column("pre_trash_status", sa.String(length=32), nullable=True))
        batch.create_check_constraint(
            "research_session_status",
            "status in ('active', 'archived', 'trashed')",
        )
        batch.create_check_constraint(
            "research_session_pre_trash_status",
            "pre_trash_status is null or pre_trash_status in ('active', 'archived')",
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE sessions "
            "SET status = 'active', pre_trash_status = NULL "
            "WHERE status IN ('archived', 'trashed')"
        )
    )
    with op.batch_alter_table("sessions") as batch:
        batch.drop_constraint("research_session_pre_trash_status", type_="check")
        batch.drop_constraint("research_session_status", type_="check")
        batch.drop_column("pre_trash_status")
        batch.drop_column("is_pinned")
        batch.drop_column("title_override")
