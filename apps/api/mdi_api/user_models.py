"""User-scoped model authority. Credentials never enter workflow payloads."""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from mdi_llm import PlannerUserConfig, LLMProviderError
from mdi_llm.http_transport import read_provider_response
from mdi_api.config import load_settings
from mdi_api.db import user_model_settings, user_model_connections
from mdi_api.infrastructure.persistence.engine import create_engine_from_settings
from mdi_api.provider_connections import _fernet, thinking_budget


def _engine():
    return create_engine_from_settings(load_settings())


def _connection_scope(user_id: str, connection_id: str):
    if connection_id == "personal":
        return user_model_settings, user_model_settings.c.user_id == user_id
    try:
        if str(UUID(connection_id)) != connection_id:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise ValueError("连接标识无效，请重新读取配置。") from None
    return user_model_connections, (user_model_connections.c.user_id == user_id) & (user_model_connections.c.id == connection_id)


def connection_provider(connection_id: str) -> str:
    return "personal" if connection_id == "personal" else f"personal:{connection_id}"


def read_settings(user_id: str, connection_id: str = "personal") -> dict[str, Any]:
    table, scope = _connection_scope(user_id, connection_id)
    with _engine().connect() as db:
        row = db.execute(select(table).where(scope)).mappings().first()
    return dict(row) if row else {
        "user_id": user_id, "label": "我的模型服务", "protocol": "openai_chat_json", "base_url": "", "encrypted_api_key": "",
        "catalog_json": [], "selected_json": [], "revision": 0, "id": connection_id,
    }


def _write(user_id: str, values: dict[str, Any], *, expected_revision: int, connection_id: str = "personal") -> None:
    table, scope = _connection_scope(user_id, connection_id)
    values = {**values, "revision": expected_revision + 1, "updated_at": datetime.now(timezone.utc)}
    with _engine().begin() as db:
        if expected_revision == 0:
            try:
                identity = {} if connection_id == "personal" else {"id": connection_id}
                db.execute(insert(table).values(user_id=user_id, **identity, **{"label": "我的模型服务", **values}))
            except IntegrityError:
                # Concurrent first saves must not expose SQL parameters or keys.
                raise ValueError("配置已在其他窗口更新，请重新读取后再试。") from None
        else:
            result = db.execute(update(table).where(
                scope, table.c.revision == expected_revision,
            ).values(**values))
            if result.rowcount != 1:
                raise ValueError("配置已在其他窗口更新，请重新读取后再试。")


def _public_connection(row: dict[str, Any]) -> dict[str, Any]:
    connection_id = row.get("id", "personal")
    provider = connection_provider(connection_id)
    return {
        "connectionId": connection_id, "provider": provider,
        "label": row["label"], "baseUrl": row["base_url"],
        "protocol": row["protocol"],
        "secretConfigured": bool(row["encrypted_api_key"]),
        "catalog": [item for item in row["catalog_json"] if item["provider"] == provider],
        "selected": [item for item in row["selected_json"] if item["provider"] == provider],
        "revision": row["revision"],
    }


def public_settings(row: dict[str, Any]) -> dict[str, Any]:
    from mdi_api.platform_models import catalog_for_user
    user_id = row["user_id"]
    with _engine().connect() as db:
        extra = db.execute(select(user_model_connections).where(user_model_connections.c.user_id == user_id)
                           .order_by(user_model_connections.c.label, user_model_connections.c.id)).mappings().all()
    legacy = row if row.get("id", "personal") == "personal" else read_settings(user_id)
    connections = [_public_connection(legacy), *[_public_connection(dict(item)) for item in extra]]
    platform = catalog_for_user(user_id)
    return {
        **_public_connection(row), "connections": connections,
        "catalog": [item for connection in connections for item in connection["catalog"]] + platform,
        "selected": [item for connection in connections for item in connection["selected"]] + platform,
    }


