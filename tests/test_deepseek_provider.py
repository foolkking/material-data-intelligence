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
from tests.test_analysis_intent import _profile


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


def test_deepseek_retries_one_transient_failure_and_audits_each_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    backoffs: list[float] = []

    def transport(**_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise LLMProviderError(
                "temporary provider response",
                code="LLM_HTTP_ERROR",
                status_code=429,
            )
        return _completion()

    monkeypatch.setattr("mdi_llm.providers.sleep", backoffs.append)
    provider = DeepSeekProvider(transport=transport, random_source=lambda: 0.5)
    response = provider.complete_json(
        messages=[{"role": "user", "content": "Return strict JSON."}],
        purpose="PROVIDER_CONNECTION_TEST",
    )

    assert response.raw_json == {"status": "ok"}
    assert attempts == 2
    assert backoffs == [0.3]
    assert [item["outcome"] for item in provider.call_audit] == [
        "DEEPSEEK_RATE_LIMITED",
        "SUCCESS",
    ]
    assert provider.call_audit[0]["retryBaseSeconds"] == 0.25
    assert provider.call_audit[0]["retryJitterSeconds"] == 0.05
    assert provider.call_audit[0]["retryDelaySeconds"] == 0.3


def test_deepseek_honors_bounded_retry_after_and_adds_jitter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    backoffs: list[float] = []

    def transport(**_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise LLMProviderError(
                "rate limited",
                code="LLM_HTTP_ERROR",
                status_code=429,
                retry_after_seconds=0.75,
            )
        return _completion()

    monkeypatch.setattr("mdi_llm.providers.sleep", backoffs.append)
    provider = DeepSeekProvider(transport=transport, random_source=lambda: 0.25)
    provider.complete_json(messages=[], purpose="PROVIDER_CONNECTION_TEST")

    assert backoffs == [0.775]
    assert provider.call_audit[0]["retryAfterSeconds"] == 0.75
    assert provider.call_audit[0]["retryBaseSeconds"] == 0.75
    assert provider.call_audit[0]["retryJitterSeconds"] == 0.025


def test_deepseek_notifies_retry_observer_without_sensitive_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    observed: list[dict] = []

    def transport(**_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise LLMProviderError(
                "rate limited",
                code="LLM_HTTP_ERROR",
                status_code=429,
                retry_after_seconds=0.5,
            )
        return _completion()

    monkeypatch.setattr("mdi_llm.providers.sleep", lambda _delay: None)
    DeepSeekProvider(
        transport=transport,
        random_source=lambda: 0.5,
    ).complete_json(
        messages=[{"role": "user", "content": "secret prompt body"}],
        purpose="PROVIDER_CONNECTION_TEST",
        retry_observer=observed.append,
    )

    assert len(observed) == 1
    assert observed[0]["failed_attempt"] == 1
    assert observed[0]["next_attempt"] == 2
    assert observed[0]["error_code"] == "DEEPSEEK_RATE_LIMITED"
    assert observed[0]["retry_after_seconds"] == 0.5
    assert observed[0]["retry_delay_seconds"] == 0.55
    assert "secret prompt body" not in json.dumps(observed)


def test_qualification_deepseek_endpoint_is_loopback_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_KEY", "qualification-only-key")
    monkeypatch.setenv("MDI_QUALIFICATION_MODE", "true")
    monkeypatch.setenv(
        "MDI_QUALIFICATION_DEEPSEEK_BASE_URL",
        "http://127.0.0.1:18089",
    )
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
        captured["timeout"] = timeout
        return Response()

    DeepSeekProvider(urlopen=urlopen).complete_json(
        messages=[],
        purpose="PROVIDER_CONNECTION_TEST",
    )
    assert captured["url"] == "http://127.0.0.1:18089/chat/completions"

    monkeypatch.setenv(
        "MDI_QUALIFICATION_DEEPSEEK_BASE_URL",
        "http://example.com:18089",
    )
    with pytest.raises(LLMProviderError) as exc:
        DeepSeekProvider(urlopen=urlopen).complete_json(
            messages=[],
            purpose="PROVIDER_CONNECTION_TEST",
        )
    assert exc.value.code == "DEEPSEEK_CONFIGURATION_NOT_ALLOWED"


def test_deepseek_does_not_retry_authentication_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0
    backoffs: list[float] = []

    def transport(**_kwargs):
        nonlocal attempts
        attempts += 1
        raise LLMProviderError(
            "invalid credential",
            code="LLM_HTTP_ERROR",
            status_code=401,
        )

    monkeypatch.setattr("mdi_llm.providers.sleep", backoffs.append)
    provider = DeepSeekProvider(transport=transport)
    with pytest.raises(LLMProviderError) as exc:
        provider.complete_json(
            messages=[{"role": "user", "content": "Return strict JSON."}],
            purpose="PROVIDER_CONNECTION_TEST",
        )

    assert exc.value.code == "DEEPSEEK_AUTH_FAILED"
    assert attempts == 1
    assert backoffs == []
    assert [item["outcome"] for item in provider.call_audit] == [
        "DEEPSEEK_AUTH_FAILED",
    ]


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
