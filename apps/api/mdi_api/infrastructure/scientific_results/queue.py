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
        from rq import Queue

        queue = Queue(self.queue_name, connection=Redis.from_url(self.redis_url))
        job_id = f"agent2-result-{turn_id}"
        existing = queue.fetch_job(job_id)
        if existing is not None:
            status = existing.get_status(refresh=True)
            status_value = str(getattr(status, "value", status))
            if status_value in {"queued", "started", "deferred", "scheduled"}:
                return ResultProjectionQueueSubmitResult(turn_id, False, "rq", "turn already queued")
            existing.delete()
        queue.enqueue(
            worker_queue_definition("result_projection").handler,
            str(turn_id),
            job_id=job_id,
        )
        return ResultProjectionQueueSubmitResult(turn_id, True, "rq", "turn queued")


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
