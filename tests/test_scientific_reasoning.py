from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import pytest

from mdi_api.application.interpretation.grounding import (
    project_claim_support_assessments,
    validate_interpretation,
)
from mdi_api.application.scientific_knowledge.synthesis import (
    BoundedLiteratureSynthesisProvider,
    LiteratureSynthesisOutput,
    LiteratureSynthesisValidationError,
    validate_literature_synthesis,
)
from mdi_api.application.scientific_reasoning.assessment import ClaimSupportAssessor
from mdi_api.application.scientific_reports.grounding import ReportGroundingValidator
from mdi_api.domain.interpretation.contracts import ScientificInterpretationOutput
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureEvidence,
    LiteratureEvidenceScope,
    LiteratureQueryPurpose,
    LiteratureSupportType,
)
from mdi_api.domain.scientific_reasoning.contracts import (
    ClaimSupportStatus,
    MethodComparisonStatus,
    ProposedScientificClaim,
    ReasoningEvidence,
    ScientificClaimType,
    ScientificReasoningOutcome,
)
from mdi_api.domain.scientific_reports.contracts import ScientificReportOutput
from mdi_api.research_agent.llm.schemas import StructuredLLMResult


ROOT = Path(__file__).resolve().parents[1]


def _load_test_module(name: str):
    path = ROOT / "tests" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _evidence(**overrides) -> ReasoningEvidence:
    payload = {
        "ref": "result_1",
        "origin": "COMPUTED",
        "text": "The supplied Result reports an observation.",
        "scope": "material_A",
        "method": "bounded_method",
        "lineage": "source_A",
    }
    payload.update(overrides)
    return ReasoningEvidence.model_validate(payload)


def _claim(**overrides) -> ProposedScientificClaim:
    payload = {
        "claim_id": "claim_1",
        "text": "The supplied Result reports an observation.",
        "claim_type": "DIRECT_OBSERVATION",
        "support_status": "DIRECTLY_SUPPORTED",
        "evidence_refs": ["result_1"],
        "scope": "material_A",
    }
    payload.update(overrides)
    return ProposedScientificClaim.model_validate(payload)


def _literature(passage: str) -> LiteratureEvidence:
    return LiteratureEvidence(
        evidence_id=uuid4(),
        project_id="project",
        work_id=uuid4(),
        snapshot_id=uuid4(),
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=LiteratureSupportType.SUPPORTING,
        purpose=LiteratureQueryPurpose.HYPOTHESIS_CONTEXT,
        passage=passage,
        source_content_hash="a" * 64,
        selected_by="qualification",
        selected_at=datetime.now(timezone.utc),
    )


def test_reasoning_fixture_corpus_is_cross_domain_and_repository_owned() -> None:
    payload = json.loads(
        (
            ROOT
            / "docs/scientific-reasoning/fixtures/expert_reasoning_cases_v1.json"
        ).read_text(encoding="utf-8")
    )
    assert payload["contract_version"] == "expert-reasoning-case/1.0"
    assert 18 <= len(payload["cases"]) <= 30
    assert {
        "trajectory",
        "structure",
        "diffraction",
        "materials_ml",
        "composition_space",
        "electronic",
        "phonon",
        "literature",
    }.issubset({row["domain"] for row in payload["cases"]})
    assert all(row["gold_origin"] for row in payload["cases"])


def test_direct_observation_is_supported_within_exact_scope() -> None:
    assessment = ClaimSupportAssessor().assess(_claim(), [_evidence()])
    assert assessment.accepted is True
    assert assessment.support_status == ClaimSupportStatus.DIRECTLY_SUPPORTED
    assert assessment.outcome == ScientificReasoningOutcome.SUPPORTED


def test_causal_claim_fails_closed_without_causal_authority() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="Lower coordination causes faster diffusion.",
            claim_type=ScientificClaimType.CAUSAL_CLAIM,
        ),
        [_evidence()],
    )
    assert assessment.accepted is False
    assert assessment.support_status == ClaimSupportStatus.NOT_SUPPORTED
    assert "NO_CAUSAL_INFERENCE_AUTHORITY" in assessment.reason_codes


