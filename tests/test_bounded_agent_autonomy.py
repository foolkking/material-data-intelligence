from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import os
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, insert, update
from sqlalchemy.pool import StaticPool

from mdi_api.db import (
    metadata,
    organizations,
    projects,
    research_turn_events,
    research_turns,
    sessions,
    users,
)
from mdi_api.domain.scientific_results.contracts import (
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificFact,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
)
from mdi_api.research_agent.autonomy.assessment import (
    ResearchProgressAssessor,
    semantic_step_signature,
)
from mdi_api.research_agent.autonomy.evaluation import (
    GoldenAutonomyCase,
    evaluate_golden_cases,
)
from mdi_api.research_agent.autonomy.policy import CapabilityAutonomyPolicy
from mdi_api.research_agent.autonomy.schemas import (
    AutonomyPolicy,
    AutonomyProgressOutcome,
)
from mdi_api.research_agent.autonomy.service import BoundedAutonomyService
from mdi_api.research_agent.evaluation import AgentEvaluationRunner
from mdi_api.research_agent.evaluation.schemas import (
    AgentEvalCase,
    AgentEvalCategory,
    AgentEvalExpectation,
    EvalObjectCandidate,
    ExpectedToolPolicy,
)
from mdi_api.research_agent.lifecycle import build_lifecycle_projection
from mdi_api.research_agent.llm.structured_client import (
    DeepSeekStructuredLLMClient,
)
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.orchestration.queue import (
    InMemoryAgentTurnQueue,
    TurnQueueSubmitResult,
)
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES
from mdi_api.research_agent.schemas import (
    AutonomyMode,
    CreateResearchTurnRequest,
    ResearchAction,
    ResearchTurnUIContext,
)
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import (
    ScientificObjectKind,
    ScientificObjectRef,
    StorageRef,
)
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory


class FailOnceTurnQueue:
    def __init__(self) -> None:
        self.calls: list[UUID] = []
        self.failed = False

    def enqueue_turn(self, turn_id: UUID) -> TurnQueueSubmitResult:
        self.calls.append(turn_id)
        if not self.failed:
            self.failed = True
            raise RuntimeError("queue temporarily unavailable")
        return TurnQueueSubmitResult(turn_id, True, "memory", "recovered")


class ExplodingStructuredClient:
    async def generate_structured(self, **_kwargs):
        raise AssertionError("autonomous continuation must not call the LLM")


@pytest.mark.live_llm
@pytest.mark.skipif(
    os.getenv("MDI_RUN_AGENT2_LIVE") != "1"
    or not os.getenv("DEEPSEEK_KEY"),
    reason="Set MDI_RUN_AGENT2_LIVE=1 and DEEPSEEK_KEY for live qualification",
)
def test_live_provider_selects_the_bounded_trajectory_entry_before_deterministic_replanning() -> None:
    """One sanitized provider case; execution/replanning authority stays deterministic."""

    case = AgentEvalCase(
        case_id="R10-901",
        category=AgentEvalCategory.REQUIREMENT_SELECTION,
        message="Analyze the diffusion behavior in this trajectory.",
        paraphrases=[
            "Evaluate transport behavior from this trajectory.",
            "Use this trajectory to investigate diffusion.",
            "分析这条轨迹中的扩散行为。",
        ],
        object_candidates=[
            EvalObjectCandidate(
                key="obj_1",
                object_type="trajectory.atomic",
                display_name="Qualification trajectory",
                source="UI_SELECTION",
            )
        ],
        provider_decision={
            "contract_version": "1.0",
            "action": "ANALYZE",
            "assistant_message": "I will first calculate mean squared displacement.",
            "research_objective": "Analyze diffusion behavior from the selected trajectory.",
            "selected_scope_ref_keys": ["obj_1"],
            "scientific_requirements": [
                {
                    "requirement_id": "trajectory.compute_msd",
                    "criticality": "REQUIRED",
                    "subject_ref_keys": ["obj_1"],
                    "constraints": {},
                }
            ],
            "reusable_result_ref_keys": [],
            "clarification": None,
            "confidence": "HIGH",
        },
        expected=AgentEvalExpectation(
            action=ResearchAction.ANALYZE,
            selected_scope_ref_keys=["obj_1"],
            requirement_ids=["trajectory.compute_msd"],
        ),
        tool_policy=ExpectedToolPolicy.MUST_CALL_LATER,
    )
    result = asyncio.run(
        AgentEvaluationRunner(DEFAULT_AGENT2_REGISTRIES).evaluate_live(
            case,
            DeepSeekStructuredLLMClient(),
            timeout_seconds=120,
        )
    )
    assert result.passed, result

    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="trajectory.atomic",
    )
    proposal = ResearchProgressAssessor().assess(
        objective=case.message,
        current=_bundle(
            turn_id=uuid4(),
            result_id=uuid4(),
            source=source,
        ),
        completed_capability_ids={"trajectory.msd"},
    )
    assert proposal.outcome == AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS
    assert proposal.capability_id == "trajectory.diffusion"


