"""Add immutable Agent2 scientific report snapshots on the existing Report authority."""

from alembic import op
import sqlalchemy as sa


revision = "0024_agent2_scientific_reports"
down_revision = "0023_agent2_research_memory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent2_scientific_report_generations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), sa.ForeignKey("research_turns.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("requested_by", sa.String(64), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_summary", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status in ('REQUESTED', 'COMPOSING', 'READY', 'FAILED')", name="ck_agent2_report_generation_status"),
    )
    op.create_index("idx_agent2_report_generations_project_created", "agent2_scientific_report_generations", ["project_id", "created_at"])
    op.create_index("idx_agent2_report_generations_status_updated", "agent2_scientific_report_generations", ["status", "updated_at"])
    op.create_table(
        "agent2_scientific_report_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("report_id", sa.String(96), sa.ForeignKey("reports.id", ondelete="RESTRICT"), nullable=False, unique=True),
        sa.Column("project_id", sa.String(64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("research_session_id", sa.String(64), sa.ForeignKey("sessions.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("research_turn_id", sa.Uuid(), sa.ForeignKey("research_turns.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("scientific_result_snapshot_id", sa.Uuid(), sa.ForeignKey("scientific_result_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("scientific_interpretation_id", sa.Uuid(), sa.ForeignKey("agent2_scientific_interpretations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("contract_version", sa.String(32), nullable=False),
        sa.Column("composer_version", sa.String(64), nullable=False),
        sa.Column("prompt_version", sa.String(64), nullable=False),
        sa.Column("source_fingerprint", sa.String(128), nullable=False),
        sa.Column("relevance_at_generation", sa.String(32), nullable=False),
        sa.Column("grounding_status", sa.String(32), nullable=False),
        sa.Column("report_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(64), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("research_turn_id", "source_fingerprint", name="uq_agent2_report_turn_fingerprint"),
        sa.CheckConstraint("grounding_status = 'VALID'", name="ck_agent2_report_grounding"),
        sa.CheckConstraint("relevance_at_generation in ('CURRENT', 'STALE', 'SOURCE_MISSING', 'INVALIDATED')", name="ck_agent2_report_relevance"),
    )
    op.create_index("idx_agent2_report_snapshots_project_created", "agent2_scientific_report_snapshots", ["project_id", "created_at"])
    op.create_index("idx_agent2_report_snapshots_turn", "agent2_scientific_report_snapshots", ["research_turn_id"])
    op.create_index("idx_agent2_report_snapshots_result", "agent2_scientific_report_snapshots", ["scientific_result_snapshot_id"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    indexes = {item["name"] for table in tables for item in inspector.get_indexes(table)}
    if "agent2_scientific_report_snapshots" in tables:
        for name in ("idx_agent2_report_snapshots_result", "idx_agent2_report_snapshots_turn", "idx_agent2_report_snapshots_project_created"):
            if name in indexes:
                op.drop_index(name, table_name="agent2_scientific_report_snapshots")
        op.drop_table("agent2_scientific_report_snapshots")
    if "agent2_scientific_report_generations" in tables:
        for name in ("idx_agent2_report_generations_status_updated", "idx_agent2_report_generations_project_created"):
            if name in indexes:
                op.drop_index(name, table_name="agent2_scientific_report_generations")
        op.drop_table("agent2_scientific_report_generations")
