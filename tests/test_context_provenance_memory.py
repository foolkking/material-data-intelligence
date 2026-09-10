from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from mdi_api.research_agent.context.provenance import (
    ContextAuthorityClass,
    ContextFreshness,
    MemoryEpistemicStatus,
    deduplicate_provenance_items,
    freshness_for_source,
    resolve_source_conflict,
)
from mdi_api.research_agent.context.manifest import build_operation_manifest
from mdi_api.research_agent.context.policy import ContextOperation
from mdi_api.research_agent.context.schemas import (
    ReferenceCandidate,
    ReferenceCandidateSource,
)
from mdi_api.research_agent.lifecycle import build_lifecycle_projection
from mdi_api.research_agent.memory.retriever import ResearchMemoryRetriever, RetrievedMemory
from mdi_api.research_agent.memory.schemas import MemoryReference
from mdi_api.scientific_objects.schemas import ScientificObjectRef


def _object_ref(project_id: str = "project") -> ScientificObjectRef:
    return ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id=project_id,
        object_type="structure.crystal",
        display_name="Silicon",
    )


def test_reference_candidate_has_exact_source_and_authority_metadata() -> None:
    ref = _object_ref()
    candidate = ReferenceCandidate(
        candidate_key="obj_1",
        ref_type="SCIENTIFIC_OBJECT",
        object_ref=ref,
        source=ReferenceCandidateSource.UI_SELECTION,
        display_label="Silicon V7",
        recency_rank=0,
    )

    assert candidate.source_class.value == "EXPLICIT_UI_SELECTION"
    assert candidate.authority_class == ContextAuthorityClass.SCIENTIFIC_INPUT
    assert candidate.freshness == ContextFreshness.CURRENT
    assert candidate.source_ref == f"{ref.object_id}:{ref.version_id}"

    pinned_result = ReferenceCandidate(
        candidate_key="result_1",
        ref_type="SCIENTIFIC_RESULT",
        result_id=uuid4(),
        source=ReferenceCandidateSource.PINNED_CONTEXT,
        display_label="Pinned computed result",
        recency_rank=0,
    )
    assert pinned_result.source_class.value == "SCIENTIFIC_RESULT"
    assert pinned_result.authority_class == ContextAuthorityClass.SCIENTIFIC_KNOWLEDGE


def test_freshness_does_not_equate_historical_with_invalid() -> None:
    assert freshness_for_source(relevance_status="HISTORICAL") == ContextFreshness.HISTORICAL_VALID
    assert freshness_for_source(relevance_status="STALE") == ContextFreshness.STALE
    assert freshness_for_source(invalidated=True) == ContextFreshness.INVALIDATED
    assert freshness_for_source(source_exists=False) == ContextFreshness.SOURCE_MISSING


def test_provenance_dedup_and_conflict_preserve_authoritative_source() -> None:
    source_version = "object:v7"
    items = [
        {
            "kind": "SCIENTIFIC_OBJECT",
            "source": "CURRENT_SCOPE",
            "source_ref": source_version,
            "item_id": "object_1",
            "authority_class": ContextAuthorityClass.SCIENTIFIC_INPUT.value,
            "freshness": ContextFreshness.CURRENT.value,
        },
        {
            "kind": "SCIENTIFIC_OBJECT",
            "source": "CURRENT_SCOPE",
            "source_ref": source_version,
            "item_id": "object_duplicate",
            "authority_class": ContextAuthorityClass.SCIENTIFIC_INPUT.value,
            "freshness": ContextFreshness.CURRENT.value,
        },
    ]
    selected, suppressed = deduplicate_provenance_items(items)
    assert [item["item_id"] for item in selected] == ["object_1"]
    assert suppressed == ["object_duplicate"]

    conflict = resolve_source_conflict([
        {
            "kind": "MEMORY",
            "source_ref": "memory:m1",
            "authority_class": ContextAuthorityClass.MEMORY.value,
            "freshness": ContextFreshness.CURRENT.value,
        },
        {
            "kind": "SCIENTIFIC_RESULT",
            "source_ref": "result:r1",
            "authority_class": ContextAuthorityClass.SCIENTIFIC_KNOWLEDGE.value,
            "freshness": ContextFreshness.CURRENT.value,
        },
    ])
    assert conflict is not None
    assert conflict.winner == "result:r1"


def test_memory_contract_keeps_epistemic_status_and_provenance() -> None:
    memory = MemoryReference(
        ref_type="SCIENTIFIC_RESULT",
        result_id=uuid4(),
        display_label="Computed band gap",
        source="RESULT",
        epistemic_status=MemoryEpistemicStatus.COMPUTED,
        provenance_refs=["turn:t17", "result:r29", "object:v7"],
    )
    assert memory.authority_class == ContextAuthorityClass.MEMORY
    assert memory.epistemic_status == MemoryEpistemicStatus.COMPUTED
    assert memory.provenance_refs == ["turn:t17", "result:r29", "object:v7"]