def _bundle(
    *,
    turn_id: UUID,
    result_id: UUID,
    source: ScientificObjectRef,
    capability_id: str = "trajectory.msd",
    result_type: str = "trajectory.msd",
    status: ResultExecutionStatus = ResultExecutionStatus.SUCCESS,
) -> ScientificResultBundle:
    facts = []
    if result_type == "trajectory.msd":
        facts = [
            ScientificFact(
                fact_id="trajectory.msd.lag-count",
                predicate="trajectory.msd_lag_count",
                subject_ref=str(source.version_id),
                value=6,
                unit="count",
                source=FactSourceLocator(artifact_locator="/coverage/validLags"),
            ),
            ScientificFact(
                fact_id="trajectory.msd.first-lag",
                predicate="trajectory.msd_first_lag_time",
                subject_ref=str(source.version_id),
                value=1.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/0"),
            ),
            ScientificFact(
                fact_id="trajectory.msd.last-lag",
                predicate="trajectory.msd_last_lag_time",
                subject_ref=str(source.version_id),
                value=6.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/5"),
            ),
        ]
    return ScientificResultBundle(
        schema_version="1.0",
        result_id=result_id,
        project_id="project",
        research_session_id="session",
        research_turn_id=turn_id,
        research_question="Analyze diffusion behavior in this trajectory.",
        source_object_refs=[source],
        execution_status=status,
        relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[
            ScientificResultItem(
                id=result_type,
                result_type=result_type,
                role=ScientificResultRole.PRIMARY,
                title=result_type,
                artifact_ids=[],
                scientific_object_refs=[],
                fact_refs=[fact.fact_id for fact in facts],
                evidence_refs=[],
            )
        ],
        facts=facts,
        figures=[],
        tables=[],
        output_object_refs=[],
        evidence=[],
        methods=[
            MethodRecord(
                method_id=f"method:{capability_id}",
                capability_id=capability_id,
                capability_version="1.0",
                source_object_refs=[source],
            )
        ],
        limitations=[],
        warnings=[],
        provenance=ProvenanceRecord(
            research_turn_id=turn_id,
            source_object_version_ids=[source.version_id],
        ),
        projection_version="test.autonomy/1.0",
    )


