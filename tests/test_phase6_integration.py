from __future__ import annotations

import io
import os
import time
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine

from mdi_api.artifact_storage import (
    S3CompatibleArtifactStorage,
    create_minio_artifact_storage_from_settings,
)
from mdi_api.config import ApiSettings, load_settings
from mdi_api.db import metadata
from mdi_api.repositories import (
    SqlAlchemyJobEventRepository,
    SqlAlchemyRepositoryBundle,
    _lock_job_event_sequence,
)
from mdi_api.state_machine import InvalidStatusTransition
from mdi_workers import (
    InMemoryQueueBackend,
    QueueToolExecution,
    QueueWorkerRuntime,
    RedisRQQueueBackend,
)

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _pg_url() -> str | None:
    url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if url and "postgres" in url:
        return url
    return None


def _pg_engine():
    url = _pg_url()
    if url is None:
        pytest.skip("No PostgreSQL DATABASE_URL configured (set MDI_TEST_DATABASE_URL)")
    return create_engine(url, future=True)


def _live_redis_client():
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        pytest.skip("No REDIS_URL configured")
    try:
        from redis import Redis

        client = Redis.from_url(redis_url)
        client.ping()
        return client
    except Exception:
        pytest.skip("Redis not reachable")


def _minio_storage(prefix: str = "test-phase6") -> S3CompatibleArtifactStorage:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
    secret = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    try:
        import botocore

        client = _live_minio_client(endpoint, access, secret)
        return S3CompatibleArtifactStorage(
            bucket=bucket,
            endpoint_url=endpoint,
            prefix=prefix,
            access_key_id=access,
            secret_access_key=secret,
            client=client,
        )
    except Exception:
        pytest.skip("MinIO not reachable")


def _live_minio_client(endpoint, access, secret):
    import boto3

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access,
        aws_secret_access_key=secret,
        region_name="us-east-1",
    )
    try:
        client.list_buckets()
    except Exception:
        client.create_bucket(Bucket=os.getenv("MINIO_BUCKET", "mdi-artifacts"))
    return client


def _seed_repos(repos: SqlAlchemyRepositoryBundle) -> dict[str, str]:
    """Seed a project/dataset/job for integration tests.

    Uses the repository save API which handles the delete-then-insert
    pattern.  The second save on the same project_id internally deletes
    the old row first — but only the project row, not the dependent
    dataset/job rows that were already saved.  PostgreSQL enforces
    foreign keys, so that DELETE would cascade-fail on datasets.

    We therefore save in reverse-dependency order and avoid re-saving
    the project after dependents exist.  This follows the same pattern
    as Phase 5's _seed_in_memory_repos helper.
    """
    # Save project first (creates user + org internally)
    repos.projects.save({
        "id": "proj_p6", "name": "Phase 6",
        "organizationId": "org_test", "createdBy": "test_user",
    })
    # Save dependent rows — these reference proj_p6 via FK
    repos.datasets.save({
        "id": "ds_p6", "projectId": "proj_p6",
        "name": "Dataset", "createdBy": "test_user",
    })
    repos.jobs.save({
        "id": "job_p6", "projectId": "proj_p6", "datasetId": "ds_p6",
        "status": "created", "kind": "analysis", "createdBy": "test_user",
    })
    return {"project": "proj_p6", "dataset": "ds_p6", "job": "job_p6"}


# ===================================================================
# 1. Docker compose infrastructure check
# ===================================================================


@pytest.mark.integration
def test_phase6_docker_compose_services_are_reachable() -> None:
    """Verify postgres, redis, minio are reachable when MDI_RUN_INTEGRATION=1."""
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with docker compose services running")

    url = _pg_url()
    assert url is not None, "No PostgreSQL URL configured"
    engine = create_engine(url, future=True)
    with engine.connect() as conn:
        result = conn.execute(__import__("sqlalchemy").text("SELECT 1 AS ok"))
        assert result.scalar() == 1
    engine.dispose()

    # Redis
    client = _live_redis_client()
    assert client.ping() is True

    # MinIO
    storage = _minio_storage("test-reachable")
    # Verify the bucket is accessible by doing a quick put/get
    storage.put_json("test-reachable/health.json", {"ok": True})
    assert storage.exists("test-reachable/health.json")


