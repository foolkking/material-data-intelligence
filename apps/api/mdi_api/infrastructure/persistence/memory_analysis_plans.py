"""In-memory AnalysisPlan persistence implementation."""

from __future__ import annotations

from typing import Any, Mapping, TYPE_CHECKING

from mdi_api.infrastructure.persistence.base import _InMemoryRecordRepository, _required_id, _utc_now
from mdi_api.infrastructure.persistence.planning_records import (
    _analysis_plan_from_record,
    _normalize_analysis_plan_record,
)

if TYPE_CHECKING:
    from mdi_api.infrastructure.persistence.memory_jobs import InMemoryJobRepository

class InMemoryAnalysisPlanRepository(_InMemoryRecordRepository):
    def __init__(self, jobs: "InMemoryJobRepository | None" = None) -> None:
        super().__init__()
        self.jobs = jobs

    def save_plan(self, record: Mapping[str, Any]) -> dict[str, Any]:
        normalized = _normalize_analysis_plan_record(record)
        plan_id = _required_id(normalized, "planId")
        existing = self.records.get(plan_id)
        if existing is not None:
            existing_schema = (existing.get("analysisPlan") or {}).get("schemaVersion")
            new_schema = normalized["analysisPlan"].get("schemaVersion")
            if {"0.2", "0.3", "0.4"}.intersection({existing_schema, new_schema}) and existing.get("planHash") != normalized["planHash"]:
                raise ValueError("Dependency AnalysisPlan records are immutable")
        return _analysis_plan_from_record(self._save(normalized, record_id=plan_id))

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return _analysis_plan_from_record(self._get(plan_id))

    def get_plan_for_job(self, job_id: str) -> dict[str, Any]:
        if self.jobs is not None:
            try:
                job = self.jobs.get(job_id)
            except LookupError:
                job = {}
            plan_id = job.get("planId") or job.get("plan_id")
            if plan_id:
                return self.get_plan(str(plan_id))
        for record in self.records.values():
            if record.get("jobId") == job_id or record.get("job_id") == job_id:
                return _analysis_plan_from_record(record)
        raise LookupError(f"Unknown analysis plan for job id: {job_id}")

    def attach_plan_to_job(self, plan_id: str, job_id: str) -> dict[str, Any]:
        record = self._get(plan_id)
        record["jobId"] = job_id
        record["job_id"] = job_id
        record["updatedAt"] = _utc_now()
        self.records[plan_id] = record
        if self.jobs is not None:
            job = self.jobs.get(job_id)
            job["planId"] = plan_id
            job["plan_id"] = plan_id
            job["updatedAt"] = _utc_now()
            self.jobs.records[job_id] = job
        return _analysis_plan_from_record(record)

__all__ = ["InMemoryAnalysisPlanRepository"]
