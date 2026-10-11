from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock, RLock
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
from mdi_api.application.jobs.leases import ExecutionLease, ExecutionLeaseLost

class InMemoryJobRepository(_InMemoryRecordRepository):
    def __init__(self) -> None:
        super().__init__()
        self._lease_lock = RLock()

    def create(self, job: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(job)
        job_id = _required_id(record, "jobId")
        if job_id in self.records:
            return self.get(job_id)
        record["status"] = validate_job_status(record.get("status") or JobStatus.created.value)
        record.setdefault("executionAttempt", 0)
        record.setdefault("executionOwner", None)
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

    def claim_execution(
        self, job_id: str, *, owner: str, lease_seconds: int
    ) -> ExecutionLease | None:
        with self._lease_lock:
            record = self._get(job_id)
            now = datetime.now(timezone.utc)
            expiry = _dt(record.get("leaseExpiresAt"))
            status = str(record.get("status") or "created")
            if status in {"completed", "partial_success", "failed", "cancelled", "cancel_requested"}:
                return None
            if status == "running" and expiry is not None and expiry > now:
                return None
            attempt = int(record.get("executionAttempt") or 0) + 1
            expires = now + timedelta(seconds=lease_seconds)
            reclaimed = status == "running"
            record.update(
                status="running",
                executionOwner=owner,
                executionAttempt=attempt,
                leaseClaimedAt=now.isoformat(),
                leaseRenewedAt=now.isoformat(),
                leaseExpiresAt=expires.isoformat(),
                updatedAt=now.isoformat(),
            )
            self.records[job_id] = record
            return ExecutionLease(
                job_id=job_id,
                owner=owner,
                attempt=attempt,
                claimed_at=now.isoformat(),
                renewed_at=now.isoformat(),
                expires_at=expires.isoformat(),
                reclaimed=reclaimed,
            )

    def renew_execution(
        self,
        job_id: str,
        *,
        owner: str,
        attempt: int,
        lease_seconds: int,
    ) -> ExecutionLease:
        with self._lease_lock:
            record = self._current(job_id, owner=owner, attempt=attempt)
            now = datetime.now(timezone.utc)
            expires = now + timedelta(seconds=lease_seconds)
            record["leaseRenewedAt"] = now.isoformat()
            record["leaseExpiresAt"] = expires.isoformat()
            record["updatedAt"] = now.isoformat()
            self.records[job_id] = record
            return ExecutionLease(
                job_id=job_id,
                owner=owner,
                attempt=attempt,
                claimed_at=str(record["leaseClaimedAt"]),
                renewed_at=now.isoformat(),
                expires_at=expires.isoformat(),
                reclaimed=False,
            )

    def assert_current_execution(
        self, job_id: str, *, owner: str, attempt: int
    ) -> dict[str, Any]:
        with self._lease_lock:
            return _json_copy(self._current(job_id, owner=owner, attempt=attempt))

    def set_status_for_execution(
        self,
        job_id: str,
        status: JobStatus | str,
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        with self._lease_lock:
            record = self._current(job_id, owner=owner, attempt=attempt)
            requested = validate_job_status(status)
            current = str(record["status"])
            if current == "cancel_requested" and requested != "cancelled":
                raise ExecutionLeaseLost("cancellation has precedence")
            record["status"] = validate_job_transition(current, requested)
            now = datetime.now(timezone.utc).isoformat()
            record["updatedAt"] = now
            if record["status"] in {
                "completed",
                "partial_success",
                "failed",
                "cancelled",
            }:
                record["terminalAt"] = now
                record["leaseExpiresAt"] = None
                record["executionOwner"] = None
            if record["status"] == "cancelled":
                record["cancelAcknowledgedAt"] = now
            self.records[job_id] = record
            return _json_copy(record)

    def expire_abandoned_execution(
        self, job_id: str, *, stale_after_seconds: int, cancel_requested: bool = False
    ) -> dict[str, Any] | None:
        if stale_after_seconds < 1:
            raise ValueError("stale_after_seconds must be positive")
        with self._lease_lock:
            record = self._get(job_id)
            now = datetime.now(timezone.utc)
            expiry = _dt(record.get("leaseExpiresAt"))
            updated = _dt(record.get("updatedAt"))
            if (
                record["status"] not in {"created", "queued", "running", "cancel_requested"}
                or updated is None or updated > now - timedelta(seconds=stale_after_seconds)
                or (expiry is not None and expiry > now)
            ):
                return None
            cancelled = cancel_requested or record["status"] == "cancel_requested"
            record.update(
                status="cancelled" if cancelled else "failed", executionOwner=None,
                leaseExpiresAt=None, terminalAt=now.isoformat(), updatedAt=now.isoformat(),
            )
            if cancelled:
                record["cancelRequestedAt"] = record.get("cancelRequestedAt") or now.isoformat()
                record["cancelAcknowledgedAt"] = now.isoformat()
            self.records[job_id] = record
            return _json_copy(record)

    def request_cancel(self, job_id: str) -> dict[str, Any]:
        with self._lease_lock:
            record = self._get(job_id)
            status = str(record["status"])
            if status in {"completed", "partial_success", "failed", "cancelled"}:
                return record
            record["status"] = validate_job_transition(status, "cancel_requested")
            record.setdefault("cancelRequestedAt", datetime.now(timezone.utc).isoformat())
            self.records[job_id] = record
            return _json_copy(record)

    def acknowledge_cancel(
        self, job_id: str, *, owner: str | None = None, attempt: int | None = None
    ) -> dict[str, Any]:
        if owner is not None and attempt is not None:
            return self.set_status_for_execution(
                job_id, "cancelled", owner=owner, attempt=attempt
            )
        with self._lease_lock:
            record = self._get(job_id)
            if str(record["status"]) == "cancel_requested" and not record.get(
                "executionOwner"
            ):
                now = datetime.now(timezone.utc).isoformat()
                record.update(
                    status="cancelled",
                    cancelAcknowledgedAt=now,
                    terminalAt=now,
                    updatedAt=now,
                )
                self.records[job_id] = record
            return _json_copy(record)

    def lifecycle_projection(self, job_id: str) -> dict[str, Any]:
        record = self._get(job_id)
        expiry = _dt(record.get("leaseExpiresAt"))
        now = datetime.now(timezone.utc)
        status = str(record["status"])
        return {
            "executionState": status,
            "attempt": int(record.get("executionAttempt") or 0),
            "ownerPresent": bool(record.get("executionOwner")),
            "leaseStatus": (
                "EXPIRED"
                if status == "running" and expiry and expiry <= now
                else "ACTIVE"
                if status == "running" and expiry
                else "NOT_APPLICABLE"
            ),
            "leaseExpiresAt": record.get("leaseExpiresAt"),
            "cancelRequested": status == "cancel_requested"
            or bool(record.get("cancelRequestedAt")),
            "cancelRequestedAt": record.get("cancelRequestedAt"),
            "cancelAcknowledgedAt": record.get("cancelAcknowledgedAt"),
            "terminalAt": record.get("terminalAt"),
            "authority": "IN_MEMORY_JOB_ROW",
            "readOnly": True,
        }

    def _current(
        self, job_id: str, *, owner: str, attempt: int
    ) -> dict[str, Any]:
        record = self._get(job_id)
        expiry = _dt(record.get("leaseExpiresAt"))
        now = datetime.now(timezone.utc)
        if (
            str(record.get("executionOwner") or "") != owner
            or int(record.get("executionAttempt") or 0) != attempt
            or expiry is None
            or expiry <= now
            or str(record.get("status")) not in {"running", "cancel_requested"}
        ):
            raise ExecutionLeaseLost(
                f"execution lease is no longer current for {job_id} attempt {attempt}"
            )
        return record

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

    def save_for_execution(
        self,
        tool_call: ToolCall | Mapping[str, Any],
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        record = _model_to_record(tool_call)
        record["attempt"] = attempt
        existing_id = self._find_existing_id(_required_id(record), record)
        if existing_id:
            current = self.records[existing_id]
            current_attempt = int(current.get("attempt") or 1)
            if current_attempt > attempt:
                raise ExecutionLeaseLost("stale ToolCall attempt rejected")
            if current_attempt < attempt:
                record["id"] = existing_id
                self.records[existing_id] = {**_json_copy(current), **_json_copy(record)}
                return _json_copy(self.records[existing_id])
        return self.save(record)

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


def _dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