# ===================================================================
# 2. Alembic live migration smoke
# ===================================================================


@pytest.mark.integration
def test_phase6_alembic_upgrade_head_creates_all_tables(tmp_path: Path) -> None:
    """Run alembic upgrade head against a live PostgreSQL database and verify all expected tables exist."""
    url = _pg_url()
    if url is None:
        pytest.skip("No PostgreSQL DATABASE_URL configured")

    # 1. Run alembic upgrade head (real migration, not metadata.create_all)
    from alembic.command import upgrade as alembic_upgrade
    from alembic.config import Config as AlembicConfig

    alembic_cfg = AlembicConfig("apps/api/alembic.ini")
    alembic_cfg.set_main_option("script_location", "apps/api/alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_upgrade(alembic_cfg, "head")

    # 2. Verify tables exist in PostgreSQL
    expected_tables = {
        "projects",
        "datasets",
        "data_profiles",
        "jobs",
        "job_events",
        "tool_calls",
        "artifacts",
        "visualization_recipes",
        "reports",
    }
    engine = create_engine(url, future=True)
    with engine.connect() as conn:
        result = conn.execute(
            __import__("sqlalchemy").text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables = {row[0] for row in result}
    for t in expected_tables:
        assert t in tables, f"Table {t} missing from PostgreSQL after alembic upgrade head"

    # 3. Verify key indexes exist
    expected_indexes = {
        "idx_job_events_job_seq",
        "idx_jobs_project_created",
        "idx_tool_calls_job",
        "idx_artifacts_job",
        "idx_artifacts_project_created",
        "idx_reports_job",
    }
    with engine.connect() as conn:
        result = conn.execute(
            __import__("sqlalchemy").text(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY indexname"
            )
        )
        indexes = {row[0] for row in result}
    for idx in expected_indexes:
        assert idx in indexes, f"Index {idx} missing from PostgreSQL after alembic upgrade head"

    # 4. downgrade to clean up, then re-upgrade to verify reproducibility
    from alembic.command import downgrade as alembic_downgrade
    alembic_downgrade(alembic_cfg, "base")
    with engine.connect() as conn:
        result = conn.execute(
            __import__("sqlalchemy").text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables_after_downgrade = {row[0] for row in result}
    assert len(tables_after_downgrade & expected_tables) == 0, "Tables should be dropped after downgrade"

    alembic_upgrade(alembic_cfg, "head")
    with engine.connect() as conn:
        result = conn.execute(
            __import__("sqlalchemy").text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            )
        )
        tables_after_reupgrade = {row[0] for row in result}
    for t in expected_tables:
        assert t in tables_after_reupgrade, f"Table {t} missing after re-upgrade"

    engine.dispose()


# ===================================================================
# 3. PostgreSQL repository live integration
# ===================================================================


@pytest.mark.integration
def test_phase6_project_repository_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "proj_live_1", "name": "Live Project"})
    record = repos.projects.get("proj_live_1")
    assert record["projectId"] == "proj_live_1"
    assert record["name"] == "Live Project"
    engine.dispose()


@pytest.mark.integration
def test_phase6_dataset_repository_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "proj_live_2", "name": "Live Project 2"})
    repos.datasets.save({"id": "ds_live_1", "projectId": "proj_live_2", "name": "Live Dataset"})
    record = repos.datasets.get("ds_live_1")
    assert record["datasetId"] == "ds_live_1"
    datasets = repos.datasets.list_for_project("proj_live_2")
    assert len(datasets) == 1
    engine.dispose()


