from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Connection, Engine

from mdi_api.infrastructure.persistence.agent2_interpretation import Agent2ScientificInterpretationRepository
from mdi_api.infrastructure.persistence.agent2_reports import Agent2ScientificReportGenerationRepository, Agent2ScientificReportRepository
from mdi_api.infrastructure.persistence.agent2_research import (
    ResearchCapabilityPlanRepository,
    ResearchCapabilityResolutionRepository,
    ResearchContextSnapshotRepository,
    ResearchExecutionSummaryRepository,
    ResearchSessionMemoryRepository,
    ResearchTurnDecisionRepository,
    ResearchTurnEventRepository,
    ResearchTurnRepository,
)
from mdi_api.infrastructure.persistence.agent2_results import ScientificResultSnapshotRepository
from mdi_api.infrastructure.persistence.agent2_scientific_objects import ScientificObjectRepository
from mdi_api.infrastructure.persistence.scientific_knowledge import ScientificKnowledgeRepository


@dataclass(frozen=True)
class Agent2RepositoryBundle:
    scientific_objects: ScientificObjectRepository
    research_turns: ResearchTurnRepository
    research_context_snapshots: ResearchContextSnapshotRepository
    research_session_memory: ResearchSessionMemoryRepository
    research_turn_events: ResearchTurnEventRepository
    scientific_result_snapshots: ScientificResultSnapshotRepository
    research_turn_decisions: ResearchTurnDecisionRepository
    research_capability_resolutions: ResearchCapabilityResolutionRepository
    research_capability_plans: ResearchCapabilityPlanRepository
    research_execution_summaries: ResearchExecutionSummaryRepository
    interpretations: Agent2ScientificInterpretationRepository
    scientific_report_generations: Agent2ScientificReportGenerationRepository
    scientific_reports: Agent2ScientificReportRepository
    scientific_knowledge: ScientificKnowledgeRepository

    @classmethod
    def create(cls, bind: Engine | Connection) -> "Agent2RepositoryBundle":
        return cls(
            scientific_objects=ScientificObjectRepository(bind),
            research_turns=ResearchTurnRepository(bind),
            research_context_snapshots=ResearchContextSnapshotRepository(bind),
            research_session_memory=ResearchSessionMemoryRepository(bind),
            research_turn_events=ResearchTurnEventRepository(bind),
            scientific_result_snapshots=ScientificResultSnapshotRepository(bind),
            research_turn_decisions=ResearchTurnDecisionRepository(bind),
            research_capability_resolutions=ResearchCapabilityResolutionRepository(bind),
            research_capability_plans=ResearchCapabilityPlanRepository(bind),
            research_execution_summaries=ResearchExecutionSummaryRepository(bind),
            interpretations=Agent2ScientificInterpretationRepository(bind),
            scientific_report_generations=Agent2ScientificReportGenerationRepository(bind),
            scientific_reports=Agent2ScientificReportRepository(bind),
            scientific_knowledge=ScientificKnowledgeRepository(bind),
        )


__all__ = ["Agent2RepositoryBundle"]
