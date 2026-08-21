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
from tests.test_phase10n4_trajectory_analytics import _execute, _payload, _trajectory


@pytest.mark.integration
def test_phase10n4_postgres_redis_minio_msd_diffusion_dependency_closure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n4_{suffix}"
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
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0014_research_session_run_bindings"
        _redis_smoke(f"n4-{suffix}")

        msd_root = tmp_path / "msd"
        msd_artifact = _execute(msd_root, "trajectory.msd", _trajectory(), {"max_lag_count": 3})[0]
        msd_payload = _payload(msd_root, msd_artifact)
        msd_id = f"artifact_msd_{suffix}"
        diffusion_root = tmp_path / "diffusion"
        binding = {"input": {"artifactId": msd_id, "checksum": msd_artifact.contentHash}}
        diffusion_artifact = _execute(diffusion_root, "trajectory.diffusion", msd_payload, {"fit_start_time_ps": 1.0, "fit_end_time_ps": 3.0, "minimum_fit_points": 3, "minimum_fit_duration_ps": 1.0}, binding)[0]
        diffusion_payload = _payload(diffusion_root, diffusion_artifact)
        assert diffusion_payload["sourceMsd"]["artifactId"] == msd_id
        assert diffusion_payload["runtimeDiagnostics"] == {"rawTrajectoryReads": False, "msdRecomputation": False, "frontendFit": False, "automaticWindowOptimization": False}

        minio, bucket = _minio_client()
        payloads = [(msd_id, msd_artifact, msd_root, msd_payload), (f"artifact_diffusion_{suffix}", diffusion_artifact, diffusion_root, diffusion_payload)]
        for artifact_id, artifact, root, payload in payloads:
            key = f"phase10n4/{suffix}/{artifact_id}.json"
            keys.append(key)
            content = (root / artifact.storageKey).read_bytes()
            minio.put_object(Bucket=bucket, Key=key, Body=content, ContentType="application/json")
            payload["_serviceKey"] = key

        project_id, dataset_id, job_id = f"project_n4_{suffix}", f"dataset_n4_{suffix}", f"job_n4_{suffix}"
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": project_id, "name": "N4 trajectory analytics", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "Trajectory", "status": "profile_ready", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "status": "completed", "createdBy": "user_local"})
        for index, (artifact_id, artifact, _root, payload) in enumerate(payloads, 1):
            call_id = f"call_n4_{index}_{suffix}"
            repos.tool_calls.save({"id": call_id, "jobId": job_id, "stepId": f"step_{index}", "toolId": payload["tool"]["toolId"], "status": "completed", "params": payload["resolvedParameters"]})
            repos.artifacts.save({"id": artifact_id, "projectId": project_id, "datasetId": dataset_id, "jobId": job_id, "toolCallId": call_id, "type": "table_json", "version": artifact.version, "name": f"{artifact_id}.json", "storageKey": payload.pop("_serviceKey"), "storageProvider": "minio", "bucket": bucket, "sizeBytes": artifact.sizeBytes, "contentType": "application/json", "contentHash": artifact.contentHash, "sha256": artifact.contentHash, "metadata": {"artifactContractVersion": payload["schema_version"]}})

        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        response = TestClient(create_app()).get(f"/planner/jobs/{job_id}/artifacts/artifact_diffusion_{suffix}/content")
        assert response.status_code == 200
        assert response.headers["x-content-sha256"] == diffusion_artifact.contentHash
        assert json.loads(response.content)["sourceMsd"]["artifactChecksum"] == msd_artifact.contentHash
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
