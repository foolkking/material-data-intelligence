"""Persistence contracts for execution jobs and their audit records."""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence

from mdi_schemas import JobEvent, JobEventStatus, JobStatus, ToolCall
from mdi_api.application.jobs.leases import ExecutionLease


class JobRepository(Protocol):
    def create(self, job: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def save(self, job: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, job_id: str) -> dict[str, Any]:
        ...

    def set_status(self, job_id: str, status: JobStatus | str) -> dict[str, Any]:
        ...

    def claim_execution(
        self, job_id: str, *, owner: str, lease_seconds: int
    ) -> ExecutionLease | None:
        ...

    def renew_execution(
        self, job_id: str, *, owner: str, attempt: int, lease_seconds: int
    ) -> ExecutionLease:
        ...

    def assert_current_execution(
        self, job_id: str, *, owner: str, attempt: int
    ) -> dict[str, Any]:
        ...

    def set_status_for_execution(
        self,
        job_id: str,
        status: JobStatus | str,
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        ...

    def request_cancel(self, job_id: str) -> dict[str, Any]:
        ...

    def expire_abandoned_execution(
        self, job_id: str, *, stale_after_seconds: int, cancel_requested: bool = False
    ) -> dict[str, Any] | None:
        ...

    def acknowledge_cancel(
        self, job_id: str, *, owner: str | None = None, attempt: int | None = None
    ) -> dict[str, Any]:
        ...

    def lifecycle_projection(self, job_id: str) -> dict[str, Any]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...

    def list_task_feed_projection(self, job_ids: Sequence[str]) -> list[dict[str, Any]]:
        ...


class JobEventRepository(Protocol):
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
        ...

    def list_for_job(self, job_id: str) -> list[JobEvent]:
        ...

    def list_events_after_seq(self, job_id: str, after_seq: int) -> list[JobEvent]:
        ...


class ToolCallRepository(Protocol):
    def save(self, tool_call: ToolCall | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def save_for_execution(
        self,
        tool_call: ToolCall | Mapping[str, Any],
        *,
        owner: str,
        attempt: int,
    ) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...


__all__ = ["JobEventRepository", "JobRepository", "ToolCallRepository"]