def _foundation(
    *,
    mode: AutonomyMode = AutonomyMode.BOUNDED_AUTONOMOUS,
    capability_id: str = "trajectory.msd",
    result_type: str = "trajectory.msd",
) -> tuple[RepositoryFactory, CurrentUser, UUID, UUID, ScientificObjectRef]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    owner = CurrentUser(
        id="owner",
        email="owner@example.invalid",
        displayName="Owner",
        roles=[],
    )
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            {
                "id": owner.id,
                "email": owner.email,
                "display_name": owner.displayName,
                "is_active": True,
            },
        )
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(
            insert(projects),
            {
                "id": "project",
                "organization_id": "org",
                "name": "Project",
                "created_by": owner.id,
            },
        )
        connection.execute(
            insert(sessions),
            {
                "id": "session",
                "project_id": "project",
                "mode": "project",
                "status": "active",
                "created_by": owner.id,
            },
        )
    factory = RepositoryFactory(engine)
    objects = ScientificObjectService(factory, build_default_object_type_registry())
    logical = objects.create_object(
        project_id="project",
        kind=ScientificObjectKind.TRAJECTORY,
        object_type="trajectory.atomic",
        display_name="Qualification trajectory",
        created_by_user_id=owner.id,
    )
    version = objects.create_version(
        logical["id"],
        object_type="trajectory.atomic",
        object_schema_version="1.0",
        source_resource_refs=[{"project_id": "project"}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="minio",
            object_key="qualification/trajectory.json",
            checksum="sha-trajectory",
        ),
        content_hash="content-trajectory",
        semantic_hash="semantic-trajectory",
        canonical_metadata={"frame_count": 20, "timestep_fs": 500.0},
        created_by_user_id=owner.id,
    )
    source = ScientificObjectRef(
        object_id=logical["id"],
        version_id=version["id"],
        project_id="project",
        object_type="trajectory.atomic",
        display_name="Qualification trajectory",
    )
    received = ResearchTurnService(factory).receive_turn(
        project_id="project",
        session_id="session",
        current_user=owner,
        request=CreateResearchTurnRequest(
            message="Analyze diffusion behavior in this trajectory.",
            autonomy_mode=mode,
            ui_context=ResearchTurnUIContext(
                active_object_refs=[source],
                selection_refs=[source],
                explicit_object_refs=[source],
            ),
        ),
    )
    result_snapshot_id = uuid4()
    result_id = uuid4()
    bundle = _bundle(
        turn_id=received.turn_id,
        result_id=result_id,
        source=source,
        capability_id=capability_id,
        result_type=result_type,
    )
    now = datetime.now(timezone.utc)
    with factory.unit_of_work() as unit:
        unit.connection.execute(
            update(research_turns)
            .where(research_turns.c.id == received.turn_id)
            .values(
                status="COMPLETED",
                action_type="ANALYZE",
                completed_at=now,
                updated_at=now,
            )
        )
        unit.agent2.scientific_result_snapshots.add(
            {
                "id": result_snapshot_id,
                "project_id": "project",
                "research_turn_id": received.turn_id,
                "job_id": None,
                "schema_version": "1.0",
                "projection_version": bundle.projection_version,
                "execution_status": bundle.execution_status.value,
                "relevance_status": bundle.relevance_status.value,
                "source_fingerprint": "f" * 64,
                "bundle_json": bundle.model_dump(mode="json"),
                "created_at": now,
            }
        )
        unit.agent2.interpretations.add(
            {
                "id": uuid4(),
                "research_turn_id": received.turn_id,
                "result_snapshot_id": result_snapshot_id,
                "project_id": "project",
                "contract_version": "1.0",
                "prompt_version": "test/1.0",
                "provider": "fixture",
                "model": "fixture",
                "provider_request_id": None,
                "repair_attempted": False,
                "input_fingerprint": "i" * 64,
                "grounding_status": "VALID",
                "output_json": {"summary": "MSD evidence is available."},
                "created_at": now,
            }
        )
    return factory, owner, received.turn_id, result_snapshot_id, source


def test_autonomy_is_explicit_finite_and_matches_analysis_plan_cap() -> None:
    policy = AutonomyPolicy()
    assert policy.max_cycles == 4
    assert policy.max_capability_executions == 8
    assert policy.max_dependency_steps_per_cycle == 4
    assert policy.max_llm_decision_calls == 8
    assert policy.fingerprint == AutonomyPolicy().fingerprint


def test_quality_policy_requires_current_evidence_and_preserves_external_scope() -> None:
    policy = CapabilityAutonomyPolicy()
    diffusion = DEFAULT_AGENT2_REGISTRIES.capabilities.require(
        "trajectory.diffusion", "1.0"
    )
    qualified = policy.qualification_snapshot(diffusion)
    assert qualified.allowed_for_autonomy is True
    assert qualified.qualification_level == "DOMAIN_VALIDATED"

    electronic = DEFAULT_AGENT2_REGISTRIES.capabilities.require(
        "electronic.band_structure", "1.0"
    )
    external = policy.qualification_snapshot(electronic)
    assert external.allowed_for_autonomy is True
    assert (
        external.qualification_level
        == "EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED"
    )
    assert external.known_limitations

    stale = diffusion.model_copy(
        update={
            "qualification": diffusion.qualification.model_copy(
                update={"evidence_fingerprint": "0" * 64}
            )
        }
    )
    rejected = policy.qualification_snapshot(stale)
    assert rejected.allowed_for_autonomy is False
    assert rejected.reason_code == "QUALIFICATION_EVIDENCE_STALE_OR_MISSING"


