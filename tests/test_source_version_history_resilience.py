from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from mdi_api.research_agent.context.assembler import (
    ResearchContextCandidateAssembler,
)
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.policy import (
    ContextOperation,
    context_budget_policy,
)
from mdi_api.research_agent.context.provenance import (
    ContextFreshness,
    support_eligibility_for_item,
)


PROJECT_ID = "project-f14"
SESSION_ID = "session-f14"


class _Turns:
    def __init__(
        self,
        *,
        current_turn_id: UUID,
        current_message: str,
        previous_turns: list[dict],
        explicit_refs: list[dict],
    ) -> None:
        self.current_turn_id = current_turn_id
        self.current_message = current_message
        self.previous_turns = previous_turns
        self.explicit_refs = explicit_refs

    def list_recent_before(self, _session_id: str, _sequence: int, limit: int):
        assert limit == 6
        return list(reversed(self.previous_turns[-limit:]))

    def list_all_before(self, _session_id: str, _sequence: int, limit: int):
        assert limit == 500
        return list(reversed(self.previous_turns[-limit:]))

    def referenced_messages(self, turn: dict):
        if turn["id"] == self.current_turn_id:
            return [{
                "role": "user",
                "content_summary": self.current_message,
                "created_at": datetime.now(timezone.utc),
            }]
        sequence = int(turn["sequence_no"])
        return [
            {
                "role": "user",
                "content_summary": f"Distinct user question {sequence}",
                "created_at": datetime.now(timezone.utc),
            },
            {
                "role": "agent",
                "content_summary": f"Bounded answer {sequence}",
                "created_at": datetime.now(timezone.utc),
            },
        ]


class _TurnEvents:
    def __init__(self, explicit_refs: list[dict]) -> None:
        self.explicit_refs = explicit_refs

    def list_for_turn(self, _turn_id: UUID):
        return [{
            "event_type": "TURN_RECEIVED",
            "payload_json": {
                "ui_context": {
                    "explicit_object_refs": self.explicit_refs,
                }
            },
        }]


class _ContextSnapshots:
    def __init__(self, refs_by_turn: dict[UUID, list[dict]]) -> None:
        self.refs_by_turn = refs_by_turn

    def get_for_turn(self, turn_id: UUID):
        refs = self.refs_by_turn.get(turn_id)
        if refs is None:
            return None
        return {
            "selection_refs_json": refs,
            "active_scope_refs_json": refs,
            "resolved_references_json": [
                {"display_label": ref["display_name"], "object_ref": ref}
                for ref in refs
            ],
            "effective_constraints_json": [],
            "unresolved_questions_json": [],
            "research_goal": "Compare immutable source versions",
        }


class _ScientificObjects:
    def __init__(
        self,
        *,
        object_id: UUID,
        current_version_id: UUID,
        versions: dict[UUID, dict],
    ) -> None:
        self.logical = {
            "id": object_id,
            "project_id": PROJECT_ID,
            "object_type": "materials.table",
            "display_name": "F14 versioned table",
            "current_version_id": current_version_id,
            "lifecycle_status": "ACTIVE",
        }
        self.versions = versions

    def get_object(self, object_id: UUID):
        assert object_id == self.logical["id"]
        return self.logical

    def get_version(self, version_id: UUID):
        return self.versions[version_id]


class _NoResults:
    def exists_for_turn(self, _turn_id: UUID):
        return False


class _Memory:
    def get_state(self, _session_id: str):
        return {
            "active_scope_refs_json": [],
            "pinned_object_refs_json": [],
            "pinned_result_refs_json": [],
            "session_constraints_json": [],
            "active_research_goal": None,
        }


def _ref(object_id: UUID, version_id: UUID, label: str) -> dict:
    return {
        "object_id": str(object_id),
        "version_id": str(version_id),
        "project_id": PROJECT_ID,
        "object_type": "materials.table",
        "display_name": label,
    }


def _unit(
    *,
    current_turn_id: UUID,
    current_message: str,
    previous_turns: list[dict],
    explicit_refs: list[dict],
    refs_by_turn: dict[UUID, list[dict]],
    object_id: UUID,
    current_version_id: UUID,
    versions: dict[UUID, dict],
):
    turns = _Turns(
        current_turn_id=current_turn_id,
        current_message=current_message,
        previous_turns=previous_turns,
        explicit_refs=explicit_refs,
    )
    return SimpleNamespace(
        agent2=SimpleNamespace(
            research_turn_events=_TurnEvents(explicit_refs),
            research_turns=turns,
            research_context_snapshots=_ContextSnapshots(refs_by_turn),
            research_session_memory=_Memory(),
            scientific_result_snapshots=_NoResults(),
            scientific_objects=_ScientificObjects(
                object_id=object_id,
                current_version_id=current_version_id,
                versions=versions,
            ),
        )
    )


