from __future__ import annotations

import asyncio
import json
import traceback
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4
import pytest
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from mdi_api import user_models as models
from mdi_api.db import users, user_model_settings, user_model_connections, provider_connections, platform_model_offerings, user_model_plan_grants
from mdi_api.transport.routers.auth import CurrentUser, get_current_user
from mdi_api.main import create_app
from mdi_llm.providers import PlannerUserConfig
from mdi_llm.user_connection_provider import UserConnectionProvider


@pytest.fixture
def store(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    users.create(engine); user_model_settings.create(engine)
    user_model_connections.create(engine)
    provider_connections.create(engine)
    platform_model_offerings.create(engine)
    user_model_plan_grants.create(engine)
    with engine.begin() as db:
        db.execute(insert(users), [{"id": name, "email": f"{name}@example.invalid", "display_name": name} for name in ("alice", "bob")])
    monkeypatch.setattr(models, "_engine", lambda: engine)
    monkeypatch.setenv("MDI_PROVIDER_ENCRYPTION_KEY", Fernet.generate_key().decode())
    yield engine
    engine.dispose()


def save(user="alice", **kwargs):
    return models.save_personal_connection(user, label="Mine", base_url="https://example.com/v1", api_key="private-test-key", revision=0, **kwargs)


def test_additional_connection_migration_preserves_the_existing_encrypted_row():
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    engine = create_engine("sqlite://")
    users.create(engine); user_model_settings.create(engine)
    with engine.begin() as db:
        db.execute(insert(users).values(id="legacy", email="legacy@example.invalid", display_name="Legacy"))
        db.execute(insert(user_model_settings).values(user_id="legacy", label="Original", encrypted_api_key="opaque-encrypted-value",
            selected_json=[{"provider": "personal", "model": "unchanged-id"}], revision=17))
        before = dict(db.execute(select(user_model_settings)).mappings().one())
        path = Path(__file__).resolve().parents[1] / "apps/api/alembic/versions/0038_user_model_connections.py"
        spec = importlib.util.spec_from_file_location("connection_migration", path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.op = Operations(MigrationContext.configure(db))
        assert migration.down_revision == "0037_platform_model_offerings"
        migration.upgrade()
        assert dict(db.execute(select(user_model_settings)).mappings().one()) == before
        assert db.execute(select(user_model_connections)).all() == []
    engine.dispose()


def test_multiple_connections_preserve_legacy_and_resolve_duplicate_model_ids_by_owner(store, monkeypatch):
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["Vendor/Exact-ID"])
    monkeypatch.setattr(models, "validate_endpoint", lambda value, **kwargs: value)
    save()
    first = models.discover_user_models("alice")
    models.select_user_models("alice", [{"provider": "personal", "model": "Vendor/Exact-ID"}], first["revision"])
    original = models.read_settings("alice")
    connection_id = str(uuid4())
    second = models.save_personal_connection("alice", label="Second", base_url="https://second.example.com/v1",
        api_key="second-private-key", protocol="anthropic", revision=0, connection_id=connection_id)
    second = models.discover_user_models("alice", connection_id)
    provider = f"personal:{connection_id}"
    second = models.select_user_models("alice", [{"provider": provider, "model": "Vendor/Exact-ID"}], second["revision"], connection_id)
    assert models.read_settings("alice") == original
    assert len(second["connections"]) == 2
    assert {item["provider"] for item in second["selected"]} == {"personal", provider}
    assert "second-private-key" not in json.dumps(second)
    assert "encrypted_api_key" not in json.dumps(second)
    assert models.public_settings(models.read_settings("bob"))["selected"] == []
    for source, endpoint, key, protocol in [("personal", "https://example.com/v1", "private-test-key", "openai_chat_json"),
                                             (provider, "https://second.example.com/v1", "second-private-key", "anthropic")]:
        adapter, config = models.resolve_user_selection({"user_id": "alice", "provider": source, "model": "Vendor/Exact-ID"})
        assert config.base_url == endpoint and config.api_key == key and config.model == "Vendor/Exact-ID"
        assert adapter.protocol == protocol
    with pytest.raises(ValueError, match="可用模型"):
        models.validate_user_selection("bob", {"provider": provider, "model": "Vendor/Exact-ID"})
    with pytest.raises(ValueError, match="探测"):
        models.select_user_models("alice", [{"provider": "personal", "model": "Vendor/Exact-ID"}], second["revision"], connection_id)


def test_connections_reject_stale_discovery_without_overwriting_keys_or_sibling_choices(store, monkeypatch):
    save()
    connection_id = str(uuid4())
    save(connection_id=connection_id)
    original = models.read_settings("alice")
    def remote(*args):
        models.save_personal_connection("alice", label="Updated elsewhere", base_url="https://example.com/v1",
            api_key="rotated-key", revision=1, connection_id=connection_id)
        return ["stale-model"]
    monkeypatch.setattr(models, "discover_remote_models", remote)
    with pytest.raises(ValueError, match="其他窗口更新"):
        models.discover_user_models("alice", connection_id)
    assert models.read_settings("alice") == original
    latest = models.read_settings("alice", connection_id)
    assert latest["label"] == "Updated elsewhere" and latest["catalog_json"] == []
    with pytest.raises(ValueError, match="已更新"):
        save(connection_id=connection_id)


def test_connection_api_keeps_identity_and_rejects_cross_connection_selection(store, monkeypatch):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="alice", email="alice@example.invalid", displayName="alice", roles=[])
    client = TestClient(app)
    connection_id = str(uuid4())
    body = {"label": "Second", "baseUrl": "https://example.com/v1", "apiKey": "only-on-server", "revision": 0, "connectionId": connection_id}
    created = client.put("/account/models/connection", json=body)
    assert created.status_code == 200
    assert created.json()["connectionId"] == connection_id
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["exact-id"])
    discovered = client.post("/account/models/discover", json={"connectionId": connection_id})
    assert discovered.status_code == 200
    choice = {"provider": f"personal:{connection_id}", "model": "exact-id"}
    assert client.put("/account/models/selection", json={"selected": [choice], "revision": discovered.json()["revision"], "connectionId": connection_id}).status_code == 200
    rejected = client.put("/account/models/selection", json={"selected": [choice], "revision": 0})
    assert rejected.status_code == 422
    invalid = client.put("/account/models/connection", json={**body, "connectionId": "invalid"})
    assert invalid.status_code == 422 and "only-on-server" not in invalid.text


