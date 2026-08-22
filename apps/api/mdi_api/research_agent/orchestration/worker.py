from __future__ import annotations

import asyncio
from uuid import UUID

from mdi_api.database import create_repository_factory
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor, ProcessTurnResult
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.planning.queue import DisabledCapabilityPlanningQueue, RedisRQCapabilityPlanningQueue
from mdi_api.config import load_settings


def run_queued_turn(turn_id: str) -> ProcessTurnResult:
    """RQ entry point. The queue supplies only the Turn identity."""

    settings = load_settings()
    planning_queue = RedisRQCapabilityPlanningQueue(redis_url=settings.redis_url) if settings.agent2_orchestration_enabled and settings.queue_backend == "redis" else DisabledCapabilityPlanningQueue()
    processor = AgentTurnProcessor(
        repository_factory=create_repository_factory(),
        registries=build_default_agent2_registries(),
        llm_client=DeepSeekStructuredLLMClient(),
        planning_queue=planning_queue,
    )
    return asyncio.run(processor.process(UUID(turn_id)))
