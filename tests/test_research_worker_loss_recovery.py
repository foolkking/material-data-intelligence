from __future__ import annotations

from datetime import datetime, timedelta, timezone
import asyncio
from threading import Event, Lock
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, insert, update

from mdi_api.config import ApiSettings
from mdi_api.db import messages, research_turn_events, research_turns
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.unit_of_work import RepositoryFactory
from tests.test_research_recovery import _factory


def _stalled_turn(status: str, *, age_minutes: int = 60):
    factory, session_id = _factory()
    turn_id = uuid4()
    message_id = f"message_loss_{turn_id.hex}"
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    with factory.engine.begin() as connection:
        connection.execute(insert(messages), {
            "id": message_id, "session_id": session_id, "role": "user",
            "content_summary": "保留这条研究问题", "payload_json": {}, "created_at": timestamp,
        })
        connection.execute(insert(research_turns), {
            "id": turn_id, "project_id": "product", "research_session_id": session_id,
            "sequence_no": 1, "user_message_id": message_id, "status": status,
            "row_version": 4, "created_at": timestamp, "updated_at": timestamp,
        })
    return factory, turn_id


@pytest.mark.parametrize("stage", ["RESOLVING_CONTEXT", "ORCHESTRATING", "PLANNING"])
def test_lost_pre_execution_worker_reaches_visible_failure_without_replaying_model(stage):
    factory, turn_id = _stalled_turn(stage)
    service = StaleResearchRecoveryService(factory, settings=ApiSettings())
    outcome = service.reconcile_turn(turn_id)
    service.reconcile_turn(turn_id)
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
        message = session.agent2.research_turns.get_message(turn["user_message_id"])
    assert outcome.accepted and outcome.action == "STALLED_STAGE_TERMINALIZED"
    assert turn["status"] == "FAILED"
    assert turn["error_code"] == "RESEARCH_STAGE_TIMEOUT"
    assert turn["completed_at"] is not None
    assert turn["job_id"] is None
    assert message["content_summary"] == "保留这条研究问题"
    assert [event["event_type"] for event in events].count("TURN_FAILED") == 1


@pytest.mark.parametrize("stage", ["RESOLVING_CONTEXT", "ORCHESTRATING", "PLANNING"])
def test_recent_pre_execution_stage_is_not_failed(stage):
    factory, turn_id = _stalled_turn(stage, age_minutes=2)
    StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_turn(turn_id)
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == []


@pytest.mark.parametrize("new_status", ["PLANNING", "RUNNING", "CANCELING", "COMPLETED"])
def test_timeout_observation_cannot_fail_newer_durable_work(monkeypatch, new_status):
    factory, turn_id = _stalled_turn("PLANNING")
    original = ResearchTurnService.fail_if_active

    def advance_then_fail(self, *args, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status=new_status, row_version=5, updated_at=datetime.now(timezone.utc),
            ))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ResearchTurnService, "fail_if_active", advance_then_fail)
    StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_turn(turn_id)
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == new_status
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == []


@pytest.mark.parametrize("stage", ["RUNNING", "CANCELING", "COMPLETED", "CANCELED"])
def test_pre_execution_deadline_does_not_terminate_science_or_terminal_stages(stage):
    factory, turn_id = _stalled_turn(stage)
    StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_turn(turn_id)
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage


def test_recovery_window_cannot_shorten_bounded_provider_calls():
    factory, turn_id = _stalled_turn("PLANNING", age_minutes=2)
    service = StaleResearchRecoveryService(factory, settings=ApiSettings(agent2_startup_recovery_stale_minutes=1))
    service.reconcile_turn(turn_id)
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "PLANNING"


def test_watchdog_rechecks_candidate_and_never_enqueues_newer_ready_work(monkeypatch):
    factory, turn_id = _stalled_turn("PLANNING")
    service = StaleResearchRecoveryService(factory, settings=ApiSettings())
    original = service.list_stale

    def advance_after_listing(**kwargs):
        result = original(**kwargs)
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status="READY_TO_PLAN", row_version=5,
            ))
        return result

    monkeypatch.setattr(service, "list_stale", advance_after_listing)
    assert service.expire_stalled_pre_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "READY_TO_PLAN"
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == []


def test_periodic_watchdog_survives_failure_without_blocking_requests_or_overlapping_cycles(monkeypatch):
    factory, turn_id = _stalled_turn("ORCHESTRATING")
    entered, release = Event(), Event()
    lock = Lock()
    calls = 0
    active = 0
    max_active = 0

    def cycle(_settings):
        nonlocal calls, active, max_active
        with lock:
            calls += 1
            current = calls
            active += 1
            max_active = max(max_active, active)
        try:
            if current == 1:
                entered.set()
                assert release.wait(timeout=5)
                raise ConnectionError("private-watchdog-exception-sentinel")
            return StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_pre_execution()
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(recovery_module, "_watchdog_cycle", cycle)
    settings = ApiSettings(database_url="postgresql://unused", queue_backend="redis", agent2_orchestration_enabled=True)

    async def exercise():
        try:
            async with recovery_module.research_stage_watchdog(settings, interval_seconds=0.01):
                assert await asyncio.to_thread(entered.wait, 2)
                # An API coroutine can run while the database worker is held.
                assert await asyncio.wait_for(asyncio.sleep(0, result="request served"), timeout=0.2) == "request served"
                release.set()

                async def await_failure_state():
                    while True:
                        with factory.session() as session:
                            if session.agent2.research_turns.get(turn_id)["status"] == "FAILED":
                                return
                        await asyncio.sleep(0.01)

                await asyncio.wait_for(await_failure_state(), timeout=3)
            stopped_at = calls
            await asyncio.sleep(0.04)
            assert calls == stopped_at
        finally:
            release.set()

    asyncio.run(exercise())
    assert calls >= 2 and max_active == 1 and active == 0


def test_disabled_watchdog_does_not_open_database(monkeypatch):
    calls = []
    def unexpected(_settings):
        calls.append(True)
        return 0

    monkeypatch.setattr(recovery_module, "_watchdog_cycle", unexpected)

    async def exercise():
        async with recovery_module.research_stage_watchdog(ApiSettings()):
            await asyncio.sleep(0.01)

    asyncio.run(exercise())
    assert calls == []


def _exit_after_stage_claim(database_path: str, turn_id: str):
    """Test-only RQ target: exit without running any exception/finally handler."""
    connection = sqlite3.connect(database_path)
    connection.execute(
        "UPDATE research_turns SET status = 'ORCHESTRATING', row_version = row_version + 1, updated_at = datetime('now') WHERE id = ?",
        (turn_id.replace("-", ""),),
    )
    connection.commit()
    connection.close()
    os._exit(77)


@pytest.mark.integration
def test_actual_worker_exit_is_terminalized_by_a_later_watchdog_cycle(tmp_path, monkeypatch):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses an isolated queue and SQLite database")
    from redis import Redis
    from rq import Queue, Worker

    factory, turn_id = _stalled_turn("RECEIVED")
    database_path = tmp_path / "worker-loss.sqlite3"
    # Only this test's data is copied to its owned disposable child directory.
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-worker-loss-{suffix}", connection=connection)
    worker_name = f"mdi-test-worker-loss-{suffix}"
    wakeup = queue.enqueue(_exit_after_stage_claim, str(database_path), str(turn_id), job_id=f"mdi-test-loss-job-{suffix}", job_timeout=30)
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
    try:
        result = subprocess.run(
            [sys.executable, "-c", command, redis_url, queue.name, worker_name],
            env=environment, cwd=Path(__file__).resolve().parents[1],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 77, result.stderr
        with durable.session() as session:
            stored = session.agent2.research_turns.get(turn_id)
            assert stored["status"] == "ORCHESTRATING"
            assert not session.agent2.research_turn_events.list_for_turn(turn_id)
        assert wakeup.get_status(refresh=True).value == "started"

        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_pre_execution() == 0
        # Advance this fixture's inactivity clock, without changing any product
        # record or waiting for the production fifteen-minute deadline.
        with durable.engine.begin() as database:
            database.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
            ))
        monkeypatch.setattr(recovery_module, "_watchdog_cycle", lambda settings: StaleResearchRecoveryService(durable, settings=settings).expire_stalled_pre_execution())
        settings = ApiSettings(database_url="postgresql://unused", queue_backend="redis", agent2_orchestration_enabled=True)

        async def exercise():
            async with recovery_module.research_stage_watchdog(settings, interval_seconds=0.01):
                async def await_terminal():
                    while True:
                        with durable.session() as session:
                            if session.agent2.research_turns.get(turn_id)["status"] == "FAILED":
                                return
                        await asyncio.sleep(0.01)
                await asyncio.wait_for(await_terminal(), timeout=3)

        asyncio.run(exercise())
        with durable.session() as session:
            stored = session.agent2.research_turns.get(turn_id)
            assert stored["error_code"] == "RESEARCH_STAGE_TIMEOUT"
            assert stored["job_id"] is None
            assert session.agent2.research_turns.get_message(stored["user_message_id"])["content_summary"] == "保留这条研究问题"
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()