def test_twenty_plus_turn_history_stays_bounded_and_distinguishes_v1_v2() -> None:
    object_id = uuid4()
    v1_id = uuid4()
    v2_id = uuid4()
    current_turn_id = uuid4()
    previous_turns = [
        {"id": uuid4(), "sequence_no": sequence}
        for sequence in range(1, 23)
    ]
    v1_ref = _ref(object_id, v1_id, "F14 table V1")
    v2_ref = _ref(object_id, v2_id, "F14 table V2")
    versions = {
        v1_id: {
            "id": v1_id,
            "scientific_object_id": object_id,
            "object_type": "materials.table",
            "availability_status": "AVAILABLE",
            "canonical_metadata_json": {"rowCount": 2, "marker": "V1"},
        },
        v2_id: {
            "id": v2_id,
            "scientific_object_id": object_id,
            "object_type": "materials.table",
            "availability_status": "AVAILABLE",
            "canonical_metadata_json": {"rowCount": 3, "marker": "V2"},
        },
    }
    unit = _unit(
        current_turn_id=current_turn_id,
        current_message="Compare the exact original V1 with the exact new V2.",
        previous_turns=previous_turns,
        explicit_refs=[v1_ref, v2_ref],
        refs_by_turn={turn["id"]: [v1_ref] for turn in previous_turns},
        object_id=object_id,
        current_version_id=v2_id,
        versions=versions,
    )

    candidates = ResearchContextCandidateAssembler().assemble(
        unit,
        {
            "id": current_turn_id,
            "project_id": PROJECT_ID,
            "research_session_id": SESSION_ID,
            "sequence_no": 23,
            "parent_turn_id": None,
        },
    )

    assert len(candidates.recent_turn_ids) == 6
    assert len(candidates.recent_messages) == 12
    assert len(candidates.active_object_candidates) == 2
    by_version = {
        item.object_ref.version_id: item
        for item in candidates.active_object_candidates
    }
    assert by_version[v1_id].freshness == ContextFreshness.HISTORICAL_VALID
    assert by_version[v1_id].stale is True
    assert by_version[v2_id].freshness == ContextFreshness.CURRENT
    assert by_version[v2_id].stale is False
    assert '"marker":"V1"' in (by_version[v1_id].semantic_summary or "")
    assert '"marker":"V2"' in (by_version[v2_id].semantic_summary or "")
    assert all(item.support_eligible is False for item in by_version.values())

    budget = context_budget_policy(ContextOperation.ORCHESTRATOR)
    compact = ResearchContextCompiler().compile(
        turn={"id": current_turn_id},
        candidates=candidates,
        token_budget=budget.effective_input_budget,
    )
    encoded = compact.model_dump_json().encode("utf-8")
    assert len(encoded) <= budget.effective_input_budget * 4
    assert {item.ref_key for item in compact.objects} == {"obj_1", "obj_2"}
    assert len(compact.recent_conversation) <= 12


def test_old_v1_history_never_rebinds_to_current_v2() -> None:
    object_id = uuid4()
    v1_id = uuid4()
    v2_id = uuid4()
    previous_turn = {"id": uuid4(), "sequence_no": 1}
    current_turn_id = uuid4()
    v1_ref = _ref(object_id, v1_id, "Original V1")
    versions = {
        v1_id: {
            "id": v1_id,
            "scientific_object_id": object_id,
            "object_type": "materials.table",
            "availability_status": "AVAILABLE",
            "canonical_metadata_json": {"marker": "V1-original"},
        },
        v2_id: {
            "id": v2_id,
            "scientific_object_id": object_id,
            "object_type": "materials.table",
            "availability_status": "AVAILABLE",
            "canonical_metadata_json": {"marker": "V2-current"},
        },
    }
    unit = _unit(
        current_turn_id=current_turn_id,
        current_message="Reopen the original result.",
        previous_turns=[previous_turn],
        explicit_refs=[],
        refs_by_turn={previous_turn["id"]: [v1_ref]},
        object_id=object_id,
        current_version_id=v2_id,
        versions=versions,
    )

    candidates = ResearchContextCandidateAssembler().assemble(
        unit,
        {
            "id": current_turn_id,
            "project_id": PROJECT_ID,
            "research_session_id": SESSION_ID,
            "sequence_no": 2,
            "parent_turn_id": None,
        },
    )

    assert len(candidates.active_object_candidates) == 1
    recovered = candidates.active_object_candidates[0]
    assert recovered.object_ref.version_id == v1_id
    assert recovered.freshness == ContextFreshness.HISTORICAL_VALID
    assert '"marker":"V1-original"' in (recovered.semantic_summary or "")
    assert "V2-current" not in (recovered.semantic_summary or "")


def test_projection_types_never_escalate_into_scientific_support() -> None:
    for kind, authority in (
        ("INTERPRETATION", "PRESENTATION"),
        ("REPORT", "PRESENTATION"),
        ("MEMORY", "MEMORY"),
        ("ASSISTANT_MESSAGE", "HISTORICAL_CONTEXT"),
        ("HISTORY_SUMMARY", "HISTORICAL_CONTEXT"),
    ):
        assert support_eligibility_for_item(kind, authority) is False

    assert support_eligibility_for_item(
        "SCIENTIFIC_RESULT",
        "SCIENTIFIC_KNOWLEDGE",
    ) is True
