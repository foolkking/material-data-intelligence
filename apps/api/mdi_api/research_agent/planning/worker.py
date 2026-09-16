from __future__ import annotations

from uuid import UUID

from mdi_api.application.research.worker_entrypoints import process_queued_planning
from mdi_api.bootstrap.repository_factory import create_repository_factory
from mdi_api.config import load_settings
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient


def run_queued_planning(turn_id: str) -> dict:
    """Plan a Research turn and durably dispatch an executable plan.

    A Research submission is an asynchronous product lifecycle, not a
    browser-owned workflow. The browser may still issue the idempotent
    dispatch request for compatibility, but closing or reloading the browser
    must not strand an accepted turn at ``PLAN_READY``.
    """

    settings = load_settings()
    processor = CapabilityPlanningProcessor(
        create_repository_factory(),
        llm_client=DeepSeekStructuredLLMClient(),
    )
    from mdi_workers.queue_runtime import RedisRQQueueBackend

    dispatcher = ResearchExecutionDispatcher(
        create_repository_factory(),
        queue=RedisRQQueueBackend(
            redis_url=settings.redis_url,
            queue_name=settings.agent2_execution_queue_name,
        ),
    )
    return _process_and_dispatch(
        turn_id,
        processor=processor,
        dispatcher=dispatcher,
    )


def _process_and_dispatch(
    turn_id: str,
    *,
    processor: CapabilityPlanningProcessor,
    dispatcher: ResearchExecutionDispatcher,
) -> dict:
    result = process_queued_planning(turn_id, processor=processor)
    if str(result.get("status") or "") != "PLAN_READY":
        return result
    dispatched = dispatcher.dispatch_turn(UUID(turn_id))
    return {
        **result,
        "execution_dispatch": {
            "job_id": dispatched.job_id,
            "queued": dispatched.queued,
            "queue_backend": dispatched.queue_backend,
            "message": dispatched.message,
        },
    }