def validate_endpoint(value: str, *, resolve: bool = False) -> str:
    parsed = urllib.parse.urlsplit(value.strip())
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.port not in (None, 443)):
        raise ValueError("请输入不含账号、查询参数的 HTTPS 服务地址。")
    hostname = parsed.hostname.lower()
    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
        raise ValueError("个人模型服务需要使用公网 HTTPS 地址。")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address and not address.is_global:
        raise ValueError("个人模型服务需要使用公网 HTTPS 地址。")
    if resolve:
        try:
            addresses = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError("无法解析模型服务地址，请检查地址后重试。") from exc
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            raise ValueError("模型服务地址解析到了非公网网络。")
    path = parsed.path.rstrip("/")
    # Users commonly paste a documented request URL rather than its API root.
    # Strip only recognized terminal operations, never arbitrary path segments.
    for operation in ("/chat/completions", "/responses", "/messages", "/models"):
        if path.endswith(operation):
            path = path[:-len(operation)]
            break
    return urllib.parse.urlunsplit(("https", parsed.netloc, path or "/v1", "", ""))


def save_personal_connection(user_id: str, *, label: str, base_url: str, api_key: str | None, revision: int, protocol: str = "openai_chat_json", connection_id: str = "personal") -> dict[str, Any]:
    previous = read_settings(user_id, connection_id)
    if previous["revision"] != revision:
        raise ValueError("配置已更新，请重新读取后再保存。")
    endpoint = validate_endpoint(base_url)
    key = (api_key or "").strip()
    previous_endpoint = validate_endpoint(previous["base_url"]) if previous["base_url"] else ""
    if not key and (not previous["encrypted_api_key"] or endpoint != previous_endpoint):
        raise ValueError("新连接或更换服务地址时，请输入 API Key。")
    encrypted = (_fernet(stable_required=True).encrypt(key.encode()).decode() if key else previous["encrypted_api_key"])
    if protocol not in {"openai_chat_json", "openai_chat", "openai_responses", "anthropic"}:
        raise ValueError("请选择支持的请求协议。")
    changed = endpoint != previous["base_url"] or bool(key) or protocol != previous["protocol"]
    _write(user_id, {
        "label": label.strip() or "我的模型服务", "protocol": protocol, "base_url": endpoint, "encrypted_api_key": encrypted,
        "catalog_json": [] if changed else previous["catalog_json"],
        "selected_json": [] if changed else previous["selected_json"],
    }, expected_revision=revision, connection_id=connection_id)
    return public_settings(read_settings(user_id, connection_id))


def discover_remote_models(base_url: str, api_key: str, protocol: str = "openai_chat_json") -> list[str]:
    endpoint = validate_endpoint(base_url, resolve=True)
    headers = ({"x-api-key": api_key, "anthropic-version": "2023-06-01"} if protocol == "anthropic" else {"Authorization": f"Bearer {api_key}"})
    request = urllib.request.Request(f"{endpoint}/models", headers={**headers, "Accept": "application/json", "User-Agent": "MDI/1.0"})
    raw = read_provider_response(request, timeout=12, byte_limit=2_000_000)
    if len(raw) > 2_000_000:
        raise ValueError("模型目录过大，请联系服务提供方。")
    payload = json.loads(raw)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        raise ValueError("服务未返回有效的模型目录。")
    model_ids = []
    for item in data:
        model_id = item.get("id") if isinstance(item, dict) else None
        if not isinstance(model_id, str) or not model_id.strip() or len(model_id) > 128:
            raise ValueError("模型目录包含无效或过长的模型 ID。")
        # The provider ID is the request identity, not a display-name slug.
        if model_id not in model_ids:
            model_ids.append(model_id)
    if len(model_ids) > 256:
        raise ValueError("模型目录超过 256 项，请使用范围更小的服务目录。")
    return model_ids


