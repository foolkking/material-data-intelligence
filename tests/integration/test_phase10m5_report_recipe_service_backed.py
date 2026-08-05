from __future__ import annotations

from hashlib import sha256
import json
import os
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.db import reports as reports_table, visualization_recipes
from mdi_api.main import create_app
from mdi_api.repositories import SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_api.workspaces import WorkspaceProjectionService

from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _redis_smoke,
    _required_postgres_url,
    _schema_database_url,
)


@pytest.mark.integration
def test_phase10m5_postgres_redis_minio_report_recipe_composition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m5_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_key = f"phase10m5/{suffix}/table.json"
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")

        engine = create_engine(schema_url, future=True)
        assert inspect(engine).get_table_names()
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0007_phase10m1_workspace_domain"
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))

        _redis_smoke(f"m5-{suffix}")
        minio, bucket = _minio_client()
        payload = json.dumps({"columns": ["value"], "rows": [{"objectId": "sample_1", "value": 2.0}]}, sort_keys=True, separators=(",", ":")).encode("utf-8")
        checksum = sha256(payload).hexdigest()
        minio.put_object(Bucket=bucket, Key=object_key, Body=payload, ContentType="application/json")

        repos = SqlAlchemyRepositoryBundle.create(engine)
        project_id = f"project_m5_{suffix}"
        dataset_id = f"dataset_m5_{suffix}"
        plan_id = f"plan_m5_{suffix}"
        job_id = f"job_m5_{suffix}"
        call_id = f"call_m5_{suffix}"
        artifact_id = f"artifact_m5_{suffix}"
        repos.projects.save({"id": project_id, "name": "M5 service", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "M5 data", "status": "profile_ready", "createdBy": "user_local"})
        plan = {
            "schemaVersion": "0.1", "goal": "Summarize exact persisted values.",
            "datasetId": dataset_id, "profileId": f"profile_m5_{suffix}", "toolRegistryVersion": "1.0",
            "assumptions": [], "warnings": [],
            "steps": [{
                "stepId": "step_summary", "toolId": "table.numeric_summary",
                "purpose": "Persist exact statistics.", "reason": "Requested summary.",
                "inputRefs": [{"refType": "normalized_object", "ref": "table_1", "datasetId": dataset_id, "objectId": "table_1", "objectType": "DataFrame"}],
                "params": {"columns": ["value"]}, "output": {"artifactTypes": ["table_json"]},
            }],
            "expectedArtifacts": [{"name": "summary", "type": "table_json", "fromStepId": "step_summary"}],
        }
        plan_hash = compute_plan_hash(plan)
        repos.analysis_plans.save_plan({"id": plan_id, "projectId": project_id, "datasetId": dataset_id, "profileId": f"profile_m5_{suffix}", "analysisPlan": plan, "planHash": plan_hash, "validationStatus": "validated", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "planId": plan_id, "status": "completed", "kind": "analysis", "createdBy": "user_local"})
        repos.tool_calls.save({"id": call_id, "jobId": job_id, "stepId": "step_summary", "toolId": "table.numeric_summary", "status": "completed", "params": {"columns": ["value"]}})
        repos.artifacts.save({
            "id": artifact_id, "projectId": project_id, "datasetId": dataset_id, "jobId": job_id,
            "toolCallId": call_id, "type": "table_json", "version": "1", "name": "ignored-name.html",
            "storageKey": object_key, "storageProvider": "minio", "bucket": bucket,
            "sizeBytes": len(payload), "contentType": "application/json", "contentHash": checksum,
            "sha256": checksum, "metadata": {"toolId": "table.numeric_summary", "toolVersion": "1.0", "adapterVersion": "1.0", "rawPayload": "PRIVATE_M5_PAYLOAD"},
        })
        workspace_snapshot, created = WorkspaceProjectionService(repos).project_job(source_job_id=job_id, created_by="user_local", title="M5 service Workspace")
        assert created is True
        workspace = workspace_snapshot.body["workspace"]
        workspace_id = workspace["workspaceId"]

        before_execution_rows = (
            len(repos.jobs.list_by_project(project_id)),
            len(repos.tool_calls.list_for_job(job_id)),
            len(repos.artifacts.list_for_job(job_id)),
        )
        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        client = TestClient(create_app())
        try:
            content = client.get(f"/planner/jobs/{job_id}/artifacts/{artifact_id}/content")
            assert content.status_code == 200
            assert content.content == payload
            assert content.headers["x-content-sha256"] == checksum

            sources = client.get(f"/workspaces/{workspace_id}/report-composition/sources")
            assert sources.status_code == 200
            source_body = sources.json()
            assert source_body["metadataOnly"] is True
            assert source_body["heavyArtifactPayloadRequests"] == 0
            serialized_sources = json.dumps(source_body, sort_keys=True)
            assert object_key not in serialized_sources and bucket not in serialized_sources
            assert "PRIVATE_M5_PAYLOAD" not in serialized_sources

            request = {
                "schemaVersion": "1.0", "workspaceId": workspace_id,
                "expectedWorkspaceRevision": workspace["revision"], "title": "Service-backed report",
                "selectedPanelIds": [], "selectedArtifactIds": [artifact_id],
                "selectedClaimIds": [], "selectedEvidenceItemIds": [], "itemOrder": [artifact_id],
                "captions": [{"sourceId": artifact_id, "text": "Exact persisted table."}],
                "exportFormats": ["json", "markdown"],
            }
            before_pair = _pair_count(engine)
            preview = client.post(f"/workspaces/{workspace_id}/report-compositions/preview", json=request)
            assert preview.status_code == 200
            assert preview.json()["persisted"] is False
            assert _pair_count(engine) == before_pair

            created_pair = client.post(f"/workspaces/{workspace_id}/report-compositions", headers={"Idempotency-Key": f"m5-service-{suffix}"}, json=request)
            assert created_pair.status_code == 201
            pair = created_pair.json()
            assert _pair_count(engine) == (before_pair[0] + 1, before_pair[1] + 1)
            replay = client.post(f"/workspaces/{workspace_id}/report-compositions", headers={"Idempotency-Key": f"m5-service-{suffix}"}, json=request)
            assert replay.status_code == 200
            assert replay.json()["reportId"] == pair["reportId"]
            assert replay.headers["x-idempotent-replay"] == "true"
            assert _pair_count(engine) == (before_pair[0] + 1, before_pair[1] + 1)

            history = client.get(f"/workspaces/{workspace_id}/report-compositions")
            recipe = client.get(f"/workspaces/{workspace_id}/report-compositions/{pair['reportId']}/recipe")
            export_json = client.get(f"/workspaces/{workspace_id}/report-compositions/{pair['reportId']}/exports/json")
            export_markdown = client.get(f"/workspaces/{workspace_id}/report-compositions/{pair['reportId']}/exports/markdown")
            assert history.status_code == recipe.status_code == export_json.status_code == export_markdown.status_code == 200
            assert history.json()["count"] == 1
            assert recipe.json()["recipe"]["planSchemaVersion"] == "0.1"
            assert recipe.json()["recipe"]["dependencyBindings"] == []
            assert recipe.json()["recipe"]["executionAuthorized"] is False
            assert export_json.content.endswith(b"\n") and export_markdown.content.endswith(b"\n")

            injected = {**request, "selectedArtifactIds": [f"artifact_foreign_{suffix}"], "itemOrder": [f"artifact_foreign_{suffix}"]}
            rejected = client.post(f"/workspaces/{workspace_id}/report-compositions/preview", json=injected)
            assert rejected.status_code == 404
            assert rejected.json()["detail"]["code"] == "REPORT_SOURCE_NOT_FOUND"
            assert _pair_count(engine) == (before_pair[0] + 1, before_pair[1] + 1)
        finally:
            client.close()

        assert before_execution_rows == (
            len(repos.jobs.list_by_project(project_id)),
            len(repos.tool_calls.list_for_job(job_id)),
            len(repos.artifacts.list_for_job(job_id)),
        )
    finally:
        if minio is not None:
            try:
                minio.delete_object(Bucket=bucket, Key=object_key)
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()


def _pair_count(engine) -> tuple[int, int]:
    with engine.connect() as connection:
        return (
            int(connection.scalar(select(func.count()).select_from(reports_table)) or 0),
            int(connection.scalar(select(func.count()).select_from(visualization_recipes)) or 0),
        )
