from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mdi_schemas.worker_queues import worker_queue_definition


@dataclass(frozen=True)
class InterpretationQueueSubmitResult:
    turn_id: UUID
    enqueued: bool
    backend: str
    message: str


class DisabledInterpretationQueue:
    def enqueue_turn(self, turn_id: UUID) -> InterpretationQueueSubmitResult:
        return InterpretationQueueSubmitResult(turn_id, False, "disabled", "interpretation queue is disabled")


class InMemoryInterpretationQueue:
    def __init__(self) -> None:
        self._items: list[UUID] = []
        self._known: set[UUID] = set()

    def enqueue_turn(self, turn_id: UUID) -> InterpretationQueueSubmitResult:
        if turn_id in self._known:
            return InterpretationQueueSubmitResult(turn_id, False, "memory", "turn already queued")
        self._known.add(turn_id)
        self._items.append(turn_id)
        return InterpretationQueueSubmitResult(turn_id, True, "memory", "turn queued")

    def pop_next(self) -> UUID | None:
        return self._items.pop(0) if self._items else None


class RedisRQInterpretationQueue:
    def __init__(
        self,
        *,
        redis_url: str,
        queue_name: str = worker_queue_definition("interpretation").default_name,
    ) -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_turn(self, turn_id: UUID) -> InterpretationQueueSubmitResult:
        from redis import Redis
        from rq import Queue

        queue = Queue(self.queue_name, connection=Redis.from_url(self.redis_url))
        job_id = f"agent2-interpretation-{turn_id}"
        existing = queue.fetch_job(job_id)
        if existing is not None:
            status = str(getattr(existing.get_status(refresh=True), "value", existing.get_status(refresh=True)))
            if status in {"queued", "started", "deferred", "scheduled", "finished"}:
                return InterpretationQueueSubmitResult(turn_id, False, "rq", "turn already queued")
            existing.delete()
        queue.enqueue(
            worker_queue_definition("interpretation").handler,
            str(turn_id),
            job_id=job_id,
        )
        return InterpretationQueueSubmitResult(turn_id, True, "rq", f"turn queued on {self.queue_name}")


__all__ = ["DisabledInterpretationQueue", "InMemoryInterpretationQueue", "InterpretationQueueSubmitResult", "RedisRQInterpretationQueue"]
