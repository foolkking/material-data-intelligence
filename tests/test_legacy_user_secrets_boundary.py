from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mdi_api.config import ApiSettings
from mdi_api.routers import secrets
from mdi_api.routers.auth import CurrentUser


def _reset_store(monkeypatch) -> None:
    monkeypatch.setattr(secrets, "_store", None)
    secrets._SECRET_ALIASES.clear()
    secrets._SECRET_LAST_USED.clear()


def _client() -> TestClient:
    app = FastAPI()
    app.add_api_route("/me/secrets", secrets.create_secret, methods=["POST"])
    app.add_api_route("/me/secrets", secrets.list_secrets, methods=["GET"])
    app.add_api_route(
        "/me/secrets/{secret_id}",
        secrets.delete_secret,
        methods=["DELETE"],
    )
    app.dependency_overrides[secrets.get_current_user_compat] = lambda: CurrentUser(
        id="test-user",
        email="test-user@example.invalid",
        displayName="Test User",
        roles=[],
    )
    return TestClient(app)


def test_same_stack_secret_api_is_typed_unavailable_without_storing_value(
    monkeypatch,
) -> None:
    _reset_store(monkeypatch)
    monkeypatch.setattr(
        secrets,
        "load_settings",
        lambda: ApiSettings(runtime_profile="same-stack", environment="local"),
    )
    client = _client()
    plaintext = "must-not-enter-process-memory"

    response = client.post(
        "/me/secrets",
        json={"provider": "deepseek", "value": plaintext},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "LEGACY_USER_SECRET_API_UNAVAILABLE",
        "feature": "legacy_user_secrets",
        "message": (
            "Legacy in-memory user secret storage is unavailable in this runtime."
        ),
    }
    assert secrets._store is None
    assert plaintext not in json.dumps(response.json())


def test_production_environment_secret_routes_all_fail_closed(monkeypatch) -> None:
    _reset_store(monkeypatch)
    monkeypatch.setattr(
        secrets,
        "load_settings",
        lambda: ApiSettings(runtime_profile="local", environment="production"),
    )
    client = _client()

    assert client.get("/me/secrets").status_code == 503
    assert client.delete("/me/secrets/secret_0001").status_code == 503
    assert secrets._store is None


def test_local_test_secret_api_retains_scoped_compatibility(monkeypatch) -> None:
    _reset_store(monkeypatch)
    monkeypatch.setattr(
        secrets,
        "load_settings",
        lambda: ApiSettings(runtime_profile="local", environment="test"),
    )
    client = _client()
    plaintext = "local-test-only-value"

    created = client.post(
        "/me/secrets",
        json={
            "provider": "deepseek",
            "alias": "Local test",
            "value": plaintext,
        },
    )
    listed = client.get("/me/secrets")

    assert created.status_code == 200
    assert listed.status_code == 200
    assert plaintext not in json.dumps(
        {"created": created.json(), "listed": listed.json()}
    )
    assert listed.json()[0]["id"] == created.json()["id"]


def test_internal_lookup_and_usage_require_exact_scope(monkeypatch) -> None:
    _reset_store(monkeypatch)
    monkeypatch.setattr(
        secrets,
        "load_settings",
        lambda: ApiSettings(runtime_profile="local", environment="test"),
    )
    store = secrets._legacy_secret_store()
    secret = store.create_secret("user-a", "deepseek", "scoped-value")

    assert secrets.get_secret_value(secret.id, scope_id="user-b") is None
    assert secrets.mark_secret_used(secret.id, scope_id="user-b") is False
    assert secrets.get_secret_value(secret.id, scope_id="user-a") == "scoped-value"
    assert secrets.mark_secret_used(secret.id, scope_id="user-a") is True
