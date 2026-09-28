from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from mdi_api.agent2_errors import InvalidResearchTurnDecision
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.resolver import DeterministicReferenceResolver
from mdi_api.research_agent.context.schemas import (
    CompactMessage,
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.orchestration.schemas import (
    ClarificationRequest,
    OrchestratorConfidence,
    ProposedRequirement,
    ResearchOrchestratorInput,
    ResearchTurnDecision,
)
from mdi_api.research_agent.orchestration.validator import ResearchTurnDecisionValidator
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.schemas import ResearchAction, RequirementCriticality
from mdi_api.research_agent.schemas import ResearchTurnUIContext
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def object_ref(project_id: str = "project") -> ScientificObjectRef:
    return ScientificObjectRef(
        object_id=uuid4(), version_id=uuid4(), project_id=project_id,
        object_type="structure.crystal", display_name="Si",
    )


def test_reference_candidate_is_strict_opaque_and_cross_field_validated():
    ref = object_ref()
    candidate = ReferenceCandidate(
        candidate_key="obj_1", ref_type="SCIENTIFIC_OBJECT", object_ref=ref,
        source=ReferenceCandidateSource.UI_SELECTION, display_label="Si", recency_rank=0,
    )
    assert candidate.object_ref == ref
    with pytest.raises(ValidationError):
        ReferenceCandidate(
            candidate_key=str(ref.object_id), ref_type="SCIENTIFIC_OBJECT", object_ref=ref,
            source=ReferenceCandidateSource.UI_SELECTION, display_label="Si", recency_rank=0,
        )
    with pytest.raises(ValidationError):
        ReferenceCandidate(
            candidate_key="obj_2", ref_type="SCIENTIFIC_OBJECT", object_ref=ref, result_id=uuid4(),
            source=ReferenceCandidateSource.UI_SELECTION, display_label="Si", recency_rank=0,
        )
    with pytest.raises(ValidationError):
        ReferenceCandidate(
            candidate_key="result_1", ref_type="SCIENTIFIC_RESULT",
            source=ReferenceCandidateSource.PREVIOUS_TURN_RESULT, display_label="RDF", recency_rank=0,
        )


@pytest.mark.parametrize(
    "source",
    [
        ReferenceCandidateSource.UI_SELECTION,
        ReferenceCandidateSource.EXPLICIT_REFERENCE,
    ],
)
def test_multiple_exact_user_bindings_form_one_authorized_scope(source):
    candidates = [
        ReferenceCandidate(
            candidate_key=f"obj_{index}",
            ref_type="SCIENTIFIC_OBJECT",
            object_ref=object_ref(),
            source=source,
            display_label=f"Selected {index}",
            recency_rank=index - 1,
        )
        for index in (1, 2)
    ]
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=candidates,
        result_candidates=[],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[],
    )

    resolution = DeterministicReferenceResolver().resolve(bundle)

    assert resolution.selected_object_keys == ("obj_1", "obj_2")
    assert resolution.ambiguous_object_keys == ()


def test_multiple_explicit_results_form_one_authorized_comparison_scope():
    candidates = [
        ReferenceCandidate(
            candidate_key=f"result_{index}",
            ref_type="SCIENTIFIC_RESULT",
            result_id=uuid4(),
            source=ReferenceCandidateSource.EXPLICIT_REFERENCE,
            display_label=f"Selected result {index}",
            recency_rank=0,
        )
        for index in (1, 2)
    ]
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[],
        result_candidates=candidates,
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[],
    )

    resolution = DeterministicReferenceResolver().resolve(bundle)

    assert resolution.selected_result_keys == ("result_1", "result_2")
    assert resolution.ambiguous_result_keys == ()


