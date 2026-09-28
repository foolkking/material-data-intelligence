from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from sqlalchemy import create_engine, insert, select
from sqlalchemy.pool import StaticPool

from mdi_api.config import ApiSettings
from mdi_api.db import (
    messages,
    metadata,
    organizations,
    projects,
    research_turn_decisions,
    research_turn_events,
    research_turns,
    sessions,
    users,
)
from mdi_api.research_agent.orchestration.queue import RedisRQAgentTurnQueue
from mdi_api.research_agent.planning.queue import RedisRQCapabilityPlanningQueue
from mdi_api.research_agent.recovery import (
    StaleResearchRecoveryService,
    is_qualification_project,
)
from mdi_api.unit_of_work import RepositoryFactory


def _factory() -> tuple[RepositoryFactory, str]:
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
                "email": "owner@example.invalid",
                "display_name": "Owner",
                "is_active": True,
            },
        )
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(
            insert(projects),
            {
                "id": "product",
                "organization_id": "org",
                "name": "Product",
                "created_by": "owner",
            },
        )
        connection.execute(
            insert(sessions),
            {
                "id": "session",
                "project_id": "product",
                "mode": "project",
                "status": "active",
                "created_by": "owner",
            },
        )
    return RepositoryFactory(engine), "session"


def test_qualification_identity_requires_bounded_actor_and_project_convention():
    assert is_qualification_project(
        project_id="agent2-phase4-project-deadbeef",
        created_by="agent2-phase4-owner-deadbeef",
    )
    assert is_qualification_project(
        project_id="project_l5_structure_deadbeef",
        created_by="phase10l5_ci",
    )
    assert is_qualification_project(
        project_id="proj_p6_1",
        created_by="test_user",
    )
    assert not is_qualification_project(
        project_id="project_0002_1a0af866391f412d",
        created_by="user_local",
    )
    assert not is_qualification_project(
        project_id="agent2-phase4-project-deadbeef",
        created_by="real-researcher",
    )


def test_stale_recovery_partitions_product_and_qualification_turns() -> None:
    factory, session_id = _factory()
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    product_message = "product-recovery-message"
    qualification_message = "qualification-recovery-message"
    with factory.engine.begin() as connection:
        connection.execute(insert(projects), {
            "id": "agent2-phase4-project-deadbeef",
            "organization_id": "org",
            "name": "Qualification",
            "created_by": "agent2-phase4-owner-deadbeef",
        })
        connection.execute(insert(sessions), {
            "id": "qualification-session",
            "project_id": "agent2-phase4-project-deadbeef",
            "mode": "project",
            "status": "active",
            "created_by": "owner",
        })
        connection.execute(insert(messages), [
            {
                "id": product_message,
                "session_id": session_id,
                "role": "user",
                "content_summary": "recover product turn",
                "payload_json": {},
                "created_at": now,
            },
            {
                "id": qualification_message,
                "session_id": "qualification-session",
                "role": "user",
                "content_summary": "retain qualification turn",
                "payload_json": {},
                "created_at": now,
            },
        ])
        connection.execute(insert(research_turns), [
            {
                "id": uuid4(),
                "project_id": "product",
                "research_session_id": session_id,
                "sequence_no": 1,
                "user_message_id": product_message,
                "status": "RECEIVED",
                "row_version": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid4(),
                "project_id": "agent2-phase4-project-deadbeef",
                "research_session_id": "qualification-session",
                "sequence_no": 1,
                "user_message_id": qualification_message,
                "status": "RECEIVED",
                "row_version": 1,
                "created_at": now,
                "updated_at": now,
            },
        ])

    product, qualification = StaleResearchRecoveryService(factory).list_stale(
        stale_minutes=15,
        limit=10,
    )

    assert len(product) == 1
    assert product[0]["project_id"] == "product"
    assert len(qualification) == 1
    assert qualification[0]["project_id"] == "agent2-phase4-project-deadbeef"


def test_legacy_query_data_recovery_terminalizes_without_scientific_execution():
    factory, session_id = _factory()
    turn_id = uuid4()
    message_id = "message_user"
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    with factory.engine.begin() as connection:
        connection.execute(
            insert(messages),
            {
                "id": message_id,
                "session_id": session_id,
                "role": "user",
                "content_summary": "列出 band_gap 样本",
                "payload_json": {},
                "created_at": now,
            },
        )
        connection.execute(
            insert(research_turns),
            {
                "id": turn_id,
                "project_id": "product",
                "research_session_id": session_id,
                "sequence_no": 1,
                "user_message_id": message_id,
                "action_type": "QUERY_DATA",
                "status": "ORCHESTRATING",
                "row_version": 5,
                "created_at": now,
                "updated_at": now,
            },
        )
        connection.execute(
            insert(research_turn_decisions),
            {
                "id": uuid4(),
                "research_turn_id": turn_id,
                "contract_version": "1.0",
                "action": "QUERY_DATA",
                "decision_json": {
                    "action": "QUERY_DATA",
                    "assistant_message": "请在数据平台查看筛选结果。",
                },
                "input_context_fingerprint": "f" * 64,
                "prompt_version": "legacy",
                "provider": "fixture",
                "model": "fixture",
                "repair_attempted": False,
                "validation_status": "VALIDATED",
                "action_dispatch_status": "READY_FOR_DOWNSTREAM",
                "created_at": now,
            },
        )

    outcome = StaleResearchRecoveryService(
        factory,
        settings=ApiSettings(),
    ).reconcile_turn(turn_id)

    assert outcome.accepted is True
    assert outcome.action == "LEGACY_QUERY_DATA_TERMINALIZED"
    with factory.engine.connect() as connection:
        turn = connection.execute(
            select(research_turns).where(research_turns.c.id == turn_id)
        ).mappings().one()
        decision = connection.execute(
            select(research_turn_decisions).where(
                research_turn_decisions.c.research_turn_id == turn_id
            )
        ).mappings().one()
        events = connection.execute(
            select(research_turn_events.c.event_type)
            .where(research_turn_events.c.turn_id == turn_id)
            .order_by(research_turn_events.c.sequence_no)
        ).scalars().all()
    assert turn["status"] == "ANSWERED"
    assert turn["assistant_final_message_id"] == f"message_recovery_{turn_id.hex}"
    assert turn["job_id"] is None
    assert decision["action_dispatch_status"] == "COMPLETED"
    assert events == ["DIRECT_ANSWER_READY", "TURN_COMPLETED"]