@pytest.mark.integration
def test_phase6_job_and_toolcall_and_artifact_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    # Job
    job = repos.jobs.get(ids["job"])
    assert job["status"] == "created"
    job = repos.jobs.set_status(ids["job"], "queued")
    assert job["status"] == "queued"

    # ToolCall
    tc = repos.tool_calls.save(
        {
            "id": "tc_live_1",
            "jobId": ids["job"],
            "stepId": "step_1",
            "toolId": "ml.basic_metrics",
            "status": "planned",
            "idempotencyKey": f"{ids['job']}:step_1",
            "params": {},
        }
    )
    assert tc["status"] == "planned"
    tc2 = repos.tool_calls.save(
        {
            "id": "tc_live_1_retry",
            "jobId": ids["job"],
            "stepId": "step_1",
            "toolId": "ml.basic_metrics",
            "status": "running",
            "idempotencyKey": f"{ids['job']}:step_1",
            "params": {},
            "attempt": 2,
        }
    )
    assert tc2["id"] == tc["id"]
    assert tc2["status"] == "running"

    # Artifact
    art = repos.artifacts.save(
        {
            "id": "art_live_1",
            "projectId": ids["project"],
            "jobId": ids["job"],
            "toolCallId": tc["id"],
            "type": "metrics_json",
            "name": "metrics.json",
            "storageKey": "live/metrics.json",
            "storageProvider": "local",
            "sizeBytes": 100,
            "contentType": "application/json",
            "contentHash": "abc_live",
            "sha256": "abc_live",
            "metadata": {"createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
        }
    )
    assert art["storageProvider"] == "local"
    arts = repos.artifacts.list_for_job(ids["job"])
    assert len(arts) == 1
    engine.dispose()


@pytest.mark.integration
def test_phase6_recipe_and_report_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    repos.recipes.save({"id": "recipe_live", "projectId": ids["project"], "sourceJobId": ids["job"], "name": "Live Recipe"})
    repos.reports.save(
        {"id": "report_live", "projectId": ids["project"], "jobId": ids["job"], "title": "Live Report", "markdownKey": "reports/r.md"}
    )
    assert repos.recipes.get("recipe_live")["recipeId"] == "recipe_live"
    assert repos.reports.get("report_live")["reportId"] == "report_live"
    assert len(repos.reports.list_for_job(ids["job"])) == 1
    engine.dispose()


@pytest.mark.integration
def test_phase6_transaction_rollback_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    from mdi_api.unit_of_work import RepositoryFactory

    factory = RepositoryFactory(engine)
    with pytest.raises(RuntimeError, match="rollback_test"):
        with factory.session() as session:
            session.repositories.projects.save({"id": "proj_rollback_p6", "name": "Rollback"})
            raise RuntimeError("rollback_test")
    with pytest.raises(LookupError):
        factory.create_repositories().projects.get("proj_rollback_p6")
    engine.dispose()


@pytest.mark.integration
def test_phase6_failed_job_status_transition_rejected_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)
    repos.jobs.set_status(ids["job"], "completed")
    with pytest.raises(InvalidStatusTransition):
        repos.jobs.set_status(ids["job"], "running")
    engine.dispose()


# ===================================================================
# 4. PostgreSQL JobEvent seq live integration
# ===================================================================


@pytest.mark.integration
def test_phase6_job_event_seq_monotonic_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    for i in range(5):
        event = repos.job_events.append_event(ids["job"], event_type=f"test.{i}", status="info", message=f"event {i}")
        assert event.seq == i + 1

    events = repos.job_events.list_events_after_seq(ids["job"], 2)
    assert [e.seq for e in events] == [3, 4, 5]
    engine.dispose()


@pytest.mark.integration
def test_phase6_job_event_seq_advisory_lock_strategy_live() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    # Verify the advisory lock SQL exists and contains expected token
    assert "pg_advisory_xact_lock" in SqlAlchemyJobEventRepository.POSTGRES_ADVISORY_LOCK_SQL

    # Append events - seq must be strictly monotonic
    for i in range(20):
        repos.job_events.append_event(ids["job"], event_type=f"seq_test.{i}", status="info", message=f"seq {i}")

    all_events = repos.job_events.list_for_job(ids["job"])
    seqs = [e.seq for e in all_events]
    assert seqs == list(range(1, 21))
    assert sorted(seqs) == seqs  # strictly monotonic, no gaps
    engine.dispose()


