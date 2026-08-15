from __future__ import annotations

import os
import json
from pathlib import Path
from types import SimpleNamespace
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.main import create_app
from mdi_api.artifact_storage import create_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.phase2_runtime import get_phase2_runtime, reset_phase2_runtime
from mdi_api.routers.planner import _planner_repositories_and_runtime
from mdi_workers.object_store import DurableObjectStoreResolver
from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _required_postgres_url,
    _schema_database_url,
)


@pytest.mark.integration
def test_phase13_1_fix_forward_3_real_upload_to_fresh_worker_d0(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Prove durable upload reconstruction through the first worker Artifact."""

    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase13r3_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    queued_job_id: str | None = None
    redis = Redis.from_url(os.environ["REDIS_URL"])
    queue = Queue("mdi-jobs", connection=redis)
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        monkeypatch.setenv("DATABASE_URL", schema_url)
        alembic_upgrade(config, "head")
        engine = create_engine(schema_url, future=True)

        monkeypatch.setenv("MDI_RUNTIME_BACKEND", "postgresql")
        monkeypatch.setenv("MDI_QUEUE_BACKEND", "redis")
        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "1")
        client_s3, bucket = _minio_client()
        client_s3.head_bucket(Bucket=bucket)
        assert redis.ping() is True

        reset_phase2_runtime(tmp_path / "phase2-uploads")
        client = TestClient(create_app())
        project_response = client.post("/projects", json={"name": f"Attempt 3 {suffix}"})
        assert project_response.status_code == 200
        project = project_response.json()
        upload_response = client.post(
            "/datasets/upload",
            json={
                "projectId": project["id"],
                "datasetName": "Attempt 3 real upload",
                "filePaths": ["tests/fixtures/tables/formulas.csv"],
            },
        )
        assert upload_response.status_code == 200
        dataset = upload_response.json()
        profile = dataset["profile"]
        selected_ids = [
            item["resourceId"]
            for item in profile["resourceSemantics"]
            if item.get("resourceId")
        ]

        planned_response = client.post(
            "/planner/jobs",
            json={
                "projectId": project["id"],
                "datasetId": dataset["id"],
                "profileId": profile["profileId"],
                "userPrompt": (
                    "Explore this materials table, summarize its quality, and show how "
                    "the compositions are distributed."
                ),
                "intentSchemaVersion": "1.0",
                "selectedResourceIds": selected_ids,
                "provider": "mock",
                "enqueue": True,
            },
        )
        assert planned_response.status_code == 200
        planned = planned_response.json()
        assert planned["ok"] is True, json.dumps(planned, indent=2)
        assert planned["enqueued"] is True
        queued_job_id = planned["job_id"]
        queued_job = queue.fetch_job(planned["job_id"])
        assert queued_job is not None
        assert queued_job.args == (planned["job_id"],)

        phase2_record = get_phase2_runtime().datasets[dataset["id"]]
        assert phase2_record.normalized_exports
        upload_exports = {
            item["objectId"]: (item["storageKey"], item["contentHash"])
            for item in phase2_record.normalized_exports
        }

        # Destroy all process-local upload state before constructing the worker.
        reset_phase2_runtime(tmp_path / "fresh-process-empty")
        repositories, fresh_worker = _planner_repositories_and_runtime(
            repositories=None,
            queue_runtime=None,
        )
        persisted_dataset = repositories.datasets.get(dataset["id"])
        persisted_exports = persisted_dataset["metadata"]["normalizedExports"]
        assert {
            item["objectId"]: (item["storageKey"], item["contentHash"])
            for item in persisted_exports
        } == upload_exports
        assert get_phase2_runtime().datasets == {}

        executed = fresh_worker.handle_job(planned["job_id"])
        assert executed.status == "completed", executed.message
        tool_calls = repositories.tool_calls.list_for_job(planned["job_id"])
        artifacts = repositories.artifacts.list_for_job(planned["job_id"])
        assert tool_calls
        assert artifacts
        assert all(item.get("storageKey") for item in artifacts)
        assert all(client_s3.head_object(Bucket=bucket, Key=item["storageKey"]) for item in artifacts)

        storage = create_artifact_storage_from_settings(load_settings())
        resolver = DurableObjectStoreResolver(repositories=repositories, artifact_storage=storage)
        source_export = persisted_exports[0]
        source_key = source_export["storageKey"]
        source_bytes = storage.get_bytes(source_key)

        client_s3.delete_object(Bucket=bucket, Key=source_key)
        with pytest.raises(ValueError, match="payload is unavailable"):
            resolver.resolve(dataset["id"], profile_id=profile["profileId"])
        storage.put_bytes(source_key, source_bytes, content_type="application/json")

        storage.put_bytes(source_key, b"{}", content_type="application/json")
        with pytest.raises(ValueError, match="payload checksum mismatch"):
            resolver.resolve(dataset["id"], profile_id=profile["profileId"])
        storage.put_bytes(source_key, source_bytes, content_type="application/json")

        original_metadata = persisted_dataset["metadata"]
        foreign_exports = [
            {
                **item,
                "storageKey": item["storageKey"].replace(
                    f"projects/{project['id']}/", "projects/foreign_project/"
                ),
            }
            for item in persisted_exports
        ]
        foreign_repositories = SimpleNamespace(
            datasets=SimpleNamespace(
                get=lambda _dataset_id: {
                    **persisted_dataset,
                    "metadata": {**original_metadata, "normalizedExports": foreign_exports},
                }
            ),
            data_profiles=repositories.data_profiles,
        )
        with pytest.raises(ValueError, match="outside the persisted dataset scope"):
            DurableObjectStoreResolver(
                repositories=foreign_repositories,
                artifact_storage=storage,
            ).resolve(dataset["id"], profile_id=profile["profileId"])
        with pytest.raises(LookupError, match="DataProfile is unavailable"):
            resolver.resolve(dataset["id"], profile_id="profile_stale")
    finally:
        if queued_job_id:
            queued_job = queue.fetch_job(queued_job_id)
            if queued_job is not None:
                queued_job.delete()
        reset_phase2_runtime()
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
