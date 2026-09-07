from __future__ import annotations

from typing import Protocol, TypeVar


T = TypeVar("T")


class QueuedJobRuntimePort(Protocol[T]):
    def handle_job(self, job_id: str) -> T: ...

    def notify_job_progress(self, job_id: str) -> None: ...


def execute_queued_job(
    job_id: str,
    *,
    runtime: QueuedJobRuntimePort[T],
) -> T:
    """Execute one persisted Job and then publish committed progress."""

    result = runtime.handle_job(job_id)
    runtime.notify_job_progress(job_id)
    return result


__all__ = ["QueuedJobRuntimePort", "execute_queued_job"]
