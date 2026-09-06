"""Add one-time administrator-issued account invitations.

Revision ID: 0030_account_invitations
Revises: 0029_product_maturity_platform_roles
"""

from alembic import op
import sqlalchemy as sa


revision = "0030_account_invitations"
down_revision = "0029_product_maturity_platform_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account_invitations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invited_by_user_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"], name="fk_account_invitations_invited_by_user_id_users"),
        sa.UniqueConstraint("token_hash", name="uq_account_invitations_token_hash"),
    )
    op.create_index(
        "idx_account_invitations_email_created",
        "account_invitations",
        ["email", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_account_invitations_email_created", table_name="account_invitations")
    op.drop_table("account_invitations")
