"""Additional personal connections; the original personal identity is preserved."""

from alembic import op
import sqlalchemy as sa

revision = "0038_user_model_connections"
down_revision = "0037_platform_model_offerings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_model_connections",
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("label", sa.String(120), nullable=False, server_default=""),
        sa.Column("protocol", sa.String(32), nullable=False, server_default="openai_chat_json"),
        sa.Column("base_url", sa.String(512), nullable=False, server_default=""),
        sa.Column("encrypted_api_key", sa.Text(), nullable=False, server_default=""),
        sa.Column("catalog_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("selected_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("user_model_connections")
