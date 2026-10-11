from __future__ import annotations

from datetime import datetime, timedelta, timezone
import asyncio
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, update

from mdi_api.application.jobs.leases import ExecutionLeaseLost
from mdi_api.config import ApiSettings
from mdi_api.db import artifacts, jobs, metadata, research_turns
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.unit_of_work import RepositoryFactory
from tests.test_agent2_execution import CaptureQueue, _factory


def _lost_execution(*, cancel=False, age_minutes=20, lease_expired=True):
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        lease = unit.repositories.jobs.claim_execution(dispatch.job_id, owner="lost-worker", lease_seconds=3600)
        unit.repositories.tool_calls.save_for_execution({
            "id": "lost-call", "jobId": dispatch.job_id, "stepId": "step_1",
            "toolId": "structure.xrd", "status": "running", "params": {},
        }, owner=lease.owner, attempt=lease.attempt)
    ResearchExecutionSupervisor(factory).sync_for_job(dispatch.job_id)
    if cancel:
        ResearchExecutionSupervisor(factory).request_cancel(turn_id)
    old = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    with engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == dispatch.job_id).values(
            updated_at=old,
            lease_expires_at=old if lease_expired else datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(updated_at=old))
    return factory, turn_id, dispatch.job_id, lease


@pytest.mark.parametrize("cancel", [False, True])
def test_lost_execution_terminalizes_once_and_fences_late_writes(cancel):
    factory, turn_id, job_id, lease = _lost_execution(cancel=cancel)
    service = StaleResearchRecoveryService(factory, settings=ApiSettings())
    assert service.expire_stalled_execution() == 1
    assert service.expire_stalled_execution() == 0
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        job = session.repositories.jobs.get(job_id)
        calls = session.repositories.tool_calls.list_for_job(job_id)
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert turn["status"] == ("CANCELED" if cancel else "FAILED")
        assert turn["error_code"] == (None if cancel else "EXECUTION_WORKER_LOST")
        assert job["status"] == ("cancelled" if cancel else "failed")
        assert job["terminalAt"] and not job["executionOwner"] and not job["leaseExpiresAt"]
        assert calls[0]["status"] == ("skipped" if cancel else "failed")
        assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "Run the analysis"
        assert len([e for e in events if e["event_type"] == ("EXECUTION_CANCELED" if cancel else "TURN_FAILED")]) == 1
    with factory.unit_of_work() as unit:
        assert unit.repositories.jobs.claim_execution(job_id, owner="late-wakeup", lease_seconds=60) is None
        with pytest.raises(ExecutionLeaseLost):
            unit.repositories.jobs.set_status_for_execution(job_id, "completed", owner=lease.owner, attempt=lease.attempt)
    progress = ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    assert progress.status.value == turn["status"]
    assert progress.active_step_ids == []


@pytest.mark.parametrize("cancel", [False, True])
@pytest.mark.parametrize("age,expired", [(1, True), (20, False)])
def test_recent_or_live_execution_is_preserved(cancel, age, expired):
    factory, turn_id, job_id, _ = _lost_execution(cancel=cancel, age_minutes=age, lease_expired=expired)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == ("cancel_requested" if cancel else "running")
        assert session.agent2.research_turns.get(turn_id)["status"] == ("CANCELING" if cancel else "RUNNING")


def test_completed_output_is_preserved_when_another_step_loses_its_worker():
    factory, turn_id, job_id, _ = _lost_execution()
    with factory.unit_of_work() as unit:
        unit.repositories.tool_calls.save({
            "id": "finished-call", "jobId": job_id, "stepId": "finished-step",
            "toolId": "structure.summary", "status": "completed", "params": {},
        })
    with factory.engine.begin() as connection:
        connection.execute(artifacts.insert(), {
            "id": "saved-output", "project_id": "project", "dataset_id": "dataset",
            "job_id": job_id, "tool_call_id": "finished-call", "type": "table_json",
            "name": "saved.json", "version": "1", "storage_key": "unchanged/saved.json",
            "storage_provider": "local", "size_bytes": 42, "content_type": "application/json",
            "content_hash": "a" * 64, "sha256": "a" * 64, "metadata_json": {},
        })
        before = dict(connection.execute(select(artifacts)).mappings().one())
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 1
    with factory.session() as session:
        assert session.repositories.tool_calls.get("finished-call")["status"] == "completed"
        assert dict(session.connection.execute(select(artifacts)).mappings().one()) == before


