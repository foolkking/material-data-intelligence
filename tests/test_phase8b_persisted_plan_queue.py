from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import create_engine

from mdi_api.artifact_storage import S3CompatibleArtifactStorage
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.db import metadata
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider
from mdi_schemas import AnalysisPlan
from mdi_tool_registry import load_manifests
from mdi_workers import InMemoryQueueBackend, QueueToolExecution, QueueWorkerRuntime, RedisRQQueueBackend


def test_analysis_plan_repository_round_trip_and_stable_hash_sqlite(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{(tmp_path / 'phase8b.sqlite').as_posix()}", future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    _seed_repos(repos, project_id="project_8b", dataset_id="dataset_8b")

    plan = _one_step_plan("dataset_8b")
    plan_hash = compute_plan_hash(plan)
    saved = repos.analysis_plans.save_plan(
        {
            "id": "plan_8b",
            "projectId": "project_8b",
            "datasetId": "dataset_8b",
            "profileId": "profile_8b",
            "planSource": "llm",
            "plannerProvider": "mock",
            "analysisPlan": plan.model_dump(mode="json"),
            "createdBy": "test_user",
        }
    )

    loaded = repos.analysis_plans.get_plan("plan_8b")
    assert saved["planHash"] == plan_hash
    assert loaded["analysisPlan"] == plan.model_dump(mode="json")
    assert compute_plan_hash(dict(reversed(list(plan.model_dump(mode="json").items())))) == plan_hash
    with pytest.raises(ValueError, match="planHash"):
        repos.analysis_plans.save_plan(
            {
                "id": "plan_bad_hash",
                "projectId": "project_8b",
                "datasetId": "dataset_8b",
                "analysisPlan": plan.model_dump(mode="json"),
                "planHash": "0" * 64,
            }
        )
    engine.dispose()


def test_planner_jobs_success_persists_plan_and_job_with_plan_id() -> None:
    repos = InMemoryRepositoryBundle.create()
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", projectId="project_8b", datasetId="dataset_8b", profileId="profile_8b"),
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok
    assert result.job_id is not None
    assert result.plan_id is not None
    assert result.plan_hash is not None
    assert result.enqueued is False
    assert result.executed is False
    assert repos.jobs.get(result.job_id)["planId"] == result.plan_id
    assert repos.analysis_plans.get_plan(result.plan_id)["planHash"] == result.plan_hash


def test_planner_jobs_validation_failure_persists_nothing() -> None:
    repos = InMemoryRepositoryBundle.create()
    provider = MockLLMProvider(fixed_plan={"not": "an analysis plan"})
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", projectId="project_8b", datasetId="dataset_8b"),
        provider=provider,
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok is False
    assert result.job_id is None
    assert result.plan_id is None
    assert repos.jobs.records == {}
    assert repos.analysis_plans.records == {}


def test_planner_jobs_enqueue_false_does_not_enqueue_or_execute() -> None:
    repos = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(repositories=repos, queue_backend=queue, tool_executor=_fake_executor)

    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", projectId="project_8b", datasetId="dataset_8b", enqueue=False),
        repositories=repos,
        queue_runtime=runtime,
        registry=load_manifests(),
    )

    assert result.ok
    assert result.enqueued is False
    assert result.executed is False
    assert queue.pop_next() is None
    assert repos.tool_calls.list_for_job(result.job_id or "") == []


def test_planner_jobs_enqueue_true_enqueues_only_job_id() -> None:
    repos = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(repositories=repos, queue_backend=queue, tool_executor=_fake_executor)

    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", projectId="project_8b", datasetId="dataset_8b", enqueue=True),
        repositories=repos,
        queue_runtime=runtime,
        registry=load_manifests(),
    )

    assert result.ok
    assert result.enqueued is True
    assert result.executed is False
    assert queue.pop_next() == result.job_id
    assert repos.tool_calls.list_for_job(result.job_id or "") == []


def test_worker_loads_persisted_plan_by_job_id_and_executes_exact_one_step(monkeypatch: pytest.MonkeyPatch) -> None:
    repos, ids, plan_hash = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("build_phase2_plan must not run for persisted plans")

    monkeypatch.setattr("mdi_api.phase2_runtime.build_phase2_plan", forbidden)
    result = runtime.handle_job(ids["job"], plan=_partial_plan())

    tool_calls = repos.tool_calls.list_for_job(ids["job"])
    events = repos.job_events.list_for_job(ids["job"])
    artifacts = repos.artifacts.list_for_job(ids["job"])

    assert result.status == "completed"
    assert result.plan_id == ids["plan"]
    assert result.plan_hash == plan_hash
    assert result.tool_call_count == 1
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"
    assert len(artifacts) == 1
    assert repos.jobs.get(ids["job"])["status"] == "completed"
    plan_loaded = [event for event in events if event.eventType == "plan.loaded"]
    assert plan_loaded
    assert plan_loaded[0].payload["planId"] == ids["plan"]
    assert plan_loaded[0].payload["planHash"] == plan_hash


