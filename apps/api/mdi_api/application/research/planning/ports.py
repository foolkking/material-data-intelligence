"""Persistence contracts for research planning records."""

from __future__ import annotations

from typing import Any, Mapping, Protocol


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


__all__ = ["AnalysisIntentRepository", "CapabilityPlanningRepository"]
