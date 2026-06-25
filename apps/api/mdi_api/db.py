from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
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
    Column("kind", String(64), nullable=False),
    Column("status", String(32), nullable=False, server_default="created"),
    Column("created_by", String(64), ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
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
    Column("status", String(32), nullable=False, server_default="created"),
    Column("params_json", JSON, nullable=False, server_default="{}"),
    Column("error_json", JSON, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
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
    Column("storage_key", Text, nullable=False),
    Column("content_hash", String(64), nullable=False),
    Column("metadata_json", JSON, nullable=False, server_default="{}"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
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
Index("idx_jobs_project_created", jobs.c.project_id, jobs.c.created_at)
Index("idx_job_events_job_seq", job_events.c.job_id, job_events.c.seq)
Index("idx_tool_calls_job", tool_calls.c.job_id)
Index("idx_artifacts_job", artifacts.c.job_id)
Index("idx_audit_logs_project_created", audit_logs.c.project_id, audit_logs.c.created_at)


PHASE1_TABLES = (
    "users",
    "organizations",
    "projects",
    "project_members",
    "datasets",
    "files",
    "data_profiles",
    "field_mappings",
    "sessions",
    "messages",
    "jobs",
    "job_events",
    "tool_calls",
    "artifacts",
    "visualization_recipes",
    "user_configs",
    "project_configs",
    "secrets",
    "audit_logs",
)