def test_concurrent_initial_save_returns_safe_conflict_and_preserves_owner_data(store):
    save()
    before = models.read_settings("alice")
    with pytest.raises(ValueError, match="其他窗口更新") as error:
        models._write("alice", {"encrypted_api_key": "must-not-be-exposed"}, expected_revision=0)
    assert "must-not-be-exposed" not in str(error.value)
    assert models.read_settings("alice") == before


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
def test_model_directory_request_preserves_exact_ids_and_versioned_url(monkeypatch, protocol):
    ids = ["Vendor/Model:2026-09", "gpt-5.6-sol", " model-with-spaces "]
    captured = {}
    def read_response(request, *, timeout, byte_limit):
        captured.update(url=request.full_url, method=request.get_method(), headers=dict(request.header_items()), timeout=timeout, byte_limit=byte_limit)
        return json.dumps({"object": "list", "data": [{"id": model} for model in ids + ids]}).encode()
    monkeypatch.setattr(models.socket, "getaddrinfo", lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))])
    monkeypatch.setattr(models, "read_provider_response", read_response)
    assert models.discover_remote_models("https://example.com/v1/", "test-directory-key", protocol) == ids
    assert captured["url"] == "https://example.com/v1/models"
    assert captured["method"] == "GET"
    assert captured["timeout"] == 12 and captured["byte_limit"] == 2_000_000
    assert captured["headers"]["User-agent"] == "MDI/1.0"
    if protocol == "anthropic":
        assert captured["headers"]["X-api-key"] == "test-directory-key"
    else:
        assert captured["headers"]["Authorization"] == "Bearer test-directory-key"


