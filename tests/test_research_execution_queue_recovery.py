from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, update

from mdi_api.config import ApiSettings
from mdi_api.db import jobs, research_turns
from mdi_api.infrastructure.persistence.sqlalchemy_jobs import SqlAlchemyJobRepository
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.errors import ExecutionPlanNotReady
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.unit_of_work import RepositoryFactory
from tests.test_agent2_execution import CaptureQueue, _factory
from tests.test_research_execution_loss_recovery import isolated_postgres_execution


def _queued_execution(*, status="queued", age_minutes=20, cancel=False):
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    if cancel:
        ResearchExecutionSupervisor(factory).request_cancel(turn_id)
    with engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == dispatch.job_id).values(
            status="cancel_requested" if cancel else status,
            updated_at=datetime.now(timezone.utc) - timedelta(minutes=age_minutes),
        ))
    return factory, turn_id, dispatch.job_id


@pytest.mark.parametrize("status", ["created", "queued"])
@pytest.mark.parametrize("cancel", [False, True])
def test_unclaimed_scientific_job_ends_once_without_losing_plan_or_question(monkeypatch, status, cancel):
    factory, turn_id, job_id = _queued_execution(status=status, cancel=cancel)
    with factory.session() as session:
        before = session.agent2.research_turns.get(turn_id)
        plan = session.repositories.analysis_plans.get_plan(before["analysis_plan_id"])
        context = session.agent2.research_context_snapshots.get_for_turn(turn_id)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _settings: factory)
    assert recovery_module._watchdog_cycle(ApiSettings()) == 1
    assert recovery_module._watchdog_cycle(ApiSettings()) == 0
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        job = session.repositories.jobs.get(job_id)
        assert turn["status"] == ("CANCELED" if cancel else "FAILED")
        assert turn["error_code"] == (None if cancel else "EXECUTION_QUEUE_TIMEOUT")
        assert turn["job_id"] == job_id and turn["completed_at"] is not None
        assert job["status"] == ("cancelled" if cancel else "failed")
        assert job["executionAttempt"] == 0 and job["terminalAt"]
        assert session.repositories.tool_calls.list_for_job(job_id) == []
        assert session.repositories.analysis_plans.get_plan(before["analysis_plan_id"]) == plan
        assert session.agent2.research_context_snapshots.get_for_turn(turn_id) == context
        assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "Run the analysis"
        terminal = [e for e in session.agent2.research_turn_events.list_for_turn(turn_id) if e["event_type"] in {"TURN_FAILED", "EXECUTION_CANCELED"}]
        assert len(terminal) == 1
    assert factory.create_repositories().jobs.claim_execution(job_id, owner="late", lease_seconds=60) is None
    assert ResearchExecutionSupervisor(factory).sync_for_job(job_id).status.value == turn["status"]


@pytest.mark.parametrize("status", ["created", "queued"])
def test_recent_queue_wait_is_preserved(status):
    factory, turn_id, job_id = _queued_execution(status=status, age_minutes=2)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings(agent2_startup_recovery_stale_minutes=1)).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == status
        assert session.agent2.research_turns.get(turn_id)["status"] == "QUEUED"


def test_new_execution_claim_winning_before_expiry_is_preserved(monkeypatch):
    factory, turn_id, job_id = _queued_execution()
    original = SqlAlchemyJobRepository.expire_abandoned_execution

    def claim_first(self, *args, **kwargs):
        assert self.claim_execution(job_id, owner="new-worker", lease_seconds=60)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SqlAlchemyJobRepository, "expire_abandoned_execution", claim_first)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["executionOwner"] == "new-worker"
        assert session.agent2.research_turns.get(turn_id)["status"] == "QUEUED"


def test_active_lease_is_preserved_even_if_queue_status_is_old():
    factory, _turn_id, job_id = _queued_execution()
    with factory.engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(
            execution_owner="active-worker", lease_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        ))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0


def test_missed_job_cancel_request_still_honors_turn_intent():
    factory, turn_id, job_id = _queued_execution()
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="CANCELING"))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 1
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "cancelled"
        assert session.agent2.research_turns.get(turn_id)["status"] == "CANCELED"


def test_queued_expiry_rolls_back_if_turn_publication_fails(monkeypatch):
    factory, turn_id, job_id = _queued_execution()
    with factory.session() as session:
        turn_repository = type(session.agent2.research_turns)

    def fail(*args, **kwargs):
        raise RuntimeError("test-only publication failure")

    monkeypatch.setattr(turn_repository, "compare_and_set_status", fail)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "queued"
        assert session.repositories.tool_calls.list_for_job(job_id) == []
        assert session.agent2.research_turns.get(turn_id)["status"] == "QUEUED"


