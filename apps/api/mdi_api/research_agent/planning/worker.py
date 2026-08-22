from __future__ import annotations

from uuid import UUID

from mdi_api.database import create_repository_factory
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient


def run_queued_planning(turn_id: str) -> dict:
    return CapabilityPlanningProcessor(create_repository_factory(), llm_client=DeepSeekStructuredLLMClient()).process(UUID(turn_id))