def test_worker_explicit_fallback_works_only_when_no_persisted_plan() -> None:
    repos = InMemoryRepositoryBundle.create()
    repos.projects.save({"id": "project_8b", "name": "Project 8B"})
    repos.datasets.save({"id": "dataset_8b", "projectId": "project_8b", "name": "Dataset 8B"})
    repos.jobs.save({"id": "job_no_plan", "projectId": "project_8b", "datasetId": "dataset_8b", "status": "created"})
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)

    no_plan = runtime.handle_job("job_no_plan")
    assert no_plan.tool_call_count == 0

    repos.jobs.save({"id": "job_explicit", "projectId": "project_8b", "datasetId": "dataset_8b", "status": "created"})
    explicit = runtime.handle_job("job_explicit", plan=_partial_plan())
    assert explicit.status == "completed"
    assert explicit.tool_call_count == 1
    assert repos.tool_calls.list_for_job("job_explicit")[0]["stepId"] == "explicit_step"


def test_unknown_tool_rejected_before_persistence() -> None:
    repos = InMemoryRepositoryBundle.create()
    bad_plan = _one_step_plan("dataset_8b").model_dump(mode="json")
    bad_plan["steps"][0]["toolId"] = "unknown.not_registered"
    provider = MockLLMProvider(fixed_plan=bad_plan)

    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", projectId="project_8b", datasetId="dataset_8b"),
        provider=provider,
        repositories=repos,
        registry=load_manifests(),
    )

    assert result.ok is False
    assert any(error["code"] == "UNKNOWN_TOOL" for error in result.validation_errors)
    assert repos.analysis_plans.records == {}
    assert repos.jobs.records == {}


@pytest.mark.integration
def test_phase8b_service_backed_persisted_plan_queue_exact_execution(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    engine = _pg_engine()
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    suffix = uuid.uuid4().hex[:10]
    ids = {
        "project": f"project_8b_{suffix}",
        "dataset": f"dataset_8b_{suffix}",
        "job": f"job_8b_{suffix}",
        "plan": f"plan_8b_{suffix}",
    }
    _seed_repos(repos, project_id=ids["project"], dataset_id=ids["dataset"])
    plan = _one_step_plan(ids["dataset"])
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan(
        {
            "id": ids["plan"],
            "projectId": ids["project"],
            "datasetId": ids["dataset"],
            "profileId": ids["dataset"],
            "planSource": "llm",
            "plannerProvider": "mock",
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "createdBy": "test_user",
        }
    )
    repos.jobs.save(
        {
            "id": ids["job"],
            "projectId": ids["project"],
            "datasetId": ids["dataset"],
            "planId": ids["plan"],
            "status": "created",
            "kind": "analysis",
            "createdBy": "test_user",
        }
    )
    repos.analysis_plans.attach_plan_to_job(ids["plan"], ids["job"])

    runtime = QueueWorkerRuntime(
        repository_factory=create_repository_factory(load_settings()),
        queue_backend=_live_redis_queue_backend(),
        artifact_storage=_minio_storage(f"phase8b-{suffix}"),
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter-artifacts",
    )

    submit = runtime.submit_job(ids["job"])
    assert submit.enqueued is True
    assert _redis_queue_has_job(ids["job"], queue_name="mdi-test-phase8b")
    result = runtime.handle_job(ids["job"], object_store=_object_store())

    tool_calls = repos.tool_calls.list_for_job(ids["job"])
    artifacts = repos.artifacts.list_for_job(ids["job"])
    events = repos.job_events.list_for_job(ids["job"])

    assert result.status == "completed"
    assert result.plan_id == ids["plan"]
    assert result.plan_hash == plan_hash
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"
    assert len(artifacts) >= 1
    assert artifacts[0]["storageProvider"] == "s3"
    assert artifacts[0]["bucket"] == os.getenv("MINIO_BUCKET", "mdi-artifacts")
    assert _minio_storage("").exists(artifacts[0]["storageKey"])
    assert repos.jobs.get(ids["job"])["status"] == "completed"
    plan_events = [event for event in events if event.eventType == "plan.loaded"]
    assert plan_events
    assert plan_events[0].payload["planId"] == ids["plan"]
    assert plan_events[0].payload["planHash"] == plan_hash
    engine.dispose()


def _seed_repos(repos: Any, *, project_id: str, dataset_id: str) -> None:
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "test_user"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "test_user"})