def test_negative_causal_boundary_is_admissible_as_insufficient_evidence() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text=(
                "The available evidence does not establish that coordination "
                "causes diffusion."
            ),
            claim_type=ScientificClaimType.CAUSAL_CLAIM,
            support_status=ClaimSupportStatus.INSUFFICIENT_EVIDENCE,
        ),
        [_evidence()],
    )
    assert assessment.accepted is True
    assert assessment.outcome == ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
    assert "NO_CAUSAL_INFERENCE_AUTHORITY" not in assessment.reason_codes


def test_mechanism_is_hypothesis_not_established_fact() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The structural mechanism is proven.",
            claim_type=ScientificClaimType.MECHANISTIC_INTERPRETATION,
            evidence_refs=["result_1", "literature_1"],
        ),
        [
            _evidence(),
            _evidence(
                ref="literature_1",
                origin="LITERATURE",
                text="The authors suggest the mechanism may contribute.",
                lineage="work_A",
            ),
        ],
    )
    assert assessment.support_status == ClaimSupportStatus.SUGGESTIVE
    assert assessment.outcome == ScientificReasoningOutcome.SUPPORTED_ONLY_AS_HYPOTHESIS
    assert "HYPOTHESIS_ESCALATION" in {item.value for item in assessment.defects}


def test_single_source_tentative_mechanism_remains_a_hypothesis() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The observation may be consistent with a tentative mechanism.",
            claim_type=ScientificClaimType.MECHANISTIC_INTERPRETATION,
            support_status=ClaimSupportStatus.SUGGESTIVE,
            hypothesis_status="PROPOSED",
        ),
        [_evidence()],
    )
    assert assessment.accepted is True
    assert assessment.outcome == (
        ScientificReasoningOutcome.SUPPORTED_ONLY_AS_HYPOTHESIS
    )


def test_generalization_preserves_studied_system_scope() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="All materials behave this way.",
            claim_type=ScientificClaimType.GENERALIZATION,
            scope="all materials",
        ),
        [_evidence(scope="one studied material")],
    )
    assert assessment.outcome == ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE
    assert "SCOPE_EXPANSION" in {item.value for item in assessment.defects}


def test_finite_dataset_collection_generalization_is_bounded() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="All compositions in the supplied dataset are valid.",
            claim_type=ScientificClaimType.GENERALIZATION,
            support_status=ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
            scope="the supplied dataset",
        ),
        [
            _evidence(
                text=(
                    "composition.valid_count=576; "
                    "composition.invalid_count=0"
                ),
                scope="the supplied dataset",
            )
        ],
    )
    assert assessment.accepted is True
    assert "SCOPE_EXPANSION" not in {item.value for item in assessment.defects}


def test_finite_dataset_negative_collection_generalization_is_bounded() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="There are no invalid composition samples in this dataset.",
            claim_type=ScientificClaimType.GENERALIZATION,
            support_status=ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
            scope="this dataset",
        ),
        [
            _evidence(
                text=(
                    "composition.valid_count=576; "
                    "composition.invalid_count=0"
                ),
                scope="this dataset",
            )
        ],
    )
    assert assessment.accepted is True
    assert "SCOPE_EXPANSION" not in {item.value for item in assessment.defects}


def test_exploratory_result_can_report_counted_invalid_entries() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text=(
                "Composition coverage reports 576 valid composition samples "
                "and 0 invalid composition samples."
            ),
            claim_type=ScientificClaimType.DIRECT_OBSERVATION,
            scope="the supplied dataset",
        ),
        [
            _evidence(
                text=(
                    "composition.valid_count=576; "
                    "composition.invalid_count=0"
                ),
                semantic_tags=["EXPLORATORY_OUTLIER"],
                scope="the supplied dataset",
            )
        ],
    )
    assert assessment.accepted is True
    assert "EXPLORATORY_OUTLIER_DOES_NOT_ESTABLISH_INVALIDITY" not in assessment.reason_codes


def test_negative_generalization_boundary_does_not_become_overclaim() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text=(
                "The current evidence does not establish that this applies "
                "to all materials."
            ),
            claim_type=ScientificClaimType.GENERALIZATION,
            support_status=ClaimSupportStatus.INSUFFICIENT_EVIDENCE,
            scope="the studied material; not all materials",
        ),
        [_evidence(scope="one studied material")],
    )
    assert assessment.accepted is True
    assert assessment.outcome == ScientificReasoningOutcome.INSUFFICIENT_EVIDENCE


