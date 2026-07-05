from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mdi_api.phase2_runtime import reset_phase2_runtime
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    get_planner_job,
    get_planner_job_artifacts,
    get_planner_job_events,
    get_planner_job_result,
    get_planner_job_tool_calls,
    planner_jobs,
    reset_planner_runtime,
)
from mdi_llm import OpenAICompatibleProvider, PlannerRequest
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan


@pytest.mark.llm_integration
def test_openai_compatible_llm_live_gated_plan_validation() -> None:
    _require_live_llm_env()

    registry = load_manifests()
    provider = OpenAICompatibleProvider()
    request = PlannerRequest(
        user_prompt="Create one safe AnalysisPlan step using ml.basic_metrics for y_true and y_pred.",
        dataset_id="dataset_llm_live",
        profile_id="profile_llm_live",
        tool_registry_version=registry.version,
    )
    profile = DataProfile(
        profileId="profile_llm_live",
        datasetId="dataset_llm_live",
        version="0.1",
        datasetType="ml",
        createdAt="2026-07-03T00:00:00+00:00",
    )

    response = provider.generate_plan(request, tools=[tool for tool in registry.tools if tool.stage == "mvp"], data_profile=profile)

    assert response.raw_json is not None
    result = validate_plan(response.raw_json, registry=registry)
    assert result.ok, [error.code for error in result.errors]
    _assert_live_key_not_leaked(response.raw_json)


@pytest.mark.llm_integration
def test_openai_compatible_llm_live_gated_persisted_job_execution(tmp_path: Path) -> None:
    _require_live_llm_env()

    phase2 = reset_phase2_runtime(tmp_path / "phase9d")
    phase2.ensure_project("project_9d_live")
    uploaded = phase2.upload_dataset(
        {
            "projectId": "project_9d_live",
            "datasetName": "Phase 9D live metrics",
            "files": [
                {
                    "fileName": "metrics.csv",
                    "content": "formula,y_true,y_pred\nSiO2,2.1,2.0\nAl2O3,3.4,3.5\nCaO,1.8,1.9\nMgO,4.2,4.0\n",
                }
            ],
        }
    )
    dataset_id = uploaded["datasetId"]
    profile_id = uploaded["profile"]["profileId"]
    reset_planner_runtime()

    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt=(
                "Create exactly one executable AnalysisPlan JSON step using toolId ml.basic_metrics. "
                "Use normalized object ml_table, targetColumn y_true, predictionColumn y_pred, "
                "and output metrics_json only."
            ),
            projectId="project_9d_live",
            datasetId=dataset_id,
            profileId=profile_id,
            provider="openai_compatible",
            enqueue=True,
        ),
        registry=load_manifests(),
    )

    if not result.ok:
        codes = [error.get("code") for error in result.validation_errors]
        pytest.fail(f"Live LLM planner job failed before persistence with validation/error codes: {codes}")

    assert result.job_id is not None
    assert result.plan_id is not None
    assert result.plan_hash is not None
    assert result.enqueued is True
    assert result.executed is True
    assert result.planner_provider == "openai_compatible"

    job = get_planner_job(result.job_id)
    events = get_planner_job_events(result.job_id)
    tool_calls = get_planner_job_tool_calls(result.job_id)
    artifacts = get_planner_job_artifacts(result.job_id)
    summary = get_planner_job_result(result.job_id)

    assert job["status"] == "completed"
    assert job["planId"] == result.plan_id
    assert {event["eventType"] for event in events} >= {"plan.loaded", "data.loaded", "tool.completed", "job.completed"}
    assert len(tool_calls) == 1
    assert tool_calls[0]["toolId"] == "ml.basic_metrics"
    assert tool_calls[0]["status"] == "completed"
    assert any(artifact["type"] == "metrics_json" for artifact in artifacts)
    assert summary["status"] == "completed"
    assert summary["artifactCount"] >= 1
    _assert_live_key_not_leaked(result.__dict__, job, events, tool_calls, artifacts, summary)


def _require_live_llm_env() -> None:
    if os.getenv("MDI_RUN_LLM_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_LLM_INTEGRATION=1 to run live OpenAI-compatible LLM integration")

    required = ["MDI_LLM_BASE_URL", "MDI_LLM_API_KEY", "MDI_LLM_MODEL"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing required LLM integration env vars: {', '.join(missing)}")


def _assert_live_key_not_leaked(*values: object) -> None:
    api_key = os.getenv("MDI_LLM_API_KEY") or ""
    if not api_key:
        return
    dumped = json.dumps(values, ensure_ascii=False, default=str)
    if api_key in dumped:
        pytest.fail("Live LLM API key leaked into persisted planner evidence")
