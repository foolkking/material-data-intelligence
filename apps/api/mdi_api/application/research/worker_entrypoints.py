from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Protocol, TypeVar
from uuid import UUID

from mdi_api.application.research.ports import ResearchRepositoryFactoryPort


T = TypeVar("T")


class ResearchTurnProcessorPort(Protocol[T]):
    def process(self, turn_id: UUID) -> Awaitable[T]: ...


class ResearchPlanningProcessorPort(Protocol[T]):
    def process(self, turn_id: UUID) -> T: ...


class ResearchResultProjectionQueuePort(Protocol):
    def enqueue_turn(self, turn_id: UUID) -> Any: ...


def process_queued_turn(
    turn_id: str,
    *,
    processor: ResearchTurnProcessorPort[T],
) -> T:
    """Execute one queued Research turn through its application processor."""

    return asyncio.run(processor.process(UUID(turn_id)))


def process_queued_planning(
    turn_id: str,
    *,
    processor: ResearchPlanningProcessorPort[T],
) -> T:
    """Execute one queued capability-planning use case."""

    return processor.process(UUID(turn_id))


def synchronize_queued_execution_progress(
    job_id: str,
    *,
    repository_factory: ResearchRepositoryFactoryPort,
    result_projection_queue: ResearchResultProjectionQueuePort,
) -> Any | None:
    """Project committed execution progress and publish result work if ready."""

    from mdi_api.research_agent.execution import supervisor as supervisor_module

    view = supervisor_module.ResearchExecutionSupervisor(
        repository_factory
    ).sync_for_job(job_id)
    view_status = getattr(view, "status", None) if view is not None else None
    if getattr(view_status, "value", view_status) == "RESULT_PENDING":
        result_projection_queue.enqueue_turn(UUID(str(view.turn_id)))
    return view


__all__ = [
    "ResearchPlanningProcessorPort",
    "ResearchResultProjectionQueuePort",
    "ResearchTurnProcessorPort",
    "process_queued_planning",
    "process_queued_turn",
    "synchronize_queued_execution_progress",
]
