from __future__ import annotations


PHASE4_MIGRATION_BASELINE_SQL = """
-- Phase 4 baseline migration: production persistence hardening.
-- PostgreSQL-oriented SQL; SQLAlchemy metadata remains SQLite-compatible for tests.

CREATE TABLE IF NOT EXISTS projects (
    id varchar(64) PRIMARY KEY,
    organization_id varchar(64) NOT NULL,
    name varchar(160) NOT NULL,
    description text NOT NULL DEFAULT '',
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_projects_org_name UNIQUE (organization_id, name)
);

CREATE TABLE IF NOT EXISTS datasets (
    id varchar(64) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    name varchar(160) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'created',
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_datasets_project_name UNIQUE (project_id, name),
    CONSTRAINT dataset_status CHECK (status in ('created', 'uploading', 'profile_ready', 'failed', 'archived'))
);

CREATE TABLE IF NOT EXISTS data_profiles (
    id varchar(64) PRIMARY KEY,
    dataset_id varchar(64) NOT NULL REFERENCES datasets(id),
    version varchar(32) NOT NULL,
    profile_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_data_profiles_dataset_version UNIQUE (dataset_id, version)
);

CREATE TABLE IF NOT EXISTS jobs (
    id varchar(64) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    dataset_id varchar(64) REFERENCES datasets(id),
    kind varchar(64) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'created',
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT job_status CHECK (
        status in ('created', 'queued', 'running', 'partial_success', 'completed', 'failed', 'cancel_requested', 'cancelled')
    )
);
CREATE INDEX IF NOT EXISTS idx_jobs_project_created ON jobs(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS job_events (
    id varchar(64) PRIMARY KEY,
    job_id varchar(64) NOT NULL REFERENCES jobs(id),
    seq integer NOT NULL,
    event_type varchar(80) NOT NULL,
    status varchar(32) NOT NULL,
    message text NOT NULL,
    progress double precision,
    payload_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_job_events_job_seq UNIQUE (job_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_job_events_job_seq ON job_events(job_id, seq);

CREATE TABLE IF NOT EXISTS tool_calls (
    id varchar(64) PRIMARY KEY,
    job_id varchar(64) NOT NULL REFERENCES jobs(id),
    step_id varchar(64) NOT NULL,
    tool_id varchar(160) NOT NULL,
    idempotency_key varchar(160),
    attempt integer NOT NULL DEFAULT 1,
    status varchar(32) NOT NULL DEFAULT 'planned',
    params_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_json jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_tool_calls_job_step UNIQUE (job_id, step_id),
    CONSTRAINT uq_tool_calls_job_idempotency_key UNIQUE (job_id, idempotency_key),
    CONSTRAINT tool_call_attempt_positive CHECK (attempt >= 1),
    CONSTRAINT tool_call_status CHECK (status in ('planned', 'running', 'completed', 'failed', 'skipped'))
);
CREATE INDEX IF NOT EXISTS idx_tool_calls_job ON tool_calls(job_id);

CREATE TABLE IF NOT EXISTS artifacts (
    id varchar(96) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    dataset_id varchar(64) REFERENCES datasets(id),
    job_id varchar(64) NOT NULL REFERENCES jobs(id),
    tool_call_id varchar(64) REFERENCES tool_calls(id),
    type varchar(64) NOT NULL,
    name varchar(255) NOT NULL,
    version varchar(32) NOT NULL DEFAULT '1',
    storage_key text NOT NULL,
    storage_provider varchar(32) NOT NULL DEFAULT 'local',
    bucket varchar(160),
    preview_key text,
    size_bytes integer NOT NULL DEFAULT 0,
    content_type varchar(160) NOT NULL DEFAULT 'application/octet-stream',
    content_hash varchar(64) NOT NULL,
    sha256 varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_artifacts_job_storage_sha UNIQUE (job_id, storage_key, sha256),
    CONSTRAINT artifact_size_non_negative CHECK (size_bytes >= 0),
    CONSTRAINT artifact_storage_provider CHECK (storage_provider in ('local', 's3', 'minio'))
);
CREATE INDEX IF NOT EXISTS idx_artifacts_job ON artifacts(job_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_project_created ON artifacts(project_id, created_at DESC);

CREATE TABLE IF NOT EXISTS visualization_recipes (
    id varchar(64) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    source_job_id varchar(64) REFERENCES jobs(id),
    name varchar(160) NOT NULL,
    recipe_json jsonb NOT NULL,
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reports (
    id varchar(96) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    dataset_id varchar(64) REFERENCES datasets(id),
    job_id varchar(64) NOT NULL REFERENCES jobs(id),
    version varchar(32) NOT NULL DEFAULT '1',
    title varchar(255) NOT NULL,
    markdown_key text,
    html_key text,
    report_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_reports_job ON reports(job_id);
"""

PHASE3_MIGRATION_DRAFT_SQL = PHASE4_MIGRATION_BASELINE_SQL
