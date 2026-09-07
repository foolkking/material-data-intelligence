from __future__ import annotations

from mdi_api.application.research.worker_entrypoints import process_queued_turn
from mdi_api.database import create_repository_factory
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor, ProcessTurnResult
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.planning.queue import DisabledCapabilityPlanningQueue, RedisRQCapabilityPlanningQueue
from mdi_api.config import load_settings
from mdi_api.interpretation.queue import DisabledInterpretationQueue, RedisRQInterpretationQueue


def run_queued_turn(turn_id: str) -> ProcessTurnResult:
    """RQ entry point. The queue supplies only the Turn identity."""

    settings = load_settings()
    planning_queue = (
        RedisRQCapabilityPlanningQueue(
            redis_url=settings.redis_url,
            queue_name=settings.agent2_planning_queue_name,
        )
        if settings.agent2_orchestration_enabled and settings.queue_backend == "redis"
        else DisabledCapabilityPlanningQueue()
    )
    interpretation_queue = (
        RedisRQInterpretationQueue(redis_url=settings.redis_url, queue_name=settings.agent2_interpretation_queue_name)
        if settings.agent2_interpretation_enabled and settings.queue_backend == "redis"
        else DisabledInterpretationQueue()
    )
    processor = AgentTurnProcessor(
        repository_factory=create_repository_factory(),
        registries=build_default_agent2_registries(),
        llm_client=DeepSeekStructuredLLMClient(),
        planning_queue=planning_queue,
        interpretation_queue=interpretation_queue,
    )
    return process_queued_turn(turn_id, processor=processor)