@pytest.mark.parametrize("payload", [{"models": []}, {"data": [{"name": "not-an-id"}]}, {"data": [{"id": ""}]}, {"data": [{"id": str(i)} for i in range(257)]}])
def test_model_directory_does_not_invent_ids_or_silently_truncate(monkeypatch, payload):
    monkeypatch.setattr(models, "validate_endpoint", lambda value, **kwargs: value)
    monkeypatch.setattr(models, "read_provider_response", lambda *_args, **_kwargs: json.dumps(payload).encode())
    with pytest.raises(ValueError):
        models.discover_remote_models("https://example.com/v1", "test-key")


def test_personal_connections_are_isolated_encrypted_and_discovery_is_authoritative(store, monkeypatch):
    state = save()
    assert "private-test-key" not in json.dumps(state)
    assert models.read_settings("alice")["encrypted_api_key"] != "private-test-key"
    assert not models.public_settings(models.read_settings("bob"))["secretConfigured"]
    with pytest.raises(ValueError, match="探测"):
        models.select_user_models("alice", [{"provider": "personal", "model": "invented"}], 1)
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["a", "b"])
    discovered = models.discover_user_models("alice")
    assert discovered["selected"] == []
    selected = models.select_user_models("alice", [{"provider": "personal", "model": "b"}], discovered["revision"])
    assert selected["selected"] == [{"provider": "personal", "model": "b"}]
    with pytest.raises(ValueError, match="可用模型"):
        models.validate_user_selection("bob", {"provider": "personal", "model": "b"})
    with pytest.raises(ValueError, match="已更新"):
        models.select_user_models("alice", [], discovered["revision"])


@pytest.mark.parametrize("connection_id", ["personal", "d1681e2c-c4ee-4b65-b923-9d9083a5c4f7"])
def test_model_directory_timeout_preserves_catalog_and_selected_models(store, monkeypatch, connection_id):
    save(connection_id=connection_id)
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["Vendor/Exact-ID", "another-model"])
    discovered = models.discover_user_models("alice", connection_id)
    choice = {"provider": models.connection_provider(connection_id), "model": "Vendor/Exact-ID"}
    selected = models.select_user_models("alice", [choice], discovered["revision"], connection_id)
    before = models.read_settings("alice", connection_id)

    def timeout(*args):
        raise TimeoutError("private-test-key: private upstream response")

    monkeypatch.setattr(models, "discover_remote_models", timeout)
    result = models.discover_user_models("alice", connection_id)
    after = models.read_settings("alice", connection_id)
    assert result["catalog"] == selected["catalog"]
    assert result["selected"] == selected["selected"] == [choice]
    for field in ("catalog_json", "selected_json", "encrypted_api_key", "base_url", "protocol"):
        assert after[field] == before[field]
    assert result["warnings"] == ["模型目录读取超时，已保留原模型列表，请稍后重试。"]
    assert models.validate_user_selection("alice", choice) == {"user_id": "alice", **choice}
    assert "private-test-key" not in json.dumps(result)
    assert "private upstream response" not in json.dumps(result)


def test_server_connection_is_not_automatically_published_to_users(store, monkeypatch):
    assert models.discover_user_models("alice")["catalog"] == []
    monkeypatch.setenv("DEEPSEEK_KEY", "system-secret")
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: pytest.fail("Platform offers must not require personal discovery"))
    result = models.discover_user_models("alice")
    assert result["catalog"] == []
    assert "system-secret" not in json.dumps(result)


