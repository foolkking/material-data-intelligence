from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from mdi_api.artifact_storage import S3CompatibleArtifactStorage, create_minio_artifact_storage_from_settings
from mdi_api.config import load_settings
from mdi_api.db import metadata
from mdi_api.repositories import (
    InMemoryRepositoryBundle,
    SqlAlchemyJobEventRepository,
    SqlAlchemyRepositoryBundle,
    _lock_job_event_sequence,
)
from mdi_workers import InMemoryQueueBackend, QueueToolExecution, QueueWorkerRuntime


def test_phase5_runtime_config_supports_standard_and_mdi_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "DATABASE_URL",
        "MDI_DATABASE_URL",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "REDIS_URL",
        "MDI_REDIS_URL",
        "MINIO_ENDPOINT",
        "MINIO_ACCESS_KEY",
        "MINIO_SECRET_KEY",
        "MINIO_BUCKET",
        "MINIO_SECURE",
    ):
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5544")
    monkeypatch.setenv("POSTGRES_DB", "mdi_test")
    monkeypatch.setenv("POSTGRES_USER", "mdi_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "mdi_password")
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/1")
    monkeypatch.setenv("MINIO_ENDPOINT", "http://minio:9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "access")
    monkeypatch.setenv("MINIO_SECRET_KEY", "secret")
    monkeypatch.setenv("MINIO_BUCKET", "phase5-artifacts")
    monkeypatch.setenv("MINIO_SECURE", "true")

    settings = load_settings()

    assert settings.database_url == "postgresql+psycopg://mdi_user:mdi_password@postgres:5544/mdi_test"
    assert settings.redis_url == "redis://redis:6379/1"
    assert settings.minio_endpoint == "http://minio:9000"
    assert settings.minio_bucket == "phase5-artifacts"
    assert settings.minio_secure is True

    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://override/mdi")
    assert load_settings().database_url == "postgresql+psycopg://override/mdi"


def test_phase5_alembic_env_and_runbook_are_present(repo_root: Path) -> None:
    env_py = (repo_root / "apps/api/alembic/env.py").read_text(encoding="utf-8")
    runbook = (repo_root / "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md").read_text(encoding="utf-8")

    assert "DATABASE_URL" in env_py
    assert "load_settings().database_url" in env_py
    assert "docker compose up -d postgres redis minio" in runbook
    assert "python -m alembic -c apps/api/alembic.ini upgrade head" in runbook


def test_phase5_postgresql_job_event_lock_strategy_is_documented_and_callable() -> None:
    class _Dialect:
        name = "postgresql"

    class _Connection:
        dialect = _Dialect()

        def __init__(self) -> None:
            self.calls: list[tuple[object, object]] = []

        def execute(self, statement: object, params: object | None = None) -> None:
            self.calls.append((statement, params))

    connection = _Connection()
    _lock_job_event_sequence(connection, "job_pg")  # type: ignore[arg-type]

    assert "pg_advisory_xact_lock" in SqlAlchemyJobEventRepository.POSTGRES_ADVISORY_LOCK_SQL
    assert connection.calls
    assert connection.calls[0][1] == {"job_id": "job_pg"}


def test_phase5_queue_worker_submit_and_retry_are_idempotent(tmp_path: Path) -> None:
    repos = _seed_in_memory_repos()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(
        repositories=repos,
        artifact_storage=S3CompatibleArtifactStorage(bucket="mdi-artifacts", endpoint_url="http://minio:9000", prefix="phase5", client=_FakeS3Client()),
        queue_backend=queue,
        tool_executor=_fake_executor,
    )

    first_submit = runtime.submit_job("job_phase5")
    second_submit = runtime.submit_job("job_phase5")
    first_run = runtime.handle_job("job_phase5", plan=_plan())
    second_run = runtime.handle_job("job_phase5", plan=_plan())

    assert first_submit.enqueued is True
    assert second_submit.enqueued is False
    assert first_run.status == "completed"
    assert second_run.status == "completed"
    assert second_run.tool_call_count == 1
    assert second_run.artifact_count == 1
    assert repos.artifacts.list_for_job("job_phase5")[0]["storageProvider"] == "s3"


def test_phase5_queue_worker_crash_retry_preserves_one_tool_call_and_artifact(tmp_path: Path) -> None:
    repos = _seed_in_memory_repos()
    attempts = {"count": 0}

    def flaky_executor(request: object, context: object) -> QueueToolExecution:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("simulated worker crash")
        return _fake_executor(request, context)

    runtime = QueueWorkerRuntime(
        repositories=repos,
        artifact_storage=S3CompatibleArtifactStorage(bucket="mdi-artifacts", endpoint_url="http://minio:9000", prefix="phase5", client=_FakeS3Client()),
        tool_executor=flaky_executor,
    )

    failed = runtime.handle_job("job_phase5", plan=_plan())
    recovered = runtime.handle_job("job_phase5", plan=_plan())

    assert failed.status == "failed"
    assert recovered.status == "completed"
    assert recovered.tool_call_count == 1
    assert recovered.artifact_count == 1
    assert repos.tool_calls.list_for_job("job_phase5")[0]["status"] == "completed"


def test_phase5_s3_minio_live_client_interface_and_signed_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MINIO_ENDPOINT", "http://minio:9000")
    monkeypatch.setenv("MINIO_ACCESS_KEY", "access")
    monkeypatch.setenv("MINIO_SECRET_KEY", "secret")
    monkeypatch.setenv("MINIO_BUCKET", "mdi-artifacts")
    fake_client = _FakeS3Client()
    storage = create_minio_artifact_storage_from_settings(load_settings(), client=fake_client, prefix="phase5")

    metadata_record = storage.put_json("projects/p/jobs/j/metrics.json", {"ok": True})
    signed = storage.signed_url("projects/p/jobs/j/metrics.json", expires_in_sec=60, content_type="application/json")
    signed_from_full_key = storage.signed_url(metadata_record.storage_key, expires_in_sec=60, content_type="application/json")

    assert metadata_record.storage_provider == "s3"
    assert metadata_record.bucket == "mdi-artifacts"
    assert metadata_record.storage_key == "phase5/projects/p/jobs/j/metrics.json"
    assert storage.exists("projects/p/jobs/j/metrics.json")
    assert storage.get_json("projects/p/jobs/j/metrics.json") == {"ok": True}
    assert signed.status == "ok"
    assert signed.url.startswith("http://fake-minio/mdi-artifacts/phase5/projects/p/jobs/j/metrics.json")
    assert signed_from_full_key.url == signed.url


def test_phase5_sqlalchemy_after_seq_regression_on_sqlite(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{(tmp_path / 'phase5.sqlite').as_posix()}", future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "project_phase5", "name": "Phase 5"})
    repos.datasets.save({"id": "dataset_phase5", "projectId": "project_phase5", "name": "Dataset"})
    repos.jobs.save({"id": "job_phase5", "projectId": "project_phase5", "datasetId": "dataset_phase5", "status": "created"})

    for index in range(5):
        repos.job_events.append_event("job_phase5", event_type=f"phase5.{index}", status="info", message=f"event {index}")

    assert [event.seq for event in repos.job_events.list_events_after_seq("job_phase5", 2)] == [3, 4, 5]
    engine.dispose()


@pytest.mark.integration
def test_phase5_postgresql_repository_smoke_if_enabled() -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL running to enable this test.")

    engine = create_engine(load_settings().database_url, future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    repos.projects.save({"id": "project_phase5_integration", "name": "Phase 5 Integration"})
    assert repos.projects.get("project_phase5_integration")["projectId"] == "project_phase5_integration"
    engine.dispose()


class _FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], tuple[bytes, str]] = {}

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str) -> None:
        self.objects[(Bucket, Key)] = (bytes(Body), ContentType)

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, object]:
        body, _ = self.objects[(Bucket, Key)]
        return {"Body": io.BytesIO(body)}

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, object]:
        if (Bucket, Key) not in self.objects:
            raise KeyError(Key)
        return {}

    def generate_presigned_url(self, *, ClientMethod: str, Params: dict[str, str], ExpiresIn: int, HttpMethod: str) -> str:
        assert ClientMethod == "get_object"
        assert HttpMethod == "GET"
        return f"http://fake-minio/{Params['Bucket']}/{Params['Key']}?expires={ExpiresIn}"


def _seed_in_memory_repos() -> InMemoryRepositoryBundle:
    repos = InMemoryRepositoryBundle.create()
    repos.projects.save({"id": "project_phase5", "name": "Phase 5"})
    repos.datasets.save({"id": "dataset_phase5", "projectId": "project_phase5", "name": "Dataset"})
    repos.jobs.save({"id": "job_phase5", "projectId": "project_phase5", "datasetId": "dataset_phase5", "status": "created"})
    return repos


def _plan() -> dict[str, object]:
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


def _fake_executor(request: object, context: object) -> QueueToolExecution:
    return QueueToolExecution(
        artifacts=[
            {
                "id": "artifact_metrics",
                "type": "metrics_json",
                "name": "metrics.json",
                "content": {"toolId": getattr(request, "toolId"), "ok": True},
                "contentType": "application/json",
                "version": "1",
                "metadata": {"inputHashes": [], "createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
            }
        ]
    )