@pytest.mark.parametrize("status", ["created", "queued"])
def test_memory_repository_matches_queued_expiry_and_late_claim(status):
    from mdi_api.infrastructure.persistence.memory_jobs import InMemoryJobRepository

    repository = InMemoryJobRepository()
    repository.create({"jobId": "waiting", "status": status})
    assert repository.expire_abandoned_execution("waiting", stale_after_seconds=900) is None
    repository.records["waiting"]["updatedAt"] = (datetime.now(timezone.utc) - timedelta(minutes=16)).isoformat()
    assert repository.expire_abandoned_execution("waiting", stale_after_seconds=900)["status"] == "failed"
    assert repository.claim_execution("waiting", owner="late", lease_seconds=60) is None


@pytest.mark.parametrize("stage", ["FAILED", "CANCELED", "CANCELING", "COMPLETED"])
def test_ended_or_canceling_turn_cannot_republish_existing_job(stage):
    factory, turn_id, _job_id = _queued_execution()
    queue = CaptureQueue()
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=stage))
    with pytest.raises(ExecutionPlanNotReady):
        ResearchExecutionDispatcher(factory, queue=queue).dispatch_turn(turn_id)
    assert queue.ids == []


@pytest.mark.integration
@pytest.mark.parametrize("competitor", ["watchdog", "claim"])
def test_postgres_queue_expiry_serializes_with_claim_or_second_watchdog(isolated_postgres_execution, competitor):
    factory, turn_id, job_id, _lease = isolated_postgres_execution
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="QUEUED"))
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(
            status="queued", execution_owner=None, lease_expires_at=None, execution_attempt=0,
        ))
    barrier = Barrier(2)

    def expire():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution()

    def claim():
        barrier.wait(timeout=5)
        return factory.create_repositories().jobs.claim_execution(job_id, owner="late", lease_seconds=60)

    with ThreadPoolExecutor(max_workers=2) as pool:
        left, right = pool.submit(expire), pool.submit(expire if competitor == "watchdog" else claim)
        ended, other = left.result(timeout=10), right.result(timeout=10)
    if competitor == "watchdog":
        assert ended + other == 1
    else:
        assert bool(ended) != (other is not None)
    with factory.session() as session:
        job = session.repositories.jobs.get(job_id)
        assert job["status"] in {"failed", "running"}
        events = [e for e in session.agent2.research_turn_events.list_for_turn(turn_id) if e["event_type"] == "TURN_FAILED"]
        assert len(events) == int(job["status"] == "failed")


def _deliver_expired_scientific_job(database_path: str, job_id: str):
    from mdi_workers.queue_runtime import QueueWorkerRuntime

    class NoScientificExecution(QueueWorkerRuntime):
        def _handle_claimed_job(self, *args, **kwargs):
            raise AssertionError("An expired queued job must never enter scientific execution")

    factory = RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}"))
    try:
        result = NoScientificExecution(
            repository_factory=factory, artifact_root=Path(database_path).parent / "artifacts",
            renewal_enabled=False, worker_identity="delayed-test-worker",
        ).handle_job(job_id)
        assert not result.authoritative
        assert factory.create_repositories().jobs.get(job_id)["executionAttempt"] == 0
        return "no-science-executed"
    finally:
        factory.engine.dispose()


@pytest.mark.integration
@pytest.mark.parametrize("cancel", [False, True])
def test_real_delayed_scientific_queue_delivery_is_fenced_after_timeout(tmp_path, cancel):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; isolated queue and database only")
    from redis import Redis
    from rq import Queue, Worker

    factory, turn_id, job_id = _queued_execution(cancel=cancel)
    database_path = tmp_path / "waiting-execution.sqlite3"
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-execution-wait-{suffix}", connection=connection)
    worker_name = f"mdi-test-execution-wait-{suffix}"
    wakeup = queue.enqueue(_deliver_expired_scientific_job, str(database_path), job_id, job_timeout=30)
    try:
        assert wakeup.get_status(refresh=True).value == "queued"
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_execution() == 1
        command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
        child = subprocess.run(
            [sys.executable, "-c", command, redis_url, queue.name, worker_name],
            env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)},
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        assert child.returncode == 0, child.stderr
        assert wakeup.get_status(refresh=True).value == "finished", wakeup.exc_info
        assert wakeup.return_value() == "no-science-executed"
        with durable.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == ("CANCELED" if cancel else "FAILED")
            assert session.repositories.jobs.get(job_id)["status"] == ("cancelled" if cancel else "failed")
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()
