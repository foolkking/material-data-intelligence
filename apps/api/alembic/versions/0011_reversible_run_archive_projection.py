"""Add the existing project configuration document used by reversible run visibility."""

from alembic import op
import sqlalchemy as sa


revision = "0011_reversible_run_archive_projection"
down_revision = "0010_product_research_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alembic's default PostgreSQL version table is VARCHAR(32), while the
    # post-release migration identifiers are descriptive and longer. Expand
    # it before this revision is recorded; SQLite does not enforce VARCHAR
    # length and keeps the baseline-compatible path.
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column("alembic_version", "version_num", type_=sa.String(64), existing_type=sa.String(32), existing_nullable=False)
    op.create_table(
        "project_configs",
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id"), primary_key=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    # This table contains only reversible presentation metadata. No scientific
    # record is removed when an older schema is selected.
    op.drop_table("project_configs")
