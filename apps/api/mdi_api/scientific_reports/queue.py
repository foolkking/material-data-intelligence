from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mdi_schemas.worker_queues import worker_queue_definition


@dataclass(frozen=True)
class ReportQueueSubmitResult:
    generation_id: UUID
    enqueued: bool
    backend: str
    message: str


class DisabledReportQueue:
    def enqueue_generation(self, generation_id: UUID) -> ReportQueueSubmitResult:
        return ReportQueueSubmitResult(generation_id, False, "disabled", "report queue is disabled")


class InMemoryReportQueue:
    def __init__(self) -> None:
        self._items: list[UUID] = []
        self._known: set[UUID] = set()

    def enqueue_generation(self, generation_id: UUID) -> ReportQueueSubmitResult:
        if generation_id in self._known:
            return ReportQueueSubmitResult(generation_id, False, "memory", "report generation already queued")
        self._known.add(generation_id)
        self._items.append(generation_id)
        return ReportQueueSubmitResult(generation_id, True, "memory", "report generation queued")

    def pop_next(self) -> UUID | None:
        return self._items.pop(0) if self._items else None


class RedisRQReportQueue:
    def __init__(
        self,
        *,
        redis_url: str,
        queue_name: str = worker_queue_definition("report").default_name,
    ) -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_generation(self, generation_id: UUID) -> ReportQueueSubmitResult:
        from redis import Redis
        from rq import Queue

        queue = Queue(self.queue_name, connection=Redis.from_url(self.redis_url))
        job_id = f"agent2-report-{generation_id}"
        existing = queue.fetch_job(job_id)
        if existing is not None:
            status = str(getattr(existing.get_status(refresh=True), "value", existing.get_status(refresh=True)))
            if status in {"queued", "started", "deferred", "scheduled", "finished"}:
                return ReportQueueSubmitResult(generation_id, False, "rq", "report generation already queued")
            existing.delete()
        queue.enqueue(
            worker_queue_definition("report").handler,
            str(generation_id),
            job_id=job_id,
        )
        return ReportQueueSubmitResult(generation_id, True, "rq", f"report generation queued on {self.queue_name}")


__all__ = ["DisabledReportQueue", "InMemoryReportQueue", "RedisRQReportQueue", "ReportQueueSubmitResult"]