def test_platform_models_are_ready_without_personal_setup_and_recheck_entitlement(store, monkeypatch):
    from mdi_api import platform_models
    monkeypatch.setattr(platform_models, "get_connection", lambda provider: SimpleNamespace(base_url="https://example.com/v1"))
    monkeypatch.setattr(platform_models, "decrypt_api_key", lambda connection: "platform-secret")
    with store.begin() as db:
        db.execute(insert(platform_model_offerings), [
            {"id": "public", "provider": "service", "model": "exact-public-id", "label": "公共模型", "protocol": "openai_chat", "audience": "all", "plans_json": [], "enabled": True},
            {"id": "premium", "provider": "service", "model": "exact-premium-id", "label": "套餐模型", "protocol": "openai_responses", "audience": "plans", "plans_json": ["research"], "enabled": True},
        ])
        db.execute(insert(user_model_plan_grants).values(user_id="alice", plan="research", expires_at=datetime.now(timezone.utc) + timedelta(days=1)))
    alice = models.public_settings(models.read_settings("alice"))
    assert not alice["secretConfigured"]
    assert {item["model"] for item in alice["selected"]} == {"exact-public-id", "exact-premium-id"}
    assert [item["model"] for item in models.public_settings(models.read_settings("bob"))["selected"]] == ["exact-public-id"]
    choice = models.validate_user_selection("alice", {"provider": "platform:premium", "model": "exact-premium-id"})
    provider, config = models.resolve_user_selection(choice)
    assert provider.protocol == "openai_responses"
    assert config.api_key == "platform-secret"
    assert "platform-secret" not in json.dumps(alice)
    with store.begin() as db:
        db.execute(update(user_model_plan_grants).values(expires_at=datetime.now(timezone.utc) - timedelta(seconds=1)))
    with pytest.raises(Exception, match="连接已不可用"):
        models.resolve_user_selection(choice)
    with store.begin() as db:
        db.execute(update(platform_model_offerings).values(enabled=False))
    assert models.public_settings(models.read_settings("alice"))["selected"] == []


def test_platform_publication_and_plan_routes_deny_ordinary_accounts(store):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="alice", email="alice@example.invalid", displayName="Alice", roles=[])
    client = TestClient(app)
    assert client.get("/admin/model-offerings").status_code == 403
    assert client.put("/admin/model-offerings/example", json={"provider": "service", "model": "id", "label": "Label", "protocol": "openai_chat", "audience": "all"}).status_code == 403
    assert client.put("/admin/accounts/alice/model-plans/research", json={"enabled": True}).status_code == 403


def test_platform_admin_can_publish_disable_and_grant_plans(store, monkeypatch):
    from mdi_api.transport.routers import platform_models as routes
    monkeypatch.setattr(routes, "_engine", lambda: store)
    monkeypatch.setattr(routes, "get_connection", lambda provider: object())
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="alice", email="alice@example.invalid", displayName="Alice", roles=[], platformRole="PLATFORM_ADMIN")
    client = TestClient(app)
    offer = {"provider": "service", "model": "Vendor/Exact-ID", "label": "Shared", "protocol": "anthropic", "audience": "plans", "plans": ["research"]}
    assert client.put("/admin/model-offerings/shared", json=offer).status_code == 200
    assert client.get("/admin/model-offerings").json()[0]["model"] == "Vendor/Exact-ID"
    assert client.put("/admin/model-offerings/shared", json={**offer, "enabled": False}).status_code == 200
    assert client.get("/admin/model-offerings").json()[0]["enabled"] is False
    assert client.put("/admin/accounts/bob/model-plans/research", json={"enabled": True}).status_code == 200
    assert client.put("/admin/accounts/bob/model-plans/research", json={"enabled": False}).status_code == 200


