from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, projects, sessions, users, scientific_result_snapshots
from mdi_api.research_agent.memory.retriever import ResearchMemoryRetriever, RetrievedMemory
from mdi_api.research_agent.memory.service import ResearchSessionMemoryService
from mdi_api.research_agent.context.compiler import ResearchContextCompiler
from mdi_api.research_agent.context.resolver import DeterministicReferenceResolver
from mdi_api.research_agent.context.schemas import (
    CompactMessage,
    ReferenceCandidate,
    ReferenceCandidateSource,
    ResearchContextCandidateBundle,
)
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.schemas import ScientificObjectRef
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.research_agent.service import ResearchTurnService


def foundation():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    owner = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": "project", "organization_id": "org", "name": "Project", "created_by": owner.id})
        connection.execute(insert(sessions), {"id": "session", "project_id": "project", "mode": "project", "status": "active", "created_by": owner.id})
    return engine, owner, RepositoryFactory(engine)


def test_session_constraint_is_explicit_and_persistent():
    _engine, owner, factory = foundation()
    turns = ResearchTurnService(factory)
    received = turns.receive_turn(
        project_id="project", session_id="session", current_user=owner,
        request=CreateResearchTurnRequest(message="后面这个 Session 都用 cutoff 8 Å"),
    )
    with factory.session() as session:
        state = ResearchSessionMemoryService().get_state(session, session_id="session", project_id="project")
    assert state.version == 2
    assert state.session_constraints[0].structured_constraint == {"name": "cutoff", "value": 8.0, "unit": "Å"}
    assert state.session_constraints[0].source_message_id == received.user_message.id


def test_pinned_result_survives_repository_reload_and_unpin() -> None:
    _engine, owner, factory = foundation()
    result_id = uuid4()
    turn_id = uuid4()
    with factory.unit_of_work() as unit:
        user_message_id = f"memory-test-message-{turn_id.hex[:12]}"
        unit.agent2.research_turns.add_message({
            "id": user_message_id,
            "session_id": "session",
            "role": "user",
            "content_summary": "Inspect RDF",
            "payload_json": {},
        })
        unit.agent2.research_turns.add({
            "id": turn_id,
            "project_id": "project",
            "research_session_id": "session",
            "sequence_no": 1,
            "status": "COMPLETED",
            "row_version": 1,
            "user_message_id": user_message_id,
        })
        unit.connection.execute(insert(scientific_result_snapshots).values(
            id=result_id,
            project_id="project",
            research_turn_id=turn_id,
            job_id=None,
            schema_version="1.0",
            projection_version="test",
            execution_status="SUCCESS",
            relevance_status="CURRENT",
            source_fingerprint="f" * 64,
            bundle_json={"research_question": "Inspect RDF", "result_items": []},
        ))
        memory = ResearchSessionMemoryService()
        pinned = memory.pin_result(unit, session_id="session", project_id="project", result_id=result_id)
        assert pinned.pinned_result_refs == [result_id]
        item = next(
            row
            for row in unit.agent2.research_session_memory.list_items("session")
            if row["item_type"] == "PINNED_RESULT"
        )
        assert item["ref_json"]["epistemic_status"] == "COMPUTED"
        assert item["ref_json"]["authority_class"] == "MEMORY"
        assert item["ref_json"]["provenance_refs"] == [
            f"turn:{turn_id}",
            f"result:{result_id}",
        ]

    with factory.session() as session:
        reloaded = ResearchSessionMemoryService().get_state(
            session, session_id="session", project_id="project"
        )
        assert reloaded.pinned_result_refs == [result_id]

    with factory.unit_of_work() as unit:
        unpinned = ResearchSessionMemoryService().unpin_result(
            unit, session_id="session", project_id="project", result_id=result_id
        )
        assert unpinned.pinned_result_refs == []

    with factory.session() as session:
        final = ResearchSessionMemoryService().get_state(
            session, session_id="session", project_id="project"
        )
        assert final.pinned_result_refs == []


def test_turn_scoped_constraint_is_not_promoted_to_session():
    _engine, owner, factory = foundation()
    ResearchTurnService(factory).receive_turn(
        project_id="project", session_id="session", current_user=owner,
        request=CreateResearchTurnRequest(message="这次 RDF cutoff 用 8 Å"),
    )
    with factory.session() as session:
        state = ResearchSessionMemoryService().get_state(session, session_id="session", project_id="project")
    assert state.session_constraints == []


def test_session_constraint_override_and_clear_are_versioned():
    _engine, owner, factory = foundation()
    turns = ResearchTurnService(factory)
    for message in (
        "后面这个 Session 都用 cutoff 8 Å",
        "接下来改成 10 Å",
    ):
        turns.receive_turn(project_id="project", session_id="session", current_user=owner, request=CreateResearchTurnRequest(message=message))
    with factory.session() as session:
        state = ResearchSessionMemoryService().get_state(session, session_id="session", project_id="project")
    assert [item.structured_constraint["value"] for item in state.session_constraints] == [10.0]
    turns.receive_turn(project_id="project", session_id="session", current_user=owner, request=CreateResearchTurnRequest(message="取消刚才那个 cutoff 限制"))
    with factory.session() as session:
        state = ResearchSessionMemoryService().get_state(session, session_id="session", project_id="project")
    assert state.session_constraints == []


