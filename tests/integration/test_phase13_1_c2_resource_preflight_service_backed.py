from __future__ import annotations

import os
import uuid
from pathlib import Path

from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
import pytest
from redis import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.artifact_storage import S3CompatibleArtifactStorage
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_tool_registry import load_manifests
from mdi_workers import preflight_execution_resources
from mdi_workers.object_store import DurableObjectStoreResolver
from scripts.generate_phase13_1_product_entry_fix_forward import DEMO_SPECS
from scripts.generate_phase13_1_runtime_resource_fix_forward_2 import _c2_record
from tests.integration.test_phase10m1_workspace_service_backed import (
    _minio_client,
    _redis_smoke,
    _required_postgres_url,
    _schema_database_url,
)


@pytest.mark.integration
def test_phase13_1_postgres_redis_minio_c2_exact_resource_resolution(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase13c2_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    storage = None
    keys: list[str] = []
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        previous_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = schema_url
        try:
            alembic_upgrade(config, "head")
        finally:
            if previous_url is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = previous_url
        engine = create_engine(schema_url, future=True)
        _redis_smoke(f"phase13-c2-{suffix}")
        redis = Redis.from_url(os.environ["REDIS_URL"])
        queue_before = int(redis.llen("mdi:jobs"))
        client, bucket = _minio_client()
        storage = S3CompatibleArtifactStorage(bucket=bucket, client=client)
        repositories = SqlAlchemyRepositoryBundle.create(engine)

        for spec in (DEMO_SPECS[4], DEMO_SPECS[6]):
            _, _, plan, profile, objects = _c2_record(spec)
            project_id = f"project_{spec['demoId'].lower()}_{suffix}"
            exports = []
            for obj in objects:
                base = f"projects/{project_id}/datasets/{profile.datasetId}/normalized/{obj.id}"
                data_key = f"{base}/data.json"
                metadata_key = f"{base}/metadata.json"
                stored = storage.put_json(data_key, obj.payload)
                storage.put_json(metadata_key, {
                    "objectId": obj.id,
                    "contentHash": stored.sha256,
                    "metadata": obj.metadata,
                    "provenance": {"objectType": obj.object_type.value},
                })
                keys.extend((data_key, metadata_key))
                exports.append({"objectId": obj.id, "storageKey": data_key, "metadataKey": metadata_key, "objectHash": obj.hash, "contentHash": stored.sha256})
            repositories.projects.save({"id": project_id, "name": project_id, "createdBy": "phase13_c2"})
            repositories.datasets.save({
                "id": profile.datasetId,
                "projectId": project_id,
                "name": profile.datasetId,
                "status": "profile_ready",
                "createdBy": "phase13_c2",
                "normalizedExports": exports,
            })
            repositories.data_profiles.save(profile)
            resolved = DurableObjectStoreResolver(repositories=repositories, artifact_storage=storage).resolve(
                profile.datasetId,
                profile_id=profile.profileId,
            )
            assert resolved is not None
            result = preflight_execution_resources(
                plan,
                object_store=resolved,
                registry=load_manifests(),
                dataset_id=profile.datasetId,
            )
            assert result.ok, result.issues
        assert int(redis.llen("mdi:jobs")) == queue_before
    finally:
        if storage is not None:
            for key in keys:
                try:
                    storage._require_client().delete_object(Bucket=storage.bucket, Key=key)
                except Exception:
                    pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