def test_protocol_change_invalidates_discovered_models(store, monkeypatch):
    save()
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["a"])
    state = models.discover_user_models("alice")
    state = models.select_user_models("alice", [{"provider": "personal", "model": "a"}], state["revision"])
    changed = models.save_personal_connection("alice", label="Mine", base_url="https://example.com/v1", api_key=None, protocol="anthropic", revision=state["revision"])
    assert changed["catalog"] == changed["selected"] == []
    assert changed["secretConfigured"]


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
def test_discovered_id_survives_selection_resolution_and_actual_payload(store, monkeypatch, protocol):
    model_id = "Vendor/Exact-Model:2026-09"
    save(protocol=protocol)
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: [model_id])
    state = models.discover_user_models("alice")
    choice = {"provider": "personal", "model": model_id}
    models.select_user_models("alice", [choice], state["revision"])
    monkeypatch.setattr(models, "validate_endpoint", lambda value, **kwargs: value)
    provider, config = models.resolve_user_selection(models.validate_user_selection("alice", choice))
    captured = {}
    def transport(**kwargs):
        captured.update(kwargs)
        if protocol == "anthropic":
            return {"content": [{"type": "text", "text": '{"ok":true}'}]}
        if protocol == "openai_responses":
            return {"output": [{"type": "message", "content": [{"type": "output_text", "text": '{"ok":true}'}]}]}
        return {"choices": [{"message": {"content": '{"ok":true}'}}]}
    provider.transport = transport
    result = provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert captured["payload"]["model"] == model_id
    assert result.model == model_id
    assert "private-test-key" not in json.dumps(captured["payload"])


@pytest.mark.parametrize("endpoint", ["http://example.com", "https://localhost/v1", "https://127.0.0.1/v1", "https://user:secret@example.com", "https://example.com?api_key=secret", "https://10.0.0.1/v1"])
def test_personal_endpoints_cannot_target_private_services_or_embed_credentials(endpoint):
    with pytest.raises(ValueError):
        models.validate_endpoint(endpoint)


@pytest.mark.parametrize("suffix", ["/chat/completions", "/responses", "/messages", "/models", "/"])
def test_full_request_urls_normalize_to_api_root(suffix):
    assert models.validate_endpoint("https://example.com/v1" + suffix) == "https://example.com/v1"


def test_bare_domain_defaults_to_versioned_api_root():
    assert models.validate_endpoint("https://example.com") == "https://example.com/v1"


@pytest.mark.parametrize("base_url", ["https://example.com", "https://example.com/", "https://example.com/v1", "https://example.com/v1/", "https://example.com/v1/chat/completions"])
def test_base_url_adaptation_never_duplicates_version(monkeypatch, base_url):
    urls = []
    def read_response(request, **_kwargs):
        urls.append(request.full_url)
        return b'{"data":[{"id":"exact-id"}]}'
    monkeypatch.setattr(models.socket, "getaddrinfo", lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))])
    monkeypatch.setattr(models, "read_provider_response", read_response)
    assert models.discover_remote_models(base_url, "test-key") == ["exact-id"]
    assert urls == ["https://example.com/v1/models"]


def test_correcting_legacy_operation_url_preserves_existing_key(store):
    save()
    with store.begin() as db:
        db.execute(update(user_model_settings).where(user_model_settings.c.user_id == "alice").values(base_url="https://example.com/v1/chat/completions"))
    before = models.read_settings("alice")["encrypted_api_key"]
    state = models.save_personal_connection("alice", label="Mine", base_url="https://example.com/v1", api_key=None, revision=1)
    assert state["baseUrl"] == "https://example.com/v1"
    assert models.read_settings("alice")["encrypted_api_key"] == before


def test_personal_api_uses_authenticated_owner_and_redacts_validation(store):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="alice", email="alice@example.invalid", displayName="Alice", roles=[])
    client = TestClient(app)
    result = client.put("/account/models/connection", json={"baseUrl": "https://example.com/v1", "apiKey": "secret-a", "revision": 0})
    assert result.status_code == 200
    assert "secret-a" not in result.text
    invalid = client.put("/account/models/connection", json={"baseUrl": "https://example.com/v1", "apiKey": "secret-a", "user_id": "bob", "revision": 1})
    assert invalid.status_code == 422
    assert "secret-a" not in invalid.text
    assert not models.read_settings("bob")["encrypted_api_key"]
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id="bob", email="bob@example.invalid", displayName="Bob", roles=[])
    assert client.get("/account/models").json()["secretConfigured"] is False


