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
def test_phase10n2_postgres_redis_minio_exact_n1_dependency_closure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n2_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_keys: list[str] = []
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

        _redis_smoke(f"n2-{suffix}")
        registry = load_manifests()
        n1_tool = registry.get_tool_by_id("structure.coordination_crystalnn")
        n2_tool = registry.get_tool_by_id("structure.local_environment_polyhedra")
        assert len(registry.tools) == 57
        structure = Structure(Lattice.cubic(3.57), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
        project_id, dataset_id, job_id = (f"project_n2_{suffix}", f"dataset_n2_{suffix}", f"job_n2_{suffix}")

        n1_context = ToolExecutionContext(
            job_id=job_id, project_id=project_id, dataset_id=dataset_id,
            tool_id=n1_tool.toolId, tool_version=n1_tool.version, adapter_version="0.1.0",
            registry_version=registry.version, artifact_root=tmp_path / "n1", tool_call_id=f"call_n1_{suffix}",
            plan_id=f"plan_n2_{suffix}", plan_version="0.2", object_store={"structure": structure},
            resource_limits=n1_tool.resourceLimits,
        )
        n1_execution = execute_tool_request(n1_context, ToolExecutionRequest(
            jobId=job_id, stepId="step_n1", toolId=n1_tool.toolId,
            inputRefs=[InputRef(refType="normalized_object", ref="structure", objectType=MaterialObjectType.Structure)],
            params={}, artifactTypes=["table_json"],
        ), registry=registry)
        n1_table = next(item for item in n1_execution.artifacts if item.type.value == "table_json")
        n1_bytes = (tmp_path / "n1" / n1_table.storageKey).read_bytes()
        n1_payload = json.loads(n1_bytes)
        n1_artifact_id = f"artifact_n1_{suffix}"

        n2_context = ToolExecutionContext(
            job_id=job_id, project_id=project_id, dataset_id=dataset_id,
            tool_id=n2_tool.toolId, tool_version=n2_tool.version, adapter_version="0.1.0",
            registry_version=registry.version, artifact_root=tmp_path / "n2", tool_call_id=f"call_n2_{suffix}",
            plan_id=f"plan_n2_{suffix}", plan_version="0.2",
            object_store={"structure": structure, "coordination": n1_payload},
            artifact_bindings={"coordination": {"artifactId": n1_artifact_id, "checksum": n1_table.contentHash, "artifactContractVersion": n1_payload["schema_version"]}},
            resource_limits=n2_tool.resourceLimits,
        )
        n2_execution = execute_tool_request(n2_context, ToolExecutionRequest(
            jobId=job_id, stepId="step_n2", toolId=n2_tool.toolId,
            inputRefs=[
                InputRef(refType="normalized_object", ref="structure", objectType=MaterialObjectType.Structure),
                InputRef(refType="artifact", ref="coordination", fieldRole="coordination_artifact", objectType=MaterialObjectType.Structure),
            ],
            params={"site_indices": [0]}, artifactTypes=["table_json"],
        ), registry=registry)
        n2_table = next(item for item in n2_execution.artifacts if item.type.value == "table_json")
        n2_bytes = (tmp_path / "n2" / n2_table.storageKey).read_bytes()
        n2_payload = json.loads(n2_bytes)
        assert n2_payload["sourceCoordination"]["artifactId"] == n1_artifact_id
        assert n2_payload["sourceCoordination"]["artifactChecksum"] == n1_table.contentHash
        assert n2_payload["runtimeDiagnostics"]["n1NeighborRecomputation"] is False
        assert n2_payload["runtimeDiagnostics"]["coordinationAlgorithmFallback"] is False

        minio, bucket = _minio_client()
        n1_key = f"phase10n2/{suffix}/n1-coordination.json"
        n2_key = f"phase10n2/{suffix}/n2-local-environment.json"
        object_keys.extend([n1_key, n2_key])
        minio.put_object(Bucket=bucket, Key=n1_key, Body=n1_bytes, ContentType="application/json")
        minio.put_object(Bucket=bucket, Key=n2_key, Body=n2_bytes, ContentType="application/json")

        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": project_id, "name": "N2 local environment", "createdBy": "user_local"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "Periodic structure", "status": "profile_ready", "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "status": "completed", "createdBy": "user_local"})
        repos.tool_calls.save({"id": n1_context.tool_call_id, "jobId": job_id, "stepId": "step_n1", "toolId": n1_tool.toolId, "status": "completed", "params": n1_payload["resolvedParameters"]})
        repos.tool_calls.save({"id": n2_context.tool_call_id, "jobId": job_id, "stepId": "step_n2", "toolId": n2_tool.toolId, "status": "completed", "params": n2_payload["resolvedParameters"]})
        for artifact_id, table, key, name, call_id, contract in (
            (n1_artifact_id, n1_table, n1_key, "n1-coordination.json", n1_context.tool_call_id, n1_payload["schema_version"]),
            (f"artifact_n2_{suffix}", n2_table, n2_key, "n2-local-environment.json", n2_context.tool_call_id, n2_payload["schema_version"]),
        ):
            repos.artifacts.save({
                "id": artifact_id, "projectId": project_id, "datasetId": dataset_id, "jobId": job_id,
                "toolCallId": call_id, "type": "table_json", "version": table.version, "name": name,
                "storageKey": key, "storageProvider": "minio", "bucket": bucket, "sizeBytes": table.sizeBytes,
                "contentType": "application/json", "contentHash": table.contentHash, "sha256": table.contentHash,
                "metadata": {"artifactContractVersion": contract},
            })

        monkeypatch.setenv("MDI_ARTIFACT_BACKEND", "minio")
        client = TestClient(create_app())
        response = client.get(f"/planner/jobs/{job_id}/artifacts/artifact_n2_{suffix}/content")
        assert response.status_code == 200
        assert response.content == n2_bytes
        assert response.headers["x-content-sha256"] == n2_table.contentHash
    finally:
        if minio is not None:
            for key in object_keys:
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
