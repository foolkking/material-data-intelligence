from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import uuid

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.schema import CreateSchema, DropSchema

from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _redis_smoke,
    _required_postgres_url,
    _schema_database_url,
)


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_phase10m7_postgres_redis_minio_workspace_integration_closure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m7_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    bucket = ""
    object_key = f"phase10m7/{suffix}/identity-continuity.json"
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
        tables = set(inspect(engine).get_table_names())
        assert {
            "data_profiles", "analysis_intents", "capability_eligibility_resolutions",
            "capability_planning_decisions", "analysis_plans", "jobs",
            "tool_calls", "dependency_execution_records", "artifacts",
            "scientific_evidence_bundles", "scientific_interpretations",
            "scientific_interpretation_claims", "scientific_interpretation_evidence_links",
            "scientific_workspaces", "workspace_panels",
            "workspace_layout_revisions", "reports", "visualization_recipes",
        }.issubset(tables)

        _redis_smoke(f"m7-{suffix}")
        minio, bucket = _minio_client()
        payload = json.dumps(
            {"schemaVersion": "phase10m7.service.v1", "identityContinuity": True},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        checksum = sha256(payload).hexdigest()
        minio.put_object(Bucket=bucket, Key=object_key, Body=payload, ContentType="application/json")
        response = minio.get_object(Bucket=bucket, Key=object_key)
        assert sha256(response["Body"].read()).hexdigest() == checksum

        retained = json.loads(
            (ROOT / "docs/phase10l/evidence/phase10l5_natural_language_closure/deepseek_real_verification.json").read_text(encoding="utf-8")
        )
        assert retained["provider"] == "deepseek"
        assert retained["totalRealCallCount"] >= 1
        assert len(retained["cases"]) == 5
        assert all(item["verdict"] == "PASS" for item in retained["cases"])
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
