"""In-memory planning persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from mdi_api.infrastructure.persistence.base import _InMemoryRecordRepository, _json_copy, _utc_now
from mdi_api.infrastructure.persistence.planning import (
    analysis_intent_from_record,
    normalize_analysis_intent_record,
    normalize_capability_decision_record,
    normalize_capability_resolution_record,
)


class InMemoryAnalysisIntentRepository(_InMemoryRecordRepository):
    def __init__(self) -> None:
        super().__init__()
        self.executions: dict[tuple[str, str, str], dict[str, Any]] = {}

    def save_intent(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_analysis_intent_record(record)
        intent_id = str(normalized["intentId"])
        existing = self.records.get(intent_id)
        if existing is not None:
            if existing.get("intentHash") != normalized.get("intentHash"):
                raise ValueError("AnalysisIntent records are immutable")
            return analysis_intent_from_record(existing)
        return analysis_intent_from_record(self._save(normalized, record_id=intent_id))

    def get_intent(self, intent_id: str) -> dict[str, Any]:
        return analysis_intent_from_record(self._get(intent_id))

    def attach_execution(self, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        self.get_intent(intent_id)
        key = (intent_id, plan_id, job_id)
        binding = {
            "id": f"intent_exec_{intent_id.removeprefix('intent_')[:12]}_{plan_id.removeprefix('plan_')[:12]}_{job_id.removeprefix('job_')[:12]}",
            "intentId": intent_id,
            "planId": plan_id,
            "jobId": job_id,
            "createdAt": _utc_now(),
        }
        self.executions.setdefault(key, binding)
        return _json_copy(self.executions[key])

    def get_execution(self, intent_id: str) -> dict[str, Any] | None:
        value = next((item for item in self.executions.values() if item["intentId"] == intent_id), None)
        return _json_copy(value) if value is not None else None

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = next((item for item in self.executions.values() if item["jobId"] == job_id), None)
        return _json_copy(value) if value is not None else None


class InMemoryCapabilityPlanningRepository:
    def __init__(self) -> None:
        self.resolutions: dict[str, dict[str, Any]] = {}
        self.decisions: dict[str, dict[str, Any]] = {}
        self.executions: dict[tuple[str, str, str], dict[str, Any]] = {}

    def save_resolution(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_capability_resolution_record(record)
        resolution_id = normalized["resolutionId"]
        existing = self.resolutions.get(resolution_id)
        if existing is not None and existing["resolutionHash"] != normalized["resolutionHash"]:
            raise ValueError("Eligibility Resolution records are immutable")
        self.resolutions.setdefault(resolution_id, normalized)
        return _json_copy(self.resolutions[resolution_id])

    def get_resolution(self, resolution_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.resolutions[resolution_id])
        except KeyError as exc:
            raise LookupError(f"Unknown Eligibility Resolution: {resolution_id}") from exc

    def save_decision(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = normalize_capability_decision_record(record)
        self.get_resolution(normalized["resolutionId"])
        decision_id = normalized["decisionId"]
        existing = self.decisions.get(decision_id)
        if existing is not None and existing["decisionHash"] != normalized["decisionHash"]:
            raise ValueError("Capability Planning Decision records are immutable")
        self.decisions.setdefault(decision_id, normalized)
        return _json_copy(self.decisions[decision_id])

    def get_decision(self, decision_id: str) -> dict[str, Any]:
        try:
            return _json_copy(self.decisions[decision_id])
        except KeyError as exc:
            raise LookupError(f"Unknown Capability Planning Decision: {decision_id}") from exc

    def attach_execution(self, decision_id: str, intent_id: str, plan_id: str, job_id: str) -> dict[str, Any]:
        decision = self.get_decision(decision_id)
        if decision["intentId"] != intent_id or decision["outcome"] != "PLAN_READY":
            raise ValueError("Only a matching PLAN_READY decision can be attached to execution")
        binding = {
            "id": f"cap_exec_{decision_id.removeprefix('decision_')[:12]}_{plan_id.removeprefix('plan_')[:12]}_{job_id.removeprefix('job_')[:12]}",
            "decisionId": decision_id,
            "intentId": intent_id,
            "planId": plan_id,
            "jobId": job_id,
            "createdAt": _utc_now(),
        }
        key = (decision_id, plan_id, job_id)
        self.executions.setdefault(key, binding)
        return _json_copy(self.executions[key])

    def get_execution_for_job(self, job_id: str) -> dict[str, Any] | None:
        value = next((item for item in self.executions.values() if item["jobId"] == job_id), None)
        return _json_copy(value) if value is not None else None


__all__ = ["InMemoryAnalysisIntentRepository", "InMemoryCapabilityPlanningRepository"]
