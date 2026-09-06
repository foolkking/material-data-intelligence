from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException
from fastapi.testclient import TestClient

from mdi_api.database import create_engine_from_settings, dispose_cached_engines
from mdi_api.db import metadata
from mdi_api.main import create_app
from mdi_api.provider_connections import decrypt_api_key, get_connection, public_connection, reset_connections_for_tests, save_connection, thinking_budget
from mdi_api.routers.planner import PlannerPreviewRequest, _planner_user_config_from_request
from mdi_api.routers.auth import CurrentUser, get_current_user
from mdi_api.routers.planner_providers import (
    ProviderConfigureRequest,
    ProviderModelsUpdateRequest,
    ProviderResolveRequest,
    ProviderTestRequest,
    configure_planner_provider,
    list_planner_providers,
    planner_provider_status,
    remove_planner_provider,
    resolve_planner_provider_route,
    test_planner_provider_route as run_planner_provider_test,
    update_planner_provider_models,
)


PLATFORM_ADMIN = CurrentUser(
    id="platform-admin",
    email="platform-admin@example.invalid",
    displayName="Platform Admin",
    roles=[],
    platformRole="PLATFORM_ADMIN",
)
ORDINARY_USER = CurrentUser(
    id="researcher",
    email="researcher@example.invalid",
    displayName="Researcher",
    roles=["owner"],
)


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
    result = configure_planner_provider(
        ProviderConfigureRequest(
            provider="route-compatible",
            label="Route",
            baseUrl="https://example.com/v1",
            apiKey="secret-value",
        ),
        PLATFORM_ADMIN,
    )
    assert result["ok"] is True
    assert "secret-value" not in json.dumps(result, ensure_ascii=False)
    assert get_connection("route-compatible") is not None


def test_private_or_invalid_base_url_is_rejected():
    result = configure_planner_provider(
        ProviderConfigureRequest(
            provider="bad-compatible",
            label="Bad",
            baseUrl="http://example.com/v1",
            apiKey="secret-value",
        ),
        PLATFORM_ADMIN,
    )
    assert result["ok"] is False
    assert result["errorType"] == "provider_configuration_invalid"


def test_model_group_can_be_updated_without_resubmitting_api_key():
    configure_planner_provider(
        ProviderConfigureRequest(
            provider="group-compatible",
            label="Group",
            baseUrl="https://example.com/v1",
            apiKey="secret-value",
        ),
        PLATFORM_ADMIN,
    )
    result = update_planner_provider_models(
        "group-compatible",
        ProviderModelsUpdateRequest(modelIds=["model-a", "model-b"], defaultModel="model-a"),
        PLATFORM_ADMIN,
    )
    connection = get_connection("group-compatible")
    assert result["ok"] is True
    assert connection is not None
    assert connection.model_ids == ("model-a", "model-b")
    assert connection.default_model == "model-a"
    assert decrypt_api_key(connection) == "secret-value"
    assert "secret-value" not in json.dumps(result, ensure_ascii=False)


@pytest.mark.parametrize("operation", ["configure", "update", "delete"])
def test_provider_mutations_require_platform_admin(operation: str) -> None:
    save_connection(
        provider="protected-compatible",
        label="Protected",
        kind="openai_compatible",
        base_url="https://example.com/v1",
        api_key="existing-secret",
        model_ids=["model-a"],
        default_model="model-a",
    )

    with pytest.raises(HTTPException) as raised:
        if operation == "configure":
            configure_planner_provider(
                ProviderConfigureRequest(
                    provider="ordinary-attempt",
                    label="Denied",
                    baseUrl="https://example.com/v1",
                    apiKey="new-secret",
                ),
                ORDINARY_USER,
            )
        elif operation == "update":
            update_planner_provider_models(
                "protected-compatible",
                ProviderModelsUpdateRequest(
                    modelIds=["model-b"],
                    defaultModel="model-b",
                ),
                ORDINARY_USER,
            )
        else:
            remove_planner_provider("protected-compatible", ORDINARY_USER)

    assert raised.value.status_code == 403
    assert raised.value.detail["code"] == "PLATFORM_ADMIN_REQUIRED"
    protected = get_connection("protected-compatible")
    assert protected is not None
    assert protected.model_ids == ("model-a",)
    assert decrypt_api_key(protected) == "existing-secret"
    assert get_connection("ordinary-attempt") is None


def test_provider_configuration_http_route_enforces_platform_role() -> None:
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: ORDINARY_USER
    client = TestClient(app)

    denied = client.post(
        "/planner/providers/configure",
        json={
            "provider": "http-compatible",
            "label": "HTTP",
            "baseUrl": "https://example.com/v1",
            "apiKey": "route-secret",
        },
    )

    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "PLATFORM_ADMIN_REQUIRED"
    assert get_connection("http-compatible") is None

    app.dependency_overrides[get_current_user] = lambda: PLATFORM_ADMIN
    allowed = client.post(
        "/planner/providers/configure",
        json={
            "provider": "http-compatible",
            "label": "HTTP",
            "baseUrl": "https://example.com/v1",
            "apiKey": "route-secret",
        },
    )

    assert allowed.status_code == 200
    assert allowed.json()["ok"] is True
    assert "route-secret" not in allowed.text