def test_material_limitation_matching_is_semantic_not_punctuation_exact() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The coordination observation is method dependent.",
            limitations=["Coordination is method dependent"],
        ),
        [_evidence(limitations=["Coordination is method-dependent."])],
    )
    assert assessment.accepted is True
    assert "MATERIAL_EVIDENCE_LIMITATION_OMITTED" not in assessment.reason_codes


def test_unrelated_result_limitation_does_not_reject_direct_finding() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(text="The result reports a bounded radius parameter."),
        [
            _evidence(
                limitations=[
                    "The result projector does not infer peaks or coordination shells from the RDF curve."
                ]
            )
        ],
    )
    assert assessment.accepted is True
    assert "MATERIAL_EVIDENCE_LIMITATION_OMITTED" not in assessment.reason_codes


def test_material_limitation_still_constrains_related_finding() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The RDF peak identifies the coordination shell.",
            claim_type=ScientificClaimType.METHOD_INTERPRETATION,
        ),
        [
            _evidence(
                limitations=[
                    "The result projector does not infer peaks or coordination shells from the RDF curve."
                ]
            )
        ],
    )
    assert assessment.accepted is False
    assert "MATERIAL_EVIDENCE_LIMITATION_OMITTED" in assessment.reason_codes


def test_condition_difference_prevents_equivalent_comparison() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The values are directly comparable under equivalent conditions.",
            claim_type=ScientificClaimType.QUANTITATIVE_COMPARISON,
            evidence_refs=["result_1", "literature_1"],
        ),
        [
            _evidence(conditions=["800 K"]),
            _evidence(
                ref="literature_1",
                origin="LITERATURE",
                conditions=["600 K"],
                lineage="work_A",
            ),
        ],
    )
    assert assessment.comparison_status == (
        MethodComparisonStatus.COMPARABLE_WITH_QUALIFIERS
    )
    assert "INVALID_COMPARISON" in {item.value for item in assessment.defects}


def test_method_difference_is_not_a_universal_method_ranking() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="Method A is universally more accurate.",
            claim_type=ScientificClaimType.METHOD_INTERPRETATION,
            evidence_refs=["result_1", "result_2"],
        ),
        [
            _evidence(method="CrystalNN"),
            _evidence(ref="result_2", method="VoronoiNN"),
        ],
    )
    assert assessment.comparison_status == MethodComparisonStatus.COMPLEMENTARY
    assert assessment.support_status == ClaimSupportStatus.NOT_SUPPORTED


def test_acknowledged_method_dependence_is_not_itself_a_reasoning_defect() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text=(
                "The two coordination results differ under method-dependent "
                "scientific definitions."
            ),
            claim_type=ScientificClaimType.METHOD_INTERPRETATION,
            support_status=ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
            evidence_refs=["result_1", "result_2"],
            comparison_status=MethodComparisonStatus.METHOD_DEPENDENT_DIFFERENCE,
        ),
        [
            _evidence(method="CrystalNN", lineage="structure_v2"),
            _evidence(
                ref="result_2",
                method="VoronoiNN",
                lineage="structure_v2",
            ),
        ],
    )
    assert assessment.accepted is True
    assert assessment.outcome == ScientificReasoningOutcome.METHOD_DEPENDENT_DIFFERENCE
    assert "METHOD_MISINTERPRETATION" not in {
        item.value for item in assessment.defects
    }


def test_common_lineage_cannot_be_called_independent_evidence() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="Two independent datasets confirm the finding.",
            claim_type=ScientificClaimType.DESCRIPTIVE_SYNTHESIS,
            evidence_refs=["result_1", "result_2"],
        ),
        [
            _evidence(lineage="trajectory_v3"),
            _evidence(ref="result_2", lineage="trajectory_v3"),
        ],
    )
    assert assessment.independent_evidence_groups == 1
    assert "EVIDENCE_DOUBLE_COUNT" in {item.value for item in assessment.defects}


def test_twenty_turn_repetition_does_not_inflate_support_but_new_result_can() -> None:
    assessor = ClaimSupportAssessor()
    original = _evidence(lineage="trajectory_v3")
    repeated_assessments = [
        assessor.assess(
            _claim(
                text="The supplied Result reports an observation.",
                evidence_refs=["result_1"],
            ),
            [original],
        )
        for _ in range(20)
    ]

    assert {
        assessment.independent_evidence_groups
        for assessment in repeated_assessments
    } == {1}
    assert {
        assessment.support_status
        for assessment in repeated_assessments
    } == {ClaimSupportStatus.DIRECTLY_SUPPORTED}

    updated = assessor.assess(
        _claim(
            text="Two separately sourced Results report the observation.",
            claim_type=ScientificClaimType.DESCRIPTIVE_SYNTHESIS,
            support_status=ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE,
            evidence_refs=["result_1", "result_2"],
        ),
        [
            original,
            _evidence(ref="result_2", lineage="trajectory_v4"),
        ],
    )
    assert updated.independent_evidence_groups == 2
    assert updated.support_status == ClaimSupportStatus.SUPPORTED_WITHIN_SCOPE


