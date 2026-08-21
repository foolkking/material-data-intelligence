from __future__ import annotations

import json

import pytest

from mdi_api.provider_connections import decrypt_api_key, get_connection, public_connection, reset_connections_for_tests, save_connection, thinking_budget
from mdi_api.routers.planner_providers import ProviderConfigureRequest, ProviderModelsUpdateRequest, configure_planner_provider, update_planner_provider_models


@pytest.fixture(autouse=True)
def isolate_provider_connections():
    reset_connections_for_tests()
    yield
    reset_connections_for_tests()


def test_provider_configuration_redacts_secret_and_supports_replacement(monkeypatch):
    monkeypatch.delenv("MDI_PROVIDER_ENCRYPTION_KEY", raising=False)
    first = save_connection(provider="test-compatible", label="测试服务", kind="openai_compatible", base_url="https://example.com/v1", api_key="first-key", model_ids=["model-a"])
    assert "first-key" not in json.dumps(public_connection(first), ensure_ascii=False)
    assert decrypt_api_key(first) == "first-key"
    second = save_connection(provider="test-compatible", label="测试服务", kind="openai_compatible", base_url="https://example.com/v1", api_key="second-key", model_ids=["model-b"])
    assert decrypt_api_key(second) == "second-key"
    assert "encrypted_api_key" not in public_connection(second)


def test_configuration_route_never_returns_key(monkeypatch):
    result = configure_planner_provider(ProviderConfigureRequest(provider="route-compatible", label="Route", baseUrl="https://example.com/v1", apiKey="secret-value"))
    assert result["ok"] is True
    assert "secret-value" not in json.dumps(result, ensure_ascii=False)
    assert get_connection("route-compatible") is not None


def test_private_or_invalid_base_url_is_rejected():
    result = configure_planner_provider(ProviderConfigureRequest(provider="bad-compatible", label="Bad", baseUrl="http://example.com/v1", apiKey="secret-value"))
    assert result["ok"] is False
    assert result["errorType"] == "provider_configuration_invalid"


def test_model_group_can_be_updated_without_resubmitting_api_key():
    configure_planner_provider(ProviderConfigureRequest(provider="group-compatible", label="Group", baseUrl="https://example.com/v1", apiKey="secret-value"))
    result = update_planner_provider_models(
        "group-compatible",
        ProviderModelsUpdateRequest(modelIds=["model-a", "model-b"], defaultModel="model-a"),
    )
    connection = get_connection("group-compatible")
    assert result["ok"] is True
    assert connection is not None
    assert connection.model_ids == ("model-a", "model-b")
    assert connection.default_model == "model-a"
    assert decrypt_api_key(connection) == "secret-value"
    assert "secret-value" not in json.dumps(result, ensure_ascii=False)


def test_thinking_depth_is_provider_neutral_and_bounded():
    assert thinking_budget("quick", 8192) == 2048
    assert thinking_budget("standard", 8192) == 4096
    assert thinking_budget("deep", 8192) == 8192
    assert thinking_budget("unknown", 8192) == 4096
