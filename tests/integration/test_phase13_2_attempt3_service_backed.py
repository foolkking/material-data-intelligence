from __future__ import annotations

import os
import json
from pathlib import Path
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
from mdi_api.phase2_runtime import get_phase2_runtime, reset_phase2_runtime
from mdi_api.routers.planner import _planner_repositories_and_runtime
from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _required_postgres_url,
    _schema_database_url,
)


@pytest.mark.integration
def test_phase13_2_attempt3_real_upload_to_fresh_worker_gap(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Preserve the Attempt 3 P0 at the real upload/worker process boundary."""

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
        with engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, "
                "name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT "
                "CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            ))
            connection.execute(text(
                "CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, "
                "email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, "
                "is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL "
                "DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            ))

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
        assert queue.fetch_job(planned["job_id"]) is not None

        phase2_record = get_phase2_runtime().datasets[dataset["id"]]
        assert phase2_record.normalized_exports
        repositories, fresh_worker = _planner_repositories_and_runtime(
            repositories=None,
            queue_runtime=None,
        )
        persisted_dataset = repositories.datasets.get(dataset["id"])
        assert persisted_dataset["metadata"].get("normalizedExports") in (None, [])

        executed = fresh_worker.handle_job(planned["job_id"])
        assert executed.status == "failed"
        assert "Unknown input ref: profile" in executed.message
        assert repositories.artifacts.list_for_job(planned["job_id"]) == []
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