def _seed_persisted_plan_repos() -> tuple[InMemoryRepositoryBundle, dict[str, str], str]:
    repos = InMemoryRepositoryBundle.create()
    ids = {"project": "project_8b", "dataset": "dataset_8b", "job": "job_8b", "plan": "plan_8b"}
    _seed_repos(repos, project_id=ids["project"], dataset_id=ids["dataset"])
    plan = _one_step_plan(ids["dataset"])
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan(
        {
            "id": ids["plan"],
            "projectId": ids["project"],
            "datasetId": ids["dataset"],
            "profileId": ids["dataset"],
            "planSource": "llm",
            "plannerProvider": "mock",
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "createdBy": "test_user",
        }
    )
    repos.jobs.save({"id": ids["job"], "projectId": ids["project"], "datasetId": ids["dataset"], "planId": ids["plan"], "status": "created"})
    repos.analysis_plans.attach_plan_to_job(ids["plan"], ids["job"])
    return repos, ids, plan_hash


def _one_step_plan(dataset_id: str) -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "compute metrics",
            "datasetId": dataset_id,
            "profileId": dataset_id,
            "toolRegistryVersion": load_manifests().version,
            "assumptions": [],
            "warnings": [],
            "steps": [
                {
                    "stepId": "llm_step_1",
                    "toolId": "ml.basic_metrics",
                    "purpose": "metrics",
                    "reason": "user asked",
                    "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
                    "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
                    "output": {"artifactTypes": ["metrics_json"]},
                }
            ],
            "expectedArtifacts": [{"name": "metrics.json", "type": "metrics_json", "fromStepId": "llm_step_1"}],
        }
    )


def _partial_plan() -> dict[str, Any]:
    return {
        "steps": [
            {
                "stepId": "explicit_step",
                "toolId": "ml.basic_metrics",
                "inputRefs": [],
                "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
                "output": {"artifactTypes": ["metrics_json"]},
            }
        ]
    }


def _fake_executor(request: Any, context: Any) -> QueueToolExecution:
    return QueueToolExecution(
        artifacts=[
            {
                "id": f"artifact_{request.stepId}",
                "type": "metrics_json",
                "name": "metrics.json",
                "content": {"stepId": request.stepId, "toolId": request.toolId, "ok": True},
                "contentType": "application/json",
                "version": "1",
                "metadata": {"inputHashes": [], "createdAt": "2026-07-03T00:00:00+00:00", "provenance": {}},
            }
        ]
    )


def _object_store() -> dict[str, Any]:
    import pandas as pd

    return {
        "ml_table": pd.DataFrame(
            {
                "formula": ["SiO2", "Al2O3", "CaO", "MgO"],
                "y_true": [2.1, 3.4, 1.8, 4.2],
                "y_pred": [2.0, 3.5, 1.9, 4.0],
            }
        )
    }


def _pg_engine() -> Any:
    url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url or "postgres" not in url:
        pytest.skip("No PostgreSQL DATABASE_URL configured")
    return create_engine(url, future=True)


def _live_redis_queue_backend() -> RedisRQQueueBackend:
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        pytest.skip("No REDIS_URL configured")
    try:
        from redis import Redis

        Redis.from_url(redis_url).ping()
    except Exception:
        pytest.skip("Redis not reachable")
    return RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase8b")


def _redis_queue_has_job(job_id: str, *, queue_name: str) -> bool:
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        pytest.skip("No REDIS_URL configured")
    try:
        from redis import Redis
        from rq import Queue

        return Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(job_id) is not None
    except Exception:
        pytest.skip("Redis/RQ job lookup not reachable")


def _minio_storage(prefix: str) -> S3CompatibleArtifactStorage:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
    secret = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    try:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access,
            aws_secret_access_key=secret,
            region_name="us-east-1",
        )
        try:
            client.head_bucket(Bucket=bucket)
        except Exception:
            client.create_bucket(Bucket=bucket)
    except Exception:
        pytest.skip("MinIO not reachable")
    return S3CompatibleArtifactStorage(
        bucket=bucket,
        endpoint_url=endpoint,
        prefix=prefix,
        access_key_id=access,
        secret_access_key=secret,
        client=client,
    )
