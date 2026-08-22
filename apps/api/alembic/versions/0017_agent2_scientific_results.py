"""Agent 2.0 deterministic scientific result projection snapshots."""

from alembic import op
import sqlalchemy as sa


revision = "0017_agent2_scientific_results"
down_revision = "0016_agent2_research_turns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scientific_result_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("research_turn_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("schema_version", sa.String(length=32), nullable=False),
        sa.Column("projection_version", sa.String(length=64), nullable=False),
        sa.Column("execution_status", sa.String(length=32), nullable=False),
        sa.Column("relevance_status", sa.String(length=32), nullable=False),
        sa.Column("source_fingerprint", sa.String(length=128), nullable=False),
        sa.Column("bundle_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("execution_status in ('SUCCESS', 'PARTIAL', 'FAILED')", name="ck_srs_execution_status"),
        sa.CheckConstraint("relevance_status in ('CURRENT', 'STALE', 'SOURCE_MISSING', 'INVALIDATED')", name="ck_srs_relevance_status"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_srs_project", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["research_turn_id"], ["research_turns.id"], name="fk_srs_turn", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], name="fk_srs_job", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_scientific_result_snapshots"),
        sa.UniqueConstraint("research_turn_id", "projection_version", "source_fingerprint", name="uq_scientific_result_snapshot_projection"),
    )
    op.create_index("idx_scientific_result_snapshots_turn", "scientific_result_snapshots", ["research_turn_id"])
    op.create_index("idx_scientific_result_snapshots_job", "scientific_result_snapshots", ["job_id"])
    op.create_index("idx_scientific_result_snapshots_project_created", "scientific_result_snapshots", ["project_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_scientific_result_snapshots_project_created", table_name="scientific_result_snapshots")
    op.drop_index("idx_scientific_result_snapshots_job", table_name="scientific_result_snapshots")
    op.drop_index("idx_scientific_result_snapshots_turn", table_name="scientific_result_snapshots")
    op.drop_table("scientific_result_snapshots")
