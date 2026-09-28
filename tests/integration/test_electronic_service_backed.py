from __future__ import annotations

import json
import os
from pathlib import Path
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
import pytest
from tests.integration.alembic_helpers import current_alembic_head
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.main import create_app
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from tests.integration.test_workspace_service_backed import _minio_client, _redis_smoke, _required_postgres_url, _schema_database_url
from tests.test_electronic_band_dos import _execute, band_resource, dos_resource


@pytest.mark.integration
def test_phase10n5_postgres_redis_minio_band_dos_closure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n5_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = minio = None
    bucket = ""
    keys: list[str] = []
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
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == current_alembic_head()
        _redis_smoke(f"n5-{suffix}")

        generated = []
        for tool_id, resource in (("electronic.band_structure", band_resource()), ("electronic.dos", dos_resource())):
            root = tmp_path / tool_id.replace(".", "_")
            payload = _execute(root, tool_id, resource)
            artifact_file = next(root.rglob("*.json"))
            generated.append((tool_id, root, payload, artifact_file))
        minio, bucket = _minio_client()
        project_id, dataset_id, job_id = f"project_n5_{suffix}", f"dataset_n5_{suffix}", f"job_n5_{suffix}"
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": project_id, "name": "N5 supplied electronic output", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "Electronic", "status": "profile_ready", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "status": "completed", "createdBy": "user_local"})
        for index, (tool_id, _root, payload, artifact_file) in enumerate(generated, 1):
            artifact_id, call_id = f"artifact_n5_{index}_{suffix}", f"call_n5_{index}_{suffix}"
            key = f"phase10n5/{suffix}/{artifact_id}.json"
            keys.append(key)
            content = artifact_file.read_bytes()
            import hashlib
            checksum = hashlib.sha256(content).hexdigest()
            minio.put_object(Bucket=bucket, Key=key, Body=content, ContentType="application/json")
            repos.tool_calls.save({"id": call_id, "jobId": job_id, "stepId": f"step_{index}", "toolId": tool_id, "status": "completed", "params": payload["resolvedParameters"]})
            repos.artifacts.save({"id": artifact_id, "projectId": project_id, "datasetId": dataset_id, "jobId": job_id, "toolCallId": call_id, "type": "table_json", "version": "1", "name": f"{artifact_id}.json", "storageKey": key, "storageProvider": "minio", "bucket": bucket, "sizeBytes": len(content), "contentType": "application/json", "contentHash": checksum, "sha256": checksum, "metadata": {"artifactContractVersion": payload["schemaVersion"]}})
        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        response = TestClient(create_app()).get(f"/planner/jobs/{job_id}/artifacts/artifact_n5_2_{suffix}/content")
        assert response.status_code == 200
        assert json.loads(response.content)["runtimeDiagnostics"]["dosGenerationFromBands"] is False
    finally:
        if minio is not None:
            for key in keys:
                try:
                    minio.delete_object(Bucket=bucket, Key=key)
                except Exception:
                    pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
