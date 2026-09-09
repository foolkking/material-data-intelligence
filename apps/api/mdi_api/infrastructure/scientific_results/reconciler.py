from __future__ import annotations

from uuid import UUID

from mdi_api.infrastructure.scientific_results.queue import ResultProjectionQueue
from mdi_api.research_agent.schemas import ResearchTurnStatus


class ScientificResultReconciler:
    def __init__(self, repository_factory: object, queue: ResultProjectionQueue) -> None:
        self.repository_factory = repository_factory
        self.queue = queue

    def reconcile_turn(self, turn_id: UUID):
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
        if str(turn["status"]) == ResearchTurnStatus.RESULT_PENDING.value:
            return self.queue.enqueue_turn(turn_id)
        return None


__all__ = ["ScientificResultReconciler"]