def test_progress_assessment_is_minimum_sufficient_and_stops_causal_overclaim() -> None:
    turn_id, result_id = uuid4(), uuid4()
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="trajectory.atomic",
    )
    bundle = _bundle(turn_id=turn_id, result_id=result_id, source=source)
    assessor = ResearchProgressAssessor()
    continuation = assessor.assess(
        objective="Analyze the diffusion behavior.",
        current=bundle,
        completed_capability_ids={"trajectory.msd"},
    )
    assert continuation.outcome == AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS
    assert continuation.capability_id == "trajectory.diffusion"
    assert continuation.parameter_dict == {
        "fit_start_time_ps": 1.0,
        "fit_end_time_ps": 6.0,
    }

    sufficient = assessor.assess(
        objective="Analyze the diffusion behavior.",
        current=bundle,
        completed_capability_ids={"trajectory.msd", "trajectory.diffusion"},
    )
    assert sufficient.outcome == AutonomyProgressOutcome.GOAL_SATISFIED

    limited = assessor.assess(
        objective="Prove that this structure causes better transport.",
        current=bundle,
        completed_capability_ids={"trajectory.msd"},
    )
    assert limited.outcome == AutonomyProgressOutcome.STOP_WITH_LIMITATIONS
    assert limited.reason_codes == ("UNSUPPORTED_CAUSAL_INFERENCE",)


def test_semantic_signature_prevents_parameter_insensitive_duplicate_steps() -> None:
    source_ids = [str(uuid4()), str(uuid4())]
    first = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=source_ids,
        parameters={"fit_start_time_ps": 0.0, "fit_end_time_ps": 1.0},
    )
    replay = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=reversed(source_ids),
        parameters={"fit_end_time_ps": 1.0, "fit_start_time_ps": 0.0},
    )
    changed = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=source_ids,
        parameters={"fit_start_time_ps": 1.0, "fit_end_time_ps": 2.0},
    )
    assert first == replay
    assert changed != first


def test_diffusion_continuation_fails_closed_without_authoritative_fit_window() -> None:
    turn_id, result_id = uuid4(), uuid4()
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="trajectory.atomic",
    )
    bundle = _bundle(turn_id=turn_id, result_id=result_id, source=source)
    bundle = bundle.model_copy(
        update={
            "facts": [],
            "result_items": [
                bundle.result_items[0].model_copy(update={"fact_refs": []})
            ],
        }
    )

    assessment = ResearchProgressAssessor().assess(
        objective="Analyze the diffusion behavior.",
        current=bundle,
        completed_capability_ids={"trajectory.msd"},
    )

    assert assessment.outcome == AutonomyProgressOutcome.NEEDS_CLARIFICATION
    assert assessment.capability_id is None
    assert assessment.reason_codes == (
        "AUTHORITATIVE_DIFFUSION_FIT_WINDOW_UNAVAILABLE",
    )


