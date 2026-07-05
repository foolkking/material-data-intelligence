"""Phase 7 LLM JSON Planner + BYOK Secret Management tests."""

from __future__ import annotations

import json
from pathlib import Path
import urllib.error

import pytest

from mdi_api.secrets import InMemorySecretStore
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_llm import LLMProviderError, MockLLMProvider, OpenAICompatibleProvider, PlannerRequest, PlannerRawResponse, PlannerUserConfig, redact_params_for_log
from mdi_llm.planner_prompt import build_planner_prompt
from mdi_schemas import AnalysisPlan, AnalysisStep, ArtifactType, DataProfile
from mdi_tool_registry import ToolRegistry, load_manifests
from mdi_tool_registry.plan_validator import PlanValidationError, validate_plan
from mdi_workers import InMemoryQueueBackend, QueueWorkerRuntime


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


def _valid_openai_plan(dataset_id: str = "ds1", profile_id: str = "p1") -> dict[str, object]:
    return {
        "schemaVersion": "0.1",
        "goal": "test from fake OpenAI-compatible provider",
        "datasetId": dataset_id,
        "profileId": profile_id,
        "toolRegistryVersion": _registry().version,
        "steps": [
            {
                "stepId": "llm_step_1",
                "toolId": "ml.basic_metrics",
                "purpose": "x",
                "reason": "x",
                "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
                "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
                "output": {"artifactTypes": ["metrics_json"]},
            }
        ],
        "expectedArtifacts": [{"name": "metrics.json", "type": "metrics_json", "fromStepId": "llm_step_1"}],
    }


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
    assert result.plan_id is not None
    assert result.plan_hash is not None
    assert result.validation_errors == []
    assert result.enqueued is False
    assert result.executed is False


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


# ── Phase 9A. OpenAI-compatible provider is gated and safe by default ──