@pytest.mark.integration
def test_phase6_job_event_concurrent_seq_live() -> None:
    from concurrent.futures import ThreadPoolExecutor

    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    def append(i: int) -> int:
        return repos.job_events.append_event(ids["job"], event_type=f"conc.{i}", status="info", message=f"concurrent {i}", payload={"index": i}).seq

    with ThreadPoolExecutor(max_workers=6) as pool:
        seqs = list(pool.map(append, range(30)))

    assert sorted(seqs) == list(range(1, 31))
    after_15 = repos.job_events.list_events_after_seq(ids["job"], 15)
    assert [e.seq for e in after_15] == list(range(16, 31))
    engine.dispose()


# ===================================================================
# 5. Redis queue live integration
# ===================================================================


def _live_redis_queue_backend() -> RedisRQQueueBackend:
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        pytest.skip("No REDIS_URL configured")
    try:
        from redis import Redis
        Redis.from_url(redis_url).ping()
    except Exception:
        pytest.skip("Redis not reachable")
    return RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase6")


@pytest.mark.integration
def test_phase6_redis_queue_enqueue_and_dequeue_live() -> None:
    backend = _live_redis_queue_backend()
    result = backend.enqueue_job("test_redis_live")
    assert result.enqueued is True
    assert result.backend == "rq"
    # Duplicate enqueue should not re-enqueue
    result2 = backend.enqueue_job("test_redis_live")
    assert result2.enqueued is False


@pytest.mark.integration
def test_phase6_queue_worker_runtime_with_live_redis_postgres() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    from mdi_api.database import create_repository_factory
    factory = create_repository_factory()

    backend = _live_redis_queue_backend()
    runtime = QueueWorkerRuntime(
        repository_factory=factory,
        queue_backend=backend,
        tool_executor=_fake_tool_executor,
    )

    submit_result = runtime.submit_job(ids["job"])
    assert submit_result.enqueued is True
    assert submit_result.backend == "rq"

    # Handle job synchronously (simulating worker process)
    handle_result = runtime.handle_job(ids["job"], plan=_plan())
    assert handle_result.status == "completed"
    assert handle_result.tool_call_count == 1
    assert handle_result.artifact_count == 1

    # Verify events in repository
    events = repos.job_events.list_for_job(ids["job"])
    assert len(events) >= 3  # job.running, tool.started, tool.completed, job.completed, artifact.ready
    engine.dispose()


# ===================================================================
# 6. Queue retry idempotency live smoke
# ===================================================================


@pytest.mark.integration
def test_phase6_queue_retry_idempotency_with_live_repos() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    from mdi_api.database import create_repository_factory
    factory = create_repository_factory()

    runtime = QueueWorkerRuntime(
        repository_factory=factory,
        tool_executor=_fake_tool_executor,
    )

    # First run
    r1 = runtime.handle_job(ids["job"], plan=_plan())
    assert r1.status == "completed"
    assert r1.tool_call_count == 1

    # Second run — idempotent
    r2 = runtime.handle_job(ids["job"], plan=_plan())
    assert r2.status == "completed"
    assert r2.tool_call_count == 1  # no new tool calls
    assert r2.artifact_count == 1   # no new artifacts

    tool_calls = repos.tool_calls.list_for_job(ids["job"])
    assert len(tool_calls) == 1  # one tool call, reused
    artifacts = repos.artifacts.list_for_job(ids["job"])
    assert len(artifacts) == 1  # one artifact, reused


@pytest.mark.integration
def test_phase6_queue_crash_retry_with_live_repos() -> None:
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    from mdi_api.database import create_repository_factory
    factory = create_repository_factory()

    crash_count = {"n": 0}

    def flaky(req, ctx):
        crash_count["n"] += 1
        if crash_count["n"] <= 1:
            raise RuntimeError("simulated worker crash")
        return _fake_tool_executor(req, ctx)

    runtime = QueueWorkerRuntime(repository_factory=factory, tool_executor=flaky)

    # First run crashes
    try:
        runtime.handle_job(ids["job"], plan=_plan())
    except RuntimeError:
        pass

    # Verify failed state recorded
    job = repos.jobs.get(ids["job"])
    assert job["status"] in ("failed", "created", "queued")
    tc = repos.tool_calls.list_for_job(ids["job"])
    assert len(tc) == 1
    assert tc[0]["status"] == "failed"

    # Second run recovers
    r2 = runtime.handle_job(ids["job"], plan=_plan())
    assert r2.status == "completed"
    assert r2.tool_call_count == 1
    assert r2.artifact_count == 1

    tc2 = repos.tool_calls.list_for_job(ids["job"])
    assert tc2[0]["status"] == "completed"

    artifacts = repos.artifacts.list_for_job(ids["job"])
    assert len(artifacts) == 1
    engine.dispose()


