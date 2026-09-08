from __future__ import annotations

import mdi_api.agent2_repositories as legacy
from mdi_api.infrastructure.persistence.agent2_bundle import Agent2RepositoryBundle
from mdi_api.infrastructure.persistence.agent2_common import _Repository, _optional_dict
from mdi_api.infrastructure.persistence.agent2_interpretation import (
    Agent2ScientificInterpretationRepository,
)
from mdi_api.infrastructure.persistence.agent2_reports import (
    Agent2ScientificReportGenerationRepository,
    Agent2ScientificReportRepository,
)
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


def test_legacy_agent2_repository_symbols_are_true_aliases() -> None:
    expected = {
        "Agent2RepositoryBundle": Agent2RepositoryBundle,
        "Agent2ScientificInterpretationRepository": Agent2ScientificInterpretationRepository,
        "Agent2ScientificReportGenerationRepository": Agent2ScientificReportGenerationRepository,
        "Agent2ScientificReportRepository": Agent2ScientificReportRepository,
        "ResearchCapabilityPlanRepository": ResearchCapabilityPlanRepository,
        "ResearchCapabilityResolutionRepository": ResearchCapabilityResolutionRepository,
        "ResearchContextSnapshotRepository": ResearchContextSnapshotRepository,
        "ResearchExecutionSummaryRepository": ResearchExecutionSummaryRepository,
        "ResearchSessionMemoryRepository": ResearchSessionMemoryRepository,
        "ResearchTurnDecisionRepository": ResearchTurnDecisionRepository,
        "ResearchTurnEventRepository": ResearchTurnEventRepository,
        "ResearchTurnRepository": ResearchTurnRepository,
        "ScientificObjectRepository": ScientificObjectRepository,
        "ScientificResultSnapshotRepository": ScientificResultSnapshotRepository,
        "_Repository": _Repository,
        "_optional_dict": _optional_dict,
    }

    for name, canonical in expected.items():
        assert getattr(legacy, name) is canonical
