"""Persistence contract for stored execution artifacts."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from mdi_schemas import Artifact


class ArtifactRepository(Protocol):
    def save(self, artifact: Artifact | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def save_for_execution(
        self,
        artifact: Artifact | Mapping[str, Any],
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        ...

    def get(self, artifact_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


__all__ = ["ArtifactRepository"]
