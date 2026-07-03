from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from mdi_api import create_app
from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import (
    get_planner_analysis_plan,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
)
from mdi_schemas import AnalysisPlan
from mdi_tool_registry import load_manifests
from mdi_workers import QueueToolExecution, QueueWorkerRuntime


def test_planner_read_routes_return_persisted_job_and_plan_from_same_repository() -> None:
    client = TestClient(create_app())

    created = client.post(
        "/planner/jobs",
        json={
            "userPrompt": "compute basic metrics",
            "projectId": "project_8c_route",
            "datasetId": "dataset_8c_route",
            "profileId": "profile_8c_route",
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
