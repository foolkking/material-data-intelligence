from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from mdi_schemas.worker_queues import worker_queue_definition


@dataclass(frozen=True)
class ResultProjectionQueueSubmitResult:
    turn_id: UUID
    enqueued: bool
    backend: str
    message: str


class ResultProjectionQueue(Protocol):
    def enqueue_turn(self, turn_id: UUID) -> ResultProjectionQueueSubmitResult: ...


class DisabledResultProjectionQueue:
    def enqueue_turn(self, turn_id: UUID) -> ResultProjectionQueueSubmitResult:
        return ResultProjectionQueueSubmitResult(turn_id, False, "disabled", "result projection queue is disabled")


class InMemoryResultProjectionQueue:
    def __init__(self) -> None:
        self._items: list[UUID] = []
        self._known: set[UUID] = set()

    def enqueue_turn(self, turn_id: UUID) -> ResultProjectionQueueSubmitResult:
        if turn_id in self._known:
            return ResultProjectionQueueSubmitResult(turn_id, False, "memory", "turn already queued")
        self._known.add(turn_id)
        self._items.append(turn_id)
        return ResultProjectionQueueSubmitResult(turn_id, True, "memory", "turn queued")

    def pop_next(self) -> UUID | None:
        return self._items.pop(0) if self._items else None


class RedisRQResultProjectionQueue:
    """Identity-only durable wakeup for deterministic result projection."""

    def __init__(
        self,
        *,
        redis_url: str,
        queue_name: str = worker_queue_definition("result_projection").default_name,
    ) -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_turn(self, turn_id: UUID) -> ResultProjectionQueueSubmitResult:
        from redis import Redis
        from redis.backoff import NoBackoff
        from redis.exceptions import WatchError
        from redis.retry import Retry
        from rq import Queue
        from rq.exceptions import NoSuchJobError
        from rq.job import Job

        connection = Redis.from_url(
            self.redis_url, socket_connect_timeout=2, socket_timeout=2,
            retry=Retry(NoBackoff(), 0),
        )
        queue = Queue(self.queue_name, connection=connection)
        job_id = f"agent2-result-{turn_id}"
        try:
            for _attempt in range(4):
                try:
                    with connection.pipeline() as pipeline:
                        pipeline.watch(Job.key_for(job_id))
                        try:
                            existing = Job.fetch(job_id, connection=connection)
                        except NoSuchJobError:
                            existing = None
                        if existing is not None:
                            if existing.origin != self.queue_name:
                                raise RuntimeError("Result queue ownership does not match")
                            status = existing.get_status(refresh=False)
                            status_value = str(getattr(status, "value", status))
                            if status_value in {"queued", "started", "deferred", "scheduled"}:
                                return ResultProjectionQueueSubmitResult(turn_id, False, "rq", "turn already queued")
                            if status_value not in {"finished", "failed", "stopped", "canceled", "cancelled"}:
                                raise RuntimeError("Result queue status cannot be confirmed")
                        pipeline.multi()
                        if existing is not None:
                            existing.delete(pipeline=pipeline)
                        queue.enqueue(
                            worker_queue_definition("result_projection").handler,
                            str(turn_id), job_id=job_id, pipeline=pipeline,
                        )
                        pipeline.execute()
                    return ResultProjectionQueueSubmitResult(turn_id, True, "rq", "turn queued")
                except WatchError:
                    continue
            raise RuntimeError("Result queue publication changed concurrently; retry the same Turn")
        finally:
            connection.close()


def result_projection_queue_from_settings(settings: object) -> ResultProjectionQueue:
    enabled = bool(getattr(settings, "agent2_result_projection_enabled", False))
    if enabled and str(getattr(settings, "queue_backend", "local")) == "redis":
        return RedisRQResultProjectionQueue(
            redis_url=str(getattr(settings, "redis_url")),
            queue_name=str(
                getattr(
                    settings,
                    "agent2_result_queue_name",
                    worker_queue_definition("result_projection").default_name,
                )
            ),
        )
    return DisabledResultProjectionQueue()


__all__ = [
    "DisabledResultProjectionQueue",
    "InMemoryResultProjectionQueue",
    "RedisRQResultProjectionQueue",
    "ResultProjectionQueue",
    "ResultProjectionQueueSubmitResult",
    "result_projection_queue_from_settings",
]
