"""In-memory recipe and report persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_schemas import VisualizationRecipe

from mdi_api.infrastructure.persistence.base import (
    _InMemoryRecordRepository,
    _json_copy,
    _model_to_record,
    _required_id,
)

class InMemoryRecipeRepository(_InMemoryRecordRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        return self._save(record, record_id=_required_id(record, "recipeId"))

    def create_immutable(self, recipe: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(recipe)
        recipe_id = _required_id(record, "recipeId")
        with self._record_lock:
            existing = self.records.get(recipe_id)
            if existing is not None:
                _assert_immutable_delivery_compatible(existing, record, kind="Recipe")
                return _json_copy(existing)
            return self._save(record, record_id=recipe_id)

    def get(self, recipe_id: str) -> dict[str, Any]:
        return self._get(recipe_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("sourceJobId") == job_id]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

class InMemoryReportRepository(_InMemoryRecordRepository):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        return self._save(report, record_id=_required_id(report, "reportId"))

    def create_immutable(self, report: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(report)
        report_id = _required_id(record, "reportId")
        with self._record_lock:
            existing = self.records.get(report_id)
            if existing is not None:
                _assert_immutable_delivery_compatible(existing, record, kind="Report")
                return _json_copy(existing)
            return self._save(record, record_id=report_id)

    def get(self, report_id: str) -> dict[str, Any]:
        return self._get(report_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(record)
            for record in self.records.values()
            if record.get("jobId") == job_id or record.get("sourceJobId") == job_id
        ]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

def _assert_immutable_delivery_compatible(
    existing: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    kind: str,
) -> None:
    identity_fields = (
        "requestHash",
        "compositionHash",
        "reportId",
        "recipeId",
        "projectId",
        "sourceJobId",
        "workspaceId",
    )
    if any(existing.get(field) != candidate.get(field) for field in identity_fields):
        raise ValueError(f"{kind} immutable snapshot conflict")

__all__ = ["InMemoryRecipeRepository", "InMemoryReportRepository"]
