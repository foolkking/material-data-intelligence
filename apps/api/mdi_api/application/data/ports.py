"""Persistence ports owned by the data capability."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from mdi_schemas import DataProfile


class DatasetRepository(Protocol):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, dataset_id: str) -> dict[str, Any]:
        ...

    def list(self) -> list[dict[str, Any]]:
        ...

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class DataProfileRepository(Protocol):
    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, profile_id: str) -> dict[str, Any]:
        ...

    def list(self) -> list[dict[str, Any]]:
        ...

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


__all__ = ["DatasetRepository", "DataProfileRepository"]

