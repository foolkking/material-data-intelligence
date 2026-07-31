from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_phase10l4_interpretation"
down_revision = "0005_phase10l3_dependency"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scientific_evidence_bundles",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("bundle_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=16), nullable=False),
        sa.Column("execution_outcome", sa.String(length=32), nullable=False),
        sa.Column("evidence_item_count", sa.Integer(), nullable=False),
        sa.Column("warning_count", sa.Integer(), nullable=False),
        sa.Column("limitation_count", sa.Integer(), nullable=False),
        sa.Column("bundle_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("evidence_item_count >= 0 and evidence_item_count <= 256", name="scientific_evidence_item_count"),
    )
    op.create_index("idx_scientific_evidence_job", "scientific_evidence_bundles", ["job_id"])

    op.create_table(
        "scientific_interpretation_runs",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("execution_record_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("bundle_id", sa.String(length=96), sa.ForeignKey("scientific_evidence_bundles.id"), nullable=False),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("provider_model", sa.String(length=128), nullable=True),
        sa.Column("provider_config_hash", sa.String(length=64), nullable=True),
        sa.Column("idempotency_key_hash", sa.String(length=64), nullable=True),
        sa.Column("repair_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("outcome", sa.String(length=48), nullable=False),
        sa.Column("interpretation_id", sa.String(length=96), nullable=True, unique=True),
        sa.Column("execution_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("repair_count >= 0 and repair_count <= 1", name="scientific_interpretation_run_repair_count"),
        sa.UniqueConstraint("job_id", "mode", "idempotency_key_hash", name="uq_scientific_interpretation_run_idempotency"),
    )
    op.create_index("idx_scientific_interpretation_runs_job", "scientific_interpretation_runs", ["job_id"])

    op.create_table(
        "scientific_interpretations",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("interpretation_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("bundle_id", sa.String(length=96), sa.ForeignKey("scientific_evidence_bundles.id"), nullable=False),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("repair_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("outcome", sa.String(length=48), nullable=False),
        sa.Column("execution_record_id", sa.String(length=96), sa.ForeignKey("scientific_interpretation_runs.id"), nullable=False, unique=True),
        sa.Column("interpretation_json", sa.JSON(), nullable=False),
        sa.Column("execution_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("repair_count >= 0 and repair_count <= 1", name="scientific_interpretation_repair_count"),
    )
    op.create_index("idx_scientific_interpretations_job", "scientific_interpretations", ["job_id"])
    op.create_index("idx_scientific_interpretations_bundle", "scientific_interpretations", ["bundle_id"])

    op.create_table(
        "scientific_interpretation_claims",
        sa.Column("interpretation_id", sa.String(length=96), sa.ForeignKey("scientific_interpretations.id"), primary_key=True),
        sa.Column("claim_id", sa.String(length=96), primary_key=True),
        sa.Column("claim_type", sa.String(length=40), nullable=False),
        sa.Column("predicate", sa.String(length=64), nullable=False),
        sa.Column("confidence_class", sa.String(length=24), nullable=False),
        sa.Column("grounding_status", sa.String(length=24), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("claim_json", sa.JSON(), nullable=False),
    )

    op.create_table(
        "scientific_interpretation_evidence_links",
        sa.Column("interpretation_id", sa.String(length=96), sa.ForeignKey("scientific_interpretations.id"), primary_key=True),
        sa.Column("claim_id", sa.String(length=96), primary_key=True),
        sa.Column("evidence_item_id", sa.String(length=96), primary_key=True),
        sa.Column("role", sa.String(length=24), primary_key=True),
        sa.Column("source_artifact_id", sa.String(length=96), sa.ForeignKey("artifacts.id"), nullable=False),
        sa.Column("source_artifact_hash", sa.String(length=64), nullable=False),
        sa.Column("field_locator_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("scientific_interpretation_evidence_links")
    op.drop_table("scientific_interpretation_claims")
    op.drop_index("idx_scientific_interpretations_bundle", table_name="scientific_interpretations")
    op.drop_index("idx_scientific_interpretations_job", table_name="scientific_interpretations")
    op.drop_table("scientific_interpretations")
    op.drop_index("idx_scientific_interpretation_runs_job", table_name="scientific_interpretation_runs")
    op.drop_table("scientific_interpretation_runs")
    op.drop_index("idx_scientific_evidence_job", table_name="scientific_evidence_bundles")
    op.drop_table("scientific_evidence_bundles")