def test_durable_cycle_creation_is_idempotent_and_memory_is_result_grounded() -> None:
    factory, _owner, turn_id, result_snapshot_id, source = _foundation()
    queue = InMemoryAgentTurnQueue()
    service = BoundedAutonomyService(factory, queue=queue)

    first = service.advance_after_interpretation(turn_id)
    second = service.advance_after_interpretation(turn_id)

    assert first is not None and second is not None
    assert first.outcome == AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS
    assert first.child_turn_id == second.child_turn_id
    assert first.enqueued is True
    assert second.enqueued is False
    assert first.assessment.evidence_result_ids == [result_snapshot_id]
    assert first.assessment.exact_source_version_ids == [source.version_id]
    assert first.assessment.strategy_decision is not None
    assert first.assessment.strategy_summary is not None
    assert (
        first.assessment.strategy_decision.current_question_id
        == "q-transport"
    )
    assert (
        first.assessment.strategy_summary.evidence_state_fingerprint
        == first.assessment.strategy_decision.evidence_state_fingerprint
    )
    with factory.session() as session:
        turns = session.agent2.research_turns.list_for_session("session", limit=20)
        assert len(turns) == 2
        child = session.agent2.research_turns.get(first.child_turn_id)
        assert child["parent_turn_id"] == turn_id
        assert child["continuation_of_turn_id"] == turn_id
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert (
            sum(
                event["event_type"] == "AUTONOMY_ASSESSMENT_RECORDED"
                for event in events
            )
            == 1
        )
        memories = session.agent2.research_session_memory.list_items("session")
        autonomy_memories = [
            item for item in memories if item["item_type"] == "PRIOR_FINDING"
        ]
        assert len(autonomy_memories) == 1
        assert autonomy_memories[0]["ref_json"]["epistemic_status"] == "DECISION"
        assert f"result:{result_snapshot_id}" in autonomy_memories[0]["ref_json"][
            "provenance_refs"
        ]


def test_queue_publish_failure_recovers_same_child_without_duplicate_science() -> None:
    factory, _owner, turn_id, _result_snapshot_id, _source = _foundation()
    queue = FailOnceTurnQueue()
    service = BoundedAutonomyService(factory, queue=queue)

    with pytest.raises(RuntimeError, match="temporarily unavailable"):
        service.advance_after_interpretation(turn_id)
    recovered = service.advance_after_interpretation(turn_id)

    assert recovered is not None and recovered.enqueued is True
    assert queue.calls == [recovered.child_turn_id, recovered.child_turn_id]
    with factory.session() as session:
        turns = session.agent2.research_turns.list_for_session("session", limit=20)
        assert len(turns) == 2
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert [event["event_type"] for event in events].count(
            "AUTONOMY_CHILD_TURN_CREATED"
        ) == 1
        assert any(
            event["event_type"] == "AUTONOMY_QUEUE_PUBLISH_FAILED"
            for event in events
        )
        assert any(
            event["event_type"] == "AUTONOMY_QUEUE_PUBLISHED" for event in events
        )


def test_duplicate_semantic_step_stops_without_creating_another_child() -> None:
    factory, _owner, turn_id, _result_snapshot_id, source = _foundation()
    signature = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=[str(source.version_id)],
        parameters={
            "fit_start_time_ps": 1.0,
            "fit_end_time_ps": 6.0,
        },
    )
    with factory.unit_of_work() as unit:
        unit.agent2.research_turn_events.append_turn_event(
            {
                "id": uuid4(),
                "turn_id": turn_id,
                "sequence_no": unit.agent2.research_turn_events.next_sequence_no(
                    turn_id
                ),
                "event_type": "AUTONOMY_ASSESSMENT_RECORDED",
                "payload_json": {
                    "semantic_step_signature": signature,
                    "historical_cycle": True,
                },
                "created_at": datetime.now(timezone.utc),
            }
        )

    result = BoundedAutonomyService(
        factory, queue=InMemoryAgentTurnQueue()
    ).advance_after_interpretation(turn_id)

    assert result is not None
    assert result.outcome == AutonomyProgressOutcome.NON_PROGRESS
    assert result.child_turn_id is None
    assert result.assessment.reason_codes == [
        "DUPLICATE_SEMANTIC_STEP_PREVENTED"
    ]
    with factory.session() as session:
        turns = session.agent2.research_turns.list_for_session(
            "session", limit=20
        )
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
    assert len(turns) == 1
    assert any(
        event["event_type"] == "AUTONOMY_STOPPED"
        and event["payload_json"]["stop_reason"] == "NON_PROGRESS"
        for event in events
    )