def test_new_owner_winning_before_expiry_is_preserved(monkeypatch):
    factory, turn_id, job_id, _ = _lost_execution()
    from mdi_api.infrastructure.persistence.sqlalchemy_jobs import SqlAlchemyJobRepository
    original = SqlAlchemyJobRepository.expire_abandoned_execution

    def reclaim_before_expiry(self, *args, **kwargs):
        assert self.claim_execution(job_id, owner="replacement", lease_seconds=60)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(SqlAlchemyJobRepository, "expire_abandoned_execution", reclaim_before_expiry)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["executionOwner"] == "replacement"
        assert session.agent2.research_turns.get(turn_id)["status"] == "RUNNING"


@pytest.mark.parametrize("stage", ["RESULT_PENDING", "COMPLETED", "CANCELED"])
def test_newer_turn_stage_is_preserved(stage):
    factory, turn_id, job_id, _ = _lost_execution()
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=stage))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "running"


def test_startup_recovery_also_handles_a_lost_running_job():
    factory, turn_id, job_id, _ = _lost_execution()
    outcome = StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_turn(turn_id)
    assert outcome.accepted
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "failed"


def test_cancellation_intent_survives_a_missed_job_cancel_write():
    factory, turn_id, job_id, _ = _lost_execution()
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="CANCELING"))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 1
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "CANCELED"
        assert session.repositories.jobs.get(job_id)["status"] == "cancelled"


def test_job_cancellation_without_turn_wakeup_follows_canceling_transition():
    factory, turn_id, job_id, _ = _lost_execution(cancel=True)
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="RUNNING"))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 1
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "CANCELED"


def test_expiry_rolls_back_job_and_calls_if_turn_publication_fails(monkeypatch):
    factory, turn_id, job_id, _ = _lost_execution()
    with factory.session() as session:
        turn_repository_class = type(session.agent2.research_turns)

    def reject(*_args, **_kwargs):
        raise RuntimeError("injected database publication failure")

    monkeypatch.setattr(turn_repository_class, "compare_and_set_status", reject)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_execution() == 0
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "running"
        assert session.repositories.tool_calls.get("lost-call")["status"] == "running"


@pytest.mark.parametrize("backend", ["memory", "sql"])
def test_failed_job_cannot_be_claimed_until_explicitly_requeued(backend):
    if backend == "sql":
        from tests.test_m1_job_execution_leases import _repos
        repository = _repos().jobs
        job_id = "m1-job"
    else:
        from mdi_api.infrastructure.persistence.memory_jobs import InMemoryJobRepository
        repository = InMemoryJobRepository()
        job_id = "memory-job"
        repository.create({"jobId": job_id, "status": "queued"})
    lease = repository.claim_execution(job_id, owner="first", lease_seconds=30)
    repository.set_status_for_execution(job_id, "failed", owner=lease.owner, attempt=lease.attempt)
    assert repository.claim_execution(job_id, owner="duplicate", lease_seconds=30) is None
    repository.set_status(job_id, "queued")
    assert repository.claim_execution(job_id, owner="retry", lease_seconds=30).attempt == 2


def _exit_during_claimed_execution(database_path: str, job_id: str):
    """Exercise the production claim path, then lose the process mid-step."""
    from mdi_workers.queue_runtime import QueueWorkerRuntime

    class ExitingRuntime(QueueWorkerRuntime):
        def _handle_claimed_job(self, repos, job_id, **_kwargs):
            lease = self._require_active_lease()
            repos.tool_calls.save_for_execution({
                "id": "lost-call", "jobId": job_id, "stepId": "step_1",
                "toolId": "structure.xrd", "status": "running", "params": {},
            }, owner=lease.owner, attempt=lease.attempt)
            ResearchExecutionSupervisor(self.repository_factory).sync_for_job(job_id)
            os._exit(79)

    ExitingRuntime(
        repository_factory=RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}")),
        artifact_root=Path(database_path).parent / "artifacts", renewal_enabled=False,
        lease_seconds=900, worker_identity="exiting-execution-worker",
    ).handle_job(job_id)


