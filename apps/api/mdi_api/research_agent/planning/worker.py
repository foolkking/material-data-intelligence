from __future__ import annotations

from mdi_api.application.research.worker_entrypoints import process_queued_planning
from mdi_api.database import create_repository_factory
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient


def run_queued_planning(turn_id: str) -> dict:
    processor = CapabilityPlanningProcessor(
        create_repository_factory(),
        llm_client=DeepSeekStructuredLLMClient(),
    )
    return process_queued_planning(turn_id, processor=processor)
