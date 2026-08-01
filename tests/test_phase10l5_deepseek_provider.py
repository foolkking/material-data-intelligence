from __future__ import annotations

import json
from types import SimpleNamespace
import urllib.error

import pytest

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers import planner as planner_router
from mdi_api.routers.health import runtime_health
from mdi_api.routers.planner import PlannerIntentCreateRequest, create_planner_intent
from mdi_api.routers.planner_providers import (
    ProviderResolveRequest,
    ProviderTestRequest,
    list_planner_providers,
    resolve_planner_provider,
    test_planner_provider as run_planner_provider_test,
)
from mdi_llm import DeepSeekProvider, LLMProviderError, MockLLMProvider, PlannerUserConfig, redact_credential_values
from scripts import verify_deepseek_phase10l5 as deepseek_live_runner
from scripts.verify_deepseek_phase10l5 import MAX_PERSISTED_ERROR_BYTES, _safe_exception_summary
from tests.test_phase10l1_analysis_intent import _profile


def _completion(content: str = '{"status":"ok"}') -> dict:
    return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}


def test_fake_deepseek_is_offline_and_does_not_read_any_key(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("DEEPSEEK_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY", "MDI_LLM_API_KEY", "ANTHROPIC_API_KEY", "LLM_API_KEY"):
        monkeypatch.setenv(name, f"forbidden-{name.lower()}")
    captured: dict = {}

    def transport(**kwargs):
        captured.update(kwargs)
        return _completion()

    response = DeepSeekProvider(transport=transport).complete_json(
        messages=[{"role": "user", "content": "Return strict JSON."}],
        purpose="PROVIDER_CONNECTION_TEST",
    )
    assert response.raw_json == {"status": "ok"}
    serialized = json.dumps(captured, sort_keys=True)
    assert "forbidden-" not in serialized
    assert captured["model"] == "deepseek-v4-flash"
    assert captured["temperature"] == 0.0


def test_deepseek_call_audit_contains_hashes_and_usage_but_no_payload_or_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_KEY", "must-never-enter-audit")

    def transport(**_kwargs):
        response = _completion()
        response["usage"] = {"prompt_tokens": 12, "completion_tokens": 4, "total_tokens": 16}
        return response

    provider = DeepSeekProvider(transport=transport)
    provider.complete_json(
        messages=[{"role": "user", "content": "private prompt body"}],
        purpose="PROVIDER_CONNECTION_TEST",
    )
    assert len(provider.call_audit) == 1
    audit = provider.call_audit[0]
    assert audit["realCall"] is False
    assert audit["tokenUsage"] == {
        "promptTokens": 12,
        "completionTokens": 4,
        "totalTokens": 16,
        "estimated": False,
    }
    assert len(audit["promptHash"]) == 64
    assert len(audit["responseHash"]) == 64
    serialized = json.dumps(audit, sort_keys=True)
    assert "private prompt body" not in serialized
    assert "must-never-enter-audit" not in serialized


@pytest.mark.parametrize(
    "credential_text",
    [
        "DEEPSEEK_KEY=deepseek-secret-value",
        "token: token-secret-value",
        "password=password-secret-value",
        "apiKey: apikey-secret-value",
        "bearer bearer-secret-value",
    ],
)
def test_all_provider_messages_are_redacted_before_transport(credential_text: str) -> None:
    captured: dict = {}

    def transport(**kwargs):
        captured.update(kwargs)
        return _completion()

    DeepSeekProvider(transport=transport).complete_json(
        messages=[{"role": "user", "content": f"Analyze inert text: {credential_text}"}],
        purpose="PROVIDER_CONNECTION_TEST",
    )
    serialized = json.dumps(captured["messages"], sort_keys=True)
    assert "secret-value" not in serialized
    assert "***REDACTED***" in serialized


def test_redaction_removes_the_exact_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_KEY", "an-unstructured-provider-secret")
    assert "an-unstructured-provider-secret" not in redact_credential_values(
        "The accidental value was an-unstructured-provider-secret."
    )


def test_live_evidence_sanitizer_preserves_only_the_approved_deepseek_endpoint() -> None:
    assert deepseek_live_runner._sanitize_live_payload("https://api.deepseek.com") == "https://api.deepseek.com"
    assert deepseek_live_runner._sanitize_live_payload("https://example.invalid/artifact") == "***REDACTED_URL***"
    assert deepseek_live_runner._sanitize_live_payload("C:/private/artifact.json") == "***REDACTED_PATH***"


def test_deepseek_prompt_bytes_are_bounded_before_transport() -> None:
    called = False

    def transport(**_kwargs):
        nonlocal called
        called = True
        return _completion()

    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider(transport=transport).complete_json(
            messages=[{"role": "user", "content": "x" * 524_289}],
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "DEEPSEEK_PROMPT_TOO_LARGE"
    assert called is False


def test_live_deepseek_uses_only_exact_key_and_fixed_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    key = "phase10l5-test-only-key"
    monkeypatch.setenv("DEEPSEEK_KEY", key)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    captured: dict = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, _limit):
            return json.dumps(_completion()).encode()

    def urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.headers.get("Authorization")
        captured["body"] = json.loads(request.data)
        captured["timeout"] = timeout
        return Response()

    provider = DeepSeekProvider(urlopen=urlopen)
    response = provider.complete_json(
        messages=[{"role": "user", "content": "Return strict JSON."}],
        purpose="PROVIDER_CONNECTION_TEST",
    )
    assert response.raw_json == {"status": "ok"}
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["authorization"] == f"Bearer {key}"
    assert captured["body"]["model"] == "deepseek-v4-flash"
    assert captured["body"]["temperature"] == 0
    assert captured["body"]["thinking"] == {"type": "disabled"}
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert "must-not-be-used" not in json.dumps(captured)
    assert key not in json.dumps(response.raw_json)
    assert provider.call_audit[0]["realCall"] is False


def test_alternate_key_names_never_configure_live_deepseek(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_KEY", raising=False)
    for name in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "MDI_LLM_API_KEY", "ANTHROPIC_API_KEY", "LLM_API_KEY"):
        monkeypatch.setenv(name, "alternate-key-must-not-work")
    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider().complete_json(
            messages=[{"role": "user", "content": "Return strict JSON."}],
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "DEEPSEEK_NOT_CONFIGURED"
    assert "alternate-key" not in str(exc.value)


@pytest.mark.parametrize("model", ["deepseek-chat", "deepseek-reasoner", "gpt-4o", "custom-model"])
def test_deprecated_or_arbitrary_model_is_rejected(model: str) -> None:
    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider(transport=lambda **_: _completion()).complete_json(
            messages=[{"role": "user", "content": "Return strict JSON."}],
            user_config=PlannerUserConfig(provider="deepseek", model=model),
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "DEEPSEEK_MODEL_NOT_ALLOWED"


@pytest.mark.parametrize("provider", ["openai_compatible", "openai", "anthropic", "custom", ""])
def test_deepseek_provider_rejects_non_deepseek_request_config(provider: str) -> None:
    transport_called = False

    def transport(**_kwargs):
        nonlocal transport_called
        transport_called = True
        return _completion()

    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider(transport=transport).complete_json(
            messages=[],
            user_config=PlannerUserConfig(provider=provider, model="deepseek-v4-flash"),
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "PROVIDER_NOT_ALLOWED"
    assert transport_called is False


def test_unknown_purpose_and_request_credentials_are_rejected() -> None:
    provider = DeepSeekProvider(transport=lambda **_: _completion())
    with pytest.raises(LLMProviderError) as exc:
        provider.complete_json(messages=[], purpose="ARBITRARY_RESEARCH")
    assert exc.value.code == "LLM_CALL_PURPOSE_NOT_ALLOWED"
    with pytest.raises(LLMProviderError) as exc:
        provider.complete_json(
            messages=[],
            user_config=PlannerUserConfig(provider="deepseek", api_key="request-key"),
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "DEEPSEEK_CONFIGURATION_NOT_ALLOWED"
    assert "request-key" not in str(exc.value)


@pytest.mark.parametrize(
    ("content", "code"),
    [
        ('```json\n{"status":"ok"}\n```', "DEEPSEEK_RESPONSE_INVALID"),
        ('prefix {"status":"ok"}', "DEEPSEEK_RESPONSE_INVALID"),
        ('{"status":"ok","status":"duplicate"}', "DEEPSEEK_RESPONSE_INVALID"),
        ('{"status":NaN}', "DEEPSEEK_RESPONSE_INVALID"),
    ],
)
def test_strict_response_rejects_fences_prose_duplicates_and_nonfinite(content: str, code: str) -> None:
    provider = DeepSeekProvider(transport=lambda **_: _completion(content))
    with pytest.raises(LLMProviderError) as exc:
        provider.complete_json(messages=[], purpose="PROVIDER_CONNECTION_TEST")
    assert exc.value.code == code


@pytest.mark.parametrize(
    "response",
    [
        None,
        [],
        "not-an-envelope",
        {},
        {"choices": []},
        {"choices": [None]},
        {"choices": [{}]},
        {"choices": [{"message": None}]},
        {"choices": [{"message": {}}]},
        {"choices": [{"message": {"content": {"status": "ok"}}}]},
    ],
)
def test_malformed_deepseek_response_envelopes_use_deepseek_error_code(response: object) -> None:
    provider = DeepSeekProvider(transport=lambda **_: response)
    with pytest.raises(LLMProviderError) as exc:
        provider.complete_json(messages=[], purpose="PROVIDER_CONNECTION_TEST")
    assert exc.value.code == "DEEPSEEK_RESPONSE_INVALID"
    assert provider.call_audit[-1]["outcome"] == "DEEPSEEK_RESPONSE_INVALID"


def test_live_runner_redacts_and_bounds_generic_exception_details(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "phase10l5-runner-secret"
    monkeypatch.setenv("DEEPSEEK_KEY", secret)
    error_code, safe_details = _safe_exception_summary(
        RuntimeError(f"unsafe detail DEEPSEEK_KEY={secret} " + "x" * 10_000)
    )
    assert error_code == "LIVE_VERIFICATION_FAILED"
    assert secret not in safe_details
    assert "***REDACTED***" in safe_details
    assert len(safe_details.encode("utf-8")) <= MAX_PERSISTED_ERROR_BYTES


def test_live_runner_preserves_safe_typed_generic_error_code() -> None:
    error_code, safe_details = _safe_exception_summary(RuntimeError('LIVE_PLAN_NOT_READY:{"outcome":"FAILED"}'))
    assert error_code == "LIVE_PLAN_NOT_READY"
    assert safe_details == 'LIVE_PLAN_NOT_READY:{"outcome":"FAILED"}'


def test_live_runner_persists_only_redacted_bounded_generic_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    secret = "phase10l5-persisted-secret"
    monkeypatch.setenv("DEEPSEEK_KEY", secret)
    monkeypatch.setattr(deepseek_live_runner, "EVIDENCE", tmp_path)
    deepseek_live_runner._write_live_failure(
        case_index=0,
        model="deepseek-v4-flash",
        provider=DeepSeekProvider(transport=lambda **_: _completion()),
        started=0.0,
        exc=RuntimeError(f"generic failure DEEPSEEK_KEY={secret} " + "z" * 10_000),
    )
    persisted = (tmp_path / "deepseek_live_failure.json").read_text(encoding="utf-8")
    payload = json.loads(persisted)
    assert secret not in persisted
    assert payload["errorCode"] == "LIVE_VERIFICATION_FAILED"
    assert "***REDACTED***" in payload["safeDetails"]
    assert len(payload["safeDetails"].encode("utf-8")) <= MAX_PERSISTED_ERROR_BYTES


def test_live_runner_sanitizes_complete_chain_without_provider_payload_key_or_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "phase10l5-never-persist-this-key"
    monkeypatch.setenv("DEEPSEEK_KEY", secret)
    payload = {
        "profile": {"profileId": "profile_1", "localPath": r"C:\\temp\\profile.json"},
        "intent": {"rawGoal": f"Analyze safely; DEEPSEEK_KEY={secret}"},
        "providerResponse": {"choices": [{"message": {"content": "raw"}}]},
        "providerCallAudit": [{"promptHash": "a" * 64, "responseHash": "b" * 64}],
        "artifacts": [{"artifactId": "artifact_1", "storageKey": "private/object/key"}],
        "nested": {"note": r"read C:\\Users\\person\\AppData\\Local\\Temp\\secret.json"},
    }

    sanitized = deepseek_live_runner._sanitize_live_payload(payload)
    serialized = json.dumps(sanitized, sort_keys=True)

    assert secret not in serialized
    assert "***REDACTED***" in serialized
    assert "providerResponse" not in sanitized
    assert "localPath" not in sanitized["profile"]
    assert "storageKey" not in sanitized["artifacts"][0]
    assert "C:\\\\" not in serialized
    assert sanitized["providerCallAudit"][0] == {
        "promptHash": "a" * 64,
        "responseHash": "b" * 64,
    }


def test_live_runner_requires_selected_decision_and_provider_projection_within_eligible_set() -> None:
    planned = SimpleNamespace(
        eligibility_resolution={"eligibleToolIds": ["tool.a", "tool.b"]},
        capability_decision={"selections": [{"toolId": "tool.b"}]},
        provider_visible_tool_ids=["tool.b", "tool.a"],
    )
    eligible, visible = deepseek_live_runner._assert_selected_tools_are_eligible(planned, ["tool.b"])
    assert eligible == ["tool.a", "tool.b"]
    assert visible == eligible

    planned.capability_decision = {"selections": [{"toolId": "tool.unknown"}]}
    with pytest.raises(RuntimeError, match="LIVE_DECISION_PLAN_SELECTION_MISMATCH"):
        deepseek_live_runner._assert_selected_tools_are_eligible(planned, ["tool.b"])

    planned.capability_decision = {"selections": [{"toolId": "tool.b"}]}
    planned.provider_visible_tool_ids = ["tool.a"]
    with pytest.raises(RuntimeError, match="LIVE_PROVIDER_VISIBLE_TOOLS_DIFFER_FROM_ELIGIBLE"):
        deepseek_live_runner._assert_selected_tools_are_eligible(planned, ["tool.b"])


def test_live_runner_non_ready_response_has_no_execution_or_queue_side_effects(tmp_path) -> None:
    repositories = InMemoryRepositoryBundle.create()
    runtime = deepseek_live_runner.QueueWorkerRuntime(
        repositories=repositories,
        artifact_root=tmp_path,
    )
    planned = SimpleNamespace(
        plan=None,
        plan_id=None,
        plan_hash=None,
        job_id=None,
        enqueued=False,
        executed=False,
        dependency_bindings=[],
        topological_order=[],
    )
    counts = deepseek_live_runner._assert_non_ready_created_nothing(
        planned,
        repositories=repositories,
        runtime=runtime,
    )
    assert counts == {
        "planCount": 0,
        "jobCount": 0,
        "toolCallCount": 0,
        "artifactCount": 0,
        "plannedBindingCount": 0,
        "bindingResolutionCount": 0,
        "dependencyExecutionCount": 0,
        "lineageCount": 0,
        "queueMessageCount": 0,
    }

    repositories.jobs.records["unexpected_job"] = {"id": "unexpected_job"}
    with pytest.raises(RuntimeError, match="LIVE_NON_READY_CREATED_EXECUTION"):
        deepseek_live_runner._assert_non_ready_created_nothing(
            planned,
            repositories=repositories,
            runtime=runtime,
        )


def test_live_runner_requires_exact_real_call_hashes_and_usage() -> None:
    valid = ({
        "purpose": "INTENT_EXTRACTION",
        "model": "deepseek-v4-flash",
        "realCall": True,
        "promptHash": "a" * 64,
        "responseHash": "b" * 64,
        "promptBytes": 100,
        "responseBytes": 50,
        "tokenUsage": {
            "promptTokens": 25,
            "completionTokens": 10,
            "totalTokens": 35,
            "estimated": False,
        },
        "elapsedMs": 1.0,
        "outcome": "SUCCESS",
    },) * 3
    deepseek_live_runner._assert_provider_call_audit(valid)

    invalid = tuple({**item, "responseHash": None} for item in valid)
    with pytest.raises(RuntimeError, match="DEEPSEEK_REAL_CALL_AUDIT_INVALID"):
        deepseek_live_runner._assert_provider_call_audit(invalid)


def test_live_runner_requires_complete_persisted_chain_before_pass() -> None:
    audit_item = {
        "purpose": "INTENT_EXTRACTION",
        "model": "deepseek-v4-flash",
        "realCall": True,
        "promptHash": "a" * 64,
        "responseHash": "b" * 64,
        "promptBytes": 100,
        "responseBytes": 50,
        "tokenUsage": {
            "promptTokens": 25,
            "completionTokens": 10,
            "totalTokens": 35,
            "estimated": False,
        },
        "elapsedMs": 1.0,
        "outcome": "SUCCESS",
    }
    record = {
        "profile": {"profileId": "profile_1"},
        "intent": {"intentId": "intent_1"},
        "eligibilityResolution": {"resolutionId": "resolution_1"},
        "capabilityDecision": {"decisionId": "decision_1"},
        "eligibleToolIds": ["tool.a"],
        "selectedToolIds": ["tool.a"],
        "analysisPlan": {"planId": "plan_1"},
        "job": {"jobId": "job_1"},
        "events": [{"eventId": "event_1", "jobId": "job_1", "seq": 1}],
        "toolCalls": [{"id": "tool_call_1"}],
        "artifacts": [{"artifactId": "artifact_1", "provenance": {"planId": "plan_1"}}],
        "artifactLineage": [],
        "evidenceBundle": {"bundleId": "bundle_1"},
        "interpretation": {"interpretation": {"interpretationId": "interpretation_1"}},
        "providerCallAudit": [dict(audit_item) for _ in range(3)],
    }
    deepseek_live_runner._assert_complete_live_record(record)

    missing_profile = {**record, "profile": {}}
    with pytest.raises(RuntimeError, match="LIVE_PERSISTED_CHAIN_INCOMPLETE:profile"):
        deepseek_live_runner._assert_complete_live_record(missing_profile)

    missing_lineage = {**record, "artifacts": [{"artifactId": "artifact_1"}]}
    with pytest.raises(RuntimeError, match="LIVE_ARTIFACT_LINEAGE_OR_PROVENANCE_MISSING"):
        deepseek_live_runner._assert_complete_live_record(missing_lineage)


@pytest.mark.parametrize(
    ("status", "expected"),
    [(401, "DEEPSEEK_AUTH_FAILED"), (429, "DEEPSEEK_RATE_LIMITED"), (500, "DEEPSEEK_PROVIDER_FAILED")],
)
def test_http_failures_are_typed_without_fallback(status: int, expected: str) -> None:
    def transport(**_):
        raise urllib.error.HTTPError("https://api.deepseek.com", status, "failure", {}, None)

    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider(transport=transport).complete_json(messages=[], purpose="PROVIDER_CONNECTION_TEST")
    assert exc.value.code == expected


@pytest.mark.parametrize("provider", ["openai", "custom", "anthropic", "unknown-provider"])
def test_standalone_intent_api_rejects_non_deepseek_real_provider(provider: str) -> None:
    repos = InMemoryRepositoryBundle.create()
    profile = _profile(targets=(), uncertainty=False)
    repos.data_profiles.save(profile)
    result = create_planner_intent(
        PlannerIntentCreateRequest(
            rawGoal="Analyze this dataset.",
            projectId="project_l5_provider_gate",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            provider=provider,
        ),
        repositories=repos,
    )
    assert result.ok is False
    assert result.error_code in {"PROVIDER_NOT_ALLOWED", "LLM_PROVIDER_UNSUPPORTED"}
    assert repos.analysis_intents.records == {}


def test_official_planner_default_is_deepseek_without_calling_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MDI_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MDI_ALLOW_TEST_PROVIDERS", raising=False)

    selected = planner_router._select_planner_provider(None)

    assert isinstance(selected, DeepSeekProvider)
    assert selected.call_audit == ()


@pytest.mark.parametrize("provider_name", ["mock", "deterministic", "safe_mock"])
def test_planner_api_rejects_test_provider_without_explicit_gate(
    provider_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("MDI_ALLOW_TEST_PROVIDERS", raising=False)

    with pytest.raises(LLMProviderError) as exc:
        planner_router._select_planner_provider(provider_name)

    assert exc.value.code == "PROVIDER_NOT_ALLOWED"


def test_planner_api_allows_mock_only_with_explicit_test_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "1")

    selected = planner_router._select_planner_provider("mock")

    assert isinstance(selected, MockLLMProvider)


def test_explicitly_injected_offline_provider_bypasses_api_selection_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MDI_ALLOW_TEST_PROVIDERS", raising=False)
    injected = MockLLMProvider()

    assert planner_router._select_planner_provider(None, provider=injected) is injected

    repos = InMemoryRepositoryBundle.create()
    profile = _profile(targets=(), uncertainty=False)
    repos.data_profiles.save(profile)
    result = create_planner_intent(
        PlannerIntentCreateRequest(
            rawGoal="Analyze this dataset.",
            projectId="project_l5_offline_injection",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
        ),
        provider=injected,
        repositories=repos,
    )
    assert result.ok is True
    assert result.intent_id is not None


def test_provider_catalog_exposes_only_deepseek_without_test_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MDI_ALLOW_TEST_PROVIDERS", raising=False)
    assert [item["id"] for item in list_planner_providers()["providers"]] == ["deepseek"]

    monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "true")
    assert [item["id"] for item in list_planner_providers()["providers"]] == ["deepseek", "mock"]


def test_provider_routes_reject_mock_without_test_gate_with_typed_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MDI_ALLOW_TEST_PROVIDERS", raising=False)

    resolved = resolve_planner_provider(ProviderResolveRequest(provider="mock"))
    tested = run_planner_provider_test(ProviderTestRequest(provider="mock"))

    assert resolved["ok"] is False
    assert resolved["code"] == "PROVIDER_NOT_ALLOWED"
    assert tested["ok"] is False
    assert tested["code"] == "PROVIDER_NOT_ALLOWED"
    assert tested.get("realLlmCalls", 0) == 0


@pytest.mark.parametrize("provider_name", ["openai", "openai_compatible", "anthropic", "custom", "unknown"])
def test_provider_routes_reject_every_non_deepseek_real_provider_with_typed_code(
    provider_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "1")

    resolved = resolve_planner_provider(ProviderResolveRequest(provider=provider_name))
    tested = run_planner_provider_test(ProviderTestRequest(provider=provider_name))

    assert resolved["code"] == "PROVIDER_NOT_ALLOWED"
    assert tested["code"] == "PROVIDER_NOT_ALLOWED"
    assert resolved["willUseLiveProvider"] is False
    assert tested.get("realLlmCalls", 0) == 0


def test_runtime_health_reports_disallowed_deepseek_model_as_not_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_KEY", "configured-but-model-is-invalid")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    status = runtime_health()["llmProvider"]
    assert status["status"] == "unknown"
    assert status["configured"] is False
    assert status["model"] == "deepseek-chat"
    assert status["reason"] == "DEEPSEEK_MODEL_NOT_ALLOWED"
