"""Server-side provider connection registry.

The browser may create and revoke a connection, but it never receives the
credential again.  Credentials are encrypted in memory with a process key in
local development; deployments should set ``MDI_PROVIDER_ENCRYPTION_KEY`` to
make the key stable across restarts.
"""

from __future__ import annotations

import ipaddress
import os
import re
import threading
import urllib.parse
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from cryptography.fernet import Fernet, InvalidToken


_SLUG = re.compile(r"^[a-z][a-z0-9_.-]{1,63}$")
_THINKING_MODES = ("quick", "standard", "deep")
_LOCK = threading.RLock()
_PROCESS_KEY = Fernet.generate_key()


def _fernet() -> Fernet:
    encoded = os.getenv("MDI_PROVIDER_ENCRYPTION_KEY", "").strip()
    if encoded:
        try:
            return Fernet(encoded.encode("ascii"))
        except (ValueError, TypeError) as exc:
            raise ValueError("MDI_PROVIDER_ENCRYPTION_KEY must be a Fernet key") from exc
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


_connections: dict[str, ProviderConnection] = {}


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
    with _LOCK:
        previous = _connections.get(provider)
        record = ProviderConnection(
            provider=provider,
            label=(label or provider).strip()[:120],
            kind=kind,
            base_url=base_url,
            model_ids=models,
            default_model=default_model or (models[0] if models else None),
            encrypted_api_key=_fernet().encrypt(api_key.strip().encode("utf-8")).decode("ascii"),
            created_at=previous.created_at if previous else now,
            updated_at=now,
            persistence="environment_key" if os.getenv("MDI_PROVIDER_ENCRYPTION_KEY") else "process_only",
        )
        _connections[provider] = record
        return record


def get_connection(provider: str) -> ProviderConnection | None:
    with _LOCK:
        return _connections.get(provider.strip().lower())


def list_connections() -> list[ProviderConnection]:
    with _LOCK:
        return list(_connections.values())


def delete_connection(provider: str) -> bool:
    with _LOCK:
        return _connections.pop(provider.strip().lower(), None) is not None


def update_connection_models(*, provider: str, model_ids: list[str], default_model: str | None = None) -> ProviderConnection:
    """Persist the model group without requiring the secret again."""
    normalized = normalize_provider(provider)
    models = tuple(dict.fromkeys(item.strip() for item in model_ids if item and item.strip()))[:256]
    if default_model and default_model not in models:
        raise ValueError("默认模型必须属于已选择的模型组")
    with _LOCK:
        previous = _connections.get(normalized)
        if previous is None:
            raise ValueError("请先保存 Provider 连接")
        record = replace(
            previous,
            model_ids=models,
            default_model=default_model or (models[0] if models else None),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        _connections[normalized] = record
        return record


def reset_connections_for_tests() -> None:
    """Clear process-local connections for isolated unit tests."""
    with _LOCK:
        _connections.clear()


def decrypt_api_key(connection: ProviderConnection) -> str:
    try:
        return _fernet().decrypt(connection.encrypted_api_key.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError("Provider credential is unavailable") from exc


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
