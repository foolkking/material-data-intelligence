from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_phase10m1_workspace_domain"
down_revision = "0006_phase10l4_interpretation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scientific_workspaces",
        sa.Column("workspace_id", sa.String(length=96), primary_key=True),
        sa.Column("schema_version", sa.String(length=16), nullable=False),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_job_id", sa.String(length=64), sa.ForeignKey("jobs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_reference_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("dataset_version", sa.String(length=128), nullable=True),
        sa.Column("profile_id", sa.String(length=64), sa.ForeignKey("data_profiles.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("profile_semantic_hash", sa.String(length=64), nullable=True),
        sa.Column("intent_id", sa.String(length=96), sa.ForeignKey("analysis_intents.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("intent_semantic_hash", sa.String(length=64), nullable=True),
        sa.Column("plan_id", sa.String(length=96), sa.ForeignKey("analysis_plans.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("plan_hash", sa.String(length=64), nullable=True),
        sa.Column("plan_schema_version", sa.String(length=16), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("active_panel_id", sa.String(length=64), nullable=True),
        sa.Column("pinned_selection_json", sa.JSON(), nullable=True),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("project_id", "source_job_id", name="uq_scientific_workspaces_project_job"),
        sa.CheckConstraint("revision >= 0", name="scientific_workspace_revision_non_negative"),
    )
    op.create_index(
        "idx_workspaces_project_updated",
        "scientific_workspaces",
        ["project_id", "updated_at"],
    )
    op.create_index("idx_workspaces_source_job", "scientific_workspaces", ["source_job_id"])

    op.create_table(
        "workspace_panels",
        sa.Column(
            "workspace_id",
            sa.String(length=96),
            sa.ForeignKey("scientific_workspaces.workspace_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("panel_id", sa.String(length=64), primary_key=True),
        sa.Column("panel_kind", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("ordinal", sa.SmallInteger(), nullable=False),
        sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("source_refs_json", sa.JSON(), nullable=False),
        sa.Column("renderer_contract", sa.String(length=128), nullable=False),
        sa.Column("accepted_selection_kinds_json", sa.JSON(), nullable=False),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("panel_state_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("ordinal >= 0", name="workspace_panel_ordinal_non_negative"),
    )
    op.create_index("idx_workspace_panels_order", "workspace_panels", ["workspace_id", "ordinal"])

    op.create_table(
        "workspace_layout_revisions",
        sa.Column(
            "workspace_id",
            sa.String(length=96),
            sa.ForeignKey("scientific_workspaces.workspace_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("revision", sa.Integer(), primary_key=True),
        sa.Column("layout_json", sa.JSON(), nullable=False),
        sa.Column("selection_json", sa.JSON(), nullable=True),
        sa.Column("semantic_hash", sa.String(length=64), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("workspace_id", "semantic_hash", name="uq_workspace_layout_semantic_hash"),
        sa.CheckConstraint("revision >= 0", name="workspace_layout_revision_non_negative"),
    )


def downgrade() -> None:
    op.drop_table("workspace_layout_revisions")
    op.drop_index("idx_workspace_panels_order", table_name="workspace_panels")
    op.drop_table("workspace_panels")
    op.drop_index("idx_workspaces_source_job", table_name="scientific_workspaces")
    op.drop_index("idx_workspaces_project_updated", table_name="scientific_workspaces")
    op.drop_table("scientific_workspaces")