@pytest.mark.parametrize("protocol,path", [("openai_chat_json", "/chat/completions"), ("openai_chat", "/chat/completions"), ("openai_responses", "/responses"), ("anthropic", "/messages")])
def test_protocols_send_the_selected_model_and_parse_real_response_shapes(protocol, path):
    captured = {}
    def transport(**kwargs):
        captured.update(kwargs)
        if protocol == "anthropic": return {"content": [{"type": "text", "text": '{"answer":42}'}], "stop_reason": "end_turn"}
        if protocol == "openai_responses": return {"output": [{"type": "message", "content": [{"type": "output_text", "text": '{"answer":42}'}]}], "status": "completed"}
        return {"choices": [{"message": {"content": '{"answer":42}'}, "finish_reason": "stop"}]}
    provider = UserConnectionProvider(protocol=protocol, transport=transport)
    result = provider.complete_json(messages=[{"role": "system", "content": "Return JSON"}, {"role": "user", "content": "test"}], user_config=PlannerUserConfig(provider="personal", model="chosen-model", base_url="https://example.com/v1", api_key="only-in-header"))
    assert result.raw_json == {"answer": 42}
    assert captured["path"] == path
    assert captured["payload"]["model"] == "chosen-model"
    assert captured["headers"]["User-Agent"] == "MDI/1.0"
    assert "only-in-header" not in json.dumps(captured["payload"])
    assert ("response_format" in captured["payload"]) == (protocol == "openai_chat_json")
    if protocol == "anthropic": assert captured["headers"]["x-api-key"] == "only-in-header"
    if protocol == "openai_responses": assert captured["payload"]["store"] is False


def test_turn_client_resolves_private_model_without_including_credentials_in_prompts(monkeypatch):
    from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
    captured = {}
    def transport(**kwargs):
        captured.update(kwargs)
        return {"choices": [{"message": {"content": '{"ok":true}'}}]}
    monkeypatch.setattr(models, "selection_for_turn", lambda turn: {"user_id": "alice", "provider": "personal", "model": "chosen"})
    monkeypatch.setattr(models, "resolve_user_selection", lambda *args: (UserConnectionProvider(protocol="openai_chat", transport=transport), PlannerUserConfig(provider="personal", model="chosen", base_url="https://example.com/v1", api_key="secret-boundary")))
    result = asyncio.run(DeepSeekStructuredLLMClient(turn_id="turn-1").generate_structured(role="research_turn_orchestrator", system_prompt="Return JSON", input_payload={"question": "analyze"}, output_schema={}, timeout_seconds=10))
    assert result.provider == "personal" and result.model == "chosen"
    assert "secret-boundary" not in json.dumps(captured["payload"])


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
def test_provider_failure_traceback_does_not_expose_upstream_secret(protocol):
    def transport(**kwargs):
        raise RuntimeError("upstream body contains private-test-credential")
    provider = UserConnectionProvider(protocol=protocol, transport=transport)
    config = PlannerUserConfig(provider="personal", model="exact-id", base_url="https://example.com/v1", api_key="private-test-credential")
    with pytest.raises(Exception) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert "private-test-credential" not in "".join(traceback.format_exception(caught.value))
    assert caught.value.code == "EXTERNAL_UNAVAILABLE"


@pytest.mark.parametrize("status, code", [(401, "PROVIDER_AUTH_FAILED"), (403, "PROVIDER_AUTH_FAILED"), (429, "PROVIDER_RATE_LIMITED"), (400, "PROVIDER_REQUEST_REJECTED"), (503, "EXTERNAL_UNAVAILABLE")])
def test_personal_provider_reports_safe_http_failures(status, code):
    import urllib.error
    def transport(**kwargs):
        raise urllib.error.HTTPError("https://private-test-credential.invalid", status, "private-test-credential", {}, None)
    provider = UserConnectionProvider(protocol="openai_chat_json", transport=transport)
    config = PlannerUserConfig(provider="personal", model="exact-id", api_key="private-test-credential")
    with pytest.raises(Exception) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert caught.value.code == code
    assert caught.value.status_code == status
    assert "private-test-credential" not in "".join(traceback.format_exception(caught.value))


