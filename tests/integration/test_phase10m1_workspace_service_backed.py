from __future__ import annotations

from hashlib import sha256
import json
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateSchema, DropSchema

from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_api.main import create_app
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_api.workspaces import WorkspaceProjectionService
from mdi_llm import MockLLMProvider
from mdi_schemas import DataProfile
from mdi_schemas.workspace import (
    WorkspaceSelectionContext,
    WorkspaceSelectionKind,
    WorkspaceSelectionRef,
)

from tests.test_phase10l3_planner_api import _phonon_profile


def _required_postgres_url() -> str:
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url or not make_url(database_url).get_backend_name().startswith("postgresql"):
        raise RuntimeError(
            "A PostgreSQL MDI_TEST_DATABASE_URL or DATABASE_URL is required for "
            "the enabled Phase 10M-1 integration gate"
        )
    return database_url


def _schema_database_url(database_url: str, schema_name: str) -> str:
    url = make_url(database_url)
    query = dict(url.query)
    query["options"] = f"-csearch_path={schema_name}"
    return url.set(query=query).render_as_string(hide_password=False)


def _exact_phonon_profile(*, dataset_id: str, profile_id: str, suffix: str) -> DataProfile:
    payload = _phonon_profile().model_dump(mode="json")
    payload["datasetId"] = dataset_id
    payload["profileId"] = profile_id
    payload["version"] = f"phase10m1-{suffix}"
    payload["sampleIdentity"]["datasetVersion"] = f"{dataset_id}:v1"
    semantic_payload = {
        "datasetId": dataset_id,
        "datasetVersion": payload["version"],
        "semanticRulesVersion": payload["semanticRulesVersion"],
        "objectHashes": sorted(
            item.get("hash") or item["objectHash"] for item in payload["objects"]
        ),
        "semanticColumns": payload["semanticColumns"],
        "semanticGroups": payload["semanticGroups"],
        "resourceSemantics": payload["resourceSemantics"],
        "analysisReadiness": payload["analysisReadiness"],
        "sampleIdentity": payload["sampleIdentity"],
        "profileCoverage": payload["profileCoverage"],
    }
    payload["semanticHash"] = sha256(
        json.dumps(
            semantic_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
    ).hexdigest()
    return DataProfile.model_validate(payload)


def _redis_smoke(suffix: str) -> None:
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        raise RuntimeError("REDIS_URL is required for the enabled Phase 10M-1 integration gate")
    try:
        from redis import Redis

        client = Redis.from_url(redis_url)
        assert client.ping() is True
        key = f"mdi:phase10m1:{suffix}"
        assert client.set(key, "workspace-service-backed", ex=60) is True
        assert client.get(key) == b"workspace-service-backed"
        assert client.delete(key) == 1
    except Exception as exc:
        raise RuntimeError(
            "Redis is not reachable for the enabled Phase 10M-1 integration gate"
        ) from exc


def _minio_client() -> tuple[object, str]:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
    secret_key = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    try:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="us-east-1",
        )
        try:
            client.head_bucket(Bucket=bucket)
        except Exception:
            client.create_bucket(Bucket=bucket)
        return client, bucket
    except Exception as exc:
        raise RuntimeError(
            "MinIO is not reachable for the enabled Phase 10M-1 integration gate"
        ) from exc


