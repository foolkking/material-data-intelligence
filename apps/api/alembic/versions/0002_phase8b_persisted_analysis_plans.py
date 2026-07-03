from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_phase8b_persisted_analysis_plans"
down_revision = "0001_phase4_persistence_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_plans",
        sa.Column("id", sa.String(length=96), primary_key=True),
        sa.Column("project_id", sa.String(length=64), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("dataset_id", sa.String(length=64), sa.ForeignKey("datasets.id"), nullable=True),
        sa.Column("profile_id", sa.String(length=64), nullable=True),
        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("plan_source", sa.String(length=64), nullable=False),
        sa.Column("planner_provider", sa.String(length=80), nullable=True),
        sa.Column("analysis_plan_json", sa.JSON(), nullable=False),
        sa.Column("plan_hash", sa.String(length=64), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False),
        sa.Column("created_by", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("validation_status in ('validated', 'rejected')", name="analysis_plan_validation_status"),
    )
    op.create_index("idx_analysis_plans_project_created", "analysis_plans", ["project_id", "created_at"])
    op.create_index("idx_analysis_plans_job", "analysis_plans", ["job_id"])
    op.create_index("idx_analysis_plans_plan_hash", "analysis_plans", ["plan_hash"])

    op.add_column("jobs", sa.Column("plan_id", sa.String(length=96), nullable=True))
    op.create_foreign_key("fk_jobs_plan_id_analysis_plans", "jobs", "analysis_plans", ["plan_id"], ["id"])
    op.create_index("idx_jobs_plan_id", "jobs", ["plan_id"])


def downgrade() -> None:
    op.drop_index("idx_jobs_plan_id", table_name="jobs")
    op.drop_constraint("fk_jobs_plan_id_analysis_plans", "jobs", type_="foreignkey")
    op.drop_column("jobs", "plan_id")

    op.drop_index("idx_analysis_plans_plan_hash", table_name="analysis_plans")
    op.drop_index("idx_analysis_plans_job", table_name="analysis_plans")
    op.drop_index("idx_analysis_plans_project_created", table_name="analysis_plans")
    op.drop_table("analysis_plans")
