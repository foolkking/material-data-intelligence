"""SecretStore abstraction + implementations.

- SecretStore (protocol): create / get_by_id / list / delete
- InMemorySecretStore: stores secrets in a dict; returns only metadata
  in list calls (never plaintext values)
- EncryptedSecretStore: placeholder for production envelope encryption
"""

from __future__ import annotations

from typing import Protocol

from .models import Secret, SecretData


class SecretStore(Protocol):
    def create_secret(self, scope_id: str, provider: str, value: str) -> Secret:
        ...

    def get_secret(self, secret_id: str, scope_id: str) -> SecretData | None:
        ...

    def list_secrets(self, scope_id: str) -> list[Secret]:
        ...

    def delete_secret(self, secret_id: str, scope_id: str) -> bool:
        ...


class InMemorySecretStore:
    """Stores secrets in-memory for dev/test.  Never returns plaintext in list."""

    def __init__(self) -> None:
        self._secrets: dict[str, SecretData] = {}
        self._scopes: dict[str, str] = {}
        self._next_id = 1

    def create_secret(self, scope_id: str, provider: str, value: str) -> Secret:
        secret_id = f"secret_{self._next_id:04d}"
        self._next_id += 1
        data = SecretData(id=secret_id, value=value, provider=provider)
        self._secrets[secret_id] = data
        self._scopes[secret_id] = scope_id
        return Secret(
            id=secret_id,
            scope_type="user",
            scope_id=scope_id,
            provider=provider,
            encrypted_ref=f"memref://{secret_id}",
            created_at=data.created_at,
        )

    def get_secret(self, secret_id: str, scope_id: str) -> SecretData | None:
        if self._scopes.get(secret_id) != scope_id:
            return None
        return self._secrets.get(secret_id)

    def list_secrets(self, scope_id: str) -> list[Secret]:
        return [
            Secret(
                id=d.id,
                scope_type="user",
                scope_id=scope_id,
                provider=d.provider,
                encrypted_ref=f"memref://{d.id}",
                created_at=d.created_at,
            )
            for d in self._secrets.values()
            if self._scopes.get(d.id) == scope_id
        ]

    def delete_secret(self, secret_id: str, scope_id: str) -> bool:
        if secret_id in self._secrets and self._scopes.get(secret_id) == scope_id:
            del self._secrets[secret_id]
            self._scopes.pop(secret_id, None)
            return True
        return False


class EncryptedSecretStore:
    """Placeholder for production envelope encryption.

    Currently raises NotImplementedError — real encryption requires
    a KMS or key-management infrastructure.  Recorded in OPEN_QUESTIONS.
    """

    def create_secret(self, scope_id: str, provider: str, value: str) -> Secret:
        raise NotImplementedError("EncryptedSecretStore is a placeholder.  Use InMemorySecretStore for tests.")

    def get_secret(self, secret_id: str, scope_id: str) -> SecretData | None:
        raise NotImplementedError("EncryptedSecretStore is a placeholder.  Use InMemorySecretStore for tests.")

    def list_secrets(self, scope_id: str) -> list[Secret]:
        raise NotImplementedError("EncryptedSecretStore is a placeholder.  Use InMemorySecretStore for tests.")

    def delete_secret(self, secret_id: str, scope_id: str) -> bool:
        raise NotImplementedError("EncryptedSecretStore is a placeholder.  Use InMemorySecretStore for tests.")
