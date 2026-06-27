"""Secret / BYOK data models for Phase 7."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Secret:
    id: str
    scope_type: str  # "user"
    scope_id: str
    provider: str    # "openai", "deepseek", "custom_openai_compatible"
    encrypted_ref: str  # in production: ciphertext; in memory: stored separately
    created_at: str


@dataclass
class SecretData:
    """Full secret including plaintext value — never exposed via API."""
    id: str
    value: str
    provider: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
