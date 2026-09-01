from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class TurnQueueSubmitResult:
    turn_id: UUID
    enqueued: bool
    backend: str
    message: str


class AgentTurnQueue(Protocol):
    def enqueue_turn(self, turn_id: UUID) -> TurnQueueSubmitResult: ...


class DisabledAgentTurnQueue:
    def enqueue_turn(self, turn_id: UUID) -> TurnQueueSubmitResult:
        return TurnQueueSubmitResult(turn_id, False, "disabled", "Agent 2.0 orchestration queue is disabled")


class InMemoryAgentTurnQueue:
    """Deterministic wakeup adapter used by tests; payloads are UUIDs only."""

    def __init__(self) -> None:
        self._queued: list[UUID] = []
        self._known: set[UUID] = set()

    def enqueue_turn(self, turn_id: UUID) -> TurnQueueSubmitResult:
        if turn_id in self._known:
            return TurnQueueSubmitResult(turn_id, False, "memory", "turn already queued")
        self._known.add(turn_id)
        self._queued.append(turn_id)
        return TurnQueueSubmitResult(turn_id, True, "memory", "turn queued")

    def pop_next(self) -> UUID | None:
        return self._queued.pop(0) if self._queued else None


class RedisRQAgentTurnQueue:
    def __init__(self, *, redis_url: str, queue_name: str = "mdi-agent-turns") -> None:
        self.redis_url = redis_url
        self.queue_name = queue_name

    def enqueue_turn(self, turn_id: UUID) -> TurnQueueSubmitResult:
        from redis import Redis
        from rq import Queue

        connection = Redis.from_url(self.redis_url)
        queue = Queue(self.queue_name, connection=connection)
        rq_job_id = f"agent2-turn-{turn_id}"
        existing = queue.fetch_job(rq_job_id)
        if existing is not None:
            status = str(getattr(existing.get_status(refresh=True), "value", existing.get_status(refresh=True)))
            if status in {"queued", "started", "deferred", "scheduled"}:
                return TurnQueueSubmitResult(turn_id, False, "rq", "turn already queued")
            existing.delete()
        queue.enqueue(
            "mdi_api.research_agent_worker.run_queued_turn",
            str(turn_id),
            job_id=rq_job_id,
        )
        return TurnQueueSubmitResult(turn_id, True, "rq", "turn queued")
