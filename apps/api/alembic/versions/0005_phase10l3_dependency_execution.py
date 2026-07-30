from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_phase10l3_dependency"
down_revision = "0004_phase10l2_capability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plan_dependency_bindings",
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), primary_key=True),
        sa.Column("binding_id", sa.String(length=96), primary_key=True),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("graph_hash", sa.String(length=64), nullable=False),
        sa.Column("producer_step_id", sa.String(length=96), nullable=False),
        sa.Column("producer_output_port", sa.String(length=96), nullable=False),
        sa.Column("consumer_step_id", sa.String(length=96), nullable=False),
        sa.Column("consumer_input_port", sa.String(length=96), nullable=False),
        sa.Column("artifact_kind", sa.String(length=64), nullable=False),
        sa.Column("artifact_contract_version", sa.String(length=128), nullable=False),
        sa.Column("media_type", sa.String(length=128), nullable=False),
        sa.Column("cardinality", sa.String(length=32), nullable=False),
        sa.Column("binding_json", sa.JSON(), nullable=False),
        sa.Column("semantic_record_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("plan_id", "consumer_step_id", "consumer_input_port", name="uq_plan_binding_consumer_port"),
    )
    op.create_index("idx_plan_dependency_bindings_plan", "plan_dependency_bindings", ["plan_id"])
    op.create_index("idx_plan_dependency_bindings_graph", "plan_dependency_bindings", ["graph_hash"])

    op.create_table(
        "dependency_execution_records",
        sa.Column("execution_id", sa.String(length=96), primary_key=True),
        sa.Column("execution_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False, unique=True),
        sa.Column("graph_hash", sa.String(length=64), nullable=False),
        sa.Column("outcome", sa.String(length=32), nullable=False),
        sa.Column("record_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "outcome in ('ALL_SUCCEEDED', 'PARTIAL_RESULTS', 'ALL_FAILED', 'VALIDATION_ABORTED')",
            name="dependency_execution_outcome",
        ),
    )
    op.create_index("idx_dependency_execution_plan", "dependency_execution_records", ["plan_id"])
    op.create_index("idx_dependency_execution_job", "dependency_execution_records", ["job_id"])

    op.create_table(
        "runtime_artifact_binding_resolutions",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("record_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("binding_id", sa.String(length=96), nullable=False),
        sa.Column("producer_tool_call_id", sa.String(length=64), sa.ForeignKey("tool_calls.id"), nullable=True),
        sa.Column("producer_step_id", sa.String(length=96), nullable=False),
        sa.Column("artifact_id", sa.String(length=96), sa.ForeignKey("artifacts.id"), nullable=True),
        sa.Column("artifact_checksum", sa.String(length=64), nullable=True),
        sa.Column("artifact_kind", sa.String(length=64), nullable=True),
        sa.Column("artifact_contract_version", sa.String(length=128), nullable=True),
        sa.Column("media_type", sa.String(length=128), nullable=True),
        sa.Column("consumer_tool_call_id", sa.String(length=64), sa.ForeignKey("tool_calls.id"), nullable=True),
        sa.Column("consumer_step_id", sa.String(length=96), nullable=False),
        sa.Column("consumer_input_port", sa.String(length=96), nullable=False),
        sa.Column("validation_outcome", sa.String(length=32), nullable=False),
        sa.Column("error_code", sa.String(length=96), nullable=True),
        sa.Column("resolved_ref_json", sa.JSON(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("job_id", "binding_id", name="uq_runtime_binding_job_binding"),
    )
    op.create_index("idx_runtime_binding_job", "runtime_artifact_binding_resolutions", ["job_id"])
    op.create_index("idx_runtime_binding_artifact", "runtime_artifact_binding_resolutions", ["artifact_id"])

    op.create_table(
        "artifact_lineage_records",
        sa.Column("lineage_id", sa.String(length=96), primary_key=True),
        sa.Column("lineage_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("artifact_id", sa.String(length=96), sa.ForeignKey("artifacts.id"), nullable=False, unique=True),
        sa.Column("job_id", sa.String(length=64), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id"), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("graph_hash", sa.String(length=64), nullable=False),
        sa.Column("producer_tool_call_id", sa.String(length=64), sa.ForeignKey("tool_calls.id"), nullable=False),
        sa.Column("producer_step_id", sa.String(length=96), nullable=False),
        sa.Column("output_port", sa.String(length=96), nullable=False),
        sa.Column("record_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_artifact_lineage_job", "artifact_lineage_records", ["job_id"])
    op.create_index("idx_artifact_lineage_plan", "artifact_lineage_records", ["plan_id"])


def downgrade() -> None:
    op.drop_index("idx_artifact_lineage_plan", table_name="artifact_lineage_records")
    op.drop_index("idx_artifact_lineage_job", table_name="artifact_lineage_records")
    op.drop_table("artifact_lineage_records")
    op.drop_index("idx_runtime_binding_artifact", table_name="runtime_artifact_binding_resolutions")
    op.drop_index("idx_runtime_binding_job", table_name="runtime_artifact_binding_resolutions")
    op.drop_table("runtime_artifact_binding_resolutions")
    op.drop_index("idx_dependency_execution_job", table_name="dependency_execution_records")
    op.drop_index("idx_dependency_execution_plan", table_name="dependency_execution_records")
    op.drop_table("dependency_execution_records")
    op.drop_index("idx_plan_dependency_bindings_graph", table_name="plan_dependency_bindings")
    op.drop_index("idx_plan_dependency_bindings_plan", table_name="plan_dependency_bindings")
    op.drop_table("plan_dependency_bindings")
