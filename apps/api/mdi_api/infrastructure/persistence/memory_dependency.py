"""In-memory dependency execution persistence implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from mdi_api.infrastructure.persistence.base import _json_copy
from mdi_api.infrastructure.persistence.planning_records import (
    _normalize_artifact_lineage_record,
    _normalize_binding_resolution_record,
    _normalize_dependency_execution_record,
    _normalize_plan_bindings,
)

if TYPE_CHECKING:
    from mdi_schemas import ArtifactLineageRecord, DependencyBinding, DependencyExecutionRecord
    from mdi_api.infrastructure.persistence.memory_analysis_plans import InMemoryAnalysisPlanRepository

class InMemoryDependencyExecutionRepository:
    def __init__(self, plans: "InMemoryAnalysisPlanRepository") -> None:
        self.plans = plans
        self.plan_bindings: dict[str, dict[str, dict[str, Any]]] = {}
        self.binding_resolutions: dict[tuple[str, str], dict[str, Any]] = {}
        self.executions: dict[str, dict[str, Any]] = {}
        self.lineage: dict[str, dict[str, Any]] = {}

    def save_plan_bindings(
        self, plan_id: str, plan_hash: str, graph_hash: str, bindings: list[DependencyBinding | Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        normalized = _normalize_plan_bindings(self.plans.get_plan(plan_id), plan_id, plan_hash, graph_hash, bindings)
        requested = {item["bindingId"]: item for item in normalized}
        existing = self.plan_bindings.get(plan_id)
        if existing is not None and existing != requested:
            raise ValueError("Planned dependency binding records are immutable")
        self.plan_bindings.setdefault(plan_id, requested)
        return self.list_plan_bindings(plan_id)

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        return [_json_copy(item) for _, item in sorted(self.plan_bindings.get(plan_id, {}).items())]

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_binding_resolution_record(record)
        key = (normalized["jobId"], normalized["bindingId"])
        existing = self.binding_resolutions.get(key)
        if existing is not None and existing["recordHash"] != normalized["recordHash"]:
            raise ValueError("Runtime artifact binding resolution records are immutable")
        self.binding_resolutions.setdefault(key, normalized)
        return _json_copy(self.binding_resolutions[key])

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        return [
            _json_copy(item)
            for key, item in sorted(self.binding_resolutions.items())
            if key[0] == job_id
        ]

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_dependency_execution_record(record)
        existing = self.executions.get(normalized["jobId"])
        if existing is not None and existing["executionHash"] != normalized["executionHash"]:
            raise ValueError("Dependency execution records are immutable")
        self.executions.setdefault(normalized["jobId"], normalized)
        return _json_copy(self.executions[normalized["jobId"]])

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = self.executions.get(job_id)
        return _json_copy(value) if value is not None else None

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_artifact_lineage_record(record)
        existing = self.lineage.get(normalized["artifactId"])
        if existing is not None and existing["lineageHash"] != normalized["lineageHash"]:
            raise ValueError("Artifact lineage records are immutable")
        self.lineage.setdefault(normalized["artifactId"], normalized)
        return _json_copy(self.lineage[normalized["artifactId"]])

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(item) for _, item in sorted(self.lineage.items()) if item["jobId"] == job_id]

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        value = self.lineage.get(artifact_id)
        return _json_copy(value) if value is not None else None

__all__ = ["InMemoryDependencyExecutionRepository"]