def test_personal_provider_timeout_has_a_safe_distinct_code():
    def transport(**kwargs):
        raise TimeoutError("private-test-credential")
    provider = UserConnectionProvider(protocol="openai_chat", transport=transport)
    config = PlannerUserConfig(provider="personal", model="exact-id", api_key="private-test-credential")
    with pytest.raises(Exception) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert caught.value.code == "PROVIDER_TIMEOUT"
    assert "private-test-credential" not in "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("response, code", [
    ({"choices": [{"message": {"content": "⚠️ 所有模型均不可用: HTTP 429"}, "finish_reason": "stop"}]}, "PROVIDER_RATE_LIMITED"),
    ({"error": {"type": "authentication_error", "message": "private-test-credential"}}, "PROVIDER_AUTH_FAILED"),
    ({"error": {"code": "rate_limit_exceeded", "message": "private-test-credential"}}, "PROVIDER_RATE_LIMITED"),
    ({"error": {"type": "unknown", "message": "private-test-credential HTTP 429"}}, "EXTERNAL_UNAVAILABLE"),
    ({"choices": [{"message": {"content": "Discuss HTTP 429: private-test-credential"}}]}, "PROVIDER_INVALID_RESPONSE"),
    ({"choices": [{"message": {"content": "{\"ok\":"}, "finish_reason": "length"}]}, "PROVIDER_OUTPUT_TRUNCATED"),
    ({"choices": [{"message": {"content": None}}]}, "PROVIDER_INVALID_RESPONSE"),
    ({"choices": []}, "PROVIDER_INVALID_RESPONSE"),
    (["private-test-credential"], "PROVIDER_INVALID_RESPONSE"),
    ({"output": [], "status": "incomplete"}, "PROVIDER_OUTPUT_TRUNCATED"),
])
def test_successful_transport_still_requires_a_usable_completion(response, code):
    protocol = "openai_responses" if isinstance(response, dict) and "output" in response else "openai_chat_json"
    provider = UserConnectionProvider(protocol=protocol, transport=lambda **kwargs: response)
    config = PlannerUserConfig(provider="personal", model="deepseek-v4-pro", api_key="private-test-credential")
    with pytest.raises(Exception) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert caught.value.code == code
    assert caught.value.status_code is None  # No invented transport status.
    assert "private-test-credential" not in "".join(traceback.format_exception(caught.value))


def test_structured_answer_mentioning_rate_limits_is_not_an_upstream_failure():
    provider = UserConnectionProvider(protocol="openai_chat_json", transport=lambda **kwargs: {
        "choices": [{"message": {"content": '{"answer":"所有模型均不可用: HTTP 429 means rate limited"}'}, "finish_reason": "stop"}],
    })
    result = provider.complete_json(messages=[], user_config=PlannerUserConfig(provider="personal", model="deepseek-v4-pro"))
    assert result.raw_json["answer"].endswith("rate limited")


def test_resolution_failure_traceback_does_not_expose_internal_secret(monkeypatch):
    def unavailable(*args):
        raise RuntimeError("connection failure includes private-test-credential")
    monkeypatch.setattr(models, "validate_user_selection", unavailable)
    with pytest.raises(Exception) as caught:
        models.resolve_user_selection({"user_id": "alice", "provider": "personal", "model": "exact-id"})
    assert "private-test-credential" not in "".join(traceback.format_exception(caught.value))
    assert caught.value.code == "PROVIDER_NOT_ALLOWED"


