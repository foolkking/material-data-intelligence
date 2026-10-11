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
    def enqueue_generation(self, generation_id: UUID, *, attempt: int = 1) -> ReportQueueSubmitResult:
        return ReportQueueSubmitResult(generation_id, False, "disabled", "report queue is disabled")


class InMemoryReportQueue:
    def __init__(self) -> None:
        self._items: list[tuple[UUID, int]] = []
        self._known: set[tuple[UUID, int]] = set()

    def enqueue_generation(self, generation_id: UUID, *, attempt: int = 1) -> ReportQueueSubmitResult:
        key = (generation_id, attempt)
        if key in self._known:
            return ReportQueueSubmitResult(generation_id, False, "memory", "report generation already queued")
        self._known.add(key)
        self._items.append(key)
        return ReportQueueSubmitResult(generation_id, True, "memory", "report generation queued")

    def pop_next(self) -> UUID | None:
        if not self._items:
            return None
        key = self._items.pop(0)
        self._known.discard(key)
        return key[0]


class RedisRQReportQueue:
    def __init__(
        self,
        *,
        redis_url: str,
        queue_name: str = worker_queue_definition("report").default_name,
    ) -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_generation(self, generation_id: UUID, *, attempt: int = 1) -> ReportQueueSubmitResult:
        from redis import Redis
        from redis.backoff import NoBackoff
        from redis.exceptions import WatchError
        from redis.retry import Retry
        from rq import Queue
        from rq.exceptions import NoSuchJobError
        from rq.job import Job

        if attempt < 1:
            raise ValueError("Report attempt must be positive")
        connection = Redis.from_url(
            self.redis_url, socket_connect_timeout=2, socket_timeout=2,
            retry=Retry(NoBackoff(), 0),
        )
        queue = Queue(self.queue_name, connection=connection)
        job_id = f"agent2-report-{generation_id}-{attempt}"
        try:
            for _ in range(4):
                try:
                    with connection.pipeline() as pipeline:
                        pipeline.watch(Job.key_for(job_id))
                        try:
                            existing = Job.fetch(job_id, connection=connection)
                        except NoSuchJobError:
                            existing = None
                        if existing is not None:
                            if existing.origin != self.queue_name:
                                raise RuntimeError("Report queue ownership does not match")
                            status = existing.get_status(refresh=False)
                            value = str(getattr(status, "value", status))
                            if value in {"queued", "started", "deferred", "scheduled"}:
                                return ReportQueueSubmitResult(generation_id, False, "rq", "report generation already queued")
                            if value not in {"finished", "failed", "stopped", "canceled", "cancelled"}:
                                raise RuntimeError("Report queue status cannot be confirmed")
                        pipeline.multi()
                        if existing is not None:
                            existing.delete(pipeline=pipeline)
                        queue.enqueue(
                            worker_queue_definition("report").handler, str(generation_id),
                            expected_attempt=attempt, job_id=job_id, pipeline=pipeline,
                            # Two bounded 120-second calls plus persistence overhead.
                            job_timeout=300,
                        )
                        pipeline.execute()
                    return ReportQueueSubmitResult(generation_id, True, "rq", "report generation queued")
                except WatchError:
                    continue
            raise RuntimeError("Report queue publication changed concurrently")
        finally:
            connection.close()


__all__ = ["DisabledReportQueue", "InMemoryReportQueue", "RedisRQReportQueue", "ReportQueueSubmitResult"]
