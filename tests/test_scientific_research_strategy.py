from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import pytest

from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.llm.structured_client import (
    DeepSeekStructuredLLMClient,
)
from mdi_api.research_agent.strategy.engine import ScientificResearchStrategyEngine
from mdi_api.research_agent.strategy.evaluation import evaluate_strategy_cases
from mdi_api.research_agent.strategy.evidence import (
    ResearchEvidenceStateProjector,
    ResultEvidenceInput,
    compare_observations,
)
from mdi_api.research_agent.strategy.fixtures import (
    golden_strategy_cases,
    synthetic_bundle,
)
from mdi_api.research_agent.strategy.provider import BoundedStrategyProvider
from mdi_api.research_agent.strategy.schemas import (
    ComparisonCompatibilityStatus,
    EvidenceObservation,
    ProviderStrategyProposal,
    ResearchStrategyAction,
    ScientificHypothesisStatus,
)
from mdi_api.research_agent.strategy.validation import (
    StrategyProposalValidator,
    StrategyValidationError,
)
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def test_golden_strategy_corpus_covers_bounded_cross_family_cases() -> None:
    report = evaluate_strategy_cases(golden_strategy_cases())
    assert report.strategy_evaluation_cases == 12
    assert report.accepted is True
    assert report.passed_cases == 12
    assert report.cross_family_cases >= 1
    assert report.hypothesis_test_cases >= 1
    assert report.contradiction_cases >= 1
    assert report.irrelevant_capability_executions == 0
    assert report.redundant_executions == 0
    assert report.correct_scientific_stops == report.expected_scientific_stops


def test_strategy_state_is_reproducible_and_preserves_exact_versions() -> None:
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="strategy-fixture",
        object_type="trajectory.atomic",
    )
    bundle = synthetic_bundle(
        capability_id="trajectory.msd",
        result_type="trajectory.msd",
        source=source,
    )
    first = ResearchEvidenceStateProjector().project(
        objective="Analyze diffusion.",
        results=[ResultEvidenceInput(result_id=bundle.result_id, bundle=bundle)],
    )
    second = ResearchEvidenceStateProjector().project(
        objective="Analyze diffusion.",
        results=[ResultEvidenceInput(result_id=bundle.result_id, bundle=bundle)],
    )
    assert first.fingerprint == second.fingerprint
    assert first.exact_source_version_ids == [source.version_id]
    assert first.lineages[0].source_version_ids == [source.version_id]


def test_evidence_projection_rejects_cross_project_results() -> None:
    left = synthetic_bundle(
        capability_id="trajectory.msd",
        result_type="trajectory.msd",
        source=ScientificObjectRef(
            object_id=uuid4(),
            version_id=uuid4(),
            project_id="project-a",
            object_type="trajectory.atomic",
        ),
    )
    right = synthetic_bundle(
        capability_id="trajectory.msd",
        result_type="trajectory.msd",
        source=ScientificObjectRef(
            object_id=uuid4(),
            version_id=uuid4(),
            project_id="project-b",
            object_type="trajectory.atomic",
        ),
    )
    with pytest.raises(ValueError, match="project boundaries"):
        ResearchEvidenceStateProjector().project(
            objective="compare",
            results=[
                ResultEvidenceInput(result_id=left.result_id, bundle=left),
                ResultEvidenceInput(result_id=right.result_id, bundle=right),
            ],
        )


def test_comparison_normalizes_supported_units_and_rejects_dimensions() -> None:
    left = EvidenceObservation(
        result_id=uuid4(),
        bundle_result_id=uuid4(),
        fact_id="left",
        predicate="property.value",
        subject_ref="same",
        value=1.0,
        unit="eV",
        capability_ids=["a"],
        lineage_signature="a" * 64,
    )
    right = left.model_copy(
        update={
            "result_id": uuid4(),
            "value": 1000.0,
            "unit": "meV",
            "lineage_signature": "b" * 64,
        }
    )
    assert compare_observations(left, right).status == (
        ComparisonCompatibilityStatus.CONDITIONALLY_COMPATIBLE
    )
    invalid = right.model_copy(update={"unit": "angstrom"})
    assert compare_observations(left, invalid).status == (
        ComparisonCompatibilityStatus.NOT_COMPATIBLE
    )


