"""Secrets API routes — POST/GET/DELETE /me/secrets."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from mdi_api.config import ApiSettings, load_settings
from mdi_api.transport.routers.auth import CurrentUser, get_current_user_compat
from mdi_api.secrets import InMemorySecretStore, Secret


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


_store: InMemorySecretStore | None = None
_SECRET_ALIASES: dict[str, str] = {}
_SECRET_LAST_USED: dict[str, str] = {}


def _legacy_secret_api_available(settings: ApiSettings) -> bool:
    environment = settings.environment.strip().lower()
    return (
        settings.runtime_profile == "local"
        and environment in {"local", "development", "dev", "test", "testing", "ci"}
    )


def _legacy_secret_store() -> InMemorySecretStore:
    settings = load_settings()
    if not _legacy_secret_api_available(settings):
        raise HTTPException(
            status_code=503,
            detail={
                "code": "LEGACY_USER_SECRET_API_UNAVAILABLE",
                "feature": "legacy_user_secrets",
                "message": (
                    "Legacy in-memory user secret storage is unavailable in "
                    "this runtime."
                ),
            },
        )
    global _store
    if _store is None:
        _store = InMemorySecretStore()
    return _store


def create_secret(request: CreateSecretRequest, current_user: CurrentUser = Depends(get_current_user_compat)) -> SecretSummary:
    store = _legacy_secret_store()
    sec = store.create_secret(
        scope_id=current_user.id,
        provider=request.provider,
        value=request.value,
    )
    _SECRET_ALIASES[sec.id] = request.alias or f"{request.provider} API Key"
    return _secret_summary(sec)


def list_secrets(current_user: CurrentUser = Depends(get_current_user_compat)) -> list[SecretSummary]:
    store = _legacy_secret_store()
    return [
        _secret_summary(secret)
        for secret in store.list_secrets(scope_id=current_user.id)
    ]


def delete_secret(secret_id: str, current_user: CurrentUser = Depends(get_current_user_compat)) -> bool:
    # Scope the mutation before removing presentation metadata. A caller must
    # never be able to delete another user's secret by guessing its id.
    store = _legacy_secret_store()
    if not store.delete_secret(secret_id, scope_id=current_user.id):
        return False
    _SECRET_ALIASES.pop(secret_id, None)
    _SECRET_LAST_USED.pop(secret_id, None)
    return True


def get_secret_value(secret_id: str, *, scope_id: str) -> str | None:
    store = _legacy_secret_store()
    sd = store.get_secret(secret_id, scope_id=scope_id)
    return sd.value if sd else None


def mark_secret_used(secret_id: str, *, scope_id: str) -> bool:
    from datetime import datetime, timezone

    store = _legacy_secret_store()
    if store.get_secret(secret_id, scope_id=scope_id) is None:
        return False
    _SECRET_LAST_USED[secret_id] = datetime.now(timezone.utc).isoformat()
    return True


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
