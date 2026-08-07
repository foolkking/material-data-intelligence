from __future__ import annotations

import json
import os
from pathlib import Path
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from pymatgen.core import Lattice, Structure
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_adapters import ToolExecutionContext
from mdi_adapters.executor import execute_tool_request
from mdi_api.main import create_app
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_schemas import InputRef, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests

from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _redis_smoke,
    _required_postgres_url,
    _schema_database_url,
)


@pytest.mark.integration
def test_phase10n1_postgres_redis_minio_coordination_artifact_closure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n1_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_key = f"phase10n1/{suffix}/crystalnn-coordination.json"
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
        # The historical persistence baseline predates actor tables. Create
        # only the repository actor fixtures; N1 adds no migration or table.
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS organizations ("
                    "id VARCHAR(64) PRIMARY KEY, name VARCHAR(160) NOT NULL, "
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                    "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
            )
            connection.execute(
                text(
                    "CREATE TABLE IF NOT EXISTS users ("
                    "id VARCHAR(64) PRIMARY KEY, email VARCHAR(320) NOT NULL UNIQUE, "
                    "display_name VARCHAR(160) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, "
                    "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                    "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
            )

        _redis_smoke(f"n1-{suffix}")
        registry = load_manifests()
        tool = registry.get_tool_by_id("structure.coordination_crystalnn")
        structure = Structure(Lattice.cubic(3.57), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
        context = ToolExecutionContext(
            job_id=f"job_n1_{suffix}",
            project_id=f"project_n1_{suffix}",
            dataset_id=f"dataset_n1_{suffix}",
            tool_id=tool.toolId,
            tool_version=tool.version,
            adapter_version="0.1.0",
            registry_version=registry.version,
            artifact_root=tmp_path,
            tool_call_id=f"call_n1_{suffix}",
            plan_id=f"plan_n1_{suffix}",
            plan_version="0.1",
            object_store={"structure_resource": structure},
            resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(
            jobId=context.job_id,
            stepId="step_n1",
            toolId=tool.toolId,
            inputRefs=[InputRef(refType="normalized_object", ref="structure_resource", objectType=MaterialObjectType.Structure)],
            params={},
            artifactTypes=tool.artifactTypes,
        )
        execution = execute_tool_request(context, request, registry=registry)
        table = next(item for item in execution.artifacts if item.type.value == "table_json")
        payload = (tmp_path / table.storageKey).read_bytes()
        parsed = json.loads(payload)
        assert parsed["schema_version"] == "phase10n1.crystalnn_coordination.v1"
        assert parsed["coverage"]["status"] == "COMPLETE"

        minio, bucket = _minio_client()
        minio.put_object(Bucket=bucket, Key=object_key, Body=payload, ContentType="application/json")
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": context.project_id, "name": "N1 coordination", "createdBy": "user_local"})
        repos.datasets.save({"id": context.dataset_id, "projectId": context.project_id, "name": "N1 structure", "status": "profile_ready", "createdBy": "user_local"})
        repos.jobs.save({"id": context.job_id, "projectId": context.project_id, "datasetId": context.dataset_id, "status": "completed", "createdBy": "user_local"})
        repos.tool_calls.save({"id": context.tool_call_id, "jobId": context.job_id, "stepId": "step_n1", "toolId": tool.toolId, "status": "completed", "params": parsed["resolvedParameters"]})
        artifact_id = f"artifact_n1_{suffix}"
        repos.artifacts.save({
            "id": artifact_id,
            "projectId": context.project_id,
            "datasetId": context.dataset_id,
            "jobId": context.job_id,
            "toolCallId": context.tool_call_id,
            "type": "table_json",
            "version": "phase10n1.crystalnn_coordination.v1",
            "name": "crystalnn-coordination.json",
            "storageKey": object_key,
            "storageProvider": "minio",
            "bucket": bucket,
            "sizeBytes": len(payload),
            "contentType": "application/json",
            "contentHash": table.contentHash,
            "sha256": table.contentHash,
            "metadata": {"toolId": tool.toolId, "toolVersion": tool.version, "artifactContractVersion": parsed["schema_version"]},
        })

        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        client = TestClient(create_app())
        response = client.get(f"/planner/jobs/{context.job_id}/artifacts/{artifact_id}/content")
        assert response.status_code == 200
        assert response.content == payload
        assert response.headers["x-content-sha256"] == table.contentHash
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
