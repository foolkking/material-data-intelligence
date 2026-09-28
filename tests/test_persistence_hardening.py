from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from mdi_api.db import artifacts, jobs, metadata, tool_calls
from mdi_api.migrations import PHASE4_MIGRATION_BASELINE_SQL
from mdi_api.repositories import SqlAlchemyRepositoryBundle
from mdi_api.state_machine import InvalidStatusTransition, validate_job_transition, validate_tool_call_transition
from mdi_api.unit_of_work import RepositoryFactory


def test_phase4_migration_baseline_and_metadata_cover_required_constraints(repo_root: Path) -> None:
    assert (repo_root / "apps/api/alembic.ini").exists()
    assert (repo_root / "apps/api/alembic/versions/0001_phase4_persistence_baseline.py").exists()

    for table_name in (
        "projects",
        "datasets",
        "data_profiles",
        "jobs",
        "job_events",
        "tool_calls",
        "artifacts",
        "visualization_recipes",
        "reports",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table_name}" in PHASE4_MIGRATION_BASELINE_SQL

    for index_name in (
        "idx_job_events_job_seq",
        "idx_jobs_project_created",
        "idx_tool_calls_job",
        "idx_artifacts_job",
        "idx_artifacts_project_created",
    ):
        assert index_name in PHASE4_MIGRATION_BASELINE_SQL

    assert {"idempotency_key", "attempt"}.issubset(tool_calls.columns.keys())
    assert {"storage_provider", "bucket", "storage_key", "content_type", "size_bytes", "sha256", "created_at"}.issubset(
        artifacts.columns.keys()
    )
    job_constraint_names = {constraint.name for constraint in jobs.constraints}
    tool_call_constraint_names = {constraint.name for constraint in tool_calls.constraints}
    artifact_constraint_names = {constraint.name for constraint in artifacts.constraints}
    assert any(name and name.endswith("job_status") for name in job_constraint_names)
    assert {"uq_tool_calls_job_step", "uq_tool_calls_job_idempotency_key"}.issubset(tool_call_constraint_names)
    assert any(name and name.endswith("tool_call_status") for name in tool_call_constraint_names)
    assert "uq_artifacts_job_storage_sha" in artifact_constraint_names
    assert any(name and name.endswith("artifact_storage_provider") for name in artifact_constraint_names)