# ===================================================================
# 7. MinIO live integration
# ===================================================================


@pytest.mark.integration
def test_phase6_minio_put_get_exists_signed_url_live() -> None:
    storage = _minio_storage("test-phase6-ops")

    # put_json
    meta = storage.put_json("obj/test.json", {"key": "value"})
    assert meta.storage_provider == "s3"
    assert meta.content_type == "application/json"
    assert meta.size_bytes > 0

    # exists
    assert storage.exists("obj/test.json") is True
    assert storage.exists("obj/nonexistent.json") is False

    # get_json
    data = storage.get_json("obj/test.json")
    assert data == {"key": "value"}

    # put_text / get_text
    storage.put_text("obj/text.txt", "hello phase 6", content_type="text/plain")
    assert storage.get_text("obj/text.txt") == "hello phase 6"

    # put_bytes / get_bytes
    storage.put_bytes("obj/binary.bin", b"\x00\x01\x02\x03", content_type="application/octet-stream")
    assert storage.get_bytes("obj/binary.bin") == b"\x00\x01\x02\x03"

    # signed_url
    signed = storage.signed_url("obj/test.json", expires_in_sec=300)
    assert signed.status == "ok"
    assert signed.storage_key.endswith("obj/test.json")
    assert "test-phase6-ops/obj/test.json" in signed.url
    assert signed.expires_in_sec == 300


@pytest.mark.integration
def test_phase6_minio_signed_url_structure_validation() -> None:
    storage = _minio_storage("test-phase6-signed")
    storage.put_json("reports/rpt.json", [1, 2, 3])

    signed = storage.signed_url("reports/rpt.json", expires_in_sec=900, content_type="application/json")
    assert signed.status == "ok"
    assert signed.content_type == "application/json"
    assert "reports/rpt.json" in signed.url
    # URL must contain bucket
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    assert bucket in signed.url
    # expires_in_sec passed through
    assert signed.expires_in_sec == 900


# ===================================================================
# 8. Service-backed product-loop smoke
# ===================================================================


