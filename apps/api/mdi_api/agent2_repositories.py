"""Compatibility facade for Agent2 persistence repositories."""

from mdi_api.infrastructure.persistence.agent2_bundle import Agent2RepositoryBundle
from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
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

__all__ = [
    "Agent2RepositoryBundle",
    "Agent2ScientificInterpretationRepository",
    "Agent2ScientificReportGenerationRepository",
    "Agent2ScientificReportRepository",
    "ResearchCapabilityPlanRepository",
    "ResearchCapabilityResolutionRepository",
    "ResearchContextSnapshotRepository",
    "ResearchExecutionSummaryRepository",
    "ResearchSessionMemoryRepository",
    "ResearchTurnDecisionRepository",
    "ResearchTurnEventRepository",
    "ResearchTurnRepository",
    "ScientificObjectRepository",
    "ScientificResultSnapshotRepository",
]