def test_memory_retrieval_is_project_scoped_and_excludes_invalid_sources() -> None:
    candidates = [
        RetrievedMemory(
            candidate_id="same-project",
            source="RESULT",
            display_label="band gap",
            project_id="project",
            source_ref="result:r1",
            freshness=ContextFreshness.CURRENT.value,
        ),
        RetrievedMemory(
            candidate_id="foreign-project",
            source="RESULT",
            display_label="band gap",
            project_id="other-project",
            source_ref="result:secret",
        ),
        RetrievedMemory(
            candidate_id="invalid",
            source="RESULT",
            display_label="band gap",
            project_id="project",
            freshness=ContextFreshness.INVALIDATED.value,
        ),
    ]
    found = ResearchMemoryRetriever().retrieve(
        message="band gap",
        candidates=candidates,
        project_id="project",
    )
    assert [item.candidate_id for item in found] == ["same-project"]


def test_lifecycle_projection_exposes_context_provenance_summary() -> None:
    now = datetime.now(timezone.utc)
    projection = build_lifecycle_projection(
        {
            "id": uuid4(),
            "status": "ORCHESTRATING",
            "created_at": now,
            "updated_at": now,
        },
        context_snapshot={
            "id": uuid4(),
            "context_fingerprint": "f" * 64,
            "active_scope_refs_json": [{"object_id": "o", "version_id": "v"}],
            "selection_refs_json": [],
            "scientific_selections_json": [],
            "resolved_references_json": [],
            "referenced_result_refs_json": [{"result_id": "r"}],
            "relevant_finding_refs_json": [],
            "unresolved_questions_json": [],
        },
        events=[{
            "event_type": "CONTEXT_RESOLVED",
            "sequence_no": 1,
            "created_at": now,
            "payload_json": {
                "context_manifest": {
                    "included_items": [
                        {
                            "kind": "SCIENTIFIC_OBJECT",
                            "authority_class": "SCIENTIFIC_DATA",
                            "superseded_state": "NONE",
                        }
                    ],
                    "excluded_items": ["goal_1"],
                    "estimated_input_tokens": 100,
                    "input_budget": 12000,
                    "compaction_state": "COMPACTED",
                    "truncation_state": "NONE",
                },
            },
        }],
    )

    context = projection["context"]
    assert context["candidate_count"] == 2
    assert context["selected_count"] == 1
    assert context["excluded_count"] == 1
    assert context["degraded"] is True
    assert context["budget"]["input_budget"] == 12000


def test_operation_manifest_infers_provenance_and_rejects_unauthorized_items() -> None:
    manifest = build_operation_manifest(
        operation=ContextOperation.PLANNER,
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        context_fingerprint="a" * 64,
        items=[{
            "item_id": "object_1",
            "kind": "SCIENTIFIC_OBJECT",
            "authority_class": "SCIENTIFIC_DATA",
            "object_id": "object",
            "version_id": "version",
            "content": {"object_id": "object", "version_id": "version"},
        }],
    )
    item = manifest.included_items[0]
    assert item.source_class == "EXACT_SCIENTIFIC_OBJECT_VERSION"
    assert item.freshness == "CURRENT"
    assert item.epistemic_status == "OBSERVED"

    duplicate_manifest = build_operation_manifest(
        operation=ContextOperation.PLANNER,
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        context_fingerprint="c" * 64,
        items=[
            {
                "item_id": "object_primary",
                "kind": "SCIENTIFIC_OBJECT",
                "authority_class": "SCIENTIFIC_DATA",
                "object_id": "object",
                "version_id": "version",
                "content": {"object_id": "object", "version_id": "version"},
            },
            {
                "item_id": "object_duplicate",
                "kind": "SCIENTIFIC_OBJECT",
                "authority_class": "SCIENTIFIC_DATA",
                "object_id": "object",
                "version_id": "version",
                "content": {"object_id": "object", "version_id": "version"},
            },
        ],
    )
    assert [item.item_id for item in duplicate_manifest.included_items] == [
        "object_primary"
    ]
    assert duplicate_manifest.excluded_items == ["object_duplicate"]

    try:
        build_operation_manifest(
            operation=ContextOperation.PLANNER,
            project_id="project",
            research_session_id="session",
            research_turn_id=uuid4(),
            context_fingerprint="b" * 64,
            items=[{
                "item_id": "foreign",
                "kind": "SCIENTIFIC_RESULT",
                "authority_class": "SCIENTIFIC_RESULT",
                "authorization_checked": False,
                "content": {"result_id": "foreign"},
            }],
        )
    except ValueError as exc:
        assert "unauthorized context item" in str(exc)
    else:
        raise AssertionError("unauthorized context item was accepted")