def test_cancelled_child_is_not_republished_and_completed_result_survives() -> None:
    factory, owner, turn_id, result_snapshot_id, _source = _foundation()
    first_queue = InMemoryAgentTurnQueue()
    service = BoundedAutonomyService(factory, queue=first_queue)
    first = service.advance_after_interpretation(turn_id)
    assert first is not None and first.child_turn_id is not None

    ResearchTurnService(factory).cancel_turn(first.child_turn_id, owner)
    replacement_queue = InMemoryAgentTurnQueue()
    resumed = BoundedAutonomyService(
        factory, queue=replacement_queue
    ).advance_after_interpretation(turn_id)

    assert resumed is not None
    assert resumed.outcome == AutonomyProgressOutcome.CANCELLED
    assert resumed.enqueued is False
    assert replacement_queue.pop_next() is None
    with factory.session() as session:
        assert (
            session.agent2.scientific_result_snapshots.get(result_snapshot_id)["id"]
            == result_snapshot_id
        )


def test_standard_turn_never_enters_autonomous_cycle() -> None:
    factory, _owner, turn_id, _result_snapshot_id, _source = _foundation(
        mode=AutonomyMode.STANDARD
    )
    assert (
        BoundedAutonomyService(
            factory, queue=InMemoryAgentTurnQueue()
        ).advance_after_interpretation(turn_id)
        is None
    )


def test_autonomous_child_orchestration_is_deterministic_and_result_grounded() -> None:
    factory, _owner, turn_id, result_snapshot_id, source = _foundation()
    queue = InMemoryAgentTurnQueue()
    advanced = BoundedAutonomyService(factory, queue=queue).advance_after_interpretation(
        turn_id
    )
    assert advanced is not None and advanced.child_turn_id is not None

    processed = asyncio.run(
        AgentTurnProcessor(
            repository_factory=factory,
            registries=DEFAULT_AGENT2_REGISTRIES,
            llm_client=ExplodingStructuredClient(),
        ).process(advanced.child_turn_id)
    )

    assert processed.provider_calls == 0
    assert processed.status == "READY_TO_PLAN"
    with factory.session() as session:
        decision_row = session.agent2.research_turn_decisions.get_for_turn(
            advanced.child_turn_id
        )
        snapshot = session.agent2.research_context_snapshots.get_for_turn(
            advanced.child_turn_id
        )
    decision_json = decision_row["decision_json"]
    assert decision_row["provider"] == "deterministic_bounded_autonomy"
    assert decision_json["action"] == "CONTINUE_ANALYSIS"
    assert decision_json["reusable_result_ref_keys"]
    assert (
        decision_json["scientific_requirements"][0]["requirement_id"]
        == "trajectory.estimate_diffusion"
    )
    snapshot_object_refs = [
        *(snapshot.get("selection_refs_json") or []),
        *(snapshot.get("active_scope_refs_json") or []),
    ]
    assert {item["version_id"] for item in snapshot_object_refs} == {
        str(source.version_id)
    }
    assert decision_json["reusable_result_ref_keys"] == ["result_1"]
    assert decision_json["scientific_requirements"][0]["constraints"] == {
        "fit_start_time_ps": 1.0,
        "fit_end_time_ps": 6.0,
    }
    assert str(result_snapshot_id) in str(snapshot)


