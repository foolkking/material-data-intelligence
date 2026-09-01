"""Add recoverable trash lifecycle for scientific objects."""

from alembic import op
import sqlalchemy as sa


revision = "0026_scientific_object_trash_lifecycle"
down_revision = "0025_agent2_scientific_selection"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("scientific_objects") as batch:
        batch.add_column(sa.Column("pre_trash_lifecycle_status", sa.String(length=32), nullable=True))
        batch.drop_constraint("ck_so_lifecycle", type_="check")
        batch.create_check_constraint(
            "ck_so_lifecycle",
            "lifecycle_status in ('ACTIVE', 'ARCHIVED', 'TRASHED', 'INVALIDATED')",
        )
        batch.create_check_constraint(
            "ck_so_pre_trash_lifecycle",
            "pre_trash_lifecycle_status is null or pre_trash_lifecycle_status in ('ACTIVE', 'ARCHIVED')",
        )


def downgrade() -> None:
    # A downgrade must remain recoverable even if qualification data contains
    # trashed objects. Restore them to the safe active state before narrowing
    # the released check constraint.
    op.execute(
        sa.text(
            "UPDATE scientific_objects "
            "SET lifecycle_status = 'ACTIVE', pre_trash_lifecycle_status = NULL "
            "WHERE lifecycle_status = 'TRASHED'"
        )
    )
    with op.batch_alter_table("scientific_objects") as batch:
        batch.drop_constraint("ck_so_pre_trash_lifecycle", type_="check")
        batch.drop_constraint("ck_so_lifecycle", type_="check")
        batch.create_check_constraint(
            "ck_so_lifecycle",
            "lifecycle_status in ('ACTIVE', 'ARCHIVED', 'INVALIDATED')",
        )
        batch.drop_column("pre_trash_lifecycle_status")
