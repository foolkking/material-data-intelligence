from __future__ import annotations

from types import SimpleNamespace
import os
from uuid import uuid4

import pytest
from sqlalchemy import func, select, update

from mdi_api import research_agent_planning_worker, research_agent_worker
from mdi_api.bootstrap import repository_factory as factory_module
from mdi_api.db import jobs, research_turn_events, research_turns
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.errors import ExecutionQueuePublishFailed
from mdi_api.research_agent.execution.reconciler import ResearchExecutionReconciler
from mdi_api.research_agent.orchestration import worker as orchestration_worker
from mdi_api.research_agent.planning import worker as planning_worker
from mdi_api.transport.routers import agent2 as agent2_router
from mdi_api.routers.auth import CurrentUser
from tests.test_agent2_execution import FailOnceQueue, _factory
from mdi_workers.queue_runtime import RedisRQQueueBackend


@pytest.mark.parametrize("boundary, stage", [
    ("orchestration", "PLANNING"),
    ("orchestration", "RUNNING"),
    ("orchestration", "INTERPRETING"),
    ("planning", "RUNNING"),
    ("planning", "RESULT_PENDING"),
    ("planning", "CANCELING"),
    ("planning", "COMPLETED"),
])
def test_late_worker_failure_cannot_overwrite_downstream_progress(monkeypatch, boundary, stage):
    engine, factory, turn_id = _factory()
    monkeypatch.setattr(factory_module, "create_repository_factory", lambda: factory)
    implementation, shim, name = (
        (orchestration_worker, research_agent_worker, "run_queued_turn")
        if boundary == "orchestration"
        else (planning_worker, research_agent_planning_worker, "run_queued_planning")
    )

    def late_failure(_turn_id):
        # Another consumer has already advanced the durable Turn before the
        # preceding worker observes its delayed transport/cleanup exception.
        with engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=stage))
        raise RuntimeError("previous stage failed after handoff")

    monkeypatch.setattr(implementation, name, late_failure)
    with pytest.raises(RuntimeError, match="previous stage"):
        getattr(shim, name)(str(turn_id))
    with factory.session() as session:
        stored = session.agent2.research_turns.get(turn_id)
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
    assert stored["status"] == stage
    assert stored["error_code"] is None
    assert not any(item["event_type"] == "TURN_FAILED" for item in events)


def test_execution_publish_outage_remains_recoverable_through_planning_worker(monkeypatch):
    engine, factory, turn_id = _factory()
    monkeypatch.setattr(factory_module, "create_repository_factory", lambda: factory)
    monkeypatch.setattr(agent2_router, "create_repository_factory", lambda: factory)
    queue = FailOnceQueue()
    dispatcher = ResearchExecutionDispatcher(factory, queue=queue)
    processor = SimpleNamespace(process=lambda _turn_id: {"status": "PLAN_READY"})
    monkeypatch.setattr(planning_worker, "run_queued_planning", lambda identity: planning_worker._process_and_dispatch(identity, processor=processor, dispatcher=dispatcher))

    with pytest.raises(ExecutionQueuePublishFailed):
        research_agent_planning_worker.run_queued_planning(str(turn_id))
    with factory.session() as session:
        stored = session.agent2.research_turns.get(turn_id)
    assert stored["status"] == "QUEUED"
    assert stored["error_code"] is None
    actor = CurrentUser(id="owner", email="owner@example.invalid", displayName="Owner", roles=[])
    pending = agent2_router.get_research_turn_progress(turn_id, actor)
    assert pending["execution_dispatch_pending"] is True
    assert any(item["code"] == "EXECUTION_QUEUE_PUBLISH_PENDING" for item in pending["warnings"])
    recovered = ResearchExecutionReconciler(factory, queue=queue).reconcile_turn(turn_id)
    assert recovered.job_id == stored["job_id"]
    assert queue.ids == [stored["job_id"], stored["job_id"]]
    confirmed = agent2_router.get_research_turn_progress(turn_id, actor)
    assert confirmed["execution_dispatch_pending"] is False
    assert not any(item["code"] == "EXECUTION_QUEUE_PUBLISH_PENDING" for item in confirmed["warnings"])
    with engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(jobs)).scalar_one() == 1
        assert connection.execute(select(func.count()).select_from(research_turn_events).where(research_turn_events.c.event_type == "TURN_FAILED")).scalar_one() == 0


@pytest.mark.parametrize("boundary, stage", [
    ("orchestration", "RECEIVED"),
    ("orchestration", "RESOLVING_CONTEXT"),
    ("orchestration", "ORCHESTRATING"),
    ("orchestration", "READY_TO_PLAN"),
    ("planning", "READY_TO_PLAN"),
    ("planning", "PLANNING"),
    ("planning", "PLAN_READY"),
])
def test_owned_worker_failure_is_terminal_and_does_not_persist_exception_details(monkeypatch, boundary, stage):
    engine, factory, turn_id = _factory()
    monkeypatch.setattr(factory_module, "create_repository_factory", lambda: factory)
    with engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status=stage))
    shim = research_agent_worker if boundary == "orchestration" else research_agent_planning_worker
    shim._persist_worker_boundary_failure(str(turn_id), RuntimeError("private-credential-sentinel"))
    # Duplicate failure notifications cannot append another terminal event.
    shim._persist_worker_boundary_failure(str(turn_id), RuntimeError("again"))
    with factory.session() as session:
        stored = session.agent2.research_turns.get(turn_id)
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
    assert stored["status"] == "FAILED" and stored["completed_at"] is not None
    assert "private-credential-sentinel" not in stored["error_summary"]
    assert [item["event_type"] for item in events].count("TURN_FAILED") == 1