def test_lifecycle_projection_exposes_bounded_autonomy_without_reasoning() -> None:
    now = datetime.now(timezone.utc)
    turn_id = uuid4()
    result_id = uuid4()
    projection = build_lifecycle_projection(
        {
            "id": turn_id,
            "status": "COMPLETED",
            "created_at": now,
            "updated_at": now,
            "completed_at": now,
        },
        events=[
            {
                "event_type": "TURN_RECEIVED",
                "sequence_no": 1,
                "created_at": now,
                "payload_json": {
                    "autonomy": {
                        "mode": "BOUNDED_AUTONOMOUS",
                        "root_turn_id": str(turn_id),
                        "cycle_index": 1,
                        "policy_version": "agent2.autonomy-policy/1.0",
                        "policy_fingerprint": "a" * 64,
                        "policy": {
                            "max_cycles": 4,
                            "max_capability_executions": 8,
                            "max_dependency_steps_per_cycle": 4,
                            "max_llm_decision_calls": 8,
                        },
                    },
                    "hidden_reasoning": "must not leak",
                },
            },
            {
                "event_type": "AUTONOMY_ASSESSMENT_RECORDED",
                "sequence_no": 2,
                "created_at": now,
                "payload_json": {
                    "assessment": {
                        "cycle_index": 1,
                        "outcome": "CONTINUE_WITH_ANALYSIS",
                        "reason_codes": ["MSD_EVIDENCE_AVAILABLE"],
                        "selected_capability_id": "trajectory.diffusion",
                        "selected_parameters": {
                            "fit_start_time_ps": 1.0,
                            "fit_end_time_ps": 6.0,
                        },
                        "evidence_result_ids": [str(result_id)],
                        "exact_source_version_ids": [str(uuid4())],
                        "qualification": {
                            "qualification_level": "DOMAIN_VALIDATED",
                            "reason_code": "QUALIFICATION_CURRENT_AND_ALLOWED",
                        },
                    }
                },
            },
        ],
    )

    autonomy = projection["autonomy"]
    assert autonomy["enabled"] is True
    assert autonomy["decision"]["selected_capability_id"] == "trajectory.diffusion"
    assert autonomy["decision"]["selected_parameters"] == {
        "fit_start_time_ps": 1.0,
        "fit_end_time_ps": 6.0,
    }
    assert autonomy["decision"]["evidence_result_ids"] == [str(result_id)]
    assert autonomy["decision"]["qualification_level"] == "DOMAIN_VALIDATED"
    assert autonomy["policy"]["max_cycles"] == 4
    assert "hidden_reasoning" not in str(autonomy)


def test_lifecycle_projection_exposes_strategy_without_hidden_reasoning() -> None:
    now = datetime.now(timezone.utc)
    turn_id = uuid4()
    projection = build_lifecycle_projection(
        {
            "id": turn_id,
            "status": "COMPLETED",
            "created_at": now,
            "updated_at": now,
            "completed_at": now,
        },
        events=[
            {
                "event_type": "TURN_RECEIVED",
                "sequence_no": 1,
                "created_at": now,
                "payload_json": {
                    "autonomy": {
                        "mode": "BOUNDED_AUTONOMOUS",
                        "cycle_index": 2,
                    }
                },
            },
            {
                "event_type": "AUTONOMY_ASSESSMENT_RECORDED",
                "sequence_no": 2,
                "created_at": now,
                "payload_json": {
                    "assessment": {
                        "outcome": "CONTINUE_WITH_ANALYSIS",
                        "strategy_decision": {
                            "action": "TEST_HYPOTHESIS",
                            "current_question_id": "q-transport-structure",
                            "evidence_state_fingerprint": "a" * 64,
                            "reasoning": "must not be projected",
                        },
                        "strategy_summary": {
                            "evidence_state_fingerprint": "a" * 64,
                            "evidence_strength": "WELL_SUPPORTED",
                            "question_count": 2,
                            "resolved_question_count": 1,
                            "open_question_count": 1,
                            "evidence_gap_count": 1,
                            "hypothesis_count": 1,
                            "unresolved_contradiction_count": 0,
                            "result_count": 2,
                            "lineage_count": 2,
                            "questions": [
                                {
                                    "question_id": "q-transport",
                                    "question_type": "QUANTIFY",
                                    "statement": "Is transport elevated?",
                                    "status": "RESOLVED",
                                    "evidence_result_ids": [],
                                    "evidence_gap_ids": [],
                                },
                                {
                                    "question_id": "q-transport-structure",
                                    "question_type": "EXPLAIN",
                                    "statement": "Does local evidence help?",
                                    "status": "OPEN",
                                    "evidence_result_ids": [],
                                    "evidence_gap_ids": [
                                        "gap-local-transport-structure"
                                    ],
                                },
                            ],
                            "current_question": {
                                "question_id": "q-transport-structure",
                                "statement": "Does local evidence help?",
                            },
                            "active_evidence_gap": {
                                "gap_id": "gap-local-transport-structure",
                                "gap_type": "STRUCTURAL_CONTEXT_MISSING",
                            },
                            "active_hypothesis": {
                                "hypothesis_id": "hypothesis-local-constraint",
                                "status": "PROPOSED",
                            },
                        },
                    }
                },
            },
        ],
    )
    strategy = projection["autonomy"]["decision"]["strategy"]
    assert strategy["action"] == "TEST_HYPOTHESIS"
    assert strategy["current_question"]["question_id"] == "q-transport-structure"
    assert strategy["questions"][0]["status"] == "RESOLVED"
    assert strategy["active_hypothesis"]["status"] == "PROPOSED"
    assert "reasoning" not in str(strategy)


