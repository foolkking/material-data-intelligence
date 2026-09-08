from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkspaceDomainError(Exception):
    code: str
    message: str
    status_code: int = 400
    retryable: bool = False

    def as_detail(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }


@dataclass(frozen=True)
class WorkspaceSnapshot:
    body: dict[str, Any]
    etag: str


__all__ = ["WorkspaceDomainError", "WorkspaceSnapshot"]
