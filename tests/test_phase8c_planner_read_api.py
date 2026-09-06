from __future__ import annotations

from typing import Any

from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from fastapi import HTTPException
import pytest

from mdi_api import create_app
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import (
    get_planner_analysis_plan,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_artifact_content,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
)
from mdi_schemas import AnalysisPlan
from mdi_tool_registry import load_manifests
from mdi_workers import QueueToolExecution, QueueWorkerRuntime


def test_planner_read_routes_return_persisted_job_and_plan_from_same_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "1")
    client = TestClient(create_app())

    created = client.post(
        "/planner/jobs",
        json={
            "userPrompt": "compute basic metrics",
            "projectId": "project_8c_route",
            "datasetId": "dataset_8c_route",
            "profileId": "profile_8c_route",
            "provider": "mock",
            "enqueue": False,
        },
    ).json()

    assert created["ok"] is True
    assert created["job_id"]
    assert created["plan_id"]
    assert created["plan_hash"]
    assert created["enqueued"] is False
    assert created["executed"] is False

    job = client.get(f"/planner/jobs/{created['job_id']}").json()
    assert job["jobId"] == created["job_id"]
    assert job["planId"] == created["plan_id"]
    assert job["planHash"] == created["plan_hash"]
    assert job["toolCallCount"] == 0
    assert job["provenance"]["binding"] == "jobs.plan_id -> analysis_plans.id"
    assert job["provenance"]["fallbackUsed"] is False
    assert job["analysisPlan"]["steps"][0]["stepId"]
    assert job["analysisPlan"]["steps"][0]["toolId"] == "ml.basic_metrics"

    plan = client.get(f"/planner/analysis-plans/{created['plan_id']}").json()
    assert plan["planId"] == created["plan_id"]
    assert plan["planHash"] == created["plan_hash"]
    assert plan["validationStatus"] == "validated"
    assert plan["analysisPlan"]["steps"][0]["toolId"] == "ml.basic_metrics"

    stream = client.get(f"/planner/jobs/{created['job_id']}/events/stream")
    assert stream.status_code == 200
    assert stream.headers["content-type"].startswith("text/event-stream")
    assert "event: job.created" in stream.text
    assert "event: plan.persisted" in stream.text
    assert created["plan_id"] in stream.text
    assert created["plan_hash"] in stream.text


def test_planner_read_endpoints_expose_execution_provenance_without_mutating() -> None:
    repos, ids, plan_hash = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    result = runtime.handle_job(ids["job"])
    assert result.status == "completed"

    before_events = len(repos.job_events.list_for_job(ids["job"]))
    before_tool_calls = len(repos.tool_calls.list_for_job(ids["job"]))
    before_artifacts = len(repos.artifacts.list_for_job(ids["job"]))

    job = get_planner_job(ids["job"], repositories=repos)
    events = get_planner_job_events(ids["job"], repositories=repos)
    tool_calls = get_planner_job_tool_calls(ids["job"], repositories=repos)
    artifacts = get_planner_job_artifacts(ids["job"], repositories=repos)
    result_summary = get_planner_job_result(ids["job"], repositories=repos)
    plan = get_planner_analysis_plan(ids["plan"], repositories=repos)

    assert job["status"] == "completed"
    assert job["planId"] == ids["plan"]
    assert job["planHash"] == plan_hash
    assert plan["planHash"] == plan_hash
    assert any(event["eventType"] == "plan.loaded" and event["payload"]["planId"] == ids["plan"] for event in events)
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"
    assert tool_calls[0]["planId"] == ids["plan"]
    assert tool_calls[0]["planHash"] == plan_hash
    assert len(artifacts) == 1
    assert artifacts[0]["planId"] == ids["plan"]
    assert artifacts[0]["planHash"] == plan_hash
    assert result_summary["status"] == "completed"
    assert result_summary["planId"] == ids["plan"]
    assert result_summary["planHash"] == plan_hash
    assert "1 ToolCall" in result_summary["summary"]

    assert len(repos.job_events.list_for_job(ids["job"])) == before_events
    assert len(repos.tool_calls.list_for_job(ids["job"])) == before_tool_calls
    assert len(repos.artifacts.list_for_job(ids["job"])) == before_artifacts


def test_planner_job_artifact_content_is_job_scoped_and_hash_validated() -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]
    response = get_planner_job_artifact_content(ids["job"], artifact["id"], repositories=repos, queue_runtime=runtime)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-content-sha256"] == artifact["contentHash"]
    assert "content-disposition" not in response.headers
    assert response.body
    download = get_planner_job_artifact_content(
        ids["job"],
        artifact["id"],
        download=True,
        repositories=repos,
        queue_runtime=runtime,
    )
    assert download.headers["content-disposition"].startswith(
        'attachment; filename="'
    )
    assert "\n" not in download.headers["content-disposition"]
    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content("another_job", artifact["id"], repositories=repos, queue_runtime=runtime)
    assert raised.value.status_code == 404


