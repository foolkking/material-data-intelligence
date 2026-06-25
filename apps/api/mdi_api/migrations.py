from __future__ import annotations


PHASE3_MIGRATION_DRAFT_SQL = """
-- Phase 3 draft migration: persistence repository + SSE cursor + artifact mapping.
-- This is intentionally kept as SQL draft text until Alembic is introduced.

CREATE TABLE IF NOT EXISTS projects (
    id varchar(64) PRIMARY KEY,
    organization_id varchar(64) NOT NULL,
    name varchar(160) NOT NULL,
    description text NOT NULL DEFAULT '',
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS datasets (
    id varchar(64) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    name varchar(160) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'created',
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS data_profiles (
    id varchar(64) PRIMARY KEY,
    dataset_id varchar(64) NOT NULL REFERENCES datasets(id),
    version varchar(32) NOT NULL,
    profile_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (dataset_id, version)
);

CREATE TABLE IF NOT EXISTS jobs (
    id varchar(64) PRIMARY KEY,
    project_id varchar(64) NOT NULL REFERENCES projects(id),
    dataset_id varchar(64) REFERENCES datasets(id),
    kind varchar(64) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'created',
    created_by varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

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
    UNIQUE (job_id, seq)
);
CREATE INDEX IF NOT EXISTS idx_job_events_job_seq ON job_events(job_id, seq);

CREATE TABLE IF NOT EXISTS tool_calls (
    id varchar(64) PRIMARY KEY,
    job_id varchar(64) NOT NULL REFERENCES jobs(id),
    step_id varchar(64) NOT NULL,
    tool_id varchar(160) NOT NULL,
    status varchar(32) NOT NULL DEFAULT 'created',
    params_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    error_json jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
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
    preview_key text,
    size_bytes integer NOT NULL DEFAULT 0,
    content_type varchar(160) NOT NULL DEFAULT 'application/octet-stream',
    content_hash varchar(64) NOT NULL,
    sha256 varchar(64) NOT NULL,
    metadata_json jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_artifacts_job ON artifacts(job_id);

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
