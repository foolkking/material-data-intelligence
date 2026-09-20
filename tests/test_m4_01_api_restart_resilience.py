from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import select, update

from mdi_api.infrastructure.interpretation.reconciler import (
    ScientificInterpretationReconciler,
)
from mdi_api.config import ApiSettings
from mdi_api.infrastructure.scientific_results.service import (
    ScientificResultSnapshotService,
)
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.reconciler import ResearchExecutionReconciler
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.schemas import CreateResearchTurnRequest, ResearchTurnStatus
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.db import (
    jobs,
    research_turns,
    scientific_result_snapshots,
)
from mdi_api.domain.scientific_results.contracts import (
    ProvenanceRecord,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificResultBundle,
)
from mdi_api.routers.auth import CurrentUser
from tests.test_agent2_phase4_execution import _factory


class CaptureExecutionQueue:
    def __init__(self) -> None:
        self.job_ids: list[str] = []

    def enqueue_job(self, job_id: str) -> dict[str, object]:
        self.job_ids.append(job_id)
        return {
            "job_id": job_id,
            "enqueued": True,
            "backend": "m4-01-test",
            "message": "queued",
        }


class CaptureInterpretationQueue:
    def __init__(self) -> None:
        self.turn_ids: list[str] = []

    def enqueue_turn(self, turn_id):
        self.turn_ids.append(str(turn_id))
        return SimpleNamespace(
            turn_id=str(turn_id),
            enqueued=True,
            backend="m4-01-test",
            message="queued",
        )


def _request(message: str, admission_key: str) -> CreateResearchTurnRequest:
    return CreateResearchTurnRequest(
        message=message,
        admission_key=admission_key,
    )


def test_f11_a_lost_response_replays_same_turn_after_api_generation_changes():
    engine, _owner, factory, _objects, service = _research_foundation()
    actor = CurrentUser(
        id="owner",
        email="owner@local.invalid",
        displayName="Owner",
        roles=[],
    )
    request = _request("继续研究当前结构", "m4-01-f11-a")

    first = service.receive_turn(
        project_id="project",
        session_id="session",
        request=request,
        current_user=actor,
    )

    # A new service instance is the API-process boundary. The second call is
    # the browser retry after the first HTTP response was lost.
    restarted_service = type(service)(factory)
    replay = restarted_service.receive_turn(
        project_id="project",
        session_id="session",
        request=request,
        current_user=actor,
    )

    with engine.connect() as connection:
        assert connection.execute(
            select(research_turns.c.id).where(
                research_turns.c.research_session_id == "session"
            )
        ).fetchall().__len__() == 1

    assert replay.turn_id == first.turn_id
    assert replay.user_message.id == first.user_message.id
    assert replay.idempotent_replay is True


def test_f11_b_restart_during_job_reconciles_existing_job_identity():
    engine, factory, turn_id = _factory()
    first_queue = CaptureExecutionQueue()
    first = ResearchExecutionDispatcher(factory, queue=first_queue).dispatch_turn(turn_id)

    # The API generation disappears while the worker-owned Job remains
    # durable. The replacement generation reconciles the same Turn/Job.
    replacement_factory = RepositoryFactory(engine)
    replacement_queue = CaptureExecutionQueue()
    recovered = ResearchExecutionReconciler(
        replacement_factory,
        queue=replacement_queue,
    ).reconcile_turn(turn_id)

    with engine.connect() as connection:
        jobs_for_turn = connection.execute(
            select(jobs.c.id).where(jobs.c.id == first.job_id)
        ).fetchall()

    assert recovered is not None
    assert recovered.job_id == first.job_id
    assert len(jobs_for_turn) == 1
    assert replacement_queue.job_ids == [first.job_id]


