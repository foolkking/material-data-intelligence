"""Persist exact semantic scientific selections in ResearchContext snapshots."""

from alembic import op
import sqlalchemy as sa


revision = "0025_agent2_scientific_selection"
down_revision = "0024_agent2_scientific_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "research_context_snapshots",
        sa.Column("scientific_selections_json", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("research_context_snapshots", "scientific_selections_json")