@pytest.mark.integration
@pytest.mark.parametrize("cancel", [False, True])
def test_real_execution_worker_exit_reaches_terminal_feedback(tmp_path, monkeypatch, cancel):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses an isolated queue and SQLite database")
    from redis import Redis
    from rq import Queue, Worker

    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    database_path = tmp_path / "execution-loss.sqlite3"
    raw = engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-execution-loss-{suffix}", connection=connection)
    worker_name = f"mdi-test-execution-loss-{suffix}"
    wakeup = queue.enqueue(_exit_during_claimed_execution, str(database_path), dispatch.job_id, job_id=f"mdi-test-loss-{suffix}", job_timeout=30)
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
    try:
        result = subprocess.run(
            [sys.executable, "-c", command, redis_url, queue.name, worker_name], env=environment,
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 79, result.stderr
        assert wakeup.get_status(refresh=True).value == "started"
        with durable.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == "RUNNING"
            assert session.repositories.jobs.get(dispatch.job_id)["executionAttempt"] == 1
        if cancel:
            ResearchExecutionSupervisor(durable).request_cancel(turn_id)
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_execution() == 0
        # Only this fixture's lease/activity clock advances; production keeps
        # the configured deadline and no product record is touched.
        with durable.engine.begin() as database:
            old = datetime.now(timezone.utc) - timedelta(minutes=16)
            database.execute(update(jobs).where(jobs.c.id == dispatch.job_id).values(updated_at=old, lease_expires_at=old))
        monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _settings: durable)
        settings = ApiSettings(database_url="postgresql://unused", queue_backend="redis", agent2_orchestration_enabled=True)

        async def exercise():
            async with recovery_module.research_stage_watchdog(settings, interval_seconds=0.01):
                async def await_terminal():
                    while True:
                        with durable.session() as session:
                            if session.agent2.research_turns.get(turn_id)["status"] == ("CANCELED" if cancel else "FAILED"):
                                return
                        await asyncio.sleep(0.01)
                await asyncio.wait_for(await_terminal(), timeout=3)

        asyncio.run(exercise())
        with durable.session() as session:
            stored = session.agent2.research_turns.get(turn_id)
            assert stored["job_id"] == dispatch.job_id
            assert session.agent2.research_turns.get_message(stored["user_message_id"])["content_summary"] == "Run the analysis"
            assert session.repositories.jobs.get(dispatch.job_id)["status"] == ("cancelled" if cancel else "failed")
        assert ResearchExecutionSupervisor(durable).sync_for_job(dispatch.job_id).active_step_ids == []
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()


@pytest.fixture
def isolated_postgres_execution():
    from sqlalchemy.schema import CreateSchema, DropSchema

    url = os.getenv("MDI_TEST_DATABASE_URL")
    if not url or not url.startswith("postgresql"):
        pytest.skip("Explicit PostgreSQL MDI_TEST_DATABASE_URL required")
    schema = f"mdi_test_execution_loss_{uuid4().hex}"
    server = create_engine(url)
    source, turn_id, job_id, lease = _lost_execution()
    created = False
    scoped = server.execution_options(schema_translate_map={None: schema})
    try:
        with server.begin() as connection:
            connection.execute(CreateSchema(schema))
            created = True
        metadata.create_all(scoped)
        with source.engine.connect() as source_connection, scoped.begin() as target:
            for table in metadata.sorted_tables:
                rows = [dict(row) for row in source_connection.execute(select(table)).mappings()]
                if rows:
                    target.execute(table.insert(), rows)
        yield RepositoryFactory(scoped), turn_id, job_id, lease
    finally:
        source.engine.dispose()
        if created:
            # Only the random schema successfully created by this fixture;
            # public/product tables and their records are never modified.
            assert schema.startswith("mdi_test_execution_loss_") and len(schema) == 56
            with server.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
        server.dispose()


@pytest.mark.integration
def test_postgres_concurrent_watchdogs_commit_one_terminal_event(isolated_postgres_execution):
    factory, turn_id, job_id, _ = isolated_postgres_execution
    barrier = Barrier(2)

    def expire():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings())._expire_execution_turn(turn_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(expire) for _ in range(2)]
        assert sorted(future.result(timeout=10) for future in futures) == [False, True]
    with factory.session() as session:
        assert session.repositories.jobs.get(job_id)["status"] == "failed"
        assert len([e for e in session.agent2.research_turn_events.list_for_turn(turn_id) if e["event_type"] == "TURN_FAILED"]) == 1


@pytest.mark.integration
def test_postgres_reclaim_racing_expiry_preserves_exactly_one_owner(isolated_postgres_execution):
    factory, turn_id, job_id, _ = isolated_postgres_execution
    barrier = Barrier(2)

    def expire():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings())._expire_execution_turn(turn_id)

    def reclaim():
        barrier.wait(timeout=5)
        return factory.create_repositories().jobs.claim_execution(job_id, owner="replacement", lease_seconds=60)

    with ThreadPoolExecutor(max_workers=2) as pool:
        expiry, claim = pool.submit(expire), pool.submit(reclaim)
        ended, new_lease = expiry.result(timeout=10), claim.result(timeout=10)
    assert ended != (new_lease is not None)
    with factory.session() as session:
        job = session.repositories.jobs.get(job_id)
        assert job["status"] == ("failed" if ended else "running")
        assert job["executionOwner"] == (None if ended else "replacement")
        assert session.agent2.research_turns.get(turn_id)["status"] == ("FAILED" if ended else "RUNNING")
