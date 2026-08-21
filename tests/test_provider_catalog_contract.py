from __future__ import annotations

from mdi_api.routers.planner_providers import (
    ProviderResolveRequest,
    ProviderTestRequest,
    list_planner_providers,
    planner_provider_status,
    resolve_planner_provider,
    test_planner_provider as run_provider_test,
)


def test_server_provider_catalog_is_provider_agnostic_and_server_secret_only(monkeypatch) -> None:
    monkeypatch.delenv("MDI_LLM_PROVIDER", raising=False)
    catalog = list_planner_providers()["providers"]

    assert catalog
    deepseek = next(item for item in catalog if item["provider"] == "deepseek")
    assert deepseek["kind"] == "openai_compatible"
    assert deepseek["baseUrl"] == "https://api.deepseek.com"
    assert deepseek["defaultModel"] in deepseek["allowedModels"]
    assert deepseek["secretSource"] == "server_environment"
    assert deepseek["execution"] == "live"
    assert "value" not in deepseek
    assert "apiKey" not in deepseek


def test_provider_status_reports_unknown_server_selection_without_fallback(monkeypatch) -> None:
    monkeypatch.setenv("MDI_LLM_PROVIDER", "unregistered-provider")

    status = planner_provider_status()

    assert status["ok"] is False
    assert status["provider"] == "unregistered-provider"
    assert status["status"] == "unsupported"
    assert status["execution"] == "unavailable"
    assert status["errorType"] == "provider_not_supported"
    assert status["baseUrl"] is None


def test_deepseek_resolution_returns_generic_contract_and_rejects_browser_endpoint_or_secret(monkeypatch) -> None:
    monkeypatch.delenv("MDI_LLM_PROVIDER", raising=False)
    monkeypatch.setenv("DEEPSEEK_KEY", "test-only-secret")

    resolved = resolve_planner_provider(
        ProviderResolveRequest(provider="deepseek", model="deepseek-v4-flash")
    )
    assert resolved["provider"] == "deepseek"
    assert resolved["kind"] == "openai_compatible"
    assert resolved["baseUrl"] == "https://api.deepseek.com"
    assert resolved["secretSource"] == "server_environment"
    assert resolved["execution"] == "live"
    assert resolved["secretConfigured"] is False

    rejected = resolve_planner_provider(
        ProviderResolveRequest(
            provider="deepseek",
            model="deepseek-v4-flash",
            baseUrl="https://attacker.example",
            secretId="browser-secret",
        )
    )
    assert rejected["ok"] is False
    assert rejected["errorType"] == "deepseek_configuration_not_allowed"
    assert "attacker.example" not in str(rejected)
    assert "browser-secret" not in str(rejected)


def test_provider_test_returns_generic_identity_without_network() -> None:
    result = run_provider_test(
        ProviderTestRequest(provider="deepseek", model="deepseek-v4-flash"),
        transport=lambda **_: {
            "choices": [{"message": {"content": '{"status":"ok"}'}, "finish_reason": "stop"}],
            "usage": {},
        },
    )

    assert result["ok"] is True
    assert result["provider"] == "deepseek"
    assert result["kind"] == "openai_compatible"
    assert result["baseUrl"] == "https://api.deepseek.com"
    assert result["model"] == "deepseek-v4-flash"
    assert result["realLlmCalls"] == 0
