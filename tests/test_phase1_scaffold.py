from __future__ import annotations

import json

import yaml
from fastapi import FastAPI

from mdi_api import create_app
from mdi_api.db import PHASE1_TABLES, metadata


def test_phase1_fastapi_app_exposes_module_boundaries():
    app = create_app()
    assert isinstance(app, FastAPI)
    paths = {route.path for route in app.routes}

    assert "/health" in paths
    assert "/auth/me" in paths
    assert "/projects" in paths
    assert "/datasets" in paths
    assert "/projects/{project_id}/upload-sessions" in paths
    assert "/analysis-requests" in paths
    assert "/jobs/{job_id}/events" in paths
    assert "/jobs/{job_id}/events/stream" in paths
    assert "/jobs/{job_id}/artifacts" in paths
    assert "/tools" in paths
    assert "/tools/mvp" in paths


def test_phase1_database_metadata_contains_auth_project_dataset_tables():
    assert set(PHASE1_TABLES).issubset(metadata.tables)

    assert {"id", "email", "display_name"}.issubset(metadata.tables["users"].columns.keys())
    assert {"id", "organization_id", "created_by"}.issubset(metadata.tables["projects"].columns.keys())
    assert {"project_id", "user_id", "role"}.issubset(metadata.tables["project_members"].columns.keys())
    assert {"id", "project_id", "status", "created_by"}.issubset(metadata.tables["datasets"].columns.keys())
    assert {"dataset_id", "storage_key", "sha256", "parse_status"}.issubset(metadata.tables["files"].columns.keys())
    assert {"dataset_id", "profile_json"}.issubset(metadata.tables["data_profiles"].columns.keys())
    assert {"job_id", "event_type", "payload_json"}.issubset(metadata.tables["job_events"].columns.keys())
    assert {"job_id", "tool_id", "params_json"}.issubset(metadata.tables["tool_calls"].columns.keys())
    assert {"project_id", "job_id", "storage_key", "content_hash"}.issubset(metadata.tables["artifacts"].columns.keys())
    assert {"project_id", "recipe_json"}.issubset(metadata.tables["visualization_recipes"].columns.keys())
    assert {"secret_ref", "encrypted_blob_key"}.issubset(metadata.tables["secrets"].columns.keys())


def test_phase1_infra_compose_defines_postgres_redis_minio(repo_root):
    compose = yaml.safe_load((repo_root / "docker-compose.yml").read_text(encoding="utf-8"))
    services = compose["services"]

    assert {"postgres", "redis", "minio"}.issubset(services)
    assert services["postgres"]["ports"] == ["5432:5432"]
    assert services["redis"]["ports"] == ["6379:6379"]
    assert services["minio"]["ports"] == ["9000:9000", "9001:9001"]

    env_example = (repo_root / ".env.example").read_text(encoding="utf-8")
    assert "<LOCAL_POSTGRES_PASSWORD>" in env_example
    assert "<LOCAL_MINIO_PASSWORD>" in env_example


def test_phase1_next_workspace_shell_files_exist(repo_root):
    web_root = repo_root / "apps" / "web"
    package_json = json.loads((web_root / "package.json").read_text(encoding="utf-8"))

    assert package_json["name"] == "@mdi/web"
    assert {"dev", "build", "typecheck"}.issubset(package_json["scripts"])
    assert (web_root / "app" / "layout.tsx").exists()
    assert (web_root / "app" / "page.tsx").exists()
    assert (web_root / "app" / "globals.css").exists()

    page = (web_root / "app" / "page.tsx").read_text(encoding="utf-8")
    workbench = (web_root / "app" / "components" / "PlannerWorkbench.tsx").read_text(encoding="utf-8")
    combined = f"{page}\n{workbench}"
    assert "PlannerWorkbench" in page
    assert "Analysis Planner" in combined
    assert "Validated Plan Preview" in combined
    assert "Plan Provenance" in combined
    assert "Agent Timeline" in combined
    assert "Tool Calls" in combined
    assert "Artifacts / Result" in combined
    assert "No deterministic fallback used" in combined