def test_existing_queue_receipt_confirms_dispatch_without_enqueuing_again():
    _engine, factory, turn_id = _factory()
    queue = SimpleNamespace(enqueue_job=lambda job_id: SimpleNamespace(enqueued=False, already_queued=True, backend="rq", message="already present"))
    result = ResearchExecutionDispatcher(factory, queue=queue).dispatch_turn(turn_id)
    assert result.queued is True
    with factory.session() as session:
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
    assert not agent2_router._execution_dispatch_pending("QUEUED", events)


@pytest.mark.parametrize("status", ["queued", "started", "deferred", "scheduled", "failed", "finished", "stopped", "canceled"])
def test_execution_queue_distinguishes_live_receipts_from_terminal_wakeups(monkeypatch, status):
    from contextlib import nullcontext
    import redis
    import rq
    from rq.job import Job

    actions = []
    receipt = SimpleNamespace(origin="owned-queue", get_status=lambda **_: status, delete=lambda **_: actions.append("delete"))
    queue = SimpleNamespace(fetch_job=lambda _: receipt, enqueue=lambda *_, **__: actions.append("enqueue"))
    pipeline = SimpleNamespace(watch=lambda _: None, multi=lambda: None, execute=lambda: None)
    connection = SimpleNamespace(pipeline=lambda: nullcontext(pipeline), close=lambda: None)
    monkeypatch.setattr(redis.Redis, "from_url", lambda *_: connection)
    monkeypatch.setattr(rq, "Queue", lambda *_, **__: queue)
    monkeypatch.setattr(Job, "fetch", lambda *_, **__: receipt)
    result = RedisRQQueueBackend(redis_url="redis://unused", queue_name="owned-queue").enqueue_job("owned-job")
    active = status in {"queued", "started", "deferred", "scheduled"}
    assert result.already_queued is active
    assert result.enqueued is not active
    assert actions == ([] if active else ["delete", "enqueue"])


@pytest.mark.integration
def test_real_rq_lost_execution_ack_recovers_same_job_after_planning_failure(monkeypatch):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses isolated temporary queues")
    from redis import Redis
    from rq import Queue, SimpleWorker

    engine, factory, turn_id = _factory()
    monkeypatch.setattr(factory_module, "create_repository_factory", lambda: factory)
    connection = Redis.from_url(redis_url)
    connection.ping()
    suffix = uuid4().hex
    planning_queue = Queue(f"mdi-test-handoff-planning-{suffix}", connection=connection)
    execution_queue = Queue(f"mdi-test-handoff-execution-{suffix}", connection=connection)
    backend = RedisRQQueueBackend(redis_url=redis_url, queue_name=execution_queue.name)

    class LoseFirstAck:
        lost = False

        def enqueue_job(self, job_id):
            result = backend.enqueue_job(job_id)
            if not self.lost:
                self.lost = True
                raise ConnectionError("controlled lost execution queue acknowledgement")
            return result

    queue = LoseFirstAck()
    dispatcher = ResearchExecutionDispatcher(factory, queue=queue)
    processor = SimpleNamespace(process=lambda _: {"status": "PLAN_READY"})
    monkeypatch.setattr(planning_worker, "run_queued_planning", lambda identity: planning_worker._process_and_dispatch(identity, processor=processor, dispatcher=dispatcher))
    wakeup = planning_queue.enqueue(research_agent_planning_worker.run_queued_planning, str(turn_id), job_id=f"mdi-test-handoff-{suffix}", job_timeout=30, failure_ttl=300, result_ttl=300)
    job_id = f"job_agent2_{turn_id.hex}"
    try:
        SimpleWorker([planning_queue], connection=connection, name=f"mdi-test-handoff-{suffix}").work(burst=True, max_jobs=1, logging_level="CRITICAL")
        assert str(getattr(wakeup.get_status(refresh=True), "value", "")) == "failed"
        with factory.session() as session:
            stored = session.agent2.research_turns.get(turn_id)
            events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert stored["status"] == "QUEUED"
        assert agent2_router._execution_dispatch_pending("QUEUED", events)
        assert execution_queue.get_job_ids() == [job_id]
        recovered = ResearchExecutionReconciler(factory, queue=queue).reconcile_turn(turn_id)
        assert recovered.queued is True and recovered.job_id == job_id
        assert execution_queue.get_job_ids() == [job_id]
        with factory.session() as session:
            events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert not agent2_router._execution_dispatch_pending("QUEUED", events)
        with engine.connect() as db:
            assert db.execute(select(func.count()).select_from(jobs)).scalar_one() == 1
    finally:
        # These exact random test queues/identities are created above. Never
        # empty Redis or consume a product queue during fault injection.
        planning_queue.remove(wakeup.id)
        wakeup.delete()
        receipt = execution_queue.fetch_job(job_id)
        if receipt is not None:
            execution_queue.remove(job_id)
            receipt.delete()
        connection.srem("rq:queues", planning_queue.key, execution_queue.key)
        connection.close()
        engine.dispose()


