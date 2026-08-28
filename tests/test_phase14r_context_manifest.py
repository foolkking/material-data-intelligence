from __future__ import annotations

from uuid import uuid4
from datetime import datetime, timezone

from mdi_api.research_agent.schemas import ResolvedResearchContext, ScientificSelectionContext
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.schemas import (
    CompactMessage,
    ContextManifest,
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def test_context_manifest_is_bounded_and_preserves_exact_scientific_identity() -> None:
    object_id = uuid4()
    version_id = uuid4()
    turn_id = uuid4()
    ref = ScientificObjectRef(
        object_id=object_id,
        version_id=version_id,
        project_id="project",
        object_type="structure.crystal",
        display_name="Silicon",
    )
    context = ResolvedResearchContext(
        project_id="project",
        research_session_id="session",
        active_objects=[ref],
        selection_refs=[ref],
        scientific_selections=[
            ScientificSelectionContext(
                object_ref=ref,
                viewer_id="structure.viewer",
                selection_type="SITE",
                semantic_locator={"site_id": 14},
                display_label="Site 14",
            )
        ],
        resolved_references=[],
        referenced_result_ids=[uuid4()],
        research_goal="Inspect coordination",
        user_constraints=["CrystalNN"],
        unresolved_questions=[],
        requires_clarification=False,
    )
    manifest = ResearchTurnService._build_context_manifest(
        turn_id=turn_id,
        context=context,
        context_fingerprint="a" * 64,
    )

    assert isinstance(manifest, ContextManifest)
    assert manifest.research_turn_id == turn_id
    assert manifest.project_id == "project"
    assert manifest.policy_version == "agent2.context-policy/2.0"
    assert manifest.context_fingerprint == "a" * 64
    assert manifest.included_items
    scientific_items = [
        item for item in manifest.included_items
        if item.kind in {"SCIENTIFIC_OBJECT", "SCIENTIFIC_SELECTION"}
    ]
    assert all(item.authorization_checked for item in scientific_items)
    assert all(item.exact_object_id == str(object_id) for item in scientific_items)
    assert all(item.exact_object_version_id == str(version_id) for item in scientific_items)
    assert all(len(item.content_fingerprint) == 64 for item in manifest.included_items)
    assert manifest.estimated_input_tokens == sum(item.estimated_tokens for item in manifest.included_items)


def test_context_budget_policy_is_operation_specific_and_reserves_output_space() -> None:
    orchestrator = context_budget_policy(ContextOperation.ORCHESTRATOR)
    planner = context_budget_policy(ContextOperation.PLANNER)
    data = context_budget_policy(ContextOperation.DATA)

    assert orchestrator.effective_input_budget == 12_000
    assert planner.effective_input_budget == 10_000
    assert data.effective_input_budget == 8_000
    assert planner.effective_input_budget < orchestrator.effective_input_budget
    assert data.effective_input_budget < planner.effective_input_budget
    assert orchestrator.reserved_output_tokens > 0
    assert orchestrator.repair_margin > 0


def test_context_compiler_compacts_conversation_before_exact_scientific_identity() -> None:
    object_id = uuid4()
    version_id = uuid4()
    ref = ScientificObjectRef(
        object_id=object_id,
        version_id=version_id,
        project_id="project",
        object_type="structure.crystal",
        display_name="Silicon",
    )
    candidates = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[
            ReferenceCandidate(
                candidate_key="obj_1",
                ref_type="SCIENTIFIC_OBJECT",
                object_ref=ref,
                source=ReferenceCandidateSource.UI_SELECTION,
                display_label="Silicon structure",
                semantic_summary="Exact selected version",
                recency_rank=0,
            )
        ],
        result_candidates=[],
        finding_candidates=[],
        explicit_constraints=["preserve exact version"],
        current_research_goal="Inspect coordination",
        unresolved_questions=[],
        recent_messages=[
            CompactMessage(
                role="USER" if index % 2 == 0 else "ASSISTANT",
                turn_sequence_no=index + 1,
                content=("historical discussion " + ("x" * 3900)),
                created_at=datetime.now(timezone.utc),
            )
            for index in range(12)
        ],
        current_user_message="Use the selected structure version exactly.",
    )

    compact = ResearchContextCompiler().compile(
        turn={"id": str(candidates.research_turn_id)},
        candidates=candidates,
        token_budget=2048,
    )

    assert compact.objects[0].summary["source"] == ReferenceCandidateSource.UI_SELECTION.value
    assert compact.objects[0].ref_key == "obj_1"
    assert compact.current_user_message == candidates.current_user_message
    assert len(compact.recent_conversation) < len(candidates.recent_messages)