def test_sqlalchemy_repository_crud_with_phase4_columns(tmp_path: Path) -> None:
    repos = _create_repos(tmp_path)
    _seed_project_dataset_job(repos)
    profile = repos.data_profiles.save({"id": "profile_phase4", "datasetId": "dataset_phase4", "version": "1", "columns": []})
    tool_call = repos.tool_calls.save(
        {
            "id": "call_phase4",
            "jobId": "job_phase4",
            "stepId": "step_metrics",
            "toolId": "ml.basic_metrics",
            "status": "planned",
            "idempotencyKey": "job_phase4:step_metrics",
            "params": {"metric": "mae"},
        }
    )
    artifact = repos.artifacts.save(
        {
            "id": "artifact_phase4",
            "projectId": "project_phase4",
            "datasetId": "dataset_phase4",
            "jobId": "job_phase4",
            "toolCallId": "call_phase4",
            "type": "metrics_json",
            "name": "metrics.json",
            "storageKey": "projects/project_phase4/jobs/job_phase4/tool_calls/call_phase4/metrics.json",
            "storageProvider": "local",
            "sizeBytes": 12,
            "contentType": "application/json",
            "contentHash": "abc123",
            "sha256": "abc123",
            "metadata": {"createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
        }
    )

    repos.recipes.save({"id": "recipe_phase4", "projectId": "project_phase4", "sourceJobId": "job_phase4", "name": "Recipe"})
    repos.reports.save(
        {
            "id": "report_phase4",
            "projectId": "project_phase4",
            "datasetId": "dataset_phase4",
            "jobId": "job_phase4",
            "title": "Report",
            "markdownKey": "reports/report.md",
        }
    )

    assert profile["profileId"] == "profile_phase4"
    assert tool_call["status"] == "planned"
    assert tool_call["idempotencyKey"] == "job_phase4:step_metrics"
    assert artifact["storageProvider"] == "local"
    assert repos.reports.list_for_job("job_phase4")[0]["reportId"] == "report_phase4"


def test_repository_session_rolls_back_failed_transaction(tmp_path: Path) -> None:
    engine = _create_engine(tmp_path)
    factory = RepositoryFactory(engine)

    with pytest.raises(RuntimeError, match="rollback please"):
        with factory.session() as session:
            session.repositories.projects.save({"id": "project_rollback", "name": "Rollback"})
            raise RuntimeError("rollback please")

    with pytest.raises(LookupError):
        factory.create_repositories().projects.get("project_rollback")


def test_existing_artifact_survives_failed_tool_call_retry_transaction(tmp_path: Path) -> None:
    engine = _create_engine(tmp_path)
    factory = RepositoryFactory(engine)
    repos = factory.create_repositories()
    _seed_project_dataset_job(repos)
    repos.tool_calls.save({"id": "call_done", "jobId": "job_phase4", "stepId": "step_done", "toolId": "ml.basic_metrics", "status": "completed"})
    repos.artifacts.save(
        {
            "id": "artifact_done",
            "projectId": "project_phase4",
            "datasetId": "dataset_phase4",
            "jobId": "job_phase4",
            "toolCallId": "call_done",
            "type": "metrics_json",
            "name": "metrics.json",
            "storageKey": "stable/metrics.json",
            "storageProvider": "local",
            "sizeBytes": 1,
            "contentType": "application/json",
            "contentHash": "donehash",
            "sha256": "donehash",
            "metadata": {"createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
        }
    )

    with pytest.raises(InvalidStatusTransition):
        with factory.session() as session:
            session.repositories.tool_calls.save(
                {"id": "call_done_retry", "jobId": "job_phase4", "stepId": "step_done", "toolId": "ml.basic_metrics", "status": "running"}
            )

    assert factory.create_repositories().artifacts.get("artifact_done")["storageKey"] == "stable/metrics.json"


def test_job_and_tool_call_status_transitions_are_enforced(tmp_path: Path) -> None:
    assert validate_job_transition("created", "queued") == "queued"
    assert validate_job_transition("created", "running") == "running"
    assert validate_job_transition("queued", "running") == "running"
    assert validate_job_transition("running", "partial_success") == "partial_success"
    with pytest.raises(InvalidStatusTransition):
        validate_job_transition("created", "completed")

    assert validate_tool_call_transition("planned", "running") == "running"
    assert validate_tool_call_transition("running", "completed") == "completed"
    with pytest.raises(InvalidStatusTransition):
        validate_tool_call_transition("completed", "running")

    repos = _create_repos(tmp_path)
    _seed_project_dataset_job(repos)
    assert repos.jobs.set_status("job_phase4", "queued")["status"] == "queued"
    assert repos.jobs.set_status("job_phase4", "running")["status"] == "running"
    assert repos.jobs.set_status("job_phase4", "completed")["status"] == "completed"
    with pytest.raises(InvalidStatusTransition):
        repos.jobs.set_status("job_phase4", "running")


def test_idempotent_tool_call_write_reuses_job_step_record(tmp_path: Path) -> None:
    repos = _create_repos(tmp_path)
    _seed_project_dataset_job(repos)

    first = repos.tool_calls.save(
        {"id": "call_first", "jobId": "job_phase4", "stepId": "step_same", "toolId": "ml.basic_metrics", "status": "planned"}
    )
    second = repos.tool_calls.save(
        {
            "id": "call_second",
            "jobId": "job_phase4",
            "stepId": "step_same",
            "toolId": "ml.basic_metrics",
            "status": "running",
            "attempt": 2,
        }
    )

    assert second["id"] == first["id"]
    assert second["status"] == "running"
    assert second["attempt"] == 2
    assert len(repos.tool_calls.list_for_job("job_phase4")) == 1


def test_idempotent_artifact_metadata_write_and_s3_bucket_validation(tmp_path: Path) -> None:
    repos = _create_repos(tmp_path)
    _seed_project_dataset_job(repos)
    repos.tool_calls.save({"id": "call_artifact", "jobId": "job_phase4", "stepId": "step_artifact", "toolId": "ml.basic_metrics", "status": "completed"})

    first = repos.artifacts.save(_artifact_record("artifact_first", storage_provider="s3", bucket="mdi-artifacts"))
    second = repos.artifacts.save(_artifact_record("artifact_second", storage_provider="s3", bucket="mdi-artifacts"))

    assert second["id"] == first["id"]
    assert second["storageProvider"] == "s3"
    assert second["bucket"] == "mdi-artifacts"
    assert len(repos.artifacts.list_for_job("job_phase4")) == 1
    with pytest.raises(ValueError, match="requires bucket"):
        repos.artifacts.save(_artifact_record("artifact_missing_bucket", storage_provider="s3", bucket=None, sha256="otherhash"))


def test_concurrent_job_event_seq_and_after_seq_ordering_are_stable(tmp_path: Path) -> None:
    repos = _create_repos(tmp_path, allow_threads=True)
    _seed_project_dataset_job(repos)

    def append(index: int) -> int:
        return repos.job_events.append_event(
            "job_phase4",
            event_type=f"phase4.event.{index}",
            status="info",
            message=f"event {index}",
            payload={"attempt": 1, "index": index},
        ).seq

    with ThreadPoolExecutor(max_workers=8) as pool:
        seqs = list(pool.map(append, range(40)))

    assert sorted(seqs) == list(range(1, 41))
    assert [event.seq for event in repos.job_events.list_events_after_seq("job_phase4", 25)] == list(range(26, 41))


def _create_engine(tmp_path: Path, *, allow_threads: bool = False) -> Engine:
    database_path = tmp_path / "phase4.sqlite"
    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        future=True,
        connect_args={"check_same_thread": not allow_threads},
    )
    metadata.create_all(engine)
    return engine


def _create_repos(tmp_path: Path, *, allow_threads: bool = False) -> SqlAlchemyRepositoryBundle:
    return SqlAlchemyRepositoryBundle.create(_create_engine(tmp_path, allow_threads=allow_threads))


def _seed_project_dataset_job(repos: SqlAlchemyRepositoryBundle) -> None:
    repos.projects.save({"id": "project_phase4", "name": "Phase 4"})
    repos.datasets.save({"id": "dataset_phase4", "projectId": "project_phase4", "name": "Dataset"})
    repos.jobs.save({"id": "job_phase4", "projectId": "project_phase4", "datasetId": "dataset_phase4", "status": "created"})


def _artifact_record(artifact_id: str, *, storage_provider: str, bucket: str | None, sha256: str = "stablehash") -> dict[str, object]:
    return {
        "id": artifact_id,
        "projectId": "project_phase4",
        "datasetId": "dataset_phase4",
        "jobId": "job_phase4",
        "toolCallId": "call_artifact",
        "type": "metrics_json",
        "name": "metrics.json",
        "storageKey": "projects/project_phase4/jobs/job_phase4/tool_calls/call_artifact/metrics.json",
        "storageProvider": storage_provider,
        "bucket": bucket,
        "previewKey": "previews/metrics.png",
        "sizeBytes": 10,
        "contentType": "application/json",
        "contentHash": sha256,
        "sha256": sha256,
        "metadata": {"createdAt": "2026-06-26T00:00:00+00:00", "provenance": {}},
    }