def test_bounded_computed_result_synthesis_may_use_all_without_scope_expansion() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text=(
                "The RDF, MSD, and diffusion results all reference the same "
                "selected trajectory interval."
            ),
            claim_type=ScientificClaimType.DESCRIPTIVE_SYNTHESIS,
            evidence_refs=["result_1", "result_2", "result_3"],
            scope="Cross-result consistency within the supplied trajectory result",
        ),
        [
            _evidence(lineage="trajectory_v3"),
            _evidence(ref="result_2", lineage="trajectory_v3"),
            _evidence(ref="result_3", lineage="trajectory_v3"),
        ],
    )

    assert assessment.accepted is True
    assert "UNIVERSAL_SCOPE_NOT_AUTHORIZED" not in assessment.reason_codes


def test_unbounded_all_results_claim_remains_rejected() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="All results are universally valid.",
            claim_type=ScientificClaimType.DESCRIPTIVE_SYNTHESIS,
            evidence_refs=["result_1"],
            scope="all results",
        ),
        [_evidence(lineage="trajectory_v3")],
    )

    assert assessment.accepted is False
    assert "UNIVERSAL_SCOPE_NOT_AUTHORIZED" in assessment.reason_codes


def test_unresolved_contradiction_is_not_collapsed_to_a_winner() -> None:
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="Study B is wrong and Study A establishes the truth.",
            claim_type=ScientificClaimType.DESCRIPTIVE_SYNTHESIS,
            evidence_refs=["literature_1", "literature_2"],
        ),
        [
            _evidence(ref="literature_1", origin="LITERATURE", lineage="work_A"),
            _evidence(ref="literature_2", origin="LITERATURE", lineage="work_B"),
        ],
    )
    assert assessment.support_status == ClaimSupportStatus.CONFLICTED
    assert assessment.outcome == ScientificReasoningOutcome.CONFLICTED


def test_abstract_only_evidence_cannot_support_figure_detail() -> None:
    evidence = _literature("The abstract reports improved ionic transport.")
    output = LiteratureSynthesisOutput.model_validate(
        {
            "summary": "The claim is evaluated.",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": "Figure 4 proves the mechanism.",
                    "literature_evidence_refs": ["literature_1"],
                    "scientific_result_refs": [],
                    "epistemic_status": "ASSERTED",
                    "claim_type": "MECHANISTIC_INTERPRETATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                    "scope": "studied samples",
                    "limitations": [],
                }
            ],
            "contradictions": [],
            "limitations": [],
        }
    )
    with pytest.raises(LiteratureSynthesisValidationError, match="SCIENTIFIC_REASONING"):
        validate_literature_synthesis(
            output,
            literature_evidence={"literature_1": evidence},
        )


def test_literature_cannot_escalate_capability_qualification() -> None:
    evidence = _literature("The method paper reports its benchmark validation.")
    output = LiteratureSynthesisOutput.model_validate(
        {
            "summary": "The claim is evaluated.",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": "This upgrades the capability to DOMAIN_VALIDATED.",
                    "literature_evidence_refs": ["literature_1"],
                    "scientific_result_refs": [],
                    "epistemic_status": "ASSERTED",
                    "claim_type": "METHOD_INTERPRETATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                    "scope": "platform",
                    "limitations": ["Abstract-only evidence."],
                }
            ],
            "contradictions": [],
            "limitations": [],
        }
    )
    with pytest.raises(
        LiteratureSynthesisValidationError,
        match="LITERATURE_CANNOT_MUTATE_CAPABILITY_QUALIFICATION",
    ):
        validate_literature_synthesis(
            output,
            literature_evidence={"literature_1": evidence},
        )