class _Provider:
    def __init__(self, payloads: list[dict]) -> None:
        self.payloads = payloads
        self.calls = 0

    async def generate_structured(self, **_kwargs):
        payload = self.payloads[min(self.calls, len(self.payloads) - 1)]
        self.calls += 1
        return StructuredLLMResult(
            provider="fixture",
            model="fixture",
            parsed=payload,
            latency_ms=1,
            prompt_version="fixture/1.0",
        )


def test_strategy_provider_repair_is_bounded_and_validates_references() -> None:
    case = golden_strategy_cases()[0]
    state = ResearchEvidenceStateProjector().project(
        objective=case.objective,
        results=[
            ResultEvidenceInput(
                result_id=case.current_result.result_id,
                bundle=case.current_result,
            )
        ],
    )
    invalid = {
        "contract_version": "1.0",
        "action": "CONTINUE_ANALYSIS",
        "current_question_id": "unknown",
        "evidence_gap_id": "unknown",
        "capability_need": "trajectory.compute_msd",
        "evidence_result_ids": [str(uuid4())],
        "hypothesis_id": None,
        "reason_codes": ["provider"],
        "limitation_refs": [],
    }
    valid = {
        **invalid,
        "current_question_id": None,
        "evidence_gap_id": None,
        "evidence_result_ids": [],
    }
    provider = _Provider([invalid, valid])
    proposal, result = asyncio.run(
        BoundedStrategyProvider(provider).propose(
            evidence_state=state,
            legal_requirement_ids={"trajectory.compute_msd"},
        )
    )
    assert proposal.action == ResearchStrategyAction.CONTINUE_ANALYSIS
    assert result.repair_attempted is True
    assert provider.calls == 2


def test_strategy_validator_rejects_unknown_result_without_repair() -> None:
    case = golden_strategy_cases()[0]
    state = ResearchEvidenceStateProjector().project(
        objective=case.objective,
        results=[
            ResultEvidenceInput(
                result_id=case.current_result.result_id,
                bundle=case.current_result,
            )
        ],
    )
    proposal = ProviderStrategyProposal(
        action=ResearchStrategyAction.CONTINUE_ANALYSIS,
        capability_need="trajectory.compute_msd",
        evidence_result_ids=[uuid4()],
        reason_codes=["invalid"],
    )
    with pytest.raises(StrategyValidationError, match="INVENTED_RESULT"):
        StrategyProposalValidator().validate(
            proposal=proposal,
            evidence_state=state,
            legal_requirement_ids={"trajectory.compute_msd"},
        )


def test_hypothesis_remains_tentative_and_non_causal() -> None:
    case = golden_strategy_cases()[1]
    report = evaluate_strategy_cases([case])
    assert report.accepted
    row = report.cases[0]
    assert row["hypothesis_id"] == "hypothesis-local-constraint"
    assert ScientificHypothesisStatus.PROPOSED.value == "PROPOSED"


@pytest.mark.live_llm
@pytest.mark.skipif(
    os.getenv("MDI_RUN_AGENT2_LIVE") != "1"
    or not os.getenv("DEEPSEEK_KEY"),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_provider_strategy_cases_remain_bounded_and_source_referenced() -> None:
    client = DeepSeekStructuredLLMClient()
    cases = golden_strategy_cases()
    selected = (
        (cases[0], {"trajectory.estimate_diffusion"}),
        (cases[2], {"data.explore_composition_space"}),
        (cases[7], set()),
    )
    for case, legal_requirements in selected:
        state, _deterministic = ScientificResearchStrategyEngine().decide(
            objective=case.objective,
            current=case.current_result,
            completed_bundles=case.completed_bundles,
            completed_capability_ids=set(case.completed_capability_ids),
        )
        proposal, result = asyncio.run(
            BoundedStrategyProvider(client, timeout_seconds=120).propose(
                evidence_state=state,
                legal_requirement_ids=legal_requirements,
            )
        )
        assert set(proposal.evidence_result_ids).issubset(set(state.result_ids))
        assert (
            proposal.capability_need is None
            or proposal.capability_need in legal_requirements
        )
        assert result.provider == "deepseek"