@pytest.mark.integration
def test_phase10m1_postgres_redis_minio_workspace_domain_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip(
            "Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running"
        )

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m1_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    minio_bucket = ""
    minio_key = f"phase10m1/{suffix}/workspace-source.json"

    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))

        # Alembic env.py intentionally gives DATABASE_URL precedence. Point it
        # at the isolated schema so this is a fresh base-to-0007 migration.
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        monkeypatch.delenv("POSTGRES_HOST", raising=False)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")

        engine = create_engine(schema_url, future=True)
        db_inspector = inspect(engine)
        assert {
            "scientific_workspaces",
            "workspace_panels",
            "workspace_layout_revisions",
        }.issubset(db_inspector.get_table_names())
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
                "0007_phase10m1_workspace_domain"
            )

        workspace_foreign_keys = db_inspector.get_foreign_keys("scientific_workspaces")
        source_job_fk = next(
            item
            for item in workspace_foreign_keys
            if item["constrained_columns"] == ["source_job_id"]
        )
        assert source_job_fk["referred_table"] == "jobs"
        assert source_job_fk.get("options", {}).get("ondelete", "").upper() == "RESTRICT"

        alembic_downgrade(config, "0006_phase10l4_interpretation")
        downgraded_tables = set(inspect(engine).get_table_names())
        assert {
            "scientific_workspaces",
            "workspace_panels",
            "workspace_layout_revisions",
        }.isdisjoint(downgraded_tables)
        alembic_upgrade(config, "head")
        upgraded_inspector = inspect(engine)
        assert {
            "scientific_workspaces",
            "workspace_panels",
            "workspace_layout_revisions",
        }.issubset(upgraded_inspector.get_table_names())
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
                "0007_phase10m1_workspace_domain"
            )

        # The historical baseline predates these actor tables. Create only the
        # repository actor fixtures explicitly; Workspace tables were already
        # proven by Alembic above. This is not a migration substitute.
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

        _redis_smoke(suffix)
        minio, minio_bucket = _minio_client()
        artifact_payload = (
            b'{"contract":"phase10h.phonon_band_dos.v1","points":4}'
        )
        minio.put_object(
            Bucket=minio_bucket,
            Key=minio_key,
            Body=artifact_payload,
            ContentType="application/json",
        )
        response = minio.get_object(Bucket=minio_bucket, Key=minio_key)
        try:
            assert response["Body"].read() == artifact_payload
        finally:
            response["Body"].close()

        repos = SqlAlchemyRepositoryBundle.create(engine)
        actor_id = f"phase10m1_ci_{suffix}"
        project_id = f"project_m1_{suffix}"
        dataset_id = f"dataset_m1_{suffix}"
        profile_id = f"profile_m1_{suffix}"
        project_record = repos.projects.save(
            {"id": project_id, "name": project_id, "createdBy": actor_id}
        )
        dataset_record = repos.datasets.save(
            {
                "id": dataset_id,
                "projectId": project_id,
                "name": dataset_id,
                "status": "profile_ready",
                "createdBy": actor_id,
            }
        )
        assert project_record["id"] == project_id
        assert project_record["createdBy"] == actor_id
        assert dataset_record["id"] == dataset_id
        assert dataset_record["projectId"] == project_id
        profile = _exact_phonon_profile(
            dataset_id=dataset_id,
            profile_id=profile_id,
            suffix=suffix,
        )
        repos.data_profiles.save(profile)

        planned = planner_jobs(
            PlannerJobsRequest(
                userPrompt="Create a combined phonon band and density of states product.",
                projectId=project_id,
                datasetId=dataset_id,
                profileId=profile_id,
                intentSchemaVersion="1.0",
                selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
                provider="mock",
            ),
            provider=MockLLMProvider(
                fixed_plan={"invalid": "legacy planner path must not execute"}
            ),
            repositories=repos,
        )
        assert planned.ok is True
        assert planned.job_id and planned.plan_id and planned.plan_hash
        assert planned.plan_schema_version == "0.2"
        repos.jobs.set_status(planned.job_id, "queued")
        repos.jobs.set_status(planned.job_id, "running")
        repos.jobs.set_status(planned.job_id, "completed")

        payload_hash = sha256(artifact_payload).hexdigest()
        artifact_id = f"artifact_m1_{suffix}"
        private_payload_marker = f"PRIVATE_ARTIFACT_PAYLOAD_{suffix}"
        artifact_record = repos.artifacts.save(
            {
                "id": artifact_id,
                "projectId": project_id,
                "datasetId": dataset_id,
                "jobId": planned.job_id,
                "type": "phonon_band_dos_json",
                "name": "phonon-band-dos.json",
                "version": "phase10h.phonon_band_dos.v1",
                "storageKey": minio_key,
                "storageProvider": "minio",
                "bucket": minio_bucket,
                "sizeBytes": len(artifact_payload),
                "contentType": "application/json",
                "contentHash": payload_hash,
                "sha256": payload_hash,
                "metadata": {
                    "toolId": "phonon.band_dos",
                    "toolVersion": "1.0",
                    "profileId": profile_id,
                    "createdAt": "2026-08-01T00:00:00+00:00",
                    "provenance": {
                        "artifactContractVersion": "phase10h.phonon_band_dos.v1",
                        "mediaType": "application/json",
                    },
                    "rawPayload": private_payload_marker,
                },
            }
        )
        job_record = repos.jobs.get(planned.job_id)
        assert job_record["id"] == planned.job_id
        assert job_record["projectId"] == project_id
        assert job_record["datasetId"] == dataset_id
        assert job_record["planId"] == planned.plan_id
        assert job_record["status"] == "completed"
        assert artifact_record["id"] == artifact_id
        assert artifact_record["projectId"] == project_id
        assert artifact_record["datasetId"] == dataset_id
        assert artifact_record["jobId"] == planned.job_id
        assert artifact_record["storageProvider"] == "minio"
        assert artifact_record["contentHash"] == payload_hash
        assert artifact_record["sha256"] == payload_hash
        assert artifact_record["sizeBytes"] == len(artifact_payload)

        service = WorkspaceProjectionService(repos)
        first, created = service.project_job(
            source_job_id=planned.job_id,
            created_by=actor_id,
            title="Service-backed scientific workspace",
        )
        replay, replay_created = service.project_job(
            source_job_id=planned.job_id,
            created_by=actor_id,
            title="Service-backed scientific workspace",
        )
        workspace_id = first.body["workspace"]["workspaceId"]
        assert created is True and replay_created is False
        assert replay.body["workspace"]["workspaceId"] == workspace_id
        assert len(repos.workspaces.list_by_project(project_id)) == 1
        stored = repos.workspaces.get(workspace_id, project_id=project_id)
        assert stored["sourceJobId"] == planned.job_id
        assert stored["planId"] == planned.plan_id
        assert stored["planHash"] == planned.plan_hash
        assert stored["profileId"] == profile_id
        assert stored["profileSemanticHash"] == profile.semanticHash
        assert any(
            source["sourceId"] == artifact_id
            for panel in first.body["panels"]
            for source in panel["sourceRefs"]
        )

        snapshot_json = json.dumps(first.body, sort_keys=True)
        assert private_payload_marker not in snapshot_json
        assert minio_key not in snapshot_json
        assert minio_bucket not in snapshot_json
        assert "storageKey" not in snapshot_json
        assert "rawPayload" not in snapshot_json
        assert first.body["sourceSummary"]["metadataOnly"] is True

        patched = service.patch_workspace(
            workspace_id=workspace_id,
            expected_revision=0,
            changes={"title": "Patched service-backed workspace"},
            updated_by=actor_id,
        )
        assert patched.body["workspace"]["title"] == "Patched service-backed workspace"
        assert patched.body["workspace"]["revision"] == 1
        assert repos.workspaces.get(workspace_id, project_id=project_id)["revision"] == 1
        history = repos.workspaces.list_layout_revisions(
            workspace_id, project_id=project_id
        )
        assert [item["revision"] for item in history] == [0, 1]
        assert repos.workspaces.get_layout_revision(
            workspace_id, 1, project_id=project_id
        )["semanticHash"] == history[1]["semanticHash"]

        # Isolate the M1 source-job FK from older job-linked tables: this
        # legacy projection has no plan, Artifact, ToolCall, or execution row.
        restrict_job_id = f"job_m1_restrict_{suffix}"
        repos.jobs.save(
            {
                "id": restrict_job_id,
                "projectId": project_id,
                "status": "completed",
                "kind": "analysis",
                "createdBy": actor_id,
            }
        )
        restricted, restricted_created = service.project_job(
            source_job_id=restrict_job_id,
            created_by=actor_id,
            title="Restrict verification workspace",
        )
        assert restricted_created is True
        assert restricted.body["workspace"]["sourceJobId"] == restrict_job_id
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(
                    text("DELETE FROM jobs WHERE id = :job_id"),
                    {"job_id": restrict_job_id},
                )
        assert repos.jobs.get(restrict_job_id)["id"] == restrict_job_id

        minio.delete_object(Bucket=minio_bucket, Key=minio_key)
        assert minio.list_objects_v2(
            Bucket=minio_bucket, Prefix=minio_key
        ).get("KeyCount", 0) == 0
        minio = None
    finally:
        if minio is not None:
            try:
                minio.delete_object(Bucket=minio_bucket, Key=minio_key)
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()


