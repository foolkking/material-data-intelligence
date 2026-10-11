"""Explicit platform model publication and user plan entitlements."""
from alembic import op
import sqlalchemy as sa

revision = "0037_platform_model_offerings"
down_revision = "0036_user_model_settings"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "platform_model_offerings",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("provider", sa.String(64), sa.ForeignKey("provider_connections.provider", ondelete="CASCADE"), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("protocol", sa.String(32), nullable=False),
        sa.Column("audience", sa.String(16), nullable=False),
        sa.Column("plans_json", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.CheckConstraint("audience in ('all', 'plans')", name="platform_model_audience"),
    )
    op.create_table(
        "user_model_plan_grants",
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("plan", sa.String(64), primary_key=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("user_model_plan_grants")
    op.drop_table("platform_model_offerings")