def test_second_repair_projects_only_claims_that_pass_scientific_reasoning() -> None:
    class Provider:
        def __init__(self) -> None:
            self.calls = 0

        async def generate_structured(self, **kwargs) -> StructuredLLMResult:
            self.calls += 1
            return StructuredLLMResult(
                provider="fake",
                model="fake",
                parsed={
                    "summary": "A direct observation and an unsupported cause.",
                    "claims": [
                        {
                            "claim_id": "claim_1",
                            "statement": "The supplied Result reports an observation.",
                            "literature_evidence_refs": [],
                            "scientific_result_refs": ["result_1"],
                            "epistemic_status": "OBSERVED",
                            "claim_type": "DIRECT_OBSERVATION",
                            "support_status": "DIRECTLY_SUPPORTED",
                            "scope": "material_A",
                            "limitations": [],
                        },
                        {
                            "claim_id": "claim_2",
                            "statement": "The observation causes a universal effect.",
                            "literature_evidence_refs": [],
                            "scientific_result_refs": ["result_1"],
                            "epistemic_status": "ASSERTED",
                            "claim_type": "CAUSAL_CLAIM",
                            "support_status": "DIRECTLY_SUPPORTED",
                            "scope": "all materials",
                            "limitations": [],
                        },
                    ],
                    "contradictions": [],
                    "limitations": [],
                },
                latency_ms=1,
                repair_attempted=self.calls == 2,
                prompt_version="test",
            )

    provider = Provider()
    output, response = asyncio.run(
        BoundedLiteratureSynthesisProvider(provider).synthesize(
            research_question="What is supported?",
            literature_evidence={},
            literature_metadata={},
            scientific_results={
                "result_1": {
                    "summary": "The supplied Result reports an observation.",
                    "scope": "material_A",
                    "method": "bounded_method",
                }
            },
        )
    )
    assert provider.calls == 2
    assert response.repair_attempted is True
    assert [claim.claim_id for claim in output.claims] == ["claim_1"]
    assert output.summary == "The supplied Result reports an observation."
    assert "excluded" in output.limitations[-1]


def test_interpretation_1_1_requires_server_claim_support_assessment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _load_test_module("test_agent2_phase6_interpretation")

    payload = fixture._output()
    payload["contract_version"] = "1.1"
    interpretation = ScientificInterpretationOutput.model_validate(payload)
    assert not validate_interpretation(interpretation, fixture._bundle()).valid
    projected = project_claim_support_assessments(
        interpretation, fixture._bundle()
    )
    assert projected.primary_findings[0].reasoning_assessment is not None
    assert validate_interpretation(projected, fixture._bundle()).valid


def test_report_rejects_a_finding_with_rejected_reasoning_assessment() -> None:
    fixture = _load_test_module("test_agent2_phase8_reports")

    bundle = fixture._bundle()
    interpretation = fixture._interpretation()
    assessment = ClaimSupportAssessor().assess(
        _claim(
            text="The result causes a universal effect.",
            claim_type=ScientificClaimType.CAUSAL_CLAIM,
        ),
        [_evidence()],
    )
    report = ScientificReportOutput.model_validate(
        {
            "title": "Bounded report",
            "research_question": bundle.research_question,
            "summary": "A bounded report.",
            "main_findings": [
                {
                    "statement": "The result causes a universal effect.",
                    "finding_refs": ["finding.rdf"],
                    "reasoning_assessment": assessment.model_dump(mode="json"),
                }
            ],
            "method_summary": "Bounded method.",
            "limitations": [],
            "data_sources": ["source_1"],
            "evidence_refs": [],
            "reproducibility_summary": "Immutable sources.",
        }
    )
    errors = ReportGroundingValidator().validate(
        report,
        bundle=bundle,
        interpretation=interpretation,
    )
    assert "report finding contains rejected scientific reasoning" in errors


def test_generated_baseline_is_retained_separately_from_final_evaluation() -> None:
    baseline = json.loads(
        (
            ROOT
            / "docs/scientific-reasoning/generated/expert_reasoning_baseline.json"
        ).read_text(encoding="utf-8")
    )
    final = json.loads(
        (
            ROOT
            / "docs/scientific-reasoning/generated/expert_reasoning_evaluation.json"
        ).read_text(encoding="utf-8")
    )
    assert baseline["metrics"]["BASELINE_REASONING_FAILURES"] > 0
    assert final["metrics"]["UNRESOLVED_SCIENTIFIC_REASONING_BLOCKERS"] == 0
    assert baseline["contract_version"] != final["contract_version"]
