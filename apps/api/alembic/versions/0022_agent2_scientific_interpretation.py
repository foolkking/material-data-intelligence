"""Persist immutable Agent2 grounded interpretation snapshots."""

from alembic import op
import sqlalchemy as sa


revision = "0022_agent2_scientific_interpretation"
down_revision = "0021_agent2_scientific_result_projection"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent2_scientific_interpretations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("research_turn_id", sa.Uuid(), sa.ForeignKey("research_turns.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("result_snapshot_id", sa.Uuid(), sa.ForeignKey("scientific_result_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("contract_version", sa.String(16), nullable=False),
        sa.Column("prompt_version", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("provider_request_id", sa.String(128), nullable=True),
        sa.Column("repair_attempted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("input_fingerprint", sa.String(128), nullable=False),
        sa.Column("grounding_status", sa.String(32), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("grounding_status = 'VALID'", name="ck_agent2_interpretation_grounding"),
    )
    op.create_index("idx_agent2_interpretations_project_created", "agent2_scientific_interpretations", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_agent2_interpretations_project_created", table_name="agent2_scientific_interpretations")
    op.drop_table("agent2_scientific_interpretations")