@pytest.mark.integration
@pytest.mark.parametrize("prior_status", [None, "failed"])
def test_real_rq_concurrent_recovery_publishes_one_execution_wakeup(monkeypatch, prior_status):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses isolated temporary queues")
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier, Lock, get_ident
    from redis import Redis
    from rq import Queue
    from rq.exceptions import NoSuchJobError
    from rq.job import Job

    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-concurrent-recovery-{suffix}", connection=connection)
    job_id = f"mdi-test-concurrent-job-{suffix}"
    backend = RedisRQQueueBackend(redis_url=redis_url, queue_name=queue.name)
    if prior_status:
        prior = queue.enqueue("mdi_workers.queue_runtime.run_queued_job", job_id, job_id=job_id)
        queue.remove(job_id)
        prior.set_status(prior_status)

    # Both independent producers observe the same old receipt. A retry must
    # re-read after the other producer has committed its queue publication.
    barrier, lock, observed = Barrier(2), Lock(), set()
    original_fetch = Job.fetch

    def synchronized_fetch(identity, **kwargs):
        try:
            result = original_fetch(identity, **kwargs)
        except NoSuchJobError:
            result = None
        if identity == job_id:
            with lock:
                first = get_ident() not in observed
                observed.add(get_ident())
            if first:
                barrier.wait(timeout=10)
        if result is None:
            raise NoSuchJobError(identity)
        return result

    try:
        with monkeypatch.context() as patch:
            patch.setattr(Job, "fetch", synchronized_fetch)
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(backend.enqueue_job, [job_id, job_id]))
        assert queue.get_job_ids() == [job_id]
        assert sum(result.enqueued for result in results) == 1
        assert sum(result.already_queued for result in results) == 1
        assert queue.fetch_job(job_id).origin == queue.name
    finally:
        queue.remove(job_id)
        receipt = queue.fetch_job(job_id)
        if receipt is not None:
            receipt.delete()
        connection.srem("rq:queues", queue.key)
        connection.close()


@pytest.mark.integration
def test_real_rq_recovery_preserves_receipt_claimed_during_terminal_replacement(monkeypatch):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses isolated temporary queues")
    from redis import Redis
    from rq import Queue
    from rq.job import Job

    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-claim-race-{suffix}", connection=connection)
    job_id = f"mdi-test-claim-job-{suffix}"
    receipt = queue.enqueue("mdi_workers.queue_runtime.run_queued_job", job_id, job_id=job_id)
    queue.remove(job_id)
    receipt.set_status("failed")
    original_fetch = Job.fetch
    advanced = False

    def advance_after_read(identity, **kwargs):
        nonlocal advanced
        result = original_fetch(identity, **kwargs)
        if identity == job_id and not advanced:
            advanced = True
            # A newer execution owner claims the same RQ identity after the
            # recovering producer has read the prior terminal record.
            connection.hset(receipt.key, mapping={"status": "started", "worker_name": "mdi-test-new-owner"})
        return result

    try:
        with monkeypatch.context() as patch:
            patch.setattr(Job, "fetch", advance_after_read)
            result = RedisRQQueueBackend(redis_url=redis_url, queue_name=queue.name).enqueue_job(job_id)
        assert result.already_queued and not result.enqueued
        assert queue.get_job_ids() == []
        saved = connection.hgetall(receipt.key)
        assert saved[b"status"] == b"started"
        assert saved[b"worker_name"] == b"mdi-test-new-owner"
    finally:
        queue.remove(job_id)
        receipt.delete()
        connection.srem("rq:queues", queue.key)
        connection.close()


@pytest.mark.integration
def test_real_rq_execution_publish_preserves_foreign_queue_identity():
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses isolated temporary queues")
    from redis import Redis
    from rq import Queue

    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    foreign = Queue(f"mdi-test-foreign-owner-{suffix}", connection=connection)
    target = Queue(f"mdi-test-target-owner-{suffix}", connection=connection)
    job_id = f"mdi-test-owned-job-{suffix}"
    receipt = foreign.enqueue("mdi_workers.queue_runtime.run_queued_job", job_id, job_id=job_id)
    saved = connection.hgetall(receipt.key)
    try:
        with pytest.raises(RuntimeError, match="ownership"):
            RedisRQQueueBackend(redis_url=redis_url, queue_name=target.name).enqueue_job(job_id)
        assert foreign.get_job_ids() == [job_id]
        assert target.get_job_ids() == []
        assert connection.hgetall(receipt.key) == saved
    finally:
        foreign.remove(job_id)
        target.remove(job_id)
        receipt.delete()
        connection.srem("rq:queues", foreign.key, target.key)
        connection.close()
