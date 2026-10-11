from __future__ import annotations

from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, update

from mdi_api.config import ApiSettings
from mdi_api.db import analysis_plans, artifacts, jobs, research_turns
from mdi_api.infrastructure.scientific_results.queue import InMemoryResultProjectionQueue, RedisRQResultProjectionQueue
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.research_agent.schemas import ResearchTurnEventType
from mdi_api.unit_of_work import RepositoryFactory
from mdi_api.repositories import compute_plan_hash
from mdi_schemas import AnalysisPlanV02
from tests.test_agent2_execution import CaptureQueue, _factory
from tests.test_research_execution_loss_recovery import isolated_postgres_execution


def _finished_execution(job_status="completed", turn_status="RUNNING"):
    engine, factory, turn_id = _factory()
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    with factory.unit_of_work() as unit:
        unit.repositories.tool_calls.save({
            "id": "finished-call", "jobId": job_id, "stepId": "step_1", "toolId": "structure.xrd",
            "status": "completed" if job_status == "completed" else "failed", "params": {},
        })
    old = datetime.now(timezone.utc) - timedelta(minutes=20)
    with engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(status=job_status, updated_at=old, terminal_at=old))
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=turn_status, updated_at=old))
    return factory, turn_id, job_id


@pytest.mark.parametrize("job_status,target", [("completed", "RESULT_PENDING"), ("failed", "FAILED"), ("cancelled", "CANCELED")])
@pytest.mark.parametrize("turn_status", ["QUEUED", "RUNNING", "CANCELING"])
def test_periodic_recovery_syncs_committed_job_without_reexecuting(monkeypatch, job_status, target, turn_status):
    factory, turn_id, job_id = _finished_execution(job_status, turn_status)
    with factory.session() as session:
        before = session.repositories.jobs.get(job_id)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda settings: factory)
    assert recovery_module._watchdog_cycle(ApiSettings()) == 1
    assert recovery_module._watchdog_cycle(ApiSettings()) == 0
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["status"] == target
        assert session.repositories.jobs.get(job_id) == before
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) is not None
        assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "Run the analysis"


def _pending_result():
    factory, turn_id, job_id = _finished_execution()
    ResearchExecutionSupervisor(factory).sync_for_job(job_id)
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
            updated_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        ))
    return factory, turn_id, job_id


def test_result_publish_failure_recovers_same_identity_without_resetting_deadline():
    factory, turn_id, job_id = _pending_result()

    class UnavailableQueue(InMemoryResultProjectionQueue):
        def enqueue_turn(self, turn_id):
            raise ConnectionError("test-only queue unavailable")

    service = StaleResearchRecoveryService(factory, settings=ApiSettings(), result_queue=UnavailableQueue())
    with factory.session() as session:
        before = session.agent2.research_turns.get(turn_id)
        job_before = session.repositories.jobs.get(job_id)
    assert service.republish_unstarted_results() == 0
    service.result_queue = InMemoryResultProjectionQueue()
    assert service.republish_unstarted_results() == 1
    assert service.republish_unstarted_results() == 0
    assert service.result_queue.pop_next() == turn_id
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id) == before
        assert session.repositories.jobs.get(job_id) == job_before


@pytest.mark.parametrize("condition", ["started", "expired", "disabled", "recent", "ended"])
def test_result_wakeup_respects_started_work_deadline_and_settings(condition):
    factory, turn_id, _ = _pending_result()
    if condition == "started":
        with factory.unit_of_work() as unit:
            recovery_module.StaleResearchRecoveryService._append_event(unit, turn_id, ResearchTurnEventType.RESULT_PROJECTION_STARTED, {})
    elif condition in {"expired", "recent", "ended"}:
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=20 if condition == "expired" else 0),
                status="FAILED" if condition == "ended" else "RESULT_PENDING",
            ))
    queue = InMemoryResultProjectionQueue()
    service = StaleResearchRecoveryService(factory, settings=ApiSettings(agent2_result_projection_enabled=condition != "disabled"), result_queue=queue)
    assert service.republish_unstarted_results() == 0
    assert queue.pop_next() is None


@pytest.mark.parametrize("status", ["QUEUED", "RUNNING", "CANCELING"])
def test_startup_recovery_never_republishes_completed_scientific_job(status):
    factory, turn_id, _ = _finished_execution(turn_status=status)
    execution, result = CaptureQueue(), InMemoryResultProjectionQueue()
    outcome = StaleResearchRecoveryService(factory, settings=ApiSettings(), execution_queue=execution, result_queue=result).reconcile_turn(turn_id)
    assert outcome.accepted and execution.ids == []
    assert result.pop_next() == turn_id