class _FailOnceRecoveryQueue:
    def __init__(self) -> None:
        self.failed = True
        self.calls: list[UUID] = []

    def enqueue_turn(self, turn_id: UUID) -> SimpleNamespace:
        self.calls.append(turn_id)
        if self.failed:
            self.failed = False
            raise ConnectionError("simulated Redis outage")
        return SimpleNamespace(enqueued=True, message="turn queued after recovery")


def test_queue_outage_is_retryable_without_mutating_durable_turn() -> None:
    factory, session_id = _factory()
    turn_id = uuid4()
    message_id = "message_queue_outage"
    now = datetime.now(timezone.utc) - timedelta(hours=1)
    with factory.engine.begin() as connection:
        connection.execute(
            insert(messages),
            {
                "id": message_id,
                "session_id": session_id,
                "role": "user",
                "content_summary": "run recovery-safe analysis",
                "payload_json": {},
                "created_at": now,
            },
        )
        connection.execute(
            insert(research_turns),
            {
                "id": turn_id,
                "project_id": "product",
                "research_session_id": session_id,
                "sequence_no": 1,
                "user_message_id": message_id,
                "action_type": "ANALYZE",
                "status": "RECEIVED",
                "row_version": 1,
                "created_at": now,
                "updated_at": now,
            },
        )

    queue = _FailOnceRecoveryQueue()
    service = StaleResearchRecoveryService(
        factory,
        settings=ApiSettings(queue_backend="redis"),
        orchestration_queue=queue,
    )
    unavailable = service.reconcile_turn(turn_id)
    assert unavailable.accepted is False
    assert unavailable.action == "QUEUE_UNAVAILABLE"
    assert unavailable.detail == "queue backend unavailable; durable state remains retryable"

    with factory.engine.connect() as connection:
        durable_status = connection.execute(
            select(research_turns.c.status).where(research_turns.c.id == turn_id)
        ).scalar_one()
    assert durable_status == "RECEIVED"

    recovered = service.reconcile_turn(turn_id)
    assert recovered.accepted is True
    assert recovered.action == "ORCHESTRATION_REPUBLISHED"
    assert queue.calls == [turn_id, turn_id]
    with factory.engine.connect() as connection:
        assert connection.execute(
            select(research_turns.c.status).where(research_turns.c.id == turn_id)
        ).scalar_one() == "RECEIVED"


class _FakeRQJob:
    def __init__(self, status: str) -> None:
        self.status = status
        self.deleted = False

    def get_status(self, refresh: bool = False) -> str:
        del refresh
        return self.status

    def delete(self) -> None:
        self.deleted = True


class _FakeRQQueue:
    def __init__(self, job: _FakeRQJob) -> None:
        self.job = job
        self.enqueued: list[tuple[tuple, dict]] = []

    def fetch_job(self, _job_id: str) -> _FakeRQJob:
        return self.job

    def enqueue(self, *args, **kwargs):
        self.enqueued.append((args, kwargs))


def test_terminal_orchestration_rq_identity_can_be_republished(monkeypatch):
    import redis
    import rq

    job = _FakeRQJob("failed")
    queue = _FakeRQQueue(job)
    monkeypatch.setattr(redis.Redis, "from_url", lambda _url: object())
    monkeypatch.setattr(rq, "Queue", lambda *_args, **_kwargs: queue)

    result = RedisRQAgentTurnQueue(
        redis_url="redis://example.invalid/0",
    ).enqueue_turn(uuid4())

    assert result.enqueued is True
    assert job.deleted is True
    assert len(queue.enqueued) == 1


def test_terminal_planning_rq_identity_can_be_republished(monkeypatch):
    import redis
    import rq

    job = _FakeRQJob("finished")
    queue = _FakeRQQueue(job)
    monkeypatch.setattr(redis.Redis, "from_url", lambda _url: object())
    monkeypatch.setattr(rq, "Queue", lambda *_args, **_kwargs: queue)

    result = RedisRQCapabilityPlanningQueue(
        redis_url="redis://example.invalid/0",
    ).enqueue_turn(uuid4())

    assert result.enqueued is True
    assert job.deleted is True
    assert len(queue.enqueued) == 1
