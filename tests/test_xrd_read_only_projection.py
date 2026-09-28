from __future__ import annotations

from uuid import uuid4

from mdi_api.research_agent.context.schemas import (
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.orchestration.router import ResearchActionRouter
from mdi_api.research_agent.orchestration.schemas import (
    OrchestratorConfidence,
    ProposedRequirement,
    ResearchTurnDecision,
)
from mdi_api.research_agent.schemas import ResearchAction, RequirementCriticality
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def test_query_data_projection_exposes_bounded_experimental_xrd_metadata() -> None:
    ref = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="diffraction.xrd.experimental",
        display_name="PbSO4 measured XRD",
    )
    candidate = ReferenceCandidate(
        candidate_key="obj_1",
        ref_type="SCIENTIFIC_OBJECT",
        object_ref=ref,
        source=ReferenceCandidateSource.EXPLICIT_REFERENCE,
        display_label="PbSO4 measured XRD",
        semantic_summary=(
            '{"canonical_metadata":{"detectedFormat":"json_limited",'
            '"experimentalXrd":{"resourceId":"pub15_pbso4_measured",'
            '"resourceVersion":"PUB-15-2026-09-13",'
            '"resourceHash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
            '"pointCount":6001,"axisMonotonicity":"STRICTLY_INCREASING",'
            '"intensitySemantic":"counts",'
            '"xAxis":{"kind":"two_theta","unit":"degree"},'
            '"wavelength":{"value":1.5405,"unit":"angstrom"}}}}'
        ),
        recency_rank=0,
        support_eligible=False,
    )
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[candidate],
        result_candidates=[],
        finding_candidates=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[],
        explicit_constraints=[],
    )
    decision = ResearchTurnDecision(
        contract_version="1.0",
        action=ResearchAction.QUERY_DATA,
        research_objective="Inspect the measured XRD resource.",
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[
            ProposedRequirement(
                requirement_id="data.query",
                criticality=RequirementCriticality.REQUIRED,
                subject_ref_keys=["obj_1"],
                constraints={},
            )
        ],
        reusable_result_ref_keys=[],
        clarification=None,
        confidence=OrchestratorConfidence.HIGH,
        assistant_message=None,
    )

    text = ResearchActionRouter._query_data_projection(decision, bundle)

    assert text is not None
    assert "测量点数：6001" in text
    assert "XRD 横轴：two_theta （degree）" in text
    assert "XRD 波长：1.5405 angstrom" in text
