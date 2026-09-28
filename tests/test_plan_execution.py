"""Phase 8A: LLM Plan Execution Bridge tests.

Core acceptance: a validated 1-step LLM AnalysisPlan executes EXACTLY that
plan (1 ToolCall), NOT the deterministic 5-tool build_phase2_plan.
"""

from __future__ import annotations

import pytest

from mdi_api.phase2_runtime import Phase2ProductRuntime
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import MockLLMProvider
from mdi_schemas import AnalysisPlan
from mdi_tool_registry import load_manifests


_CSV = "formula,y_true,y_pred\nSiO2,2.1,2.0\nAl2O3,3.4,3.5\nCaO,1.8,1.9\nMgO,4.2,4.0"


def _runtime_with_ml_dataset() -> tuple[Phase2ProductRuntime, str, str]:
    rt = Phase2ProductRuntime()
    rt.create_project({"name": "p8a"})
    project_id = list(rt.projects.keys())[0]
    rt.upload_dataset({
        "projectId": project_id,
        "datasetName": "ml",
        "files": [{"fileName": "data.csv", "content": _CSV}],
    })
    dataset_id = list(rt.datasets.keys())[0]
    return rt, project_id, dataset_id


def _one_step_llm_plan(dataset_id: str) -> AnalysisPlan:
    return AnalysisPlan.model_validate({
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
    })


# ── CORE: 1-step LLM plan executes exactly 1 ToolCall ──────────────

def test_runtime_executes_exact_provided_plan_one_tool_call() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)

    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=True,
    )

    tool_calls = rt.get_job_tool_calls(job["id"])
    # EXACTLY one ToolCall — the LLM plan's single step, NOT 5 deterministic ones
    assert len(tool_calls) == 1, f"expected 1 ToolCall, got {len(tool_calls)}"
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["stepId"] == "llm_step_1"


# ── Artifact / JobEvent / Status of exact plan execution ───────────

def test_exact_plan_execution_produces_metrics_artifact() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=True,
    )
    artifacts = rt.get_job_artifacts(job["id"])
    types = {a.get("type") for a in artifacts}
    # The ml.basic_metrics step must have produced a metrics_json artifact.
    assert any("metrics" in (t or "") for t in types), f"no metrics artifact in {types}"


def test_exact_plan_execution_emits_tool_events() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=True,
    )
    events = rt.get_job_events(job["id"])
    event_types = {e["eventType"] for e in events}
    assert "tool.started" in event_types
    assert "tool.completed" in event_types
    assert "artifact.ready" in event_types
    assert "plan.generated" in event_types


def test_exact_plan_execution_job_status_completed() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=True,
    )
    assert job["status"] == "completed"


def test_planned_only_zero_tool_calls_and_no_tool_artifact() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=False,
    )
    assert len(rt.get_job_tool_calls(job["id"])) == 0
    # System plan/recipe artifacts may exist, but NO tool-produced metrics artifact.
    artifacts = rt.get_job_artifacts(job["id"])
    types = {a.get("type") for a in artifacts}
    assert not any(t == "metrics_json" for t in types), f"unexpected tool artifact in planned-only: {types}"
    # No tool.started/completed events fired.
    event_types = {e["eventType"] for e in rt.get_job_events(job["id"])}
    assert "tool.started" not in event_types
    assert "tool.completed" not in event_types


def test_runtime_executed_plan_is_the_provided_plan() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=True,
    )
    persisted = job["plan"]
    assert len(persisted["steps"]) == 1
    assert persisted["steps"][0]["toolId"] == "ml.basic_metrics"
    assert persisted["steps"][0]["stepId"] == "llm_step_1"


# ── Deterministic fallback preserved ───────────────────────────────

def test_runtime_deterministic_fallback_when_no_plan() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    job = rt.create_job({"projectId": project_id, "datasetId": dataset_id, "userPrompt": "analyze"})
    # Deterministic planner selects multiple MVP tools; the single-CSV dataset
    # has only an ml_table, so it selects the ml tools (>= 1, and the steps are
    # NOT the LLM plan's "llm_step_1").
    tool_calls = rt.get_job_tool_calls(job["id"])
    assert len(tool_calls) >= 1
    assert all(tc["stepId"] != "llm_step_1" for tc in tool_calls)
    assert job["plan"]["steps"][0]["stepId"] != "llm_step_1"


# ── Planned-only (execute=False) does not run tools ────────────────

def test_runtime_planned_only_does_not_execute() -> None:
    rt, project_id, dataset_id = _runtime_with_ml_dataset()
    plan = _one_step_llm_plan(dataset_id)
    job = rt.create_job(
        {"projectId": project_id, "datasetId": dataset_id, "userPrompt": "metrics"},
        analysis_plan=plan,
        execute=False,
    )
    tool_calls = rt.get_job_tool_calls(job["id"])
    assert len(tool_calls) == 0
    assert job["status"] in ("queued", "created")
    # Plan is still persisted even though not executed
    assert job["plan"]["steps"][0]["toolId"] == "ml.basic_metrics"


# ── planner_jobs API: Phase 8B persisted-plan bridge ───────────────

def test_planner_jobs_execute_true_enqueues_without_sync_execution() -> None:
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", datasetId="ds8a", profileId="p8a", execute=True),
        provider=MockLLMProvider(),
        registry=load_manifests(),
    )
    assert result.ok
    assert result.job_id is not None
    assert result.plan_id is not None
    assert result.plan_hash is not None
    assert result.plan_source == "llm"
    assert result.enqueued is True
    assert result.executed is False
    # The returned plan is the validated LLM plan (1 step), not deterministic 5
    assert len(result.plan["steps"]) == 1
    assert result.plan["steps"][0]["toolId"] == "ml.basic_metrics"


def test_planner_jobs_execute_false_is_planned_only() -> None:
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", datasetId="ds8a", profileId="p8a", execute=False),
        provider=MockLLMProvider(),
        registry=load_manifests(),
    )
    assert result.ok
    assert result.job_id is not None
    assert result.plan_id is not None
    assert result.executed is False
    assert result.enqueued is False
    assert result.plan_source == "llm"


def test_planner_jobs_invalid_plan_creates_no_job() -> None:
    from mdi_llm import MockLLMProvider

    bad = MockLLMProvider(fixed_plan={"not": "a valid plan"})
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="metrics", datasetId="ds8a", profileId="p8a", execute=True),
        provider=bad,
        registry=load_manifests(),
    )
    assert not result.ok
    assert result.job_id is None
    assert len(result.validation_errors) > 0