@pytest.mark.integration
def test_phase6_service_backed_product_loop(repo_root: Path) -> None:
    """End-to-end smoke: PG repos + Redis queue + MinIO storage + real Adapter.

    Uses the real Tool Registry + Adapter path (not a fake executor). The adapter
    receives an in-memory DataFrame so no external fixture files are required.
    """
    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    ids = _seed_repos(repos)

    # Use real MinIO if available, else local fallback
    try:
        storage = _minio_storage("test-loop")
    except Exception:
        from mdi_api.artifact_storage import LocalFileArtifactStorage
        storage = LocalFileArtifactStorage(".artifacts/phase6-loop")

    # Real MVP adapter: ml.basic_metrics with an in-memory regression DataFrame
    import pandas as pd
    from mdi_adapters import ToolExecutionContext, execute_tool_request
    from mdi_schemas import ToolExecutionRequest
    from mdi_tool_registry import ToolRegistry, load_manifests

    _reg = ToolRegistry(load_manifests())
    df = pd.DataFrame({
        "formula": ["SiO2", "Al2O3", "CaO", "MgO", "Fe2O3"],
        "y_true": [2.1, 3.4, 1.8, 4.2, 2.9],
        "y_pred": [2.0, 3.5, 1.9, 4.0, 3.0],
    })
    object_store: dict[str, list[Any]] = {"dataset_ml": [df]}
    adapter_context = ToolExecutionContext(
        job_id=ids["job"],
        project_id=ids["project"],
        dataset_id=ids["dataset"] or "",
        tool_id="ml.basic_metrics",
        tool_version="0.1.0",
        adapter_version="0.1.0",
        registry_version=_reg.version,
        artifact_root=Path(".artifacts/phase6-loop"),
        tool_call_id="call_job_p6_step_metrics",
        object_store=object_store,
    )

    def real_adapter_executor(request_obj, ctx):
        """Execute through the real Tool Registry + Adapter path."""
        parsed = request_obj if isinstance(request_obj, ToolExecutionRequest) else ToolExecutionRequest.model_validate(request_obj)
        exec_ctx = ToolExecutionContext(
            job_id=ctx.job_id,
            project_id=ctx.project_id,
            dataset_id=(ctx.dataset_id or ""),
            tool_id=parsed.toolId,
            tool_version="0.1.0",
            adapter_version="0.1.0",
            registry_version=_reg.version,
            artifact_root=Path(".artifacts/phase6-loop"),
            tool_call_id=ctx.tool_call_id,
            object_store=object_store,
        )
        result = execute_tool_request(exec_ctx, parsed, registry=_reg)
        # Convert to QueueToolExecution shape
        return QueueToolExecution(
            artifacts=[
                {
                    "id": f"art_{a.type}",
                    "type": a.type.value if hasattr(a.type, "value") else str(a.type),
                    "name": a.name,
                    "content": getattr(a, "content", None),
                    "contentType": a.contentType or "application/json",
                    "version": a.version,
                    "metadata": {
                        "inputHashes": a.metadata.inputHashes if hasattr(a.metadata, "inputHashes") else [],
                        "createdAt": a.createdAt or "2026-06-26T00:00:00+00:00",
                        "provenance": a.metadata.provenance if hasattr(a.metadata, "provenance") else {},
                    },
                }
                for a in result.artifacts
            ]
        )

    from mdi_api.database import create_repository_factory
    factory = create_repository_factory()

    runtime = QueueWorkerRuntime(
        repository_factory=factory,
        artifact_storage=storage,
        tool_executor=real_adapter_executor,
    )

    # Enqueue (in-memory queue for test determinism)
    submit = runtime.submit_job(ids["job"])
    assert submit.enqueued is True

    # Handle: this invokes real_adapter_executor -> execute_tool_request -> BasicMetricsAdapter
    result = runtime.handle_job(ids["job"], plan=_plan())
    assert result.status == "completed"
    assert result.tool_call_count >= 1
    assert result.artifact_count >= 1
    assert result.event_count >= 3

    # Verify PostgreSQL state
    job = repos.jobs.get(ids["job"])
    assert job["status"] in ("completed", "running")

    events = repos.job_events.list_for_job(ids["job"])
    assert len(events) > 0
    event_types = {e.eventType for e in events}
    assert "tool.started" in event_types or "job.running" in event_types
    assert "tool.completed" in event_types

    tool_calls = repos.tool_calls.list_for_job(ids["job"])
    assert len(tool_calls) >= 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["status"] in ("completed", "running")

    artifacts = repos.artifacts.list_for_job(ids["job"])
    assert len(artifacts) >= 1
    artifact_types = [a.get("type") for a in artifacts]
    assert any("metrics" in (t or "") for t in artifact_types)

    # after_seq query stability
    if len(events) >= 3:
        after_seq = events[0].seq
        later = repos.job_events.list_events_after_seq(ids["job"], after_seq)
        assert len(later) == len(events) - 1

    engine.dispose()


# ===================================================================
# helpers
# ===================================================================


def _fake_tool_executor(request, context) -> QueueToolExecution:
    return QueueToolExecution(
        artifacts=[
            {
                "id": "art_loop",
                "type": "metrics_json",
                "name": "metrics.json",
                "content": {"toolId": getattr(request, "toolId", "unknown"), "ok": True},
                "contentType": "application/json",
                "version": "1",
                "metadata": {"inputHashes": [], "createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
            }
        ]
    )


def _plan() -> dict[str, Any]:
    return {
        "steps": [
            {
                "stepId": "step_metrics",
                "toolId": "ml.basic_metrics",
                "inputRefs": [],
                "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
                "output": {"artifactTypes": ["metrics_json"]},
            }
        ]
    }