@pytest.mark.parametrize("error_code", ["NoSuchKey", "NoSuchBucket", "NotFound", "404"])
def test_planner_job_artifact_content_maps_missing_object_storage_to_typed_404(
    error_code: str,
) -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]

    def missing(_: str) -> bytes:
        raise ClientError(
            {"Error": {"Code": error_code, "Message": "internal object-store detail"}},
            "GetObject",
        )

    runtime.artifact_storage.get_bytes = missing
    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content(
            ids["job"],
            artifact["id"],
            repositories=repos,
            queue_runtime=runtime,
        )
    assert raised.value.status_code == 404
    assert raised.value.detail == {
        "code": "ARTIFACT_CONTENT_NOT_FOUND",
        "message": "The exact Artifact payload is currently unavailable.",
    }
    assert "internal object-store detail" not in str(raised.value.detail)


def test_planner_job_artifact_content_maps_local_missing_file_to_typed_404() -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]

    def missing(_: str) -> bytes:
        raise FileNotFoundError("private local storage path")

    runtime.artifact_storage.get_bytes = missing
    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content(
            ids["job"],
            artifact["id"],
            repositories=repos,
            queue_runtime=runtime,
        )
    assert raised.value.status_code == 404
    assert raised.value.detail["code"] == "ARTIFACT_CONTENT_NOT_FOUND"
    assert "private local storage path" not in str(raised.value.detail)


def test_planner_job_artifact_content_distinguishes_gone_metadata_from_missing_storage() -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]
    stored = repos.artifacts.records[artifact["id"]]
    stored["storageKey"] = ""
    stored["storage_key"] = ""

    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content(
            ids["job"],
            artifact["id"],
            repositories=repos,
            queue_runtime=runtime,
        )

    assert raised.value.status_code == 410
    assert raised.value.detail == {
        "code": "ARTIFACT_CONTENT_GONE",
        "message": (
            "Artifact metadata is retained, but the exact persisted payload is "
            "no longer available."
        ),
    }


def test_planner_job_artifact_content_rejects_large_browser_transfer_before_storage() -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]
    stored = repos.artifacts.records[artifact["id"]]
    stored["sizeBytes"] = 67_108_865
    stored["size_bytes"] = 67_108_865
    reads: list[str] = []
    runtime.artifact_storage.get_bytes = lambda key: reads.append(key) or b""

    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content(
            ids["job"],
            artifact["id"],
            repositories=repos,
            queue_runtime=runtime,
        )

    assert raised.value.status_code == 413
    assert raised.value.detail == {
        "code": "ARTIFACT_CONTENT_TOO_LARGE",
        "message": "The exact Artifact exceeds the bounded browser transfer limit.",
        "maximumBytes": 67_108_864,
        "sizeBytes": 67_108_865,
    }
    assert reads == []


def test_planner_job_artifact_content_maps_non_missing_storage_error_to_typed_503() -> None:
    repos, ids, _ = _seed_persisted_plan_repos()
    runtime = QueueWorkerRuntime(repositories=repos, tool_executor=_fake_executor)
    assert runtime.handle_job(ids["job"]).status == "completed"
    artifact = repos.artifacts.list_for_job(ids["job"])[0]

    def denied(_: str) -> bytes:
        raise ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "private bucket detail"}},
            "GetObject",
        )

    runtime.artifact_storage.get_bytes = denied
    with pytest.raises(HTTPException) as raised:
        get_planner_job_artifact_content(
            ids["job"],
            artifact["id"],
            repositories=repos,
            queue_runtime=runtime,
        )
    assert raised.value.status_code == 503
    assert raised.value.detail == {
        "code": "ARTIFACT_STORAGE_UNAVAILABLE",
        "message": "Artifact storage is temporarily unavailable.",
    }
    assert "private bucket detail" not in str(raised.value.detail)


def _seed_persisted_plan_repos() -> tuple[InMemoryRepositoryBundle, dict[str, str], str]:
    repos = InMemoryRepositoryBundle.create()
    ids = {"project": "project_8c", "dataset": "dataset_8c", "job": "job_8c", "plan": "plan_8c"}
    repos.projects.save({"id": ids["project"], "name": ids["project"], "createdBy": "test_user"})
    repos.datasets.save({"id": ids["dataset"], "projectId": ids["project"], "name": ids["dataset"], "createdBy": "test_user"})
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