@pytest.mark.parametrize("status", ["running", "queued"])
def test_job_changed_after_scan_is_not_projected_as_terminal(monkeypatch, status):
    factory, turn_id, job_id = _finished_execution()
    original = ResearchExecutionSupervisor.sync_for_job

    def raced(self, *args, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(jobs).where(jobs.c.id == job_id).values(status=status))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ResearchExecutionSupervisor, "sync_for_job", raced)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) is None


def test_newer_turn_after_scan_is_preserved(monkeypatch):
    factory, turn_id, job_id = _finished_execution()
    original = ResearchExecutionSupervisor.sync_for_job

    def raced(self, *args, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="INTERPRETING", row_version=100))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ResearchExecutionSupervisor, "sync_for_job", raced)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) is None
        assert session.agent2.research_turns.get(turn_id)["row_version"] == 100


def test_partial_execution_preserves_saved_output_and_summary():
    factory, turn_id, job_id = _finished_execution()
    with factory.engine.begin() as connection:
        plan = connection.execute(select(analysis_plans.c.analysis_plan_json)).scalar_one()
        plan["steps"].append({**plan["steps"][0], "stepId": "uncompleted"})
        connection.execute(update(analysis_plans).values(analysis_plan_json=plan, plan_hash=compute_plan_hash(AnalysisPlanV02.model_validate(plan))))
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(status="partial_success"))
        connection.execute(artifacts.insert(), {
            "id": "saved-xrd", "project_id": "project", "dataset_id": "dataset", "job_id": job_id,
            "tool_call_id": "finished-call", "type": "table_json", "name": "saved.json", "version": "1",
            "storage_key": "retained/saved.json", "storage_provider": "local", "size_bytes": 42,
            "content_type": "application/json", "content_hash": "a" * 64, "sha256": "a" * 64, "metadata_json": {},
        })
        before = dict(connection.execute(select(artifacts)).mappings().one())
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution() == 1
    with factory.session() as session:
        summary = session.agent2.research_execution_summaries.get_for_turn(turn_id)
        assert summary["execution_outcome"] == "PARTIAL"
        assert session.agent2.research_turns.get(turn_id)["status"] == "RESULT_PENDING"
        assert dict(session.connection.execute(select(artifacts)).mappings().one()) == before


@pytest.mark.integration
def test_postgres_competing_recovery_writes_one_summary(isolated_postgres_execution):
    factory, turn_id, job_id, _ = isolated_postgres_execution
    with factory.engine.begin() as connection:
        connection.execute(update(jobs).where(jobs.c.id == job_id).values(status="failed", execution_owner=None, lease_expires_at=None))
    barrier = Barrier(2)

    def recover():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution()

    with ThreadPoolExecutor(max_workers=2) as pool:
        left, right = pool.submit(recover), pool.submit(recover)
        assert left.result(timeout=10) + right.result(timeout=10) == 1
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "FAILED"
        assert len([event for event in session.agent2.research_turn_events.list_for_turn(turn_id) if event["event_type"] == "EXECUTION_FAILED"]) == 1


@pytest.fixture
def isolated_result_queue():
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    from redis import Redis
    from rq import Queue
    from rq.job import Job

    connection = Redis.from_url(redis_url)
    turn_id = uuid4()
    queue = Queue(f"mdi-test-result-handoff-{uuid4().hex}", connection=connection)
    try:
        yield redis_url, connection, queue, turn_id
    finally:
        job_id = f"agent2-result-{turn_id}"
        queue.remove(job_id)
        if connection.exists(Job.key_for(job_id)):
            Job.fetch(job_id, connection=connection).delete()
        connection.srem("rq:queues", queue.key)
        connection.close()


@pytest.mark.integration
@pytest.mark.parametrize("existing", [False, True])
def test_real_result_queue_concurrent_publication_is_unique(isolated_result_queue, existing):
    redis_url, connection, queue, turn_id = isolated_result_queue
    from rq.job import JobStatus
    if existing:
        receipt = queue.enqueue("builtins.str", "old", job_id=f"agent2-result-{turn_id}")
        queue.remove(receipt.id)
        receipt.set_status(JobStatus.FAILED)
    barrier = Barrier(2)

    def publish():
        barrier.wait(timeout=5)
        return RedisRQResultProjectionQueue(redis_url=redis_url, queue_name=queue.name).enqueue_turn(turn_id)

    with ThreadPoolExecutor(max_workers=2) as pool:
        left, right = pool.submit(publish), pool.submit(publish)
        assert sum(result.enqueued for result in [left.result(timeout=10), right.result(timeout=10)]) == 1
    assert queue.job_ids == [f"agent2-result-{turn_id}"]
    job = queue.fetch_job(queue.job_ids[0])
    assert job.args == (str(turn_id),)