def test_legacy_account_adapter_ignores_caller_credentials_and_retains_only_identity(store, monkeypatch):
    from mdi_api.account_model_provider import AccountModelProvider
    from mdi_api.transport.routers.planner import _planner_user_config_from_request, PlannerJobsRequest
    import mdi_api.account_model_provider as binding
    save()
    monkeypatch.setattr(models, "discover_remote_models", lambda *args: ["Vendor/Exact-ID"])
    state = models.discover_user_models("alice")
    models.select_user_models("alice", [{"provider": "personal", "model": "Vendor/Exact-ID"}], state["revision"])
    bound = AccountModelProvider("alice", provider="personal", model="Vendor/Exact-ID")
    captured = {}
    def transport(**kwargs):
        captured.update(kwargs)
        return {"choices": [{"message": {"content": '{"ok":true}'}}]}
    monkeypatch.setattr(binding, "resolve_user_selection", lambda selection: (UserConnectionProvider(protocol="openai_chat", transport=transport), PlannerUserConfig(provider="personal", model=selection["model"], api_key="server-resolved-key")))
    bound.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=PlannerUserConfig(api_key="untrusted-key", model="wrong"))
    assert captured["payload"]["model"] == "Vendor/Exact-ID"
    assert captured["headers"]["Authorization"] == "Bearer server-resolved-key"
    assert "server-resolved-key" not in str(vars(bound))
    assert _planner_user_config_from_request(PlannerJobsRequest(userPrompt="Analyze", datasetId="dataset", provider="personal"), selected_provider=bound) is None


def test_legacy_job_route_binds_model_to_authenticated_user(store, monkeypatch):
    from mdi_api.transport.routers import secured_planner, planner
    import mdi_api.account_model_provider as binding
    observed = {}
    monkeypatch.setattr(secured_planner, "create_engine_from_settings", lambda settings: store)
    monkeypatch.setattr(secured_planner, "require_project_access", lambda *args, **kwargs: None)
    def validate(user_id, selection):
        observed["user_id"] = user_id
        return {"user_id": user_id, **selection}
    monkeypatch.setattr(binding, "validate_user_selection", validate)
    def create_job(request, *, provider):
        observed["provider"] = provider.meta.name
        observed["model"] = provider.meta.model
        return {"job_id": "test-job"}
    monkeypatch.setattr(planner, "planner_jobs", create_job)
    request = planner.PlannerJobsRequest(userPrompt="Analyze", datasetId="dataset", provider="platform:shared", model="Vendor/Exact-ID")
    result = secured_planner.create_planner_job_secured(request, CurrentUser(id="alice", email="alice@example.invalid", displayName="Alice", roles=[]))
    assert result == {"job_id": "test-job"}
    assert observed == {"user_id": "alice", "provider": "platform:shared", "model": "Vendor/Exact-ID"}


@pytest.mark.parametrize("entry", ["preview", "intent"])
def test_legacy_preview_and_intent_use_account_binding(store, monkeypatch, entry):
    from mdi_api.transport.routers import secured_planner, secured_runtime, planner
    import mdi_api.account_model_provider as binding
    monkeypatch.setattr(secured_planner, "create_engine_from_settings", lambda settings: store)
    monkeypatch.setattr(secured_planner, "require_project_access", lambda *args, **kwargs: None)
    monkeypatch.setattr(secured_runtime, "_dataset_project_id", lambda dataset: None)
    monkeypatch.setattr(binding, "validate_user_selection", lambda user_id, selection: {"user_id": user_id, **selection})
    observed = {}
    def invoke(request, *, provider):
        observed.update(provider._selection)
        return {"ok": True}
    user = CurrentUser(id="alice", email="alice@example.invalid", displayName="Alice", roles=[])
    if entry == "preview":
        monkeypatch.setattr(planner, "planner_preview", invoke)
        request = planner.PlannerPreviewRequest(userPrompt="Analyze", datasetId="dataset", provider="personal", model="Exact-ID")
        result = secured_planner.planner_preview_secured(request, user)
    else:
        monkeypatch.setattr(planner, "create_planner_intent", invoke)
        request = planner.PlannerIntentCreateRequest(rawGoal="Analyze", datasetId="dataset", profileId="profile", provider="personal", model="Exact-ID")
        result = secured_planner.create_planner_intent_secured(request, user)
    assert result == {"ok": True}
    assert observed == {"user_id": "alice", "provider": "personal", "model": "Exact-ID", "thinking_mode": "standard"}