@pytest.mark.integration
def test_phase10m2_postgres_redis_minio_workspace_shell_api_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise the exact metadata APIs consumed by the M2 browser shell."""

    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m2_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    minio_bucket = ""
    minio_key = f"phase10m2/{suffix}/metadata-source.json"
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        monkeypatch.delenv("POSTGRES_HOST", raising=False)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")
        engine = create_engine(schema_url, future=True)
        db_inspector = inspect(engine)
        assert {
            "scientific_workspaces",
            "workspace_panels",
            "workspace_layout_revisions",
        }.issubset(db_inspector.get_table_names())
        with engine.connect() as connection:
            assert connection.execute(text("SELECT current_schema()")).scalar_one() == schema_name
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == (
                "0007_phase10m1_workspace_domain"
            )
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))

        _redis_smoke(f"m2-{suffix}")
        minio, minio_bucket = _minio_client()
        payload = b'{"contract":"phase10m2.metadata-source.v1"}'
        minio.put_object(Bucket=minio_bucket, Key=minio_key, Body=payload, ContentType="application/json")

        repos = SqlAlchemyRepositoryBundle.create(engine)
        monkeypatch.setattr(
            "mdi_api.routers.workspaces._repositories",
            lambda: repos,
        )
        monkeypatch.setattr(
            "mdi_api.routers.workspaces._service",
            lambda: WorkspaceProjectionService(repos),
        )
        project_id = f"project_m2_{suffix}"
        job_id = f"job_m2_{suffix}"
        repos.projects.save({"id": project_id, "name": project_id, "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "status": "completed", "kind": "analysis", "createdBy": "user_local"})

        client = TestClient(create_app())
        try:
            before = client.get(f"/projects/{project_id}/workspaces")
            candidates = client.get(f"/projects/{project_id}/analysis-jobs")
            assert before.status_code == 200, before.json()
            assert candidates.status_code == 200, candidates.json()
            assert before.json()["items"] == []
            assert candidates.json()["items"][0]["jobId"] == job_id
            assert client.get("/workspaces/workspace_missing").status_code == 404
            assert client.get(f"/projects/{project_id}/workspaces").json()["items"] == []

            created = client.post(
                "/workspaces",
                headers={"Idempotency-Key": f"phase10m2-{suffix}"},
                json={"sourceJobId": job_id, "title": "Service-backed Workspace shell"},
            )
            assert created.status_code == 201
            workspace_id = created.json()["workspace"]["workspaceId"]
            etag = created.headers["etag"]
            assert created.json()["sourceSummary"]["metadataOnly"] is True
            assert "payload" not in json.dumps(created.json()).lower()
            assert minio_key not in json.dumps(created.json())

            loaded = client.get(f"/workspaces/{workspace_id}")
            panels = client.get(f"/workspaces/{workspace_id}/panels")
            history = client.get(f"/workspaces/{workspace_id}/layout-revisions")
            listed = client.get(f"/projects/{project_id}/workspaces")
            unchanged = client.get(f"/workspaces/{workspace_id}", headers={"If-None-Match": etag})
            assert loaded.status_code == panels.status_code == history.status_code == listed.status_code == 200
            assert unchanged.status_code == 304
            assert loaded.json()["workspace"]["workspaceId"] == workspace_id
            assert loaded.json()["currentLayoutRevision"]["layout"]["activePanelId"]
            assert len(panels.json()["items"]) == len(loaded.json()["panels"])
            assert listed.json()["items"][0]["workspaceId"] == workspace_id
            assert len(repos.workspaces.list_by_project(project_id)) == 1

            replay = client.post(
                "/workspaces",
                headers={"Idempotency-Key": f"phase10m2-{suffix}"},
                json={"sourceJobId": job_id, "title": "Service-backed Workspace shell"},
            )
            assert replay.status_code == 200
            assert replay.headers["x-idempotent-replay"] == "true"
            assert replay.json()["workspace"]["workspaceId"] == workspace_id
            assert len(repos.workspaces.list_by_project(project_id)) == 1
        finally:
            client.close()

        minio.delete_object(Bucket=minio_bucket, Key=minio_key)
        minio = None
    finally:
        if minio is not None:
            try:
                minio.delete_object(Bucket=minio_bucket, Key=minio_key)
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()


@pytest.mark.integration
def test_phase10m3_postgres_redis_minio_canonical_selection_and_pinning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persist exact selection metadata without creating execution authority."""

    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _required_postgres_url()
    suffix = uuid.uuid4().hex[:12]
    schema_name = f"phase10m3_{suffix}"
    schema_url = _schema_database_url(database_url, schema_name)
    base_engine = create_engine(database_url, future=True)
    engine = None
    minio = None
    minio_bucket = ""
    minio_key = f"phase10m3/{suffix}/selection-metadata.json"
    try:
        with base_engine.begin() as connection:
            connection.execute(CreateSchema(schema_name))
        monkeypatch.setenv("DATABASE_URL", schema_url)
        monkeypatch.delenv("MDI_DATABASE_URL", raising=False)
        monkeypatch.delenv("POSTGRES_HOST", raising=False)
        config = AlembicConfig("apps/api/alembic.ini")
        config.set_main_option("script_location", "apps/api/alembic")
        alembic_upgrade(config, "head")
        engine = create_engine(schema_url, future=True)
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE IF NOT EXISTS organizations (id VARCHAR(64) PRIMARY KEY, name VARCHAR(160) NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
            connection.execute(text("CREATE TABLE IF NOT EXISTS users (id VARCHAR(64) PRIMARY KEY, email VARCHAR(320) NOT NULL UNIQUE, display_name VARCHAR(160) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"))

        _redis_smoke(f"m3-{suffix}")
        minio, minio_bucket = _minio_client()
        minio.put_object(Bucket=minio_bucket, Key=minio_key, Body=b'{"contract":"phase10m3.selection-metadata.v1"}', ContentType="application/json")
        repos = SqlAlchemyRepositoryBundle.create(engine)
        monkeypatch.setattr("mdi_api.routers.workspaces._repositories", lambda: repos)
        monkeypatch.setattr("mdi_api.routers.workspaces._service", lambda: WorkspaceProjectionService(repos))
        project_id, job_id, artifact_id = f"project_m3_{suffix}", f"job_m3_{suffix}", f"artifact_m3_{suffix}"
        tool_call_id = f"call_m3_{suffix}"
        checksum = "a" * 64
        repos.projects.save({"id": project_id, "name": project_id, "createdBy": "user_local"})
        repos.jobs.save({"id": job_id, "projectId": project_id, "status": "completed", "kind": "analysis", "createdBy": "user_local"})
        repos.tool_calls.save({"id": tool_call_id, "jobId": job_id, "stepId": "phonon_band", "toolId": "phonon.band", "status": "completed"})
        repos.artifacts.save({"id": artifact_id, "projectId": project_id, "jobId": job_id, "toolCallId": tool_call_id, "type": "phonon_band_json", "version": "1.0", "contentType": "application/json", "contentHash": checksum, "sha256": checksum, "storageKey": minio_key})

        client = TestClient(create_app())
        try:
            created = client.post("/workspaces", headers={"Idempotency-Key": f"phase10m3-{suffix}"}, json={"sourceJobId": job_id, "title": "M3 canonical selection"})
            assert created.status_code == 201, created.json()
            body = created.json()
            workspace = body["workspace"]
            result_panel = next(item for item in body["panels"] if item["panelKind"] == "SCIENTIFIC_RESULT")
            assert result_panel["emittedSelectionKinds"] == ["ARTIFACT"]
            assert "ARTIFACT" in result_panel["acceptedSelectionKinds"]
            selection = WorkspaceSelectionContext(
                sourceScopeHash=workspace["sourceReferenceHash"],
                primary=WorkspaceSelectionRef(
                    kind=WorkspaceSelectionKind.ARTIFACT,
                    sourceScopeHash=workspace["sourceReferenceHash"],
                    projectId=project_id,
                    jobId=job_id,
                    artifactId=artifact_id,
                    artifactChecksum=checksum,
                    artifactContract="phonon_band_json",
                    artifactVersion="1.0",
                    toolCallId=tool_call_id,
                ),
                secondary=(),
                compatibility="EXACT",
                cleared=False,
            )
            pinned = client.patch(f"/workspaces/{workspace['workspaceId']}", headers={"If-Match": created.headers["etag"]}, json={"pinnedSelection": selection.model_dump(mode="json")})
            assert pinned.status_code == 200, pinned.json()
            assert pinned.json()["workspace"]["pinnedSelection"]["primary"]["artifactId"] == artifact_id
            assert len(repos.jobs.list_by_project(project_id)) == 1
            assert len(repos.artifacts.list_for_job(job_id)) == 1

            stale = selection.model_dump(mode="json")
            stale["sourceScopeHash"] = "b" * 64
            stale["primary"]["sourceScopeHash"] = "b" * 64
            rejected = client.patch(f"/workspaces/{workspace['workspaceId']}", headers={"If-Match": pinned.headers["etag"]}, json={"pinnedSelection": stale})
            assert rejected.status_code == 409
            assert rejected.json()["detail"]["code"] == "SELECTION_STALE"
        finally:
            client.close()

        minio.delete_object(Bucket=minio_bucket, Key=minio_key)
        minio = None
    finally:
        if minio is not None:
            try:
                minio.delete_object(Bucket=minio_bucket, Key=minio_key)
            except Exception:
                pass
        if engine is not None:
            engine.dispose()
        try:
            with base_engine.begin() as connection:
                connection.execute(DropSchema(schema_name, cascade=True))
        finally:
            base_engine.dispose()
