from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mdi_schemas.worker_queues import worker_queue_definition


@dataclass(frozen=True)
class PlanningQueueSubmitResult:
    turn_id: UUID
    enqueued: bool
    backend: str
    message: str


class DisabledCapabilityPlanningQueue:
    def enqueue_turn(self, turn_id: UUID) -> PlanningQueueSubmitResult:
        return PlanningQueueSubmitResult(turn_id, False, "disabled", "Capability planning queue is disabled")


class InMemoryCapabilityPlanningQueue:
    def __init__(self) -> None:
        self._items: list[UUID] = []
        self._known: set[UUID] = set()

    def enqueue_turn(self, turn_id: UUID) -> PlanningQueueSubmitResult:
        if turn_id in self._known:
            return PlanningQueueSubmitResult(turn_id, False, "memory", "turn already queued")
        self._known.add(turn_id)
        self._items.append(turn_id)
        return PlanningQueueSubmitResult(turn_id, True, "memory", "turn queued")

    def pop_next(self) -> UUID | None:
        return self._items.pop(0) if self._items else None


class RedisRQCapabilityPlanningQueue:
    def __init__(
        self,
        *,
        redis_url: str,
        queue_name: str = worker_queue_definition("planning").default_name,
    ) -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_turn(self, turn_id: UUID) -> PlanningQueueSubmitResult:
        from redis import Redis
        from rq import Queue
        queue = Queue(self.queue_name, connection=Redis.from_url(self.redis_url))
        job_id = f"agent2-plan-{turn_id}"
        existing = queue.fetch_job(job_id)
        if existing is not None:
            status = str(getattr(existing.get_status(refresh=True), "value", existing.get_status(refresh=True)))
            if status in {"queued", "started", "deferred", "scheduled"}:
                return PlanningQueueSubmitResult(turn_id, False, "rq", "turn already queued")
            existing.delete()
        queue.enqueue(
            worker_queue_definition("planning").handler,
            str(turn_id),
            job_id=job_id,
        )
        return PlanningQueueSubmitResult(turn_id, True, "rq", "turn queued")
