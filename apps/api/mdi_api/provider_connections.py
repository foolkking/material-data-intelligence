"""Server-side provider connection authority.

Local development and isolated tests retain a process-local adapter. A
PostgreSQL runtime stores encrypted Provider connections in the shared
database so every API/worker process resolves the same reviewed connection.
The browser never receives the credential again.
"""

from __future__ import annotations

import ipaddress
import os
import re
import threading
import urllib.parse
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Mapping, Protocol

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Engine, delete, insert, select, update

from mdi_api.config import load_settings
from mdi_api.database import create_engine_from_settings
from mdi_api.db import provider_connections


_SLUG = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
_THINKING_MODES = ("quick", "standard", "deep")
_LOCK = threading.RLock()
_PROCESS_KEY = Fernet.generate_key()


class ProviderConnectionConfigurationError(ValueError):
    """Typed fail-closed configuration error for durable credentials."""

    def __init__(self, message: str, *, code: str) -> None:
        self.code = code
        super().__init__(message)


def _fernet(*, stable_required: bool = False) -> Fernet:
    encoded = os.getenv("MDI_PROVIDER_ENCRYPTION_KEY", "").strip()
    if encoded:
        try:
            return Fernet(encoded.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise ProviderConnectionConfigurationError(
                "MDI_PROVIDER_ENCRYPTION_KEY must be a Fernet key",
                code="PROVIDER_ENCRYPTION_KEY_INVALID",
            ) from exc
    if stable_required:
        raise ProviderConnectionConfigurationError(
            "A stable Provider encryption key is required for durable credentials.",
            code="PROVIDER_ENCRYPTION_KEY_REQUIRED",
        )
    return Fernet(_PROCESS_KEY)


@dataclass(frozen=True)
class ProviderConnection:
    provider: str
    label: str
    kind: str
    base_url: str
    model_ids: tuple[str, ...]
    default_model: str | None
    encrypted_api_key: str
    created_at: str
    updated_at: str
    persistence: str

    @property
    def configured(self) -> bool:
        return bool(self.encrypted_api_key)


class _ProviderConnectionStore(Protocol):
    def save(self, connection: ProviderConnection) -> ProviderConnection:
        ...

    def get(self, provider: str) -> ProviderConnection | None:
        ...

    def list(self) -> list[ProviderConnection]:
        ...

    def delete(self, provider: str) -> bool:
        ...


class _InMemoryProviderConnectionStore:
    def __init__(self) -> None:
        self._connections: dict[str, ProviderConnection] = {}

    def save(self, connection: ProviderConnection) -> ProviderConnection:
        with _LOCK:
            self._connections[connection.provider] = connection
        return connection

    def get(self, provider: str) -> ProviderConnection | None:
        with _LOCK:
            return self._connections.get(provider)

    def list(self) -> list[ProviderConnection]:
        with _LOCK:
            return list(self._connections.values())

    def delete(self, provider: str) -> bool:
        with _LOCK:
            return self._connections.pop(provider, None) is not None

    def clear(self) -> None:
        with _LOCK:
            self._connections.clear()


class DatabaseProviderConnectionStore:
    """Shared encrypted Provider connection repository."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def save(self, connection: ProviderConnection) -> ProviderConnection:
        values = {
            "label": connection.label,
            "kind": connection.kind,
            "base_url": connection.base_url,
            "model_ids_json": list(connection.model_ids),
            "default_model": connection.default_model,
            "encrypted_api_key": connection.encrypted_api_key,
            "updated_at": _parse_timestamp(connection.updated_at),
        }
        with self._engine.begin() as database:
            updated = database.execute(
                update(provider_connections)
                .where(provider_connections.c.provider == connection.provider)
                .values(**values)
            )
            if not updated.rowcount:
                database.execute(
                    insert(provider_connections).values(
                        provider=connection.provider,
                        created_at=_parse_timestamp(connection.created_at),
                        **values,
                    )
                )
        return connection

    def get(self, provider: str) -> ProviderConnection | None:
        with self._engine.connect() as database:
            row = database.execute(
                select(provider_connections).where(
                    provider_connections.c.provider == provider
                )
            ).mappings().first()
        return _connection_from_row(row) if row is not None else None

    def list(self) -> list[ProviderConnection]:
        with self._engine.connect() as database:
            rows = database.execute(
                select(provider_connections).order_by(
                    provider_connections.c.provider
                )
            ).mappings().all()
        return [_connection_from_row(row) for row in rows]

    def delete(self, provider: str) -> bool:
        with self._engine.begin() as database:
            removed = database.execute(
                delete(provider_connections).where(
                    provider_connections.c.provider == provider
                )
            )
        return bool(removed.rowcount)


_LOCAL_STORE = _InMemoryProviderConnectionStore()


def _active_store() -> _ProviderConnectionStore:
    settings = load_settings()
    if settings.runtime_backend == "postgresql":
        return DatabaseProviderConnectionStore(
            create_engine_from_settings(settings)
        )
    return _LOCAL_STORE


def _durable_store_enabled() -> bool:
    return load_settings().runtime_backend == "postgresql"


def validate_base_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        raise ValueError("Base URL 必须是完整的 http(s) 地址")
    host = (parsed.hostname or "").lower()
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and address.is_private and host not in {"127.0.0.1", "::1"}:
        raise ValueError("Base URL 不允许指向私有网络地址")
    if parsed.scheme == "http" and host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("生产 Provider 需要使用 HTTPS；HTTP 仅允许本机调试")
    if any(token in host for token in ("169.254.", "metadata.google", "instance-data")):
        raise ValueError("Base URL 不允许指向云实例元数据地址")
    path = parsed.path.rstrip("/")
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def normalize_provider(value: str) -> str:
    provider = value.strip().lower()
    if not _SLUG.fullmatch(provider):
        raise ValueError("Provider 标识只能包含小写字母、数字、点、下划线和短横线")
    return provider


def save_connection(*, provider: str, label: str | None, kind: str, base_url: str, api_key: str, model_ids: list[str] | None = None, default_model: str | None = None) -> ProviderConnection:
    provider = normalize_provider(provider)
    if not api_key.strip():
        raise ValueError("API Key 不能为空")
    if kind not in {"openai_compatible"}:
        raise ValueError("当前支持 openai_compatible Provider；其他协议需要独立适配器")
    base_url = validate_base_url(base_url)
    models = tuple(dict.fromkeys(item.strip() for item in (model_ids or []) if item and item.strip()))[:256]
    if default_model and default_model not in models:
        models = tuple([default_model, *models])[:256]
    now = datetime.now(timezone.utc).isoformat()
    store = _active_store()
    previous = store.get(provider)
    durable = _durable_store_enabled()
    record = ProviderConnection(
        provider=provider,
        label=(label or provider).strip()[:120],
        kind=kind,
        base_url=base_url,
        model_ids=models,
        default_model=default_model or (models[0] if models else None),
        encrypted_api_key=_fernet(stable_required=durable)
        .encrypt(api_key.strip().encode("utf-8"))
        .decode("ascii"),
        created_at=previous.created_at if previous else now,
        updated_at=now,
        persistence="database_encrypted" if durable else "process_only",
    )
    return store.save(record)


def get_connection(provider: str) -> ProviderConnection | None:
    return _active_store().get(provider.strip().lower())


def list_connections() -> list[ProviderConnection]:
    return _active_store().list()


def delete_connection(provider: str) -> bool:
    return _active_store().delete(provider.strip().lower())


def update_connection_models(*, provider: str, model_ids: list[str], default_model: str | None = None) -> ProviderConnection:
    """Persist the model group without requiring the secret again."""
    normalized = normalize_provider(provider)
    models = tuple(dict.fromkeys(item.strip() for item in model_ids if item and item.strip()))[:256]
    if default_model and default_model not in models:
        raise ValueError("默认模型必须属于已选择的模型组")
    store = _active_store()
    previous = store.get(normalized)
    if previous is None:
        raise ValueError("请先保存 Provider 连接")
    record = replace(
        previous,
        model_ids=models,
        default_model=default_model or (models[0] if models else None),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    return store.save(record)


def reset_connections_for_tests() -> None:
    """Clear process-local connections for isolated unit tests."""
    _LOCAL_STORE.clear()


def decrypt_api_key(connection: ProviderConnection) -> str:
    try:
        return _fernet(
            stable_required=connection.persistence == "database_encrypted"
        ).decrypt(connection.encrypted_api_key.encode("ascii")).decode("utf-8")
    except (
        InvalidToken,
        UnicodeDecodeError,
        ProviderConnectionConfigurationError,
        ValueError,
    ) as exc:
        raise RuntimeError("Provider credential is unavailable") from exc


def _connection_from_row(row: Mapping[str, object]) -> ProviderConnection:
    values = row
    return ProviderConnection(
        provider=str(values["provider"]),
        label=str(values["label"]),
        kind=str(values["kind"]),
        base_url=str(values["base_url"]),
        model_ids=tuple(str(item) for item in (values["model_ids_json"] or [])),
        default_model=(
            str(values["default_model"])
            if values["default_model"] is not None
            else None
        ),
        encrypted_api_key=str(values["encrypted_api_key"]),
        created_at=_timestamp_text(values["created_at"]),
        updated_at=_timestamp_text(values["updated_at"]),
        persistence="database_encrypted",
    )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _timestamp_text(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def public_connection(connection: ProviderConnection) -> dict[str, object]:
    return {
        "id": connection.provider,
        "provider": connection.provider,
        "label": connection.label,
        "kind": connection.kind,
        "baseUrl": connection.base_url,
        "defaultModel": connection.default_model,
        "allowedModels": list(connection.model_ids),
        "models": list(connection.model_ids),
        "requiresSecret": True,
        "secretConfigured": connection.configured,
        "secretSource": "encrypted_server_store",
        "configurationSource": connection.persistence,
        "execution": "live",
        "thinkingModes": list(_THINKING_MODES),
        "description": "已保存的兼容模型服务。密钥仅用于服务端请求，不会返回到浏览器。",
    }


def thinking_modes() -> list[dict[str, str]]:
    return [
        {"id": "quick", "label": "快速", "description": "较低延迟，适合简单查询"},
        {"id": "standard", "label": "标准", "description": "平衡响应速度与分析深度"},
        {"id": "deep", "label": "深入", "description": "更高输出预算，适合复杂科学问题"},
    ]


def thinking_budget(mode: str | None, default: int = 4096) -> int:
    normalized = mode if mode in _THINKING_MODES else "standard"
    ceilings = {"quick": 2048, "standard": 4096, "deep": 8192}
    return min(ceilings[normalized], max(512, min(default, 8192)))
