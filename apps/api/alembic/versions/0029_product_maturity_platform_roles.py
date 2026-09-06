"""Add the bounded platform role authority used by global administration.

Revision ID: 0029_product_maturity_platform_roles
Revises: 0028_foundation_schema_reconciliation
"""

from alembic import op
import sqlalchemy as sa


revision = "0029_product_maturity_platform_roles"
down_revision = "0028_foundation_schema_reconciliation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column(
                "platform_role",
                sa.String(length=32),
                nullable=False,
                server_default="USER",
            )
        )
        batch.create_check_constraint(
            "platform_role",
            "platform_role in ('USER', 'PLATFORM_ADMIN')",
        )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("platform_role", type_="check")
        batch.drop_column("platform_role")
