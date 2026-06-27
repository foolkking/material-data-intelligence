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


@dataclass
class SecretSummary:
    id: str
    provider: str
    created_at: str


_store = InMemorySecretStore()
_CURRENT_USER_ID = "user_local"


def create_secret(request: CreateSecretRequest) -> SecretSummary:
    sec = _store.create_secret(scope_id=_CURRENT_USER_ID, provider=request.provider, value=request.value)
    return SecretSummary(id=sec.id, provider=sec.provider, created_at=sec.created_at)


def list_secrets() -> list[SecretSummary]:
    return [
        SecretSummary(id=s.id, provider=s.provider, created_at=s.created_at)
        for s in _store.list_secrets(scope_id=_CURRENT_USER_ID)
    ]


def delete_secret(secret_id: str) -> bool:
    return _store.delete_secret(secret_id)


def get_secret_value(secret_id: str) -> str | None:
    sd = _store.get_secret(secret_id)
    return sd.value if sd else None