def test_compact_message_is_bounded_and_candidate_keys_are_unique():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        CompactMessage(role="USER", turn_sequence_no=1, content="x" * 4025, created_at=now)
    ref = object_ref()
    candidate = ReferenceCandidate(
        candidate_key="obj_1", ref_type="SCIENTIFIC_OBJECT", object_ref=ref,
        source=ReferenceCandidateSource.CURRENT_SCOPE, display_label="Si", recency_rank=0,
    )
    with pytest.raises(ValidationError, match="candidate_key"):
        ResearchContextCandidateBundle(
            project_id="project", research_session_id="session", research_turn_id=uuid4(),
            active_object_candidates=[candidate, candidate], result_candidates=[], finding_candidates=[],
            explicit_constraints=[], current_research_goal=None, unresolved_questions=[], recent_messages=[],
        )


def test_context_fingerprint_is_deterministic_and_sensitive_to_exact_version():
    ref = object_ref()
    candidate = ReferenceCandidate(
        candidate_key="obj_1", ref_type="SCIENTIFIC_OBJECT", object_ref=ref,
        source=ReferenceCandidateSource.UI_SELECTION, display_label="Si", recency_rank=0,
    )
    bundle = ResearchContextCandidateBundle(
        project_id="project", research_session_id="session", research_turn_id=uuid4(),
        active_object_candidates=[candidate], result_candidates=[], finding_candidates=[],
        explicit_constraints=["temperature=300 K"], current_research_goal="Inspect Si",
        unresolved_questions=[], recent_messages=[], recent_turn_ids=[uuid4()],
    )
    compiler = ResearchContextCompiler()
    first = compiler.compile(turn={"id": bundle.research_turn_id}, candidates=bundle)
    second = compiler.compile(turn={"id": bundle.research_turn_id}, candidates=bundle)
    assert first.context_fingerprint == second.context_fingerprint
    changed_ref = ref.model_copy(update={"version_id": uuid4()})
    changed = bundle.model_copy(update={"active_object_candidates": [candidate.model_copy(update={"object_ref": changed_ref})]})
    assert compiler.compile(turn={"id": bundle.research_turn_id}, candidates=changed).context_fingerprint != first.context_fingerprint


def test_context_compiler_enforces_real_budget_and_preserves_highest_priority_ref():
    now = datetime.now(timezone.utc)
    candidates = [ReferenceCandidate(
        candidate_key=f"obj_{index}",
        ref_type="SCIENTIFIC_OBJECT",
        object_ref=object_ref(),
        source=ReferenceCandidateSource.UI_SELECTION if index == 1 else ReferenceCandidateSource.CURRENT_SCOPE,
        display_label=f"Structure {index}",
        semantic_summary="x" * 2000,
        recency_rank=index - 1,
    ) for index in range(1, 21)]
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=candidates,
        result_candidates=[],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[CompactMessage(
            role="USER",
            turn_sequence_no=index,
            content="m" * 4000,
            created_at=now,
        ) for index in range(1, 7)],
    )

    compact = ResearchContextCompiler().compile(
        turn={"id": bundle.research_turn_id},
        candidates=bundle,
        token_budget=2000,
    )

    assert len(compact.model_dump_json().encode("utf-8")) <= 8000
    assert compact.objects[0].ref_key == "obj_1"
    assert len(compact.objects) < len(candidates)


def test_turn_ui_context_rejects_unbounded_reference_lists():
    with pytest.raises(ValidationError):
        ResearchTurnUIContext(active_object_refs=[object_ref() for _ in range(65)])
    with pytest.raises(ValidationError):
        ResearchTurnUIContext(selection_refs=[object_ref() for _ in range(17)])


def test_decision_contract_rejects_extra_invalid_enum_and_negative_shape():
    decision = ResearchTurnDecision(
        contract_version="1.0", action=ResearchAction.ANALYZE,
        assistant_message="我会根据当前结构准备 RDF 分析。",
        research_objective="计算当前晶体结构的径向分布函数。",
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[ProposedRequirement(
            requirement_id="structure.compute_rdf", criticality=RequirementCriticality.REQUIRED,
            subject_ref_keys=["obj_1"], constraints={"cutoff_angstrom": 8.0},
        )],
        reusable_result_ref_keys=[], clarification=None, confidence=OrchestratorConfidence.HIGH,
    )
    assert decision.contract_version == "1.0"
    with pytest.raises(ValidationError):
        ResearchTurnDecision.model_validate({**decision.model_dump(mode="json"), "reasoning": "hidden"})
    with pytest.raises(ValidationError):
        ResearchTurnDecision.model_validate({**decision.model_dump(mode="json"), "action": "RUN_TOOL"})


