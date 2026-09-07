"""Persistence contracts for research planning records."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from mdi_schemas import ArtifactLineageRecord, DependencyBinding, DependencyExecutionRecord


class AnalysisIntentRepository(Protocol):
    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        ...

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        ...

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...


class CapabilityPlanningRepository(Protocol):
    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        ...

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        ...

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...


class AnalysisPlanRepository(Protocol):
    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        ...

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        ...

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        ...


class DependencyExecutionRepository(Protocol):
    def save_plan_bindings(
        self,
        plan_id: str,
        plan_hash: str,
        graph_hash: str,
        bindings: list[DependencyBinding | Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        ...

    def list_plan_bindings(self, plan_id: str) -> list[dict[str, Any]]:
        ...

    def save_binding_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_binding_resolutions(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def save_execution(self, record: DependencyExecutionRecord | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        ...

    def save_lineage(self, record: ArtifactLineageRecord | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def list_lineage_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def get_lineage_for_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        ...


__all__ = ["AnalysisIntentRepository", "CapabilityPlanningRepository", "AnalysisPlanRepository", "DependencyExecutionRepository"]