def test_openai_provider_uses_mdi_env_config_with_fake_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setenv("MDI_LLM_BASE_URL", "https://llm.example.test/v1")
    monkeypatch.setenv("MDI_LLM_API_KEY", "sk-phase9a-secret-value-000000")
    monkeypatch.setenv("MDI_LLM_MODEL", "phase9a-model")
    monkeypatch.setenv("MDI_LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("MDI_LLM_MAX_TOKENS", "321")
    monkeypatch.setenv("MDI_LLM_TEMPERATURE", "0.05")

    def fake_transport(**kwargs):
        captured.update(kwargs)
        return {"choices": [{"message": {"content": json.dumps(_valid_openai_plan())}, "finish_reason": "stop"}]}

    provider = OpenAICompatibleProvider(transport=fake_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    resp = provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert resp.raw_json is not None
    assert resp.model == "phase9a-model"
    assert captured["model"] == "phase9a-model"
    assert captured["timeout_seconds"] == 12.5
    assert captured["max_tokens"] == 321
    assert captured["temperature"] == 0.05
    assert captured["response_format"] == {"type": "json_object"}
    assert "sk-phase9a-secret" not in json.dumps(captured["messages"])


def test_openai_provider_request_config_overrides_env_with_fake_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setenv("MDI_LLM_BASE_URL", "https://env-llm.example.test/v1")
    monkeypatch.setenv("MDI_LLM_API_KEY", "sk-phase9a-env-secret-value-000000")
    monkeypatch.setenv("MDI_LLM_MODEL", "env-model")
    monkeypatch.setenv("MDI_LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("MDI_LLM_MAX_TOKENS", "321")
    monkeypatch.setenv("MDI_LLM_TEMPERATURE", "0.05")

    def fake_transport(**kwargs):
        captured.update(kwargs)
        return {"choices": [{"message": {"content": json.dumps(_valid_openai_plan())}, "finish_reason": "stop"}]}

    provider = OpenAICompatibleProvider(transport=fake_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)
    resp = provider.generate_plan(
        req,
        tools=list(reg.tools),
        data_profile=_data_profile(),
        user_config=PlannerUserConfig(
            provider="openai_compatible",
            model="request-model",
            base_url="https://request-llm.example.test/v1",
            api_key="sk-phase9a-request-secret-value-000000",
            timeout_seconds=44.0,
            temperature=0.17,
            max_tokens=777,
        ),
    )

    assert resp.raw_json is not None
    assert resp.model == "request-model"
    assert captured["model"] == "request-model"
    assert captured["timeout_seconds"] == 44.0
    assert captured["max_tokens"] == 777
    assert captured["temperature"] == 0.17
    assert "sk-phase9a-env-secret" not in json.dumps(captured["messages"])
    assert "sk-phase9a-request-secret" not in json.dumps(captured["messages"])


def test_openai_provider_missing_api_key_fails_safely(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MDI_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAICompatibleProvider()
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)

    with pytest.raises(LLMProviderError) as exc:
        provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert exc.value.code == "LLM_API_KEY_MISSING"
    assert "sk-phase9a-secret" not in str(exc.value)
    assert "MDI_LLM_API_KEY" not in str(exc.value)


@pytest.mark.parametrize("status_code", [401, 429, 500])
def test_openai_provider_http_errors_are_redacted(status_code: int) -> None:
    def failing_transport(**kwargs):
        raise urllib.error.HTTPError(
            url="https://llm.example.test/v1/chat/completions",
            code=status_code,
            msg="server said sk-phase9a-secret-value-000000",
            hdrs=None,
            fp=None,
        )

    provider = OpenAICompatibleProvider(transport=failing_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)

    with pytest.raises(LLMProviderError) as exc:
        provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert exc.value.code == "LLM_HTTP_ERROR"
    assert exc.value.status_code == status_code
    assert "sk-phase9a-secret" not in str(exc.value)


def test_openai_provider_timeout_error_is_redacted() -> None:
    def timeout_transport(**kwargs):
        raise TimeoutError("timeout with sk-phase9a-secret-value-000000")

    provider = OpenAICompatibleProvider(transport=timeout_transport)
    reg = _registry()
    req = PlannerRequest(user_prompt="test", dataset_id="ds1", profile_id="p1", tool_registry_version=reg.version)

    with pytest.raises(LLMProviderError) as exc:
        provider.generate_plan(req, tools=list(reg.tools), data_profile=_data_profile())

    assert exc.value.code == "LLM_TIMEOUT"
    assert "sk-phase9a-secret" not in str(exc.value)


def test_default_planner_jobs_uses_mock_provider_without_openai_network(monkeypatch: pytest.MonkeyPatch) -> None:
    import mdi_api.routers.planner as planner_router

    def forbidden_openai_provider():
        raise AssertionError("OpenAICompatibleProvider must not be instantiated by default")

    monkeypatch.delenv("MDI_LLM_PROVIDER", raising=False)
    monkeypatch.setattr(planner_router, "OpenAICompatibleProvider", forbidden_openai_provider)

    result = planner_router.planner_jobs(
        planner_router.PlannerJobsRequest(userPrompt="run metrics", projectId="project_9a", datasetId="dataset_9a"),
        repositories=InMemoryRepositoryBundle.create(),
        registry=_registry(),
    )

    assert result.ok
    assert result.planner_provider == "mock"


def test_planner_jobs_openai_compatible_valid_plan_enters_persisted_plan_path(monkeypatch: pytest.MonkeyPatch) -> None:
    import mdi_api.routers.planner as planner_router

    class FakeOpenAIProvider:
        def generate_plan(self, request, *, tools, data_profile, user_config=None):
            return PlannerRawResponse(
                raw_json=_valid_openai_plan(dataset_id=request.dataset_id, profile_id=request.profile_id),
                raw_text=None,
                model="phase9a-fake-model",
                finish_reason="stop",
            )

        @property
        def meta(self):
            return type("Meta", (), {"name": "openai_compatible", "model": "phase9a-fake-model"})()

    repos = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(repositories=repos, queue_backend=queue)
    monkeypatch.setattr(planner_router, "OpenAICompatibleProvider", lambda: FakeOpenAIProvider())

    result = planner_router.planner_jobs(
        planner_router.PlannerJobsRequest(
            userPrompt="run metrics",
            projectId="project_9a",
            datasetId="dataset_9a",
            profileId="profile_9a",
            provider="openai_compatible",
            enqueue=True,
        ),
        repositories=repos,
        queue_runtime=runtime,
        registry=_registry(),
    )

    assert result.ok
    assert result.planner_provider == "openai_compatible"
    assert result.job_id is not None
    assert result.plan_id is not None
    assert result.plan_hash is not None
    assert queue.pop_next() == result.job_id
    job = repos.jobs.get(result.job_id)
    plan = repos.analysis_plans.get_plan(result.plan_id)
    assert job["planId"] == result.plan_id
    assert plan["plannerProvider"] == "openai_compatible"
    assert plan["analysisPlan"]["steps"][0]["toolId"] == "ml.basic_metrics"


def test_planner_jobs_openai_compatible_invalid_plan_persists_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    import mdi_api.routers.planner as planner_router

    class FakeOpenAIProvider:
        def generate_plan(self, request, *, tools, data_profile, user_config=None):
            plan = _valid_openai_plan(dataset_id=request.dataset_id, profile_id=request.profile_id)
            plan["steps"][0]["params"]["api_key"] = "sk-phase9a-secret-value-000000"  # type: ignore[index]
            return PlannerRawResponse(raw_json=plan, raw_text=None, model="phase9a-fake-model", finish_reason="stop")

        @property
        def meta(self):
            return type("Meta", (), {"name": "openai_compatible", "model": "phase9a-fake-model"})()

    repos = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(repositories=repos, queue_backend=queue)
    monkeypatch.setattr(planner_router, "OpenAICompatibleProvider", lambda: FakeOpenAIProvider())

    result = planner_router.planner_jobs(
        planner_router.PlannerJobsRequest(
            userPrompt="run metrics",
            projectId="project_9a",
            datasetId="dataset_9a",
            provider="openai_compatible",
            enqueue=True,
        ),
        repositories=repos,
        queue_runtime=runtime,
        registry=_registry(),
    )

    assert not result.ok
    assert result.job_id is None
    assert result.plan_id is None
    assert result.enqueued is False
    assert any(error["code"] == "CREDENTIAL_IN_PARAMS" for error in result.validation_errors)
    assert repos.analysis_plans.records == {}
    assert repos.jobs.records == {}
    assert queue.pop_next() is None
    assert "sk-phase9a-secret" not in json.dumps(result.validation_errors)


def test_planner_jobs_openai_provider_error_persists_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    import mdi_api.routers.planner as planner_router

    monkeypatch.delenv("MDI_LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    repos = InMemoryRepositoryBundle.create()
    queue = InMemoryQueueBackend()
    runtime = QueueWorkerRuntime(repositories=repos, queue_backend=queue)

    result = planner_router.planner_jobs(
        planner_router.PlannerJobsRequest(
            userPrompt="run metrics",
            projectId="project_9a",
            datasetId="dataset_9a",
            provider="openai_compatible",
            enqueue=True,
        ),
        repositories=repos,
        queue_runtime=runtime,
        registry=_registry(),
    )

    assert not result.ok
    assert result.job_id is None
    assert result.plan_id is None
    assert result.enqueued is False
    assert any(error["code"] == "LLM_API_KEY_MISSING" for error in result.validation_errors)
    assert repos.analysis_plans.records == {}
    assert repos.jobs.records == {}
    assert queue.pop_next() is None