def discover_user_models(user_id: str, connection_id: str = "personal") -> dict[str, Any]:
    row = read_settings(user_id, connection_id)
    provider = connection_provider(connection_id)
    catalog: list[dict[str, str]] = []
    warnings: list[str] = []
    if row["encrypted_api_key"]:
        try:
            key = _fernet(stable_required=True).decrypt(row["encrypted_api_key"].encode()).decode()
            catalog.extend({"provider": provider, "model": model, "label": row["label"]} for model in discover_remote_models(row["base_url"], key, row["protocol"]))
        except urllib.error.HTTPError as exc:
            warnings.append({
                401: "模型服务拒绝认证（401），请检查 API Key。",
                403: "模型服务或网关拒绝访问（403），请检查密钥权限或供应商访问限制。",
                404: "模型列表接口不存在（404），请检查服务地址的 API 根路径。",
                429: "模型服务请求过多（429），请稍后重试。",
            }.get(exc.code, "模型服务暂时不可用，请稍后重试。"))
            catalog.extend(item for item in row["catalog_json"] if item["provider"] == provider)
        except TimeoutError:
            warnings.append("模型目录读取超时，已保留原模型列表，请稍后重试。")
            catalog.extend(item for item in row["catalog_json"] if item["provider"] == provider)
        except Exception:
            # Neither upstream response bodies nor credentials are product errors.
            warnings.append("个人服务探测失败，请检查地址、密钥与服务状态后重试。")
            catalog.extend(item for item in row["catalog_json"] if item["provider"] == provider)
    allowed = {(item["provider"], item["model"]) for item in catalog}
    selected = [item for item in row["selected_json"] if (item["provider"], item["model"]) in allowed]
    _write(user_id, {"catalog_json": catalog, "selected_json": selected}, expected_revision=row["revision"], connection_id=connection_id)
    return {**public_settings(read_settings(user_id, connection_id)), "warnings": warnings}


def select_user_models(user_id: str, selections: list[dict[str, str]], revision: int, connection_id: str = "personal") -> dict[str, Any]:
    row = read_settings(user_id, connection_id)
    if row["revision"] != revision:
        raise ValueError("模型目录已更新，请重新读取后再选择。")
    allowed = {(item["provider"], item["model"]) for item in _public_connection(row)["catalog"]}
    selected = []
    for item in selections:
        pair = (item["provider"], item["model"])
        if pair not in allowed:
            raise ValueError("只能选择探测结果中的模型，请重新探测。")
        if item not in selected:
            selected.append(item)
    _write(user_id, {"selected_json": selected}, expected_revision=revision, connection_id=connection_id)
    return public_settings(read_settings(user_id, connection_id))


def validate_user_selection(user_id: str, selection: dict[str, str]) -> dict[str, str]:
    row = read_settings(user_id)
    if not any(item["provider"] == selection["provider"] and item["model"] == selection["model"] for item in public_settings(row)["selected"]):
        raise ValueError("所选模型不在你的可用模型中，请打开模型设置重新探测并选择。")
    return {"user_id": user_id, **selection}


def resolve_user_selection(selection: dict[str, str], timeout_seconds: float = 120):
    try:
        user_id = selection["user_id"]
        validate_user_selection(user_id, selection)
        provider = selection["provider"]
        if provider == "personal" or provider.startswith("personal:"):
            row = read_settings(user_id, "personal" if provider == "personal" else provider.removeprefix("personal:"))
            endpoint = validate_endpoint(row["base_url"], resolve=True)
            key = _fernet(stable_required=True).decrypt(row["encrypted_api_key"].encode()).decode()
            protocol = row["protocol"]
        elif provider.startswith("platform:"):
            from mdi_api.platform_models import resolve_offering
            endpoint, key, protocol = resolve_offering(user_id, provider, selection["model"])
        else:
            raise ValueError("未授权的模型来源")
        config = PlannerUserConfig(
            provider=provider, model=selection["model"], base_url=endpoint, api_key=key,
            timeout_seconds=min(timeout_seconds, 120), temperature=0,
            max_tokens=thinking_budget(selection.get("thinking_mode")), thinking_mode=selection.get("thinking_mode", "standard"),
        )
        from mdi_llm.user_connection_provider import UserConnectionProvider
        return UserConnectionProvider(protocol=protocol), config
    except Exception:
        raise LLMProviderError("所选模型连接已不可用，请检查个人模型设置后重试。", code="PROVIDER_NOT_ALLOWED") from None


def selection_for_turn(turn_id: str) -> dict[str, str] | None:
    from uuid import UUID
    from mdi_api.bootstrap.repository_factory import create_repository_factory
    with create_repository_factory().session() as session:
        turn = session.agent2.research_turns.get(UUID(turn_id))
        message = session.agent2.research_turns.get_message(str(turn["user_message_id"]))
    return (message.get("payload_json") or {}).get("_model_selection")
