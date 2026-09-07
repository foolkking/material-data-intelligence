from __future__ import annotations

from threading import Lock
from typing import Any, Mapping

from mdi_schemas import JobEvent, JobEventStatus, JobStatus, ToolCall
from mdi_api.infrastructure.persistence.base import (
    _InMemoryRecordRepository,
    _enum_value,
    _json_copy,
    _model_to_record,
    _required_id,
    _utc_now,
)
from mdi_api.state_machine import (
    validate_job_transition,
    validate_job_status,
    validate_tool_call_status,
    validate_tool_call_transition,
)

class InMemoryJobRepository(_InMemoryRecordRepository):
    def create(self, job: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(job)
        job_id = _required_id(record, "jobId")
        if job_id in self.records:
            return self.get(job_id)
        record["status"] = validate_job_status(record.get("status") or JobStatus.created.value)
        return self._save(record, record_id=job_id)

    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(job)
        record["status"] = validate_job_status(record.get("status") or JobStatus.created.value)
        return self._save(record, record_id=_required_id(record, "jobId"))

    def get(self, job_id: str) -> dict[str, Any]:
        return self._get(job_id)

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        record = self._get(job_id)
        record["status"] = validate_job_transition(record.get("status") or JobStatus.created.value, status)
        record["updatedAt"] = _utc_now()
        self.records[job_id] = record
        return _json_copy(record)

    def update_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        return self.set_status(job_id, status)

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("projectId") == project_id]

class InMemoryJobEventRepository:
    def __init__(self) -> None:
        self.events_by_job: dict[str, list[JobEvent]] = {}
        self._lock = Lock()

    def append_event(
        self,
        job_id: str,
        *,
        event_type: str,
        status: JobEventStatus | str,
        message: str,
        payload: Mapping[str, Any] | None = None,
        progress: float | None = None,
    ) -> JobEvent:
        with self._lock:
            events = self.events_by_job.setdefault(job_id, [])
            seq = len(events) + 1
            event = JobEvent(
                id=f"evt_{job_id}_{seq:04d}",
                jobId=job_id,
                seq=seq,
                eventType=event_type,
                status=JobEventStatus(_enum_value(status)),
                message=message,
                progress=progress,
                payload=dict(payload or {}),
                createdAt=_utc_now(),
            )
            events.append(event)
            return event

    def save_event(self, event: JobEvent) -> JobEvent:
        with self._lock:
            events = self.events_by_job.setdefault(event.jobId, [])
            if any(existing.seq == event.seq for existing in events):
                raise ValueError(f"Duplicate job event seq {event.seq} for job {event.jobId}")
            if events and event.seq <= events[-1].seq:
                raise ValueError(f"Job event seq must increase for job {event.jobId}")
            events.append(event)
            return event

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        return list(self.events_by_job.get(job_id, []))

    def list_events(self, job_id: str) -> list[JobEvent]:
        return self.list_for_job(job_id)

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        return [event for event in self.events_by_job.get(job_id, []) if event.seq > after_seq]

class InMemoryToolCallRepository(_InMemoryRecordRepository):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        record_id = _required_id(record)
        record["status"] = validate_tool_call_status(record.get("status") or "planned")
        record["attempt"] = int(record.get("attempt") or 1)
        record["idempotencyKey"] = str(record.get("idempotencyKey") or record.get("idempotency_key") or f"{record['jobId']}:{record['stepId']}")
        existing_id = self._find_existing_id(record_id, record)
        if existing_id:
            current = self.records[existing_id]
            record["id"] = existing_id
            record["status"] = validate_tool_call_transition(current.get("status") or "planned", record["status"])
            record["attempt"] = max(int(current.get("attempt") or 1), record["attempt"])
            self.records[existing_id] = {**_json_copy(current), **_json_copy(record)}
            return _json_copy(self.records[existing_id])
        return self._save(record, record_id=record_id)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        return [_json_copy(record) for record in self.records.values() if record.get("jobId") == job_id]

    def list_by_job(self, job_id: str) -> list[dict[str, Any]]:
        return self.list_for_job(job_id)

    def _find_existing_id(self, record_id: str, record: Mapping[str, Any]) -> str | None:
        if record_id in self.records:
            return record_id
        for existing_id, existing in self.records.items():
            if existing.get("jobId") == record.get("jobId") and existing.get("stepId") == record.get("stepId"):
                return existing_id
            if (
                existing.get("jobId") == record.get("jobId")
                and existing.get("idempotencyKey")
                and existing.get("idempotencyKey") == record.get("idempotencyKey")
            ):
                return existing_id
        return None

__all__ = ["InMemoryJobEventRepository", "InMemoryJobRepository", "InMemoryToolCallRepository"]
