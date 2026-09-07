"""In-memory Project/Data persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_schemas import DataProfile

from mdi_api.infrastructure.persistence.base import (
    _InMemoryRecordRepository,
    _json_copy,
    _model_to_record,
    _required_id,
)


class InMemoryProjectRepository(_InMemoryRecordRepository):
    def save(self, project: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(project, record_id=_required_id(project, "projectId"))

    def get(self, project_id: str) -> dict[str, Any]:
        return self._get(project_id)

    def list(self) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values()]


class InMemoryDatasetRepository(_InMemoryRecordRepository):
    def save(self, dataset: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(dataset, record_id=_required_id(dataset, "datasetId"))

    def get(self, dataset_id: str) -> dict[str, Any]:
        return self._get(dataset_id)

    def list(self) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values()]

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return self.list_for_project(project_id)


class InMemoryDataProfileRepository(_InMemoryRecordRepository):
    def __init__(self, datasets: InMemoryDatasetRepository | None = None) -> None:
        super().__init__()
        self.datasets = datasets

    def save(self, profile: DataProfile | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(profile)
        return self._save(record, record_id=_required_id(record, "profileId"))

    def get(self, profile_id: str) -> dict[str, Any]:
        return self._get(profile_id)

    def list(self) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values()]

    def list_for_dataset(self, dataset_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("datasetId") == dataset_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        if self.datasets is None:
            return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]
        dataset_ids = {
            record.get("datasetId") or record.get("id")
            for record in self.datasets.list_for_project(project_id)
            if record.get("datasetId") or record.get("id")
        }
        return [_json_copy(record) for record in self.records.values() if record.get("datasetId") in dataset_ids]


__all__ = [
    "InMemoryDataProfileRepository",
    "InMemoryDatasetRepository",
    "InMemoryProjectRepository",
]
