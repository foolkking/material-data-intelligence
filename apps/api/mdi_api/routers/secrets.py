"""Secrets API routes — POST/GET/DELETE /me/secrets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from mdi_api.secrets import InMemorySecretStore, Secret, SecretData
from mdi_llm import is_credential_key, redact_credential_values


class CreateSecretRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=64)
    value: str = Field(min_length=1)
    type: str = Field(default="api_key", pattern=r"^(api_key|base_url|custom)$")
    alias: str | None = Field(default=None, max_length=120)


@dataclass
class SecretSummary:
    id: str
    secret_id: str
    alias: str
    provider: str
    created_at: str
    createdAt: str
    lastUsedAt: str | None
    status: str
    maskedPreview: str


_store = InMemorySecretStore()
_CURRENT_USER_ID = "user_local"
_SECRET_ALIASES: dict[str, str] = {}
_SECRET_LAST_USED: dict[str, str] = {}


def create_secret(request: CreateSecretRequest) -> SecretSummary:
    sec = _store.create_secret(scope_id=_CURRENT_USER_ID, provider=request.provider, value=request.value)
    _SECRET_ALIASES[sec.id] = request.alias or f"{request.provider} API Key"
    return _secret_summary(sec)


def list_secrets() -> list[SecretSummary]:
    return [_secret_summary(s) for s in _store.list_secrets(scope_id=_CURRENT_USER_ID)]


def delete_secret(secret_id: str) -> bool:
    _SECRET_ALIASES.pop(secret_id, None)
    _SECRET_LAST_USED.pop(secret_id, None)
    return _store.delete_secret(secret_id)


def get_secret_value(secret_id: str) -> str | None:
    sd = _store.get_secret(secret_id)
    return sd.value if sd else None


def mark_secret_used(secret_id: str) -> None:
    from datetime import datetime, timezone

    _SECRET_LAST_USED[secret_id] = datetime.now(timezone.utc).isoformat()


def _secret_summary(secret: Secret) -> SecretSummary:
    return SecretSummary(
        id=secret.id,
        secret_id=secret.id,
        alias=_SECRET_ALIASES.get(secret.id) or f"{secret.provider} API Key",
        provider=secret.provider,
        created_at=secret.created_at,
        createdAt=secret.created_at,
        lastUsedAt=_SECRET_LAST_USED.get(secret.id),
        status="active",
        maskedPreview="••••••••",
    )