@pytest.mark.integration
def test_real_result_queue_foreign_identity_is_preserved(isolated_result_queue):
    redis_url, connection, queue, turn_id = isolated_result_queue
    job = queue.enqueue("builtins.str", "owned", job_id=f"agent2-result-{turn_id}")
    with pytest.raises(RuntimeError, match="ownership"):
        RedisRQResultProjectionQueue(redis_url=redis_url, queue_name=f"other-{queue.name}").enqueue_turn(turn_id)
    assert queue.fetch_job(job.id).args == ("owned",)


def test_summary_and_turn_roll_back_together_after_sync_failure(monkeypatch):
    factory, turn_id, job_id = _finished_execution()
    with factory.session() as session:
        repository = type(session.agent2.research_turns)

    def fail(*args, **kwargs):
        raise RuntimeError("test-only sync commit failure")

    monkeypatch.setattr(repository, "compare_and_set_status", fail)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).reconcile_finished_execution() == 0
    with factory.session() as session:
        assert session.agent2.research_execution_summaries.get_for_turn(turn_id) is None
        assert session.agent2.research_turns.get(turn_id)["status"] == "RUNNING"
        assert session.repositories.jobs.get(job_id)["status"] == "completed"


def _commit_execution_and_exit(database_path: str, job_id: str, terminal: str):
    from mdi_workers.queue_runtime import QueueWorkerRuntime

    class ExitingRuntime(QueueWorkerRuntime):
        def _handle_claimed_job(self, repos, job_id, **kwargs):
            lease = self._require_active_lease()
            with self.repository_factory.unit_of_work() as unit:
                unit.repositories.tool_calls.save_for_execution({
                    "id": "committed-call", "jobId": job_id, "stepId": "step_1", "toolId": "structure.xrd",
                    "status": "completed" if terminal == "completed" else "failed", "params": {},
                }, owner=lease.owner, attempt=lease.attempt)
                unit.repositories.jobs.set_status_for_execution(job_id, terminal, owner=lease.owner, attempt=lease.attempt)
            os._exit(77)

    ExitingRuntime(
        repository_factory=RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}")),
        artifact_root=Path(database_path).parent / "artifacts", renewal_enabled=False,
        worker_identity="test-handoff-worker",
    ).handle_job(job_id)


@pytest.mark.integration
@pytest.mark.parametrize("terminal", ["completed", "failed"])
def test_actual_worker_exit_after_job_commit_recovers_without_browser(tmp_path, monkeypatch, terminal):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    from redis import Redis
    from rq import Queue, Worker

    engine, factory, turn_id = _factory()
    job_id = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id).job_id
    database_path = tmp_path / "handoff.sqlite3"
    raw = engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    name = f"mdi-test-committed-execution-{uuid4().hex}"
    queue = Queue(name, connection=connection)
    wakeup = queue.enqueue(_commit_execution_and_exit, str(database_path), job_id, terminal, job_timeout=30)
    try:
        command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[2]).work(burst=True,logging_level='CRITICAL')"
        child = subprocess.run(
            [sys.executable, "-c", command, redis_url, name],
            env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)},
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
        )
        assert child.returncode == 77, child.stderr
        assert wakeup.get_status(refresh=True).value == "started"
        with durable.session() as session:
            assert session.repositories.jobs.get(job_id)["status"] == terminal
            assert session.agent2.research_turns.get(turn_id)["status"] == "QUEUED"
        # Advance only this isolated fixture's post-commit grace period.
        with durable.engine.begin() as database:
            database.execute(update(jobs).where(jobs.c.id == job_id).values(updated_at=datetime.now(timezone.utc) - timedelta(minutes=2)))
        monkeypatch.setattr(recovery_module, "create_repository_factory", lambda settings: durable)
        assert recovery_module._watchdog_cycle(ApiSettings()) == 1
        with durable.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == ("RESULT_PENDING" if terminal == "completed" else "FAILED")
            assert session.repositories.jobs.get(job_id)["executionAttempt"] == 1
            assert len(session.repositories.tool_calls.list_for_job(job_id)) == 1
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()
