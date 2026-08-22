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
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.schema import conv


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
    Column("password_hash", Text, nullable=True),
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

auth_sessions = Table(
    "auth_sessions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("user_id", String(64), ForeignKey("users.id"), nullable=False),
    Column("token_hash", String(64), nullable=False, unique=True),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("last_seen_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
)
Index("idx_auth_sessions_user_expires", auth_sessions.c.user_id, auth_sessions.c.expires_at)

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
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("validation_status in ('validated', 'rejected')", name="analysis_plan_validation_status"),
)

analysis_intents = Table(
    "analysis_intents",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("profile_id", String(64), nullable=False),
    Column("schema_version", String(16), nullable=False),
    Column("intent_hash", String(64), nullable=False, unique=True),
    Column("outcome", String(32), nullable=False),
    Column("parent_intent_id", String(96), ForeignKey("analysis_intents.id"), nullable=True),
    Column("clarification_round", Integer, nullable=False, server_default="0"),
    Column("provider", String(64), nullable=False),
    Column("model", String(128), nullable=False),
    Column("prompt_version", String(64), nullable=False),
    Column("intent_json", JSON, nullable=False),
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("outcome in ('READY', 'NEEDS_CLARIFICATION', 'UNSUPPORTED')", name="analysis_intent_outcome"),
    CheckConstraint("clarification_round >= 0 and clarification_round <= 1", name="analysis_intent_round"),
)

Index("idx_analysis_intents_dataset_created", analysis_intents.c.dataset_id, analysis_intents.c.created_at)
Index("idx_analysis_intents_parent", analysis_intents.c.parent_intent_id)

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

