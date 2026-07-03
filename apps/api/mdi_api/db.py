from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Float,
    Index,
    Integer,
    JSON,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

users = Table(
    "users",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("email", String(320), nullable=False, unique=True),
    Column("display_name", String(160), nullable=False),
    Column("is_active", Boolean, nullable=False, server_default="true"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

organizations = Table(
    "organizations",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("name", String(160), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

projects = Table(
    "projects",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("organization_id", String(64), ForeignKey("organizations.id"), nullable=False),
    Column("name", String(160), nullable=False),
    Column("description", Text, nullable=False, server_default=""),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("organization_id", "name", name="uq_projects_org_name"),
)

project_members = Table(
    "project_members",
    metadata,
    Column("project_id", String(64), ForeignKey("projects.id"), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id"), primary_key=True),
    Column("role", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("role in ('owner', 'admin', 'researcher', 'viewer')", name="project_member_role"),
)

datasets = Table(
    "datasets",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("name", String(160), nullable=False),
    Column("status", String(32), nullable=False, server_default="created"),
    Column("metadata_json", JSON, nullable=False, server_default="{}"),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("project_id", "name", name="uq_datasets_project_name"),
    CheckConstraint("status in ('created', 'uploading', 'profile_ready', 'failed', 'archived')", name="dataset_status"),
)

files = Table(
    "files",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("file_name", String(255), nullable=False),
    Column("media_type", String(160), nullable=False),
    Column("detected_format", String(64), nullable=False, server_default="unknown"),
    Column("storage_key", Text, nullable=False),
    Column("sha256", String(64), nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("parse_status", String(32), nullable=False, server_default="uploaded"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("size_bytes >= 0", name="file_size_non_negative"),
)

data_profiles = Table(
    "data_profiles",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("version", String(32), nullable=False),
    Column("profile_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("dataset_id", "version", name="uq_data_profiles_dataset_version"),
)

analysis_plans = Table(
    "analysis_plans",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=True),
    Column("profile_id", String(64), nullable=True),
    Column("job_id", String(64), nullable=True),
    Column("plan_source", String(64), nullable=False),
    Column("planner_provider", String(80), nullable=True),
    Column("analysis_plan_json", JSON, nullable=False),
    Column("plan_hash", String(64), nullable=False),
    Column("validation_status", String(32), nullable=False),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("validation_status in ('validated', 'rejected')", name="analysis_plan_validation_status"),
)

field_mappings = Table(
    "field_mappings",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("mapping_json", JSON, nullable=False),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=True),
    Column("mode", String(32), nullable=False, server_default="auto"),
    Column("status", String(32), nullable=False, server_default="active"),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

messages = Table(
    "messages",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False),
    Column("role", String(32), nullable=False),
    Column("content_summary", Text, nullable=False, server_default=""),
    Column("payload_json", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("role in ('user', 'system', 'agent')", name="message_role"),
)

jobs = Table(
    "jobs",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=True),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=True),
    Column("kind", String(64), nullable=False),
    Column("status", String(32), nullable=False, server_default="created"),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "status in ('created', 'queued', 'running', 'partial_success', 'completed', 'failed', 'cancel_requested', 'cancelled')",
        name="job_status",
    ),
)

job_events = Table(
    "job_events",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("seq", Integer, nullable=False),
    Column("event_type", String(80), nullable=False),
    Column("status", String(32), nullable=False),
    Column("message", Text, nullable=False),
    Column("progress", Float, nullable=True),
    Column("payload_json", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("job_id", "seq", name="uq_job_events_job_seq"),
)

tool_calls = Table(
    "tool_calls",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("step_id", String(64), nullable=False),
    Column("tool_id", String(160), nullable=False),
    Column("idempotency_key", String(160), nullable=True),
    Column("attempt", Integer, nullable=False, server_default="1"),
    Column("status", String(32), nullable=False, server_default="planned"),
    Column("params_json", JSON, nullable=False, server_default="{}"),
    Column("error_json", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("job_id", "step_id", name="uq_tool_calls_job_step"),
    UniqueConstraint("job_id", "idempotency_key", name="uq_tool_calls_job_idempotency_key"),
    CheckConstraint("attempt >= 1", name="tool_call_attempt_positive"),
    CheckConstraint("status in ('planned', 'running', 'completed', 'failed', 'skipped')", name="tool_call_status"),
)

artifacts = Table(
    "artifacts",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("tool_call_id", String(64), ForeignKey("tool_calls.id"), nullable=True),
    Column("type", String(64), nullable=False),
    Column("name", String(255), nullable=False),
    Column("version", String(32), nullable=False, server_default="1"),
    Column("storage_key", Text, nullable=False),
    Column("storage_provider", String(32), nullable=False, server_default="local"),
    Column("bucket", String(160), nullable=True),
    Column("preview_key", Text, nullable=True),
    Column("size_bytes", Integer, nullable=False, server_default="0"),
    Column("content_type", String(160), nullable=False, server_default="application/octet-stream"),
    Column("content_hash", String(64), nullable=False),
    Column("sha256", String(64), nullable=False, server_default=""),
    Column("metadata_json", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("job_id", "storage_key", "sha256", name="uq_artifacts_job_storage_sha"),
    CheckConstraint("size_bytes >= 0", name="artifact_size_non_negative"),
    CheckConstraint("storage_provider in ('local', 's3', 'minio')", name="artifact_storage_provider"),
)

visualization_recipes = Table(
    "visualization_recipes",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("source_job_id", String(64), ForeignKey("jobs.id"), nullable=True),
    Column("name", String(160), nullable=False),
    Column("recipe_json", JSON, nullable=False),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

reports = Table(
    "reports",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("version", String(32), nullable=False, server_default="1"),
    Column("title", String(255), nullable=False),
    Column("markdown_key", Text, nullable=True),
    Column("html_key", Text, nullable=True),
    Column("report_json", JSON, nullable=False, server_default="{}"),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

user_configs = Table(
    "user_configs",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id"), nullable=False),
    Column("config_json", JSON, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

project_configs = Table(
    "project_configs",
    metadata,
    Column("project_id", String(64), ForeignKey("projects.id"), primary_key=True),
    Column("config_json", JSON, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

secrets = Table(
    "secrets",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("owner_type", String(32), nullable=False),
    Column("owner_id", String(64), nullable=False),
    Column("provider", String(80), nullable=False),
    Column("secret_ref", String(160), nullable=False),
    Column("encrypted_blob_key", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

audit_logs = Table(
    "audit_logs",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("actor_user_id", String(64), ForeignKey("users.id"), nullable=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=True),
    Column("action", String(120), nullable=False),
    Column("target_type", String(80), nullable=False),
    Column("target_id", String(96), nullable=False),
    Column("metadata_json", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

Index("idx_projects_org_created", projects.c.organization_id, projects.c.created_at)
Index("idx_project_members_user", project_members.c.user_id)
Index("idx_datasets_project_created", datasets.c.project_id, datasets.c.created_at)
Index("idx_files_dataset_created", files.c.dataset_id, files.c.created_at)
Index("idx_data_profiles_dataset_created", data_profiles.c.dataset_id, data_profiles.c.created_at)
Index("idx_analysis_plans_project_created", analysis_plans.c.project_id, analysis_plans.c.created_at)
Index("idx_analysis_plans_job", analysis_plans.c.job_id)
Index("idx_analysis_plans_plan_hash", analysis_plans.c.plan_hash)
Index("idx_jobs_project_created", jobs.c.project_id, jobs.c.created_at)
Index("idx_jobs_plan_id", jobs.c.plan_id)
Index("idx_job_events_job_seq", job_events.c.job_id, job_events.c.seq)
Index("idx_tool_calls_job", tool_calls.c.job_id)
Index("idx_artifacts_job", artifacts.c.job_id)
Index("idx_artifacts_project_created", artifacts.c.project_id, artifacts.c.created_at)
Index("idx_recipes_project_created", visualization_recipes.c.project_id, visualization_recipes.c.created_at)
Index("idx_reports_job", reports.c.job_id)
Index("idx_audit_logs_project_created", audit_logs.c.project_id, audit_logs.c.created_at)


PHASE1_TABLES = (
    "users",
    "organizations",
    "projects",
    "project_members",
    "datasets",
    "files",
    "data_profiles",
    "analysis_plans",
    "field_mappings",
    "sessions",
    "messages",
    "jobs",
    "job_events",
    "tool_calls",
    "artifacts",
    "visualization_recipes",
    "reports",
    "user_configs",
    "project_configs",
    "secrets",
    "audit_logs",
)

PHASE3_TABLES = PHASE1_TABLES