def test_budget_exhaustion_is_authoritative_even_when_assessor_wants_to_continue() -> None:
    factory, _owner, turn_id, _result_snapshot_id, _source = _foundation()
    with factory.unit_of_work() as unit:
        events = unit.agent2.research_turn_events.list_for_turn(turn_id)
        received = next(event for event in events if event["event_type"] == "TURN_RECEIVED")
        payload = dict(received["payload_json"])
        autonomy = dict(payload["autonomy"])
        policy = dict(autonomy["policy"])
        policy.pop("fingerprint", None)
        policy["max_cycles"] = 1
        limited = AutonomyPolicy.model_validate(policy)
        autonomy.update(
            {
                "policy": limited.model_dump(
                    mode="json", exclude={"fingerprint"}
                ),
                "policy_version": limited.version,
                "policy_fingerprint": limited.fingerprint,
            }
        )
        payload["autonomy"] = autonomy
        unit.connection.execute(
            research_turn_events.update()
            .where(research_turn_events.c.id == received["id"])
            .values(payload_json=payload)
        )
    result = BoundedAutonomyService(
        factory, queue=InMemoryAgentTurnQueue()
    ).advance_after_interpretation(turn_id)
    assert result is not None
    assert result.outcome == AutonomyProgressOutcome.BUDGET_EXHAUSTED
    assert result.child_turn_id is None
    assert result.assessment.reason_codes == ["AUTONOMY_CYCLE_LIMIT_REACHED"]


def test_golden_autonomy_evaluation_rewards_minimum_sufficient_work() -> None:
    turn_id = uuid4()
    result_id = uuid4()
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="trajectory.atomic",
    )
    case = GoldenAutonomyCase(
        case_id="trajectory-msd-to-diffusion",
        goal="Analyze diffusion behavior in this trajectory.",
        current_result=_bundle(
            turn_id=turn_id,
            result_id=result_id,
            source=source,
        ),
        completed_capability_ids=frozenset({"trajectory.msd"}),
        expected_outcomes=frozenset(
            {AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS}
        ),
        manifests=DEFAULT_AGENT2_REGISTRIES.capabilities,
        allowed_next_capabilities=frozenset({"trajectory.diffusion"}),
        forbidden_capabilities=frozenset(
            {"structure.rdf", "xrd.powder", "ml.regression_evaluation"}
        ),
    )

    report = evaluate_golden_cases([case])

    assert report.accepted is True
    assert report.passed_cases == 1
    assert report.qualified_capability_selection_violations == 0
    assert report.redundant_executions == 0


def test_golden_autonomy_evaluation_counts_semantic_loop_prevention() -> None:
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="project",
        object_type="trajectory.atomic",
    )
    bundle = _bundle(turn_id=uuid4(), result_id=uuid4(), source=source)
    signature = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=[str(source.version_id)],
        parameters={
            "fit_start_time_ps": 1.0,
            "fit_end_time_ps": 6.0,
        },
    )
    case = GoldenAutonomyCase(
        case_id="repeat-step",
        goal="Analyze diffusion behavior in this trajectory.",
        current_result=bundle,
        completed_capability_ids=frozenset({"trajectory.msd"}),
        expected_outcomes=frozenset({AutonomyProgressOutcome.NON_PROGRESS}),
        manifests=DEFAULT_AGENT2_REGISTRIES.capabilities,
        existing_semantic_step_signatures=frozenset({signature}),
        expected_stop=True,
    )

    report = evaluate_golden_cases([case])

    assert report.accepted is True
    assert report.loop_prevention_events == 1
    assert report.correct_scientific_stops == 1
