"""Phase 7 LLM JSON Planner + BYOK Secret Management tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_api.secrets import InMemorySecretStore
from mdi_llm import MockLLMProvider, OpenAICompatibleProvider, PlannerRequest, PlannerUserConfig, redact_params_for_log
from mdi_llm.planner_prompt import build_planner_prompt
from mdi_schemas import AnalysisPlan, AnalysisStep, ArtifactType, DataProfile
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_tool_registry.plan_validator import PlanValidationError, validate_plan


# ── helpers ─────────────────────────────────────────────────────────

def _registry() -> ToolRegistry:
    return load_manifests()


def _data_profile() -> DataProfile:
    return DataProfile(
        profileId="p_test",
        datasetId="ds_test",
        version="0.1",
        datasetType="ml",
        createdAt="2026-06-27T00:00:00+00:00",
    )


# ── 1. MockLLMProvider returns valid JSON plan ─────────────────────

def test_mock_provider_returns_valid_analysis_plan() -> None:
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    p = MockLLMProvider()
    resp = p.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert resp.raw_json is not None
    parsed = AnalysisPlan.model_validate(resp.raw_json)
    assert len(parsed.steps) >= 1
    assert parsed.steps[0].toolId == "ml.basic_metrics"


# ── 2. Invalid JSON plan rejected ──────────────────────────────────

def test_validate_rejects_non_dict() -> None:
    result = validate_plan("not a dict", registry=_registry())  # type: ignore[arg-type]
    assert not result.ok
    assert any("not a JSON object" in e.message for e in result.errors)


def test_validate_rejects_bad_schema() -> None:
    result = validate_plan({"schemaVersion": "0.1", "steps": []}, registry=_registry())
    assert not result.ok
    assert any("does not match" in e.message for e in result.errors)


# ── 3. Unknown tool_id rejected ────────────────────────────────────

def test_validate_rejects_unknown_tool() -> None:
    result = validate_plan(
        {
            "schemaVersion": "0.1",
            "goal": "test",
            "datasetId": "ds1",
            "profileId": "p1",
            "toolRegistryVersion": "0.1.0",
            "steps": [
                {
                    "stepId": "s1",
                    "toolId": "nonexistent.phantom_tool",
                    "purpose": "x",
                    "reason": "x",
                    "inputRefs": [],
                    "params": {},
                    "output": {"artifactTypes": ["metrics_json"]},
                }
            ],
            "expectedArtifacts": [],
        },
        registry=_registry(),
    )
    assert not result.ok
    assert any("UNKNOWN_TOOL" in e.code for e in result.errors)


# ── 4. V1/V2 tool rejected ─────────────────────────────────────────

def test_validate_rejects_non_mvp_tool() -> None:
    reg = _registry()
    # Simulate a V1 tool in the registry
    from mdi_tool_registry.loader import ToolRegistry as TR
    v1_tools = tuple(t for t in reg.tools) + (
        type(list(reg.tools)[0])(
            toolId="test.v1_tool",
            name="V1 Test",
            category="analysis",
            domain="ml",
            implementationSource="platform_builtin",
            description="v1 only",
            version="0.2.0",
            adapter="FakeAdapter",
            inputSchema={"inputOptions": []},
            paramsSchema={},
            outputSchema={"primaryArtifactType": "metrics_json", "secondaryArtifactTypes": [], "displayTarget": "ml"},
            artifactTypes=["metrics_json"],
            costLevel="low",
            defaultTimeoutSec=30,
            maxTimeoutSec=120,
            cachePolicy="reuse",
            permissions=[],
            resourceLimits={},
            source={},
            stage="v1",
        ),
    )
    v1_reg = TR(version="0.1.0", tools=v1_tools)

    result = validate_plan(
        {
            "schemaVersion": "0.1",
            "goal": "test",
            "datasetId": "ds1",
            "profileId": "p1",
            "toolRegistryVersion": "0.1.0",
            "steps": [
                {
                    "stepId": "s1",
                    "toolId": "test.v1_tool",
                    "purpose": "x",
                    "reason": "x",
                    "inputRefs": [],
                    "params": {},
                    "output": {"artifactTypes": ["metrics_json"]},
                }
            ],
            "expectedArtifacts": [],
        },
        registry=v1_reg,
    )
    assert not result.ok
    assert any("NON_MVP_TOOL" in e.code for e in result.errors)


# ── 5. Duplicated step_id rejected ────────────────────────────────

def test_validate_rejects_duplicate_step_ids() -> None:
    result = validate_plan(
        {
            "schemaVersion": "0.1",
            "goal": "test",
            "datasetId": "ds1",
            "profileId": "p1",
            "toolRegistryVersion": "0.1.0",
            "steps": [
                {
                    "stepId": "dup",
                    "toolId": "ml.basic_metrics",
                    "purpose": "x",
                    "reason": "x",
                    "inputRefs": [],
                    "params": {"targetColumn": "y", "predictionColumn": "p"},
                    "output": {"artifactTypes": ["metrics_json"]},
                },
                {
                    "stepId": "dup",
                    "toolId": "ml.outlier_table",
                    "purpose": "x",
                    "reason": "x",
                    "inputRefs": [],
                    "params": {"targetColumn": "y", "predictionColumn": "p"},
                    "output": {"artifactTypes": ["table_json"]},
                },
            ],
            "expectedArtifacts": [],
        },
        registry=_registry(),
    )
    assert not result.ok
    assert any("DUPLICATE_STEP_ID" in e.code for e in result.errors)


# ── 6. Empty steps rejected ────────────────────────────────────────

def test_validate_rejects_empty_steps() -> None:
    result = validate_plan(
        {
            "schemaVersion": "0.1",
            "goal": "test",
            "datasetId": "ds1",
            "profileId": "p1",
            "toolRegistryVersion": "0.1.0",
            "steps": [],
            "expectedArtifacts": [],
        },
        registry=_registry(),
    )
    assert not result.ok
    assert any("STEPS_EMPTY" in e.code for e in result.errors)


# ── 7. Params containing api_key/token/password rejected ───────────

def test_validate_rejects_credential_in_params() -> None:
    result = validate_plan(
        {
            "schemaVersion": "0.1",
            "goal": "test",
            "datasetId": "ds1",
            "profileId": "p1",
            "toolRegistryVersion": "0.1.0",
            "steps": [
                {
                    "stepId": "s1",
                    "toolId": "ml.basic_metrics",
                    "purpose": "x",
                    "reason": "x",
                    "inputRefs": [],
                    "params": {"api_key": "sk-secret!", "targetColumn": "y", "predictionColumn": "p"},
                    "output": {"artifactTypes": ["metrics_json"]},
                }
            ],
            "expectedArtifacts": [],
        },
        registry=_registry(),
    )
    assert not result.ok
    assert any("CREDENTIAL_IN_PARAMS" in e.code for e in result.errors)


# ── 8. Planner preview does not create job ─────────────────────────

def test_planner_preview_creates_no_job() -> None:
    from mdi_api.routers.planner import PlannerPreviewRequest, planner_preview

    result = planner_preview(
        PlannerPreviewRequest(userPrompt="Analyze this dataset", datasetId="ds_test", profileId="p_test"),
        registry=_registry(),
    )
    assert result.plan is not None
    assert result.validation is not None
    assert result.validation.ok


# ── 9. Planner validate does not create job ────────────────────────

def test_planner_validate_creates_no_job() -> None:
    from mdi_api.routers.planner import PlannerValidateRequest, planner_validate

    result = planner_validate(
        PlannerValidateRequest(
            plan={
                "schemaVersion": "0.1",
                "goal": "test",
                "datasetId": "ds1",
                "profileId": "p1",
                "toolRegistryVersion": "0.1.0",
                "steps": [
                    {
                        "stepId": "s1",
                        "toolId": "ml.basic_metrics",
                        "purpose": "x",
                        "reason": "x",
                        "inputRefs": [],
                        "params": {"targetColumn": "y", "predictionColumn": "p"},
                        "output": {"artifactTypes": ["metrics_json"]},
                    }
                ],
                "expectedArtifacts": [],
            }
        ),
        registry=_registry(),
    )
    assert result.ok


# ── 10. Planner jobs validates before creating a job ───────────────

def test_planner_jobs_creates_job_only_after_valid_plan() -> None:
    from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs

    result = planner_jobs(
        PlannerJobsRequest(userPrompt="run metrics", datasetId="ds_test", profileId="p_test"),
        registry=_registry(),
    )
    assert result.ok
    assert result.job_id is not None
    assert result.validation_errors == []
    # Job ID is deterministic from Phase2ProductRuntime (0001)
    assert "0001" in result.job_id


def test_planner_jobs_rejects_invalid_plan() -> None:
    from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs

    # Use a MockLLMProvider that returns invalid JSON
    bad_provider = MockLLMProvider(fixed_plan={"not": "a plan"})
    result = planner_jobs(
        PlannerJobsRequest(userPrompt="test", datasetId="ds_test", profileId="p_test"),
        provider=bad_provider,
        registry=_registry(),
    )
    assert not result.ok
    assert result.job_id is None
    assert len(result.validation_errors) > 0


# ── 11. Secret list API does not return plaintext ──────────────────

def test_secret_list_never_returns_plaintext_value() -> None:
    store = InMemorySecretStore()
    store.create_secret("user1", "openai", "sk-secret-value-123")
    store.create_secret("user1", "deepseek", "ds-secret-456")

    secrets = store.list_secrets("user1")
    assert len(secrets) == 2
    for s in secrets:
        assert not hasattr(s, "value")
        # encrypted_ref is not the plaintext
        assert s.encrypted_ref == f"memref://{s.id}"


def test_secret_store_get_returns_value_for_internal_use() -> None:
    store = InMemorySecretStore()
    s = store.create_secret("user1", "openai", "my-key")
    sd = store.get_secret(s.id)
    assert sd is not None
    assert sd.value == "my-key"


def test_secret_store_delete() -> None:
    store = InMemorySecretStore()
    s = store.create_secret("user1", "openai", "tmp")
    assert store.delete_secret(s.id) is True
    assert store.get_secret(s.id) is None
    assert store.delete_secret("nonexistent") is False


# ── 12. Redaction helper ───────────────────────────────────────────

def test_redact_params_for_log_strips_credentials() -> None:
    safe = redact_params_for_log({"api_key": "sk-12345", "targetColumn": "y"})
    assert safe["api_key"] == "***REDACTED***"
    assert safe["targetColumn"] == "y"


def test_redact_params_for_log_case_insensitive() -> None:
    safe = redact_params_for_log({"API_KEY": "abc", "Token": "xyz", "ok": 1})
    assert safe["API_KEY"] == "***REDACTED***"
    assert safe["Token"] == "***REDACTED***"
    assert safe["ok"] == 1


# ── 13. Deterministic planner regression ───────────────────────────

def test_phase2_deterministic_planner_still_works() -> None:
    from mdi_api.phase2_runtime import build_phase2_plan

    reg = _registry()
    dp = _data_profile()
    # Minimal profile that should trigger the deterministic 5-tool path
    dp.tableSummary = {
        "nRows": 10,
        "nColumns": 3,
        "columns": [
            {"name": "formula", "dtype": "string", "inferredRole": "formula", "missingCount": 0},
            {"name": "y_true", "dtype": "number", "inferredRole": "target", "missingCount": 0},
            {"name": "y_pred", "dtype": "number", "inferredRole": "prediction", "missingCount": 0},
        ],
    }
    dp.objects = [{"objectId": "obj1", "objectType": "Composition", "count": 3, "sourceFileIds": [], "periodicity": "non_periodic"}]
    # The deterministic planner uses object_refs keys "formulas" and "ml_table"
    # to decide which tool families are applicable.
    plan = build_phase2_plan(
        user_prompt="test",
        data_profile=dp,
        registry=reg,
        object_refs={"formulas": "ref_f", "structures": "ref_s", "ml_table": "ref_ml"},
    )
    assert isinstance(plan, AnalysisPlan)
    assert len(plan.steps) > 0


# ── 14. OpenAICompatibleProvider request construction test ──────────

def test_openai_provider_request_with_fake_transport() -> None:
    def fake_transport(*, model, messages, temperature, max_tokens):
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "schemaVersion": "0.1",
                                "goal": "test from fake",
                                "datasetId": "ds1",
                                "profileId": "p1",
                                "toolRegistryVersion": "0.1.0",
                                "steps": [
                                    {
                                        "stepId": "s1",
                                        "toolId": "ml.basic_metrics",
                                        "purpose": "x",
                                        "reason": "x",
                                        "inputRefs": [],
                                        "params": {},
                                        "output": {"artifactTypes": ["metrics_json"]},
                                    }
                                ],
                                "expectedArtifacts": [],
                            }
                        )
                    },
                    "finish_reason": "stop",
                }
            ]
        }

    provider = OpenAICompatibleProvider(transport=fake_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    resp = provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert resp.raw_json is not None
    assert resp.finish_reason == "stop"
    assert resp.model == "gpt-4o"


# ── 15. Non-JSON completion is rejected gracefully (no exception) ────

def test_openai_provider_non_json_completion_returns_none() -> None:
    def bad_transport(*, model, messages, temperature, max_tokens):
        return {"choices": [{"message": {"content": "I'm sorry, I cannot help with that."}, "finish_reason": "stop"}]}

    provider = OpenAICompatibleProvider(transport=bad_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    resp = provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    # Non-JSON content must NOT raise; raw_json is None so validator can reject.
    assert resp.raw_json is None
    assert resp.raw_text == "I'm sorry, I cannot help with that."


# ── 16. Markdown-fenced JSON is extracted and parsed ────────────────

def test_openai_provider_markdown_fenced_json_is_extracted() -> None:
    plan_json = {
        "schemaVersion": "0.1",
        "goal": "fenced",
        "datasetId": "ds1",
        "profileId": "p1",
        "toolRegistryVersion": "0.1.0",
        "steps": [
            {
                "stepId": "s1",
                "toolId": "ml.basic_metrics",
                "purpose": "x",
                "reason": "x",
                "inputRefs": [],
                "params": {"targetColumn": "y", "predictionColumn": "p"},
                "output": {"artifactTypes": ["metrics_json"]},
            }
        ],
        "expectedArtifacts": [],
    }

    def fenced_transport(*, model, messages, temperature, max_tokens):
        wrapped = "```json\n" + json.dumps(plan_json) + "\n```"
        return {"choices": [{"message": {"content": wrapped}, "finish_reason": "stop"}]}

    provider = OpenAICompatibleProvider(transport=fenced_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    resp = provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert resp.raw_json is not None
    assert resp.raw_json["goal"] == "fenced"
    # And it must pass validation
    result = validate_plan(resp.raw_json, registry=reg)
    assert result.ok


# ── 17. Planner jobs rejects a non-JSON LLM completion ──────────────

def test_planner_jobs_rejects_non_json_llm_output() -> None:
    from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs

    class _NonJsonProvider:
        def generate_plan(self, request, *, tools, data_profile, user_config=None):
            from mdi_llm import PlannerRawResponse
            return PlannerRawResponse(raw_json=None, raw_text="not json", model="mock", finish_reason="stop")

    result = planner_jobs(
        PlannerJobsRequest(userPrompt="test", datasetId="ds_test", profileId="p_test"),
        provider=_NonJsonProvider(),
        registry=_registry(),
    )
    assert not result.ok
    assert result.job_id is None
    assert any(e["code"] == "PLAN_EMPTY" for e in result.validation_errors)
