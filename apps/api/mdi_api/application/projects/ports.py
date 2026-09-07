"""Persistence ports owned by the project capability."""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class ProjectRepository(Protocol):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, project_id: str) -> dict[str, Any]:
        ...

    def list(self) -> list[dict[str, Any]]:
        ...


__all__ = ["ProjectRepository"]