def test_default_requirement_registry_has_only_bounded_phase2_requirements():
    registry = build_default_agent2_registries().requirements
    ids = [item.requirement_id for item in registry.list_active()]
    assert len(ids) == 29
    assert {
        "structure.inspect_view",
        "structure.inspect_brillouin_zone",
        "phonon.compose_band_dos",
        "ml.evaluate_uncertainty",
        "ml.evaluate_classification",
    }.issubset(ids)
    assert ids == sorted(ids)
    assert "structure.compute_rdf" in ids and "report.compose" in ids
    assert {
        "structure.inspect_coordination_hist", "structure.inspect_coordination_crystalnn",
        "structure.inspect_coordination_voronoi", "trajectory.compute_rdf",
        "electronic.inspect_band", "electronic.inspect_dos",
        "data.explore_composition_space", "data.explore_materials",
        "volumetric.inspect",
    }.issubset(ids)
    assert all("tool" not in item.requirement_id for item in registry.list_active())
    rdf = registry.require("structure.compute_rdf")
    assert rdf.accepted_object_types == ["structure.crystal"]
    assert rdf.constraint_schema["properties"]["cutoff_angstrom"]["exclusiveMinimum"] == 0


def test_clarification_contract_has_one_question_and_no_reasoning_field():
    clarification = ClarificationRequest(question="你指的是结构 A 还是结构 B？", candidate_keys=["obj_1", "obj_2"])
    assert clarification.question.endswith("？")
    assert "reasoning" not in ResearchTurnDecision.model_json_schema()["properties"]


def test_decision_reference_lists_reject_duplicates():
    with pytest.raises(ValidationError, match="unique"):
        ClarificationRequest(question="Which object?", candidate_keys=["obj_1", "obj_1"])
    with pytest.raises(ValidationError, match="unique"):
        ProposedRequirement(
            requirement_id="structure.compute_rdf",
            criticality=RequirementCriticality.REQUIRED,
            subject_ref_keys=["obj_1", "obj_1"],
        )


def test_action_validator_rejects_lower_priority_scope_selection():
    project_id = "project"
    lower = ReferenceCandidate(
        candidate_key="obj_1",
        ref_type="SCIENTIFIC_OBJECT",
        object_ref=object_ref(project_id),
        source=ReferenceCandidateSource.CURRENT_SCOPE,
        display_label="Scope structure",
        recency_rank=0,
    )
    selected = ReferenceCandidate(
        candidate_key="obj_2",
        ref_type="SCIENTIFIC_OBJECT",
        object_ref=object_ref(project_id),
        source=ReferenceCandidateSource.UI_SELECTION,
        display_label="Selected structure",
        recency_rank=0,
    )
    bundle = ResearchContextCandidateBundle(
        project_id=project_id,
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[lower, selected],
        result_candidates=[],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[],
    )
    decision = ResearchTurnDecision(
        contract_version="1.0",
        action=ResearchAction.OPEN_OBJECT,
        assistant_message="Open object.",
        research_objective=None,
        selected_scope_ref_keys=["obj_1"],
        scientific_requirements=[],
        reusable_result_ref_keys=[],
        clarification=None,
        confidence=OrchestratorConfidence.HIGH,
    )
    registries = build_default_agent2_registries()
    input_context = ResearchOrchestratorInput(
        contract_version="1.0",
        user_message="Open selected object",
        research_context=ResearchContextCompiler().compile(turn={"id": bundle.research_turn_id}, candidates=bundle),
        available_requirement_ids=[],
        allowed_actions=list(ResearchAction),
    )
    with pytest.raises(InvalidResearchTurnDecision, match="priority"):
        ResearchTurnDecisionValidator(registries.requirements).validate(
            decision=decision,
            input_context=input_context,
            candidate_bundle=bundle,
        )