def test_f11_c_restart_after_result_preserves_one_scientific_result():
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(
        factory,
        queue=CaptureExecutionQueue(),
    ).dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(dispatch.job_id, "running")
        unit.repositories.jobs.set_status(dispatch.job_id, "completed")
        unit.repositories.tool_calls.save(
            {
                "id": "m4-01-call",
                "jobId": dispatch.job_id,
                "stepId": "step_1",
                "toolId": "structure.xrd",
                "status": "completed",
                "idempotencyKey": f"{dispatch.job_id}:step_1",
                "params": {},
            }
        )
    assert ResearchExecutionSupervisor(factory).sync_for_job(
        dispatch.job_id
    ).status == ResearchTurnStatus.RESULT_PENDING

    bundle = ScientificResultBundle(
        schema_version="1.0",
        result_id=uuid4(),
        project_id="project",
        research_session_id="session",
        research_turn_id=turn_id,
        research_question="Run the persisted deterministic analysis",
        source_object_refs=[],
        execution_status=ResultExecutionStatus.SUCCESS,
        relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[],
        facts=[],
        figures=[],
        tables=[],
        output_object_refs=[],
        evidence=[],
        methods=[],
        limitations=[],
        warnings=[],
        provenance=ProvenanceRecord(
            research_turn_id=turn_id,
            job_id=dispatch.job_id,
        ),
        projection_version="m4-01-test/1.0",
    )
    first_snapshot = ScientificResultSnapshotService(factory).persist_snapshot(
        bundle,
        "m4-01-result-source",
        job_id=dispatch.job_id,
    )
    with engine.begin() as connection:
        connection.execute(
            update(research_turns)
            .where(research_turns.c.id == turn_id)
            .values(status=ResearchTurnStatus.RESULT_READY.value)
        )

    replacement_factory = RepositoryFactory(engine)
    replayed_snapshot = ScientificResultSnapshotService(
        replacement_factory
    ).persist_snapshot(
        bundle,
        "m4-01-result-source",
        job_id=dispatch.job_id,
    )
    with engine.connect() as connection:
        assert connection.execute(
            select(scientific_result_snapshots.c.id).where(
                scientific_result_snapshots.c.research_turn_id == turn_id
            )
        ).fetchall().__len__() == 1

    assert replayed_snapshot["id"] == first_snapshot["id"]
    assert replayed_snapshot["bundle_json"]["result_id"] == str(bundle.result_id)


def test_f11_d_restart_around_interpretation_republishes_same_turn_only(
    monkeypatch,
):
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(
        factory,
        queue=CaptureExecutionQueue(),
    ).dispatch_turn(turn_id)
    with engine.begin() as connection:
        connection.execute(
            update(research_turns)
            .where(research_turns.c.id == turn_id)
            .values(
                status=ResearchTurnStatus.RESULT_READY.value,
                job_id=dispatch.job_id,
            )
        )

    replacement_factory = RepositoryFactory(engine)
    queue = CaptureInterpretationQueue()
    monkeypatch.setattr(
        "mdi_api.infrastructure.interpretation.reconciler.load_settings",
        lambda: ApiSettings(queue_backend="redis"),
    )
    outcome = ScientificInterpretationReconciler(
        replacement_factory,
        queue=queue,
    ).reconcile_turn(turn_id)

    assert outcome["republished"] is True
    assert queue.turn_ids == [str(turn_id)]
    with engine.connect() as connection:
        assert connection.execute(
            select(research_turns.c.id).where(research_turns.c.id == turn_id)
        ).fetchone() is not None


def _research_foundation():
    from sqlalchemy import create_engine, insert
    from sqlalchemy.pool import StaticPool

    from mdi_api.db import (
        metadata,
        organizations,
        projects,
        sessions,
        users,
    )
    from mdi_api.scientific_objects.registry import (
        build_default_object_type_registry,
    )
    from mdi_api.scientific_objects.service import ScientificObjectService
    from mdi_api.research_agent.service import ResearchTurnService

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            {
                "id": "owner",
                "email": "owner@local.invalid",
                "display_name": "Owner",
                "is_active": True,
            },
        )
        connection.execute(
            insert(organizations),
            {"id": "org", "name": "Org"},
        )
        connection.execute(
            insert(projects),
            {
                "id": "project",
                "organization_id": "org",
                "name": "Project",
                "created_by": "owner",
            },
        )
        connection.execute(
            insert(sessions),
            {
                "id": "session",
                "project_id": "project",
                "mode": "project",
                "status": "active",
                "created_by": "owner",
            },
        )
    factory = RepositoryFactory(engine)
    return (
        engine,
        CurrentUser(
            id="owner",
            email="owner@local.invalid",
            displayName="Owner",
            roles=[],
        ),
        factory,
        ScientificObjectService(factory, build_default_object_type_registry()),
        ResearchTurnService(factory),
    )
