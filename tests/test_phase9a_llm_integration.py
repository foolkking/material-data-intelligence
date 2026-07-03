from __future__ import annotations

import os

import pytest

from mdi_llm import OpenAICompatibleProvider, PlannerRequest
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan


@pytest.mark.llm_integration
def test_openai_compatible_llm_live_gated_plan_validation() -> None:
    if os.getenv("MDI_RUN_LLM_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_LLM_INTEGRATION=1 to run live OpenAI-compatible LLM integration")

    required = ["MDI_LLM_BASE_URL", "MDI_LLM_API_KEY", "MDI_LLM_MODEL"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing required LLM integration env vars: {', '.join(missing)}")

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
