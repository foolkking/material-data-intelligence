from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, update

from mdi_api.config import ApiSettings
from mdi_api.db import research_turns
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.unit_of_work import RepositoryFactory
from tests.test_research_worker_loss_recovery import _stalled_turn
from tests.test_agent2_execution import _factory as ready_execution, CaptureQueue
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher


WAITING_STAGES = ["RECEIVED", "READY_TO_PLAN", "PLAN_READY"]


@pytest.mark.parametrize("stage", WAITING_STAGES)
def test_waiting_turn_expires_once_without_losing_question_or_starting_work(monkeypatch, stage):
    factory, turn_id = _stalled_turn(stage)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _settings: factory)
    assert recovery_module._watchdog_cycle(ApiSettings()) == 1
    assert recovery_module._watchdog_cycle(ApiSettings()) == 0
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["status"] == "FAILED"
        assert turn["error_code"] == "RESEARCH_QUEUE_TIMEOUT"
        assert turn["completed_at"] is not None and turn["job_id"] is None
        assert turn["assistant_final_message_id"] is None
        assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "保留这条研究问题"
        assert [e["event_type"] for e in session.agent2.research_turn_events.list_for_turn(turn_id)] == ["TURN_FAILED"]


@pytest.mark.parametrize("stage", WAITING_STAGES)
def test_recent_queued_turn_respects_minimum_deadline(stage):
    factory, turn_id = _stalled_turn(stage, age_minutes=2)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings(agent2_startup_recovery_stale_minutes=1)).expire_stalled_pre_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage


@pytest.mark.parametrize("stage", WAITING_STAGES)
def test_new_claim_between_scan_and_read_is_preserved(monkeypatch, stage):
    factory, turn_id = _stalled_turn(stage)
    recovery = StaleResearchRecoveryService(factory, settings=ApiSettings())
    original = recovery.list_stale

    def advance(**kwargs):
        result = original(**kwargs)
        # Even when a historical writer retained the timestamp, a new version
        # must receive a new watchdog observation before expiry.
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(row_version=5))
        return result

    monkeypatch.setattr(recovery, "list_stale", advance)
    assert recovery.expire_stalled_pre_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage


@pytest.mark.parametrize("new_status", ["RESOLVING_CONTEXT", "PLANNING", "QUEUED", "CANCELED"])
def test_queue_timeout_loses_race_to_claim_dispatch_or_cancel(monkeypatch, new_status):
    factory, turn_id = _stalled_turn("PLAN_READY")
    original = ResearchTurnService.fail_if_active

    def advance(self, *args, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status=new_status, row_version=5, updated_at=datetime.now(timezone.utc),
            ))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ResearchTurnService, "fail_if_active", advance)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_pre_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == new_status
        assert not session.agent2.research_turn_events.list_for_turn(turn_id)


@pytest.mark.parametrize("action", ["INTERPRET_RESULT", "QUERY_DATA"])
def test_unclaimed_result_reuse_request_also_has_queue_deadline(action):
    factory, turn_id = _stalled_turn("RECEIVED")
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(action_type=action))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_pre_execution() == 1


def test_ready_plan_is_retained_and_attached_execution_is_not_touched():
    engine, factory, turn_id = ready_execution()
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        plan = session.repositories.analysis_plans.get_plan(str(turn["analysis_plan_id"]))
        context = session.agent2.research_context_snapshots.get_for_turn(turn_id)
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
        ))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_pre_execution() == 1
    with factory.session() as session:
        assert session.repositories.analysis_plans.get_plan(str(turn["analysis_plan_id"])) == plan
        assert session.agent2.research_context_snapshots.get_for_turn(turn_id) == context

    engine, factory, turn_id = ready_execution()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            status="PLAN_READY", updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
        ))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_pre_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(dispatch.job_id)["status"] == "queued"
        assert session.agent2.research_turns.get(turn_id)["status"] == "PLAN_READY"


def _process_delayed_turn(database_path: str, turn_id: str, stage: str):
    """Real service entry after a queue delay; any downstream work is a failure."""
    from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
    from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
    from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
    from mdi_api.research_agent.execution.errors import ExecutionPlanNotReady
    from mdi_api.research_agent.registry_validation import build_default_agent2_registries

    class UnexpectedWork:
        def __getattr__(self, name):
            raise AssertionError(f"Expired queued turn attempted downstream work: {name}")

    factory = RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}"))
    try:
        if stage == "RECEIVED":
            outcome = asyncio.run(AgentTurnProcessor(
                repository_factory=factory, registries=build_default_agent2_registries(),
                llm_client=UnexpectedWork(), planning_queue=UnexpectedWork(),
            ).process(UUID(turn_id)))
            assert outcome.status == "FAILED" and outcome.provider_calls == 0
        elif stage == "READY_TO_PLAN":
            outcome = CapabilityPlanningProcessor(factory, llm_client=UnexpectedWork()).process(UUID(turn_id))
            assert outcome["status"] == "NOOP" and outcome["turn_status"] == "FAILED"
        else:
            with pytest.raises(ExecutionPlanNotReady):
                ResearchExecutionDispatcher(factory, queue=UnexpectedWork()).dispatch_turn(UUID(turn_id))
        return "expired-turn-preserved"
    finally:
        factory.engine.dispose()


@pytest.mark.integration
@pytest.mark.parametrize("stage", WAITING_STAGES)
def test_real_delayed_rq_delivery_cannot_resume_an_expired_turn(tmp_path, stage):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses an isolated queue/database")
    from redis import Redis
    from rq import Queue, Worker

    factory, turn_id = _stalled_turn(stage, age_minutes=0)
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(action_type="ANALYZE"))
    database_path = tmp_path / "delayed-queue.sqlite3"
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-queue-wait-{suffix}", connection=connection)
    worker_name = f"mdi-test-queue-wait-{suffix}"
    wakeup = queue.enqueue(_process_delayed_turn, str(database_path), str(turn_id), stage, job_timeout=30)
    try:
        assert wakeup.get_status(refresh=True).value == "queued"
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_pre_execution() == 0
        with durable.engine.begin() as database:
            database.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
            ))
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_pre_execution() == 1
        command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
        child = subprocess.run(
            [sys.executable, "-c", command, redis_url, queue.name, worker_name],
            env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)},
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        assert child.returncode == 0, child.stderr
        assert wakeup.get_status(refresh=True).value == "finished", wakeup.exc_info
        assert wakeup.return_value() == "expired-turn-preserved"
        with durable.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            assert turn["status"] == "FAILED" and turn["job_id"] is None
            assert [e["event_type"] for e in session.agent2.research_turn_events.list_for_turn(turn_id)] == ["TURN_FAILED"]
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()
