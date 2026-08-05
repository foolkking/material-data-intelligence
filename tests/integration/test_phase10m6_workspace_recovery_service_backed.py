from __future__ import annotations

from hashlib import sha256
import json
import os
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.schema import CreateSchema, DropSchema

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
def test_phase10m6_postgres_redis_minio_workspace_save_reload_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m6_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_key = f"phase10m6/{suffix}/running-result.json"
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

        _redis_smoke(f"m6-{suffix}")
        minio, bucket = _minio_client()
        payload = json.dumps({"status": "partial", "value": 2.0}, sort_keys=True, separators=(",", ":")).encode("utf-8")
        checksum = sha256(payload).hexdigest()
        minio.put_object(Bucket=bucket, Key=object_key, Body=payload, ContentType="application/json")

        repos = SqlAlchemyRepositoryBundle.create(engine)
        project_id = f"project_m6_{suffix}"
        dataset_id = f"dataset_m6_{suffix}"
        plan_id = f"plan_m6_{suffix}"
        job_id = f"job_m6_{suffix}"
        call_id = f"call_m6_{suffix}"
        artifact_id = f"artifact_m6_{suffix}"
        repos.projects.save({"id": project_id, "name": "M6 recovery", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "M6 data", "status": "profile_ready", "createdBy": "user_local"})
        plan = {
            "schemaVersion": "0.1",
            "goal": "Observe exact persisted recovery state.",
            "datasetId": dataset_id,
            "profileId": f"profile_m6_{suffix}",
            "toolRegistryVersion": "1.0",
            "assumptions": [],
            "warnings": [],
            "steps": [{
                "stepId": "step_recovery",
                "toolId": "table.numeric_summary",
                "purpose": "Persist a bounded result.",
                "reason": "Recovery fixture.",
                "inputRefs": [{"refType": "normalized_object", "ref": "table_1", "datasetId": dataset_id, "objectId": "table_1", "objectType": "DataFrame"}],
                "params": {"columns": ["value"]},
                "output": {"artifactTypes": ["table_json"]},
            }],
            "expectedArtifacts": [{"name": "summary", "type": "table_json", "fromStepId": "step_recovery"}],
        }
        plan_hash = compute_plan_hash(plan)
        repos.analysis_plans.save_plan({"id": plan_id, "projectId": project_id, "datasetId": dataset_id, "profileId": f"profile_m6_{suffix}", "analysisPlan": plan, "planHash": plan_hash, "validationStatus": "validated", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "planId": plan_id, "status": "running", "kind": "analysis", "createdBy": "user_local"})
        repos.tool_calls.save({"id": call_id, "jobId": job_id, "stepId": "step_recovery", "toolId": "table.numeric_summary", "status": "running", "params": {"columns": ["value"]}})
        repos.artifacts.save({
            "id": artifact_id, "projectId": project_id, "datasetId": dataset_id,
            "jobId": job_id, "toolCallId": call_id, "type": "table_json", "version": "1",
            "name": "ignored-recovery-name.html", "storageKey": object_key,
            "storageProvider": "minio", "bucket": bucket, "sizeBytes": len(payload),
            "contentType": "application/json", "contentHash": checksum, "sha256": checksum,
            "metadata": {"toolId": "table.numeric_summary", "toolVersion": "1.0", "adapterVersion": "1.0"},
        })

        service = WorkspaceProjectionService(repos)
        projected, created = service.project_job(source_job_id=job_id, created_by="user_local", title="M6 running Workspace")
        assert created is True
        workspace_id = projected.body["workspace"]["workspaceId"]
        before_execution = (
            len(repos.jobs.list_by_project(project_id)),
            len(repos.tool_calls.list_for_job(job_id)),
            len(repos.artifacts.list_for_job(job_id)),
        )

        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        client = TestClient(create_app())
        try:
            first = client.get(f"/workspaces/{workspace_id}")
            assert first.status_code == 200
            assert first.json()["workspace"]["projectedStatus"] == "RUNNING"
            initial_history = client.get(f"/workspaces/{workspace_id}/layout-revisions").json()["items"]
            assert len(initial_history) == 1

            saved = client.patch(
                f"/workspaces/{workspace_id}",
                headers={"If-Match": first.headers["etag"]},
                json={"title": "M6 saved Workspace", "activePanelId": first.json()["panels"][0]["panelId"]},
            )
            assert saved.status_code == 200
            assert saved.json()["workspace"]["title"] == "M6 saved Workspace"
            assert saved.json()["workspace"]["revision"] == 1

            conflict = client.patch(
                f"/workspaces/{workspace_id}",
                headers={"If-Match": first.headers["etag"]},
                json={"title": "stale writer"},
            )
            assert conflict.status_code == 412
            assert conflict.json()["detail"]["code"] == "REVISION_MISMATCH"
            assert client.get(f"/workspaces/{workspace_id}").json()["workspace"]["title"] == "M6 saved Workspace"

            with engine.begin() as connection:
                connection.execute(text("UPDATE jobs SET status = 'completed' WHERE id = :job_id"), {"job_id": job_id})
                connection.execute(text("UPDATE tool_calls SET status = 'completed' WHERE id = :call_id"), {"call_id": call_id})
            recovered = client.get(f"/workspaces/{workspace_id}")
            assert recovered.status_code == 200
            assert recovered.json()["workspace"]["projectedStatus"] == "COMPLETE"
            assert len(client.get(f"/workspaces/{workspace_id}/layout-revisions").json()["items"]) == 2

            content = client.get(f"/planner/jobs/{job_id}/artifacts/{artifact_id}/content")
            assert content.status_code == 200
            assert content.content == payload
            assert content.headers["x-content-sha256"] == checksum

            current = service.get_snapshot(workspace_id)
            for revision in range(2, 128):
                current = service.patch_workspace(
                    workspace_id=workspace_id,
                    expected_revision=revision - 1,
                    changes={"title": f"M6 bounded revision {revision}"},
                    updated_by="user_local",
                )
            assert current.body["workspace"]["revision"] == 127
            assert len(repos.workspaces.list_layout_revisions(workspace_id, project_id=project_id)) == 128
            cap = client.patch(
                f"/workspaces/{workspace_id}",
                headers={"If-Match": f'"{current.etag}"'},
                json={"title": "revision cap overflow"},
            )
            assert cap.status_code == 422
            assert cap.json()["detail"]["code"] == "REVISION_CAP_EXCEEDED"
            assert len(repos.workspaces.list_layout_revisions(workspace_id, project_id=project_id)) == 128
        finally:
            client.close()

        assert before_execution == (
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
