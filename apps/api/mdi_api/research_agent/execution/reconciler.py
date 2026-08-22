from __future__ import annotations

from typing import Any
from uuid import UUID

from mdi_api.research_agent.execution.dispatcher import DispatchResult, ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.schemas import ResearchTurnStatus


class ResearchExecutionReconciler:
    """Recover missed queue publishes and runtime projection wakeups by identity."""

    def __init__(self, repository_factory: Any, *, queue: Any | None = None) -> None:
        self.repository_factory = repository_factory
        self.queue = queue

    def reconcile_turn(self, turn_id: UUID) -> DispatchResult | Any | None:
        with self.repository_factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            status = ResearchTurnStatus(str(turn["status"]))
            job_id = str(turn.get("job_id") or "")
        if status in {ResearchTurnStatus.PLAN_READY, ResearchTurnStatus.QUEUED}:
            return ResearchExecutionDispatcher(self.repository_factory, queue=self.queue).dispatch_turn(turn_id)
        if job_id:
            return ResearchExecutionSupervisor(self.repository_factory).sync_for_job(job_id)
        return None

    def reconcile_job(self, job_id: str) -> Any | None:
        return ResearchExecutionSupervisor(self.repository_factory).sync_for_job(job_id)
