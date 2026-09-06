"""Persist encrypted platform Provider connections across API processes.

Revision ID: 0032_provider_connections
Revises: 0031_product_search_keyset
"""

from alembic import op
import sqlalchemy as sa


revision = "0032_provider_connections"
down_revision = "0031_product_search_keyset"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "provider_connections",
        sa.Column("provider", sa.String(length=64), primary_key=True),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("base_url", sa.String(length=512), nullable=False),
        sa.Column(
            "model_ids_json",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("default_model", sa.String(length=256), nullable=True),
        sa.Column("encrypted_api_key", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("provider_connections")
