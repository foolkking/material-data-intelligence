from __future__ import annotations

import json
from uuid import uuid4
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from mdi_api.research_agent.schemas import ResolvedResearchContext, ScientificSelectionContext
from mdi_api.research_agent.context.assembler import ResearchContextCandidateAssembler
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.schemas import (
    CompactMessage,
    ContextManifest,
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.context.policy import ContextOperation, context_budget_policy
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.agent2 import _compat_context_manifest_from_snapshot
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
    report = context_budget_policy(ContextOperation.REPORT)

    assert orchestrator.effective_input_budget == 12_000
    assert planner.effective_input_budget == 10_000
    assert data.effective_input_budget == 8_000
    assert planner.effective_input_budget < orchestrator.effective_input_budget
    assert data.effective_input_budget < planner.effective_input_budget
    assert report.effective_input_budget == planner.effective_input_budget
    assert orchestrator.reserved_output_tokens > 0
    assert orchestrator.repair_margin > 0


@pytest.mark.parametrize("operation", list(ContextOperation))
def test_operation_context_manifest_enforces_below_near_at_and_over_budget_boundaries(
    operation: ContextOperation,
) -> None:
    policy = context_budget_policy(operation)
    empty_payload_bytes = len(
        json.dumps(
            {"text": ""},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8"),
    )

    def item_for_tokens(
        tokens: int,
        *,
        item_id: str,
        kind: str = "USER_CONSTRAINT",
        authority_class: str = "USER_CONSTRAINT",
    ) -> dict:
        return {
            "item_id": item_id,
            "kind": kind,
            "authority_class": authority_class,
            "content": {
                "text": "x" * max(0, tokens * 4 - empty_payload_bytes),
            },
        }

    for label, tokens in (
        ("well_below", policy.effective_input_budget // 10),
        ("near", policy.effective_input_budget - 1),
        ("at", policy.effective_input_budget),
    ):
        manifest = build_operation_manifest(
            operation=operation,
            project_id="project",
            research_session_id="session",
            research_turn_id=uuid4(),
            context_fingerprint="d" * 64,
            items=[item_for_tokens(tokens, item_id=label)],
        )
        assert manifest.estimated_input_tokens == tokens
        assert manifest.estimated_input_tokens <= manifest.input_budget
        assert [item.item_id for item in manifest.included_items] == [label]
        assert manifest.excluded_items == []
        assert manifest.compaction_state == "NONE"

    for label, tokens in (
        ("over", policy.effective_input_budget + 1),
        ("significantly_over", policy.effective_input_budget + 5_000),
    ):
        manifest = build_operation_manifest(
            operation=operation,
            project_id="project",
            research_session_id="session",
            research_turn_id=uuid4(),
            context_fingerprint="e" * 64,
            items=[item_for_tokens(tokens, item_id=label)],
        )
        assert manifest.estimated_input_tokens == 0
        assert manifest.included_items == []
        assert manifest.excluded_items == [label]
        assert manifest.compaction_state == "COMPACTED"

    with pytest.raises(
        ValueError,
        match=f"critical {operation.value} context exceeds the operation budget",
    ):
        build_operation_manifest(
            operation=operation,
            project_id="project",
            research_session_id="session",
            research_turn_id=uuid4(),
            context_fingerprint="f" * 64,
            items=[
                item_for_tokens(
                    policy.effective_input_budget + 1,
                    item_id="critical_science",
                    kind="SCIENTIFIC_RESULT",
                    authority_class="SCIENTIFIC_RESULT",
                )
            ],
        )


def test_context_manifest_marks_compaction_when_authoritative_items_exceed_budget() -> None:
    object_id = uuid4()
    version_id = uuid4()
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
        active_objects=[ref] * 79,
        selection_refs=[],
        scientific_selections=[
            ScientificSelectionContext(
                object_ref=ref,
                viewer_id="structure.viewer",
                selection_type="SITE",
                semantic_locator={"site_id": index},
                display_label=f"Site {index}",
            )
            for index in range(16)
        ],
        resolved_references=[],
        referenced_result_ids=[],
        research_goal="Inspect coordination",
        user_constraints=["constraint " + ("x" * 900)] * 32,
        unresolved_questions=[],
        requires_clarification=False,
    )

    manifest = ResearchTurnService._build_context_manifest(
        turn_id=uuid4(),
        context=context,
        context_fingerprint="b" * 64,
    )

    assert manifest.compaction_state == "COMPACTED"
    assert manifest.excluded_items
    assert manifest.estimated_input_tokens <= manifest.input_budget
    assert all(item.item_id not in manifest.excluded_items for item in manifest.included_items)


def test_context_manifest_fails_closed_when_critical_science_cannot_fit() -> None:
    object_id = uuid4()
    version_id = uuid4()
    ref = ScientificObjectRef(
        object_id=object_id,
        version_id=version_id,
        project_id="project",
        object_type="structure.crystal",
        display_name="Silicon",
    )
    large_locator = {
        f"field_{index}": "x" * 300
        for index in range(23)
    }
    context = ResolvedResearchContext(
        project_id="project",
        research_session_id="session",
        active_objects=[ref],
        selection_refs=[],
        scientific_selections=[
            ScientificSelectionContext(
                object_ref=ref,
                viewer_id="structure.viewer",
                selection_type="SITE",
                semantic_locator={
                    **large_locator,
                    "site_id": index,
                },
                display_label=f"Site {index}",
            )
            for index in range(16)
        ],
        resolved_references=[],
        referenced_result_ids=[],
        research_goal=None,
        user_constraints=[],
        unresolved_questions=[],
        requires_clarification=False,
    )

    with pytest.raises(
        ValueError,
        match="critical scientific context exceeds the operation budget",
    ):
        ResearchTurnService._build_context_manifest(
            turn_id=uuid4(),
            context=context,
            context_fingerprint="c" * 64,
        )


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


def test_legacy_context_manifest_projection_compacts_noncritical_overflow() -> None:
    turn_id = uuid4()
    snapshot_id = uuid4()
    object_id = uuid4()
    version_id = uuid4()
    manifest = _compat_context_manifest_from_snapshot(
        {
            "id": str(turn_id),
            "project_id": "project",
            "research_session_id": "session",
        },
        {
            "id": str(snapshot_id),
            "project_id": "project",
            "research_session_id": "session",
            "active_scope_refs_json": [{
                "object_id": str(object_id),
                "version_id": str(version_id),
                "project_id": "project",
                "object_type": "materials.table",
                "display_name": "Dataset",
            }],
            "selection_refs_json": [],
            "scientific_selections_json": [],
            "referenced_result_refs_json": [],
            "effective_constraints_json": ["x" * 2000 for _ in range(32)],
            "research_goal": "Inspect the selected dataset",
            "context_fingerprint": "a" * 64,
        },
    )

    assert manifest["estimated_input_tokens"] <= manifest["input_budget"]
    assert manifest["compaction_state"] == "COMPACTED"
    assert manifest["excluded_items"]
    assert any(
        item["exact_object_version_id"] == str(version_id)
        for item in manifest["included_items"]
    )


def test_legacy_context_manifest_projection_fails_closed_for_critical_overflow() -> None:
    turn_id = uuid4()
    snapshot_id = uuid4()
    object_id = uuid4()
    version_id = uuid4()
    large_locator = {f"field_{index}": "x" * 300 for index in range(23)}

    with pytest.raises(ValueError, match="critical scientific context exceeds the operation budget"):
        _compat_context_manifest_from_snapshot(
            {
                "id": str(turn_id),
                "project_id": "project",
                "research_session_id": "session",
            },
            {
                "id": str(snapshot_id),
                "project_id": "project",
                "research_session_id": "session",
                "active_scope_refs_json": [],
                "selection_refs_json": [],
                "scientific_selections_json": [
                    {
                        "object_ref": {
                            "object_id": str(object_id),
                            "version_id": str(version_id),
                            "project_id": "project",
                            "object_type": "structure.crystal",
                            "display_name": "Silicon",
                        },
                        "viewer_id": "structure.viewer",
                        "selection_type": "SITE",
                        "semantic_locator": {**large_locator, "site_id": index},
                        "display_label": f"Site {index}",
                    }
                    for index in range(16)
                ],
                "referenced_result_refs_json": [],
                "effective_constraints_json": [],
                "research_goal": None,
                "context_fingerprint": "b" * 64,
            },
        )


def test_child_branch_does_not_inherit_recent_results_without_explicit_binding() -> None:
    """Editing/rerunning a terminal turn starts a fresh scientific branch.

    A child turn may retain its parent's object scope, but it must not
    silently inherit historical Result candidates.  Explicit reinterpret/
    continuation requests still bind results through ``explicit_result_ids``.
    """

    parent_id = uuid4()
    previous_id = uuid4()
    turn_id = uuid4()

    class _Turns:
        def list_recent_before(self, _session_id, _sequence, limit):
            assert limit == 6
            return [{"id": previous_id, "sequence_no": 1}]

        def list_all_before(self, _session_id, _sequence, limit):
            assert limit == 500
            return [{"id": previous_id, "sequence_no": 1}]

        def list_for_turn(self, _turn_id):
            return [{
                "event_type": "TURN_RECEIVED",
                "payload_json": {"ui_context": {"explicit_result_ids": []}},
            }]

        def referenced_messages(self, _turn):
            return [{
                "role": "user",
                "content_summary": "解释所选样本",
                "created_at": datetime.now(timezone.utc),
            }]

    class _Snapshots:
        def get_for_turn(self, _turn_id):
            return None

    class _Memory:
        def get_state(self, _session_id):
            return {"pinned_result_refs_json": []}

    class _Results:
        def exists_for_turn(self, _turn_id):
            raise AssertionError("child branches must skip recency result lookup")

    unit = SimpleNamespace(agent2=SimpleNamespace(
        research_turn_events=_Turns(),
        research_turns=_Turns(),
        research_context_snapshots=_Snapshots(),
        research_session_memory=_Memory(),
        scientific_result_snapshots=_Results(),
    ))

    bundle = ResearchContextCandidateAssembler().assemble(unit, {
        "id": turn_id,
        "project_id": "project",
        "research_session_id": "session",
        "sequence_no": 2,
        "parent_turn_id": parent_id,
    })

    assert bundle.result_candidates == []