research_session_runs = Table(
    "research_session_runs",
    metadata,
    Column("session_id", String(64), ForeignKey("sessions.id"), primary_key=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("job_id", name="uq_research_session_runs_job_id"),
)

Index("idx_research_session_runs_session_created", research_session_runs.c.session_id, research_session_runs.c.created_at)

analysis_intent_executions = Table(
    "analysis_intent_executions",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("intent_id", String(96), ForeignKey("analysis_intents.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False, unique=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("intent_id", "plan_id", "job_id", name="uq_intent_execution_binding"),
)

Index("idx_intent_executions_intent", analysis_intent_executions.c.intent_id)

capability_eligibility_resolutions = Table(
    "capability_eligibility_resolutions",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("resolution_hash", String(64), nullable=False, unique=True),
    Column("intent_id", String(96), ForeignKey("analysis_intents.id"), nullable=False),
    Column("profile_id", String(64), nullable=False),
    Column("profile_semantic_hash", String(128), nullable=False),
    Column("registry_snapshot_id", String(96), nullable=False),
    Column("registry_snapshot_hash", String(64), nullable=False),
    Column("resolver_version", String(32), nullable=False),
    Column("resolution_json", JSON, nullable=False),
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

Index("idx_capability_resolutions_intent", capability_eligibility_resolutions.c.intent_id)

capability_planning_decisions = Table(
    "capability_planning_decisions",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("decision_hash", String(64), nullable=False, unique=True),
    Column("intent_id", String(96), ForeignKey("analysis_intents.id"), nullable=False),
    Column("resolution_id", String(96), ForeignKey("capability_eligibility_resolutions.id"), nullable=False),
    Column("outcome", String(32), nullable=False),
    Column("provider", String(64), nullable=False),
    Column("provider_contract_version", String(32), nullable=False),
    Column("model", String(128), nullable=False),
    Column("repair_count", Integer, nullable=False, server_default="0"),
    Column("decision_json", JSON, nullable=False),
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "outcome in ('PLAN_READY', 'NEEDS_CLARIFICATION', 'UNSUPPORTED', 'CAPABILITY_MISMATCH', 'VALIDATION_FAILED')",
        name="capability_planning_decision_outcome",
    ),
    CheckConstraint("repair_count >= 0 and repair_count <= 1", name="capability_planning_repair_count"),
)

Index("idx_capability_decisions_intent", capability_planning_decisions.c.intent_id)
Index("idx_capability_decisions_resolution", capability_planning_decisions.c.resolution_id)

capability_planning_executions = Table(
    "capability_planning_executions",
    metadata,
    Column("id", String(96), primary_key=True),
    # A validated decision is reusable across multiple executions; plan and
    # job identities remain unique for each execution.
    Column("decision_id", String(96), ForeignKey("capability_planning_decisions.id"), nullable=False),
    Column("intent_id", String(96), ForeignKey("analysis_intents.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False, unique=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("decision_id", "intent_id", "plan_id", "job_id", name="uq_capability_planning_execution"),
)

Index("idx_capability_executions_intent", capability_planning_executions.c.intent_id)

plan_dependency_bindings = Table(
    "plan_dependency_bindings",
    metadata,
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), primary_key=True),
    Column("binding_id", String(96), primary_key=True),
    Column("plan_hash", String(64), nullable=False),
    Column("graph_hash", String(64), nullable=False),
    Column("producer_step_id", String(96), nullable=False),
    Column("producer_output_port", String(96), nullable=False),
    Column("consumer_step_id", String(96), nullable=False),
    Column("consumer_input_port", String(96), nullable=False),
    Column("artifact_kind", String(64), nullable=False),
    Column("artifact_contract_version", String(128), nullable=False),
    Column("media_type", String(128), nullable=False),
    Column("cardinality", String(32), nullable=False),
    Column("binding_json", JSON, nullable=False),
    Column("semantic_record_hash", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("plan_id", "consumer_step_id", "consumer_input_port", name="uq_plan_binding_consumer_port"),
)

Index("idx_plan_dependency_bindings_plan", plan_dependency_bindings.c.plan_id)
Index("idx_plan_dependency_bindings_graph", plan_dependency_bindings.c.graph_hash)

dependency_execution_records = Table(
    "dependency_execution_records",
    metadata,
    Column("execution_id", String(96), primary_key=True),
    Column("execution_hash", String(64), nullable=False, unique=True),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("plan_hash", String(64), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False, unique=True),
    Column("graph_hash", String(64), nullable=False),
    Column("outcome", String(32), nullable=False),
    Column("record_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint(
        "outcome in ('ALL_SUCCEEDED', 'PARTIAL_RESULTS', 'ALL_FAILED', 'VALIDATION_ABORTED')",
        name="dependency_execution_outcome",
    ),
)

Index("idx_dependency_execution_plan", dependency_execution_records.c.plan_id)
Index("idx_dependency_execution_job", dependency_execution_records.c.job_id)

runtime_artifact_binding_resolutions = Table(
    "runtime_artifact_binding_resolutions",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("record_hash", String(64), nullable=False, unique=True),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("plan_hash", String(64), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("binding_id", String(96), nullable=False),
    Column("producer_tool_call_id", String(64), ForeignKey("tool_calls.id"), nullable=True),
    Column("producer_step_id", String(96), nullable=False),
    Column("artifact_id", String(96), ForeignKey("artifacts.id"), nullable=True),
    Column("artifact_checksum", String(64), nullable=True),
    Column("artifact_kind", String(64), nullable=True),
    Column("artifact_contract_version", String(128), nullable=True),
    Column("media_type", String(128), nullable=True),
    Column("consumer_tool_call_id", String(64), ForeignKey("tool_calls.id"), nullable=True),
    Column("consumer_step_id", String(96), nullable=False),
    Column("consumer_input_port", String(96), nullable=False),
    Column("validation_outcome", String(32), nullable=False),
    Column("error_code", String(96), nullable=True),
    Column("resolved_ref_json", JSON, nullable=True),
    Column("resolved_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("job_id", "binding_id", name="uq_runtime_binding_job_binding"),
)

Index("idx_runtime_binding_job", runtime_artifact_binding_resolutions.c.job_id)
Index("idx_runtime_binding_artifact", runtime_artifact_binding_resolutions.c.artifact_id)

artifact_lineage_records = Table(
    "artifact_lineage_records",
    metadata,
    Column("lineage_id", String(96), primary_key=True),
    Column("lineage_hash", String(64), nullable=False, unique=True),
    Column("artifact_id", String(96), ForeignKey("artifacts.id"), nullable=False, unique=True),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("plan_hash", String(64), nullable=False),
    Column("graph_hash", String(64), nullable=False),
    Column("producer_tool_call_id", String(64), ForeignKey("tool_calls.id"), nullable=False),
    Column("producer_step_id", String(96), nullable=False),
    Column("output_port", String(96), nullable=False),
    Column("record_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

Index("idx_artifact_lineage_job", artifact_lineage_records.c.job_id)
Index("idx_artifact_lineage_plan", artifact_lineage_records.c.plan_id)

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

scientific_workspaces = Table(
    "scientific_workspaces",
    metadata,
    Column("workspace_id", String(96), primary_key=True),
    Column("schema_version", String(16), nullable=False),
    Column("project_id", String(64), ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False),
    Column("source_job_id", String(64), ForeignKey("jobs.id", ondelete="RESTRICT"), nullable=False),
    Column("source_reference_hash", String(64), nullable=False, unique=True),
    Column("dataset_id", String(64), ForeignKey("datasets.id", ondelete="RESTRICT"), nullable=True),
    Column("dataset_version", String(128), nullable=True),
    Column("profile_id", String(64), ForeignKey("data_profiles.id", ondelete="RESTRICT"), nullable=True),
    Column("profile_semantic_hash", String(64), nullable=True),
    Column("intent_id", String(96), ForeignKey("analysis_intents.id", ondelete="RESTRICT"), nullable=True),
    Column("intent_semantic_hash", String(64), nullable=True),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id", ondelete="RESTRICT"), nullable=True),
    Column("plan_hash", String(64), nullable=True),
    Column("plan_schema_version", String(16), nullable=True),
    Column("title", String(256), nullable=False),
    Column("active_panel_id", String(64), nullable=True),
    Column("pinned_selection_json", JSON, nullable=True),
    Column("revision", Integer, nullable=False, server_default="0"),
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("project_id", "source_job_id", name="uq_scientific_workspaces_project_job"),
    CheckConstraint("revision >= 0", name="scientific_workspace_revision_non_negative"),
)

Index(
    "idx_workspaces_project_updated",
    scientific_workspaces.c.project_id,
    scientific_workspaces.c.updated_at,
)
Index("idx_workspaces_source_job", scientific_workspaces.c.source_job_id)

workspace_panels = Table(
    "workspace_panels",
    metadata,
    Column(
        "workspace_id",
        String(96),
        ForeignKey("scientific_workspaces.workspace_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("panel_id", String(64), primary_key=True),
    Column("panel_kind", String(32), nullable=False),
    Column("title", String(256), nullable=False),
    Column("ordinal", SmallInteger, nullable=False),
    Column("visible", Boolean, nullable=False, server_default="true"),
    Column("source_refs_json", JSON, nullable=False),
    Column("renderer_contract", String(128), nullable=False),
    Column("accepted_selection_kinds_json", JSON, nullable=False),
    Column("layout_json", JSON, nullable=False),
    Column("panel_state_hash", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("ordinal >= 0", name="workspace_panel_ordinal_non_negative"),
)

Index("idx_workspace_panels_order", workspace_panels.c.workspace_id, workspace_panels.c.ordinal)

workspace_layout_revisions = Table(
    "workspace_layout_revisions",
    metadata,
    Column(
        "workspace_id",
        String(96),
        ForeignKey("scientific_workspaces.workspace_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("revision", Integer, primary_key=True),
    Column("layout_json", JSON, nullable=False),
    Column("selection_json", JSON, nullable=True),
    Column("semantic_hash", String(64), nullable=False),
    Column("created_by", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("workspace_id", "semantic_hash", name="uq_workspace_layout_semantic_hash"),
    CheckConstraint("revision >= 0", name="workspace_layout_revision_non_negative"),
)

scientific_evidence_bundles = Table(
    "scientific_evidence_bundles",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("bundle_hash", String(64), nullable=False, unique=True),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("plan_hash", String(64), nullable=False),
    Column("schema_version", String(16), nullable=False),
    Column("execution_outcome", String(32), nullable=False),
    Column("evidence_item_count", Integer, nullable=False),
    Column("warning_count", Integer, nullable=False),
    Column("limitation_count", Integer, nullable=False),
    Column("bundle_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("evidence_item_count >= 0 and evidence_item_count <= 256", name="scientific_evidence_item_count"),
)

scientific_interpretation_runs = Table(
    "scientific_interpretation_runs",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("execution_record_hash", String(64), nullable=False, unique=True),
    Column("bundle_id", String(96), ForeignKey("scientific_evidence_bundles.id"), nullable=False),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("mode", String(32), nullable=False),
    Column("provider", String(64), nullable=False),
    Column("provider_model", String(128), nullable=True),
    Column("provider_config_hash", String(64), nullable=True),
    Column("idempotency_key_hash", String(64), nullable=True),
    Column("repair_count", Integer, nullable=False, server_default="0"),
    Column("outcome", String(48), nullable=False),
    Column("interpretation_id", String(96), nullable=True, unique=True),
    Column("execution_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("repair_count >= 0 and repair_count <= 1", name="scientific_interpretation_run_repair_count"),
    UniqueConstraint("job_id", "mode", "idempotency_key_hash", name="uq_scientific_interpretation_run_idempotency"),
)

scientific_interpretations = Table(
    "scientific_interpretations",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("interpretation_hash", String(64), nullable=False, unique=True),
    Column("bundle_id", String(96), ForeignKey("scientific_evidence_bundles.id"), nullable=False),
    Column("project_id", String(64), ForeignKey("projects.id"), nullable=False),
    Column("dataset_id", String(64), ForeignKey("datasets.id"), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id"), nullable=False),
    Column("plan_id", String(96), ForeignKey("analysis_plans.id"), nullable=False),
    Column("mode", String(32), nullable=False),
    Column("provider", String(64), nullable=False),
    Column("repair_count", Integer, nullable=False, server_default="0"),
    Column("outcome", String(48), nullable=False),
    Column("execution_record_id", String(96), ForeignKey("scientific_interpretation_runs.id"), nullable=False, unique=True),
    Column("interpretation_json", JSON, nullable=False),
    Column("execution_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("repair_count >= 0 and repair_count <= 1", name="scientific_interpretation_repair_count"),
)

scientific_interpretation_claims = Table(
    "scientific_interpretation_claims",
    metadata,
    Column("interpretation_id", String(96), ForeignKey("scientific_interpretations.id"), primary_key=True),
    Column("claim_id", String(96), primary_key=True),
    Column("claim_type", String(40), nullable=False),
    Column("predicate", String(64), nullable=False),
    Column("confidence_class", String(24), nullable=False),
    Column("grounding_status", String(24), nullable=False),
    Column("display_order", Integer, nullable=False),
    Column("claim_json", JSON, nullable=False),
)

scientific_interpretation_evidence_links = Table(
    "scientific_interpretation_evidence_links",
    metadata,
    Column("interpretation_id", String(96), ForeignKey("scientific_interpretations.id"), primary_key=True),
    Column("claim_id", String(96), primary_key=True),
    Column("evidence_item_id", String(96), primary_key=True),
    Column("role", String(24), primary_key=True),
    Column("source_artifact_id", String(96), ForeignKey("artifacts.id"), nullable=False),
    Column("source_artifact_hash", String(64), nullable=False),
    Column("field_locator_json", JSON, nullable=False),
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

# Agent 2.0 deterministic domain foundation. New domain identities use
# portable UUID columns; references to established domains retain their real
# String key types.
scientific_objects = Table(
    "scientific_objects",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id", name="fk_so_project", ondelete="RESTRICT"), nullable=False),
    Column("kind", String(32), nullable=False),
    Column("object_type", String(128), nullable=False),
    Column("display_name", String(512), nullable=False),
    Column("lifecycle_status", String(32), nullable=False, server_default="ACTIVE"),
    Column(
        "current_version_id",
        Uuid,
        ForeignKey(
            "scientific_object_versions.id",
            name="fk_so_current_version",
            use_alter=True,
            ondelete="RESTRICT",
        ),
        nullable=True,
    ),
    Column("created_by_user_id", String(64), ForeignKey("users.id", name="fk_so_creator", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("archived_at", DateTime(timezone=True), nullable=True),
    Column("row_version", Integer, nullable=False, server_default="1"),
    CheckConstraint("row_version >= 1", name=conv("ck_so_row_version")),
    CheckConstraint(
        "lifecycle_status in ('ACTIVE', 'ARCHIVED', 'INVALIDATED')",
        name=conv("ck_so_lifecycle"),
    ),
)

scientific_object_versions = Table(
    "scientific_object_versions",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("scientific_object_id", Uuid, ForeignKey("scientific_objects.id", name="fk_sov_object", ondelete="RESTRICT"), nullable=False),
    Column("version_no", Integer, nullable=False),
    Column("object_type", String(128), nullable=False),
    Column("object_schema_version", String(32), nullable=False),
    Column("source_resource_refs_json", JSON, nullable=False),
    Column("parent_object_version_refs_json", JSON, nullable=False),
    Column("semantic_profile_ref_json", JSON, nullable=True),
    Column("normalized_payload_ref_json", JSON, nullable=False),
    Column("content_hash", String(128), nullable=False),
    Column("semantic_hash", String(128), nullable=False),
    Column("canonical_metadata_json", JSON, nullable=False),
    Column("availability_status", String(32), nullable=False),
    Column("created_by_user_id", String(64), ForeignKey("users.id", name="fk_sov_creator", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("scientific_object_id", "version_no", name="uq_scientific_object_versions_object_version"),
    CheckConstraint("version_no >= 1", name=conv("ck_sov_version_no")),
    CheckConstraint(
        "availability_status in ('AVAILABLE', 'PARTIALLY_AVAILABLE', 'SOURCE_MISSING', 'INVALID')",
        name=conv("ck_sov_availability"),
    ),
)

scientific_object_relationships = Table(
    "scientific_object_relationships",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id", name="fk_sor_project", ondelete="RESTRICT"), nullable=False),
    Column("source_version_id", Uuid, ForeignKey("scientific_object_versions.id", name="fk_sor_source", ondelete="RESTRICT"), nullable=False),
    Column("target_version_id", Uuid, ForeignKey("scientific_object_versions.id", name="fk_sor_target", ondelete="RESTRICT"), nullable=False),
    Column("relation_type", String(128), nullable=False),
    Column("metadata_json", JSON, nullable=False),
    Column("created_by_user_id", String(64), ForeignKey("users.id", name="fk_sor_creator", ondelete="SET NULL"), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint(
        "source_version_id",
        "target_version_id",
        "relation_type",
        name="uq_scientific_object_relationship_edge",
    ),
    CheckConstraint("source_version_id <> target_version_id", name=conv("ck_sor_not_self")),
)

research_turns = Table(
    "research_turns",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id", name="fk_rt_project", ondelete="RESTRICT"), nullable=False),
    Column("research_session_id", String(64), ForeignKey("sessions.id", name="fk_rt_session", ondelete="RESTRICT"), nullable=False),
    Column("sequence_no", Integer, nullable=False),
    Column("parent_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rt_parent", ondelete="RESTRICT"), nullable=True),
    Column("continuation_of_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rt_continuation", ondelete="RESTRICT"), nullable=True),
    Column("user_message_id", String(64), ForeignKey("messages.id", name="fk_rt_user_message", ondelete="RESTRICT"), nullable=False, unique=True),
    Column("assistant_pre_message_id", String(64), ForeignKey("messages.id", name="fk_rt_pre_message", ondelete="SET NULL"), nullable=True),
    Column("assistant_final_message_id", String(64), ForeignKey("messages.id", name="fk_rt_final_message", ondelete="SET NULL"), nullable=True),
    Column("action_type", String(32), nullable=True),
    Column("status", String(32), nullable=False),
    Column(
        "context_snapshot_id",
        Uuid,
        ForeignKey(
            "research_context_snapshots.id",
            name="fk_rt_context",
            use_alter=True,
            ondelete="RESTRICT",
        ),
        nullable=True,
    ),
    Column("analysis_intent_id", String(96), ForeignKey("analysis_intents.id", name="fk_rt_intent", ondelete="RESTRICT"), nullable=True),
    Column("analysis_plan_id", String(96), ForeignKey("analysis_plans.id", name="fk_rt_plan", ondelete="RESTRICT"), nullable=True),
    Column("job_id", String(64), ForeignKey("jobs.id", name="fk_rt_job", ondelete="RESTRICT"), nullable=True),
    Column("interpretation_id", String(96), ForeignKey("scientific_interpretations.id", name="fk_rt_interpretation", ondelete="RESTRICT"), nullable=True),
    Column("report_id", String(96), ForeignKey("reports.id", name="fk_rt_report", ondelete="RESTRICT"), nullable=True),
    Column("error_code", String(96), nullable=True),
    Column("error_summary", Text, nullable=True),
    Column("row_version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("started_at", DateTime(timezone=True), nullable=True),
    Column("completed_at", DateTime(timezone=True), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("research_session_id", "sequence_no", name="uq_research_turns_session_sequence"),
    CheckConstraint("sequence_no >= 1", name=conv("ck_rt_sequence_no")),
    CheckConstraint("row_version >= 1", name=conv("ck_rt_row_version")),
    CheckConstraint(
        "action_type is null or action_type in ('ANSWER', 'CLARIFY', 'ANALYZE', 'CONTINUE_ANALYSIS', 'INTERPRET_RESULT', 'QUERY_DATA', 'MANAGE_DATA', 'OPEN_OBJECT', 'CREATE_REPORT', 'UPDATE_REPORT', 'EXPORT')",
        name=conv("ck_rt_action"),
    ),
    CheckConstraint(
        "status in ('RECEIVED', 'RESOLVING_CONTEXT', 'ORCHESTRATING', 'NEEDS_CLARIFICATION', 'ANSWERED', 'UNSUPPORTED', 'READY_TO_PLAN', 'PLANNING', 'PLAN_READY', 'PLAN_REJECTED', 'QUEUED', 'RUNNING', 'INTERPRETING', 'COMPLETED', 'PARTIAL', 'FAILED', 'CANCELED')",
        name=conv("ck_rt_status"),
    ),
)

research_context_snapshots = Table(
    "research_context_snapshots",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id", name="fk_rcs_project", ondelete="RESTRICT"), nullable=False),
    Column("research_session_id", String(64), ForeignKey("sessions.id", name="fk_rcs_session", ondelete="RESTRICT"), nullable=False),
    Column("research_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rcs_turn", ondelete="RESTRICT"), nullable=False, unique=True),
    Column("snapshot_schema_version", String(32), nullable=False),
    Column("active_scope_refs_json", JSON, nullable=False),
    Column("selection_refs_json", JSON, nullable=False),
    Column("resolved_references_json", JSON, nullable=False),
    Column("referenced_result_refs_json", JSON, nullable=False),
    Column("relevant_finding_refs_json", JSON, nullable=False),
    Column("effective_constraints_json", JSON, nullable=False),
    Column("research_goal", Text, nullable=True),
    Column("unresolved_questions_json", JSON, nullable=False),
    Column("context_fingerprint", String(128), nullable=False),
    Column("compiler_version", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

research_turn_events = Table(
    "research_turn_events",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rte_turn", ondelete="CASCADE"), nullable=False),
    Column("sequence_no", Integer, nullable=False),
    Column("event_type", String(96), nullable=False),
    Column("payload_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("turn_id", "sequence_no", name="uq_research_turn_events_turn_sequence"),
    CheckConstraint("sequence_no >= 1", name=conv("ck_rte_sequence_no")),
)

scientific_result_snapshots = Table(
    "scientific_result_snapshots",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("project_id", String(64), ForeignKey("projects.id", name="fk_srs_project", ondelete="RESTRICT"), nullable=False),
    Column("research_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_srs_turn", ondelete="RESTRICT"), nullable=False),
    Column("job_id", String(64), ForeignKey("jobs.id", name="fk_srs_job", ondelete="RESTRICT"), nullable=True),
    Column("schema_version", String(32), nullable=False),
    Column("projection_version", String(64), nullable=False),
    Column("execution_status", String(32), nullable=False),
    Column("relevance_status", String(32), nullable=False),
    Column("source_fingerprint", String(128), nullable=False),
    Column("bundle_json", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint(
        "research_turn_id",
        "projection_version",
        "source_fingerprint",
        name="uq_scientific_result_snapshot_projection",
    ),
    CheckConstraint(
        "execution_status in ('SUCCESS', 'PARTIAL', 'FAILED')",
        name=conv("ck_srs_execution_status"),
    ),
    CheckConstraint(
        "relevance_status in ('CURRENT', 'STALE', 'SOURCE_MISSING', 'INVALIDATED')",
        name=conv("ck_srs_relevance_status"),
    ),
)

research_turn_decisions = Table(
    "research_turn_decisions",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column(
        "research_turn_id",
        Uuid,
        ForeignKey("research_turns.id", name="fk_rtd_turn", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    ),
    Column("contract_version", String(32), nullable=False),
    Column("action", String(32), nullable=False),
    Column("decision_json", JSON, nullable=False),
    Column("input_context_fingerprint", String(128), nullable=False),
    Column("prompt_version", String(64), nullable=False),
    Column("provider", String(64), nullable=False),
    Column("model", String(128), nullable=False),
    Column("provider_request_id", String(128), nullable=True),
    Column("repair_attempted", Boolean, nullable=False, server_default="false"),
    Column("validation_status", String(32), nullable=False),
    Column("action_dispatch_status", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("validation_status = 'VALIDATED'", name=conv("ck_rtd_validation")),
    CheckConstraint(
        "action_dispatch_status in ('COMPLETED', 'READY_FOR_DOWNSTREAM')",
        name=conv("ck_rtd_dispatch"),
    ),
)

research_capability_resolutions = Table(
    "research_capability_resolutions",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("research_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rcr_turn", ondelete="RESTRICT"), nullable=False, unique=True),
    Column("contract_version", String(32), nullable=False),
    Column("requirement_snapshot_json", JSON, nullable=False),
    Column("resolution_json", JSON, nullable=False),
    Column("registry_fingerprint", String(128), nullable=False),
    Column("resolver_version", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

research_capability_plans = Table(
    "research_capability_plans",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("research_turn_id", Uuid, ForeignKey("research_turns.id", name="fk_rcp_turn", ondelete="RESTRICT"), nullable=False, unique=True),
    Column("capability_resolution_id", Uuid, ForeignKey("research_capability_resolutions.id", name="fk_rcp_resolution", ondelete="RESTRICT"), nullable=False),
    Column("contract_version", String(32), nullable=False),
    Column("plan_json", JSON, nullable=False),
    Column("input_fingerprint", String(128), nullable=False),
    Column("planner_mode", String(16), nullable=False),
    Column("prompt_version", String(64), nullable=True),
    Column("provider", String(64), nullable=True),
    Column("model", String(128), nullable=True),
    Column("provider_request_id", String(128), nullable=True),
    Column("repair_attempted", Boolean, nullable=False, server_default="false"),
    Column("validation_status", String(32), nullable=False),
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
Index("idx_scientific_evidence_job", scientific_evidence_bundles.c.job_id)
Index("idx_scientific_interpretation_runs_job", scientific_interpretation_runs.c.job_id)
Index("idx_scientific_interpretations_job", scientific_interpretations.c.job_id)
Index("idx_scientific_interpretations_bundle", scientific_interpretations.c.bundle_id)
Index("idx_audit_logs_project_created", audit_logs.c.project_id, audit_logs.c.created_at)
Index("idx_scientific_objects_project_lifecycle", scientific_objects.c.project_id, scientific_objects.c.lifecycle_status)
Index("idx_scientific_objects_project_kind", scientific_objects.c.project_id, scientific_objects.c.kind)
Index("idx_scientific_objects_project_type", scientific_objects.c.project_id, scientific_objects.c.object_type)
Index("idx_scientific_objects_current_version", scientific_objects.c.current_version_id)
Index("idx_scientific_object_versions_object", scientific_object_versions.c.scientific_object_id)
Index("idx_scientific_object_versions_type", scientific_object_versions.c.object_type)
Index("idx_scientific_object_versions_content_hash", scientific_object_versions.c.content_hash)
Index("idx_scientific_object_versions_semantic_hash", scientific_object_versions.c.semantic_hash)
Index("idx_scientific_object_relationships_project", scientific_object_relationships.c.project_id)
Index("idx_scientific_object_relationships_source", scientific_object_relationships.c.source_version_id)
Index("idx_scientific_object_relationships_target", scientific_object_relationships.c.target_version_id)
Index("idx_research_turns_project_created", research_turns.c.project_id, research_turns.c.created_at)
Index("idx_research_turns_session_sequence", research_turns.c.research_session_id, research_turns.c.sequence_no)
Index("idx_research_turns_status_updated", research_turns.c.status, research_turns.c.updated_at)
Index("idx_research_turns_job", research_turns.c.job_id)
Index("idx_research_turns_plan", research_turns.c.analysis_plan_id)
Index("idx_research_context_snapshots_session", research_context_snapshots.c.research_session_id)
Index("idx_research_turn_events_turn", research_turn_events.c.turn_id)
Index("idx_scientific_result_snapshots_turn", scientific_result_snapshots.c.research_turn_id)
Index("idx_scientific_result_snapshots_job", scientific_result_snapshots.c.job_id)
Index("idx_scientific_result_snapshots_project_created", scientific_result_snapshots.c.project_id, scientific_result_snapshots.c.created_at)
Index("idx_research_turn_decisions_action_created", research_turn_decisions.c.action, research_turn_decisions.c.created_at)
Index("idx_research_turn_decisions_fingerprint", research_turn_decisions.c.input_context_fingerprint)
Index("idx_research_capability_resolutions_fingerprint", research_capability_resolutions.c.registry_fingerprint)
Index("idx_research_capability_plans_resolution", research_capability_plans.c.capability_resolution_id)
Index("idx_research_capability_plans_fingerprint", research_capability_plans.c.input_fingerprint)


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
