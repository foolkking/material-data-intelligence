from __future__ import annotations

from hashlib import sha256
import json
import os
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_llm.grounded_interpretation import ARTIFACT_PROJECTOR_CONTRACTS
from mdi_tool_registry import load_manifests
from mdi_tool_registry.dependency_ports import build_artifact_port_inventory
from tests.integration.test_phase10m1_workspace_service_backed import _minio_client, _redis_smoke, _required_postgres_url, _schema_database_url


TOOLS = (
    "structure.coordination_crystalnn", "structure.coordination_voronoinn",
    "structure.local_environment_polyhedra", "structure.experimental_xrd_comparison",
    "trajectory.rdf", "trajectory.msd", "trajectory.diffusion",
    "electronic.band_structure", "electronic.dos",
)


@pytest.mark.integration
def test_phase10n6_postgres_redis_minio_professional_integration_closure(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10n6_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = minio = None
    bucket = key = ""
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
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0008_phase_d_r1_namespace"
        _redis_smoke(f"n6-{suffix}")

        registry = load_manifests()
        ports = build_artifact_port_inventory(registry)
        inventory = {tool_id: {"version": registry.get_tool_by_id(tool_id).version, "adapter": registry.get_tool_by_id(tool_id).adapter, "ports": ports[tool_id].model_dump(mode="json"), "projector": (tool_id, "table_json") in ARTIFACT_PROJECTOR_CONTRACTS} for tool_id in TOOLS}
        assert len(registry.tools) == 62 and all(item["projector"] for item in inventory.values())
        assert ports["structure.local_environment_polyhedra"].inputPorts[0].portId == "coordination"
        assert ports["trajectory.diffusion"].inputPorts[0].portId == "msd"

        payload = json.dumps({"schemaVersion": "phase10n6.service_closure.v1", "registry": 62, "profile": "2.4", "tools": inventory}, sort_keys=True, separators=(",", ":")).encode()
        checksum = sha256(payload).hexdigest()
        minio, bucket = _minio_client()
        key = f"phase10n6/{suffix}/professional-inventory.json"
        minio.put_object(Bucket=bucket, Key=key, Body=payload, ContentType="application/json")
        assert minio.get_object(Bucket=bucket, Key=key)["Body"].read() == payload

        project_id, dataset_id, job_id = f"project_n6_{suffix}", f"dataset_n6_{suffix}", f"job_n6_{suffix}"
        repos = SqlAlchemyRepositoryBundle.create(engine)
        repos.projects.save({"id": project_id, "name": "N6 integration closure", "createdBy": "phase10n6_ci"})
        repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": "Professional inventory", "status": "profile_ready", "createdBy": "phase10n6_ci"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "datasetId": dataset_id, "status": "completed", "createdBy": "phase10n6_ci"})
        stored = repos.jobs.get(job_id)
        assert stored and stored["projectId"] == project_id and stored["status"] == "completed"
        assert checksum == sha256(minio.get_object(Bucket=bucket, Key=key)["Body"].read()).hexdigest()
    finally:
        if minio is not None and key:
            try: minio.delete_object(Bucket=bucket, Key=key)
            except Exception: pass
        if engine is not None: engine.dispose()
        try:
            with base_engine.begin() as connection: connection.execute(DropSchema(schema_name, cascade=True))
        finally: base_engine.dispose()
