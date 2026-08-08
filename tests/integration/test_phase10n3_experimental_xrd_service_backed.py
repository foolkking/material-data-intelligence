from __future__ import annotations

import json
import os
from pathlib import Path
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.main import create_app
from mdi_api.repositories import SqlAlchemyRepositoryBundle

from tests.integration.test_phase10m1_workspace_service_backed import _minio_client, _redis_smoke, _required_postgres_url, _schema_database_url
from tests.test_phase10n3_experimental_xrd import _run


@pytest.mark.integration
def test_phase10n3_postgres_redis_minio_theoretical_xrd_comparison_closure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n3_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_key = f"phase10n3/{suffix}/comparison.json"
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")
        engine = create_engine(schema_url, future=True)
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0007_phase10m1_workspace_domain"
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
        _redis_smoke(f"n3-{suffix}")
        execution, payload = _run(tmp_path / "adapter")
        table = next(item for item in execution.artifacts if item.type.value == "table_json")
        content = (tmp_path / "adapter" / table.storageKey).read_bytes()
        assert payload["theoreticalArtifact"]["artifactContractVersion"] == "phase10e4.xrd_pattern.v1"
        assert payload["runtimeDiagnostics"]["theoreticalXrdReimplementation"] is False

        minio, bucket = _minio_client()
        minio.put_object(Bucket=bucket, Key=object_key, Body=content, ContentType="application/json")
        project_id, dataset_id, job_id, artifact_id = ("project_n3", "dataset_n3", "job_n3", f"artifact_n3_{suffix}")
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": project_id, "name": "N3 XRD comparison", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "Experimental XRD", "status": "profile_ready", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "status": "completed", "createdBy": "user_local"})
        repos.tool_calls.save({"id": "call_n3", "jobId": job_id, "stepId": "step_n3", "toolId": "structure.experimental_xrd_comparison", "status": "completed", "params": payload["resolvedParameters"]})
        repos.artifacts.save({"id": artifact_id, "projectId": project_id, "datasetId": dataset_id, "jobId": job_id, "toolCallId": "call_n3", "type": "table_json", "version": table.version, "name": "comparison.json", "storageKey": object_key, "storageProvider": "minio", "bucket": bucket, "sizeBytes": table.sizeBytes, "contentType": "application/json", "contentHash": table.contentHash, "sha256": table.contentHash, "metadata": {"artifactContractVersion": payload["schema_version"]}})
        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        response = TestClient(create_app()).get(f"/planner/jobs/{job_id}/artifacts/{artifact_id}/content")
        assert response.status_code == 200 and response.content == content
        assert response.headers["x-content-sha256"] == table.contentHash
        assert json.loads(response.content)["coverage"]["matchedPairs"] == 2
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