def test_retriever_is_bounded_and_never_returns_unauthorized():
    candidates = [
        RetrievedMemory(candidate_id="result_1", source="PINNED_CONTEXT", display_label="RDF first peak", score=(0, 0, 0)),
        RetrievedMemory(candidate_id="result_2", source="RECENT_CONTEXT", display_label="XRD comparison", score=(2, 1, 0)),
        RetrievedMemory(candidate_id="result_secret", source="RECENT_CONTEXT", display_label="secret", authorized=False),
    ]
    found = ResearchMemoryRetriever().retrieve(message="解释 RDF 第一峰", candidates=candidates, limit=2)
    assert [item.candidate_id for item in found] == ["result_1", "result_2"]


def test_five_hundred_turn_retrieval_is_bounded():
    candidates = [
        RetrievedMemory(candidate_id=f"turn_{index}", source="LONG_SESSION_RETRIEVAL", display_label=f"historical turn {index}", score=(6, index, 0))
        for index in range(500)
    ]
    found = ResearchMemoryRetriever().retrieve(message="historical", candidates=candidates, limit=16)
    assert len(found) == 16
    assert found[0].candidate_id == "turn_0"


def test_context_compiler_stays_bounded_and_preserves_pinned_result():
    now = datetime.now(timezone.utc)
    bundle = ResearchContextCandidateBundle(
        project_id="project", research_session_id="session", research_turn_id=uuid4(),
        active_object_candidates=[], result_candidates=[], finding_candidates=[],
        explicit_constraints=[{"name": "cutoff_angstrom", "value": 8.0}],
        current_research_goal="understand RDF", unresolved_questions=[], recent_messages=[
            CompactMessage(role="USER", turn_sequence_no=i + 1, content="filler " * 100, created_at=now) for i in range(12)
        ], recent_turn_ids=[], current_user_message="解释刚才的 RDF", pinned_result_ids=[],
    )
    compact = ResearchContextCompiler().compile(turn={}, candidates=bundle, token_budget=2048)
    assert len(compact.model_dump_json().encode()) <= 2048 * 4
    assert compact.explicit_constraints


def test_context_compiler_keeps_turn_ids_out_of_provider_context():
    turn_ids = [uuid4(), uuid4()]
    bundle = ResearchContextCandidateBundle(
        project_id="project", research_session_id="session", research_turn_id=uuid4(),
        active_object_candidates=[], result_candidates=[], finding_candidates=[],
        explicit_constraints=[], current_research_goal=None, unresolved_questions=[],
        recent_messages=[], recent_turn_ids=turn_ids, current_user_message="继续",
        pinned_result_ids=[],
    )

    compact = ResearchContextCompiler().compile(turn={}, candidates=bundle, token_budget=2048)
    assert compact.relevant_prior_turns == ["prior_turn_1", "prior_turn_2"]
    serialized = compact.model_dump_json()
    assert all(str(turn_id) not in serialized for turn_id in turn_ids)


def test_explicit_result_outranks_lower_priority_object_candidates():
    now = datetime.now(timezone.utc)
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[ReferenceCandidate(
            candidate_key="obj_1",
            ref_type="SCIENTIFIC_OBJECT",
            object_ref=ScientificObjectRef(
                object_id=uuid4(),
                version_id=uuid4(),
                project_id="project",
                object_type="structure.crystal",
            ),
            source=ReferenceCandidateSource.RECENT_CONTEXT,
            display_label="Earlier structure",
            recency_rank=1,
        )],
        result_candidates=[ReferenceCandidate(
            candidate_key="result_1",
            ref_type="SCIENTIFIC_RESULT",
            result_id=uuid4(),
            source=ReferenceCandidateSource.EXPLICIT_REFERENCE,
            display_label="Explicit RDF result",
            recency_rank=0,
        )],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[CompactMessage(
            role="USER", turn_sequence_no=1, content="previous", created_at=now
        )],
    )
    resolution = DeterministicReferenceResolver().resolve(bundle)
    assert resolution.selected_result_keys == ("result_1",)
    assert resolution.ambiguous_object_keys == ()
    assert resolution.requires_clarification is False


def test_same_priority_result_ambiguity_requires_clarification():
    bundle = ResearchContextCandidateBundle(
        project_id="project",
        research_session_id="session",
        research_turn_id=uuid4(),
        active_object_candidates=[],
        result_candidates=[ReferenceCandidate(
            candidate_key=f"result_{index}",
            ref_type="SCIENTIFIC_RESULT",
            result_id=uuid4(),
            source=ReferenceCandidateSource.RECENT_CONTEXT,
            display_label=f"Result {index}",
            recency_rank=index,
        ) for index in (1, 2)],
        finding_candidates=[],
        explicit_constraints=[],
        current_research_goal=None,
        unresolved_questions=[],
        recent_messages=[],
    )
    resolution = DeterministicReferenceResolver().resolve(bundle)
    assert resolution.ambiguous_result_keys == ("result_1", "result_2")
    assert resolution.requires_clarification is True