def test_platform_admin_can_configure_update_and_delete_provider() -> None:
    configured = configure_planner_provider(
        ProviderConfigureRequest(
            provider="admin-compatible",
            label="Admin",
            baseUrl="https://example.com/v1",
            apiKey="admin-secret",
            modelIds=["model-a"],
            defaultModel="model-a",
        ),
        PLATFORM_ADMIN,
    )
    updated = update_planner_provider_models(
        "admin-compatible",
        ProviderModelsUpdateRequest(
            modelIds=["model-a", "model-b"],
            defaultModel="model-b",
        ),
        PLATFORM_ADMIN,
    )
    removed = remove_planner_provider("admin-compatible", PLATFORM_ADMIN)

    assert configured["ok"] is True
    assert updated["ok"] is True
    assert updated["provider"]["defaultModel"] == "model-b"
    assert removed == {
        "ok": True,
        "provider": "admin-compatible",
        "redacted": True,
    }
    assert get_connection("admin-compatible") is None


def test_ordinary_user_cannot_override_or_delete_environment_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_KEY", "server-owned-secret")
    before = planner_provider_status(ORDINARY_USER)
    assert before["configurationSource"] == "server_environment"

    with pytest.raises(HTTPException) as configure_error:
        configure_planner_provider(
            ProviderConfigureRequest(
                provider="deepseek",
                label="Untrusted override",
                baseUrl="https://attacker.example/v1",
                apiKey="untrusted-secret",
            ),
            ORDINARY_USER,
        )
    with pytest.raises(HTTPException) as delete_error:
        remove_planner_provider("deepseek", ORDINARY_USER)

    assert configure_error.value.status_code == 403
    assert delete_error.value.status_code == 403
    assert get_connection("deepseek") is None
    after = planner_provider_status(ORDINARY_USER)
    assert after["configurationSource"] == "server_environment"
    assert after["baseUrl"] == before["baseUrl"]


def test_ordinary_user_retains_provider_read_resolve_and_test_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MDI_ALLOW_TEST_PROVIDERS", "true")

    assert list_planner_providers(ORDINARY_USER)["providers"]
    assert planner_provider_status(ORDINARY_USER)["provider"] == "deepseek"
    assert resolve_planner_provider_route(
        ProviderResolveRequest(provider="mock"),
        ORDINARY_USER,
    )["ok"] is True
    assert run_planner_provider_test(
        ProviderTestRequest(provider="mock"),
        ORDINARY_USER,
    )["ok"] is True


def _configure_durable_test_store(
    monkeypatch: pytest.MonkeyPatch,
    database: Path,
    *,
    encryption_key: str | None,
) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database.as_posix()}")
    monkeypatch.setenv("MDI_RUNTIME_BACKEND", "postgresql")
    monkeypatch.setenv("MDI_RUNTIME_PROFILE", "local")
    if encryption_key is None:
        monkeypatch.delenv("MDI_PROVIDER_ENCRYPTION_KEY", raising=False)
    else:
        monkeypatch.setenv("MDI_PROVIDER_ENCRYPTION_KEY", encryption_key)
    dispose_cached_engines()
    engine = create_engine_from_settings()
    metadata.create_all(engine)


def test_durable_provider_configuration_requires_stable_encryption_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _configure_durable_test_store(
        monkeypatch,
        tmp_path / "provider-key-required.sqlite3",
        encryption_key=None,
    )

    result = configure_planner_provider(
        ProviderConfigureRequest(
            provider="durable-compatible",
            label="Durable",
            baseUrl="https://example.com/v1",
            apiKey="not-persisted",
        ),
        PLATFORM_ADMIN,
    )

    assert result["ok"] is False
    assert result["code"] == "PROVIDER_ENCRYPTION_KEY_REQUIRED"
    assert get_connection("durable-compatible") is None


def test_durable_provider_is_shared_after_process_local_state_and_engine_reset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    database = tmp_path / "provider-shared.sqlite3"
    _configure_durable_test_store(
        monkeypatch,
        database,
        encryption_key=Fernet.generate_key().decode("ascii"),
    )
    configured = configure_planner_provider(
        ProviderConfigureRequest(
            provider="shared-compatible",
            label="Shared",
            baseUrl="https://example.com/v1",
            apiKey="shared-secret",
            modelIds=["model-a"],
            defaultModel="model-a",
        ),
        PLATFORM_ADMIN,
    )
    assert configured["provider"]["configurationSource"] == "database_encrypted"

    # Neither the local adapter nor a process-scoped Engine is the authority.
    reset_connections_for_tests()
    dispose_cached_engines()
    reloaded = get_connection("shared-compatible")
    assert reloaded is not None
    assert reloaded.provider == "shared-compatible"
    assert reloaded.model_ids == ("model-a",)
    assert decrypt_api_key(reloaded) == "shared-secret"

    planner_config = _planner_user_config_from_request(
        PlannerPreviewRequest(
            userPrompt="Use the configured provider.",
            datasetId="dataset-provider-test",
            provider="shared-compatible",
            model="model-a",
        )
    )
    assert planner_config is not None
    assert planner_config.provider == "shared-compatible"
    assert planner_config.api_key == "shared-secret"

    assert remove_planner_provider("shared-compatible", PLATFORM_ADMIN)["ok"] is True
    dispose_cached_engines()
    assert get_connection("shared-compatible") is None


def test_thinking_depth_is_provider_neutral_and_bounded():
    assert thinking_budget("quick", 8192) == 2048
    assert thinking_budget("standard", 8192) == 4096
    assert thinking_budget("deep", 8192) == 8192
    assert thinking_budget("unknown", 8192) == 4096
