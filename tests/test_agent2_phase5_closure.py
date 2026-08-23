from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from mdi_api.config import ApiSettings
from mdi_api.research_agent.schemas import ResearchTurnStatus
from mdi_api.scientific_results.queue import (
    DisabledResultProjectionQueue,
    InMemoryResultProjectionQueue,
    RedisRQResultProjectionQueue,
    result_projection_queue_from_settings,
)
from mdi_api.scientific_results.reconciler import ScientificResultReconciler
from mdi_workers.queue_runtime import QueueWorkerRuntime


def test_result_projection_queue_is_identity_only_and_idempotent():
    turn_id = uuid4()
    queue = InMemoryResultProjectionQueue()
    first = queue.enqueue_turn(turn_id)
    second = queue.enqueue_turn(turn_id)
    assert first.enqueued is True
    assert second.enqueued is False
    assert queue.pop_next() == turn_id
    assert queue.pop_next() is None


def test_result_projection_queue_is_enabled_for_redis_by_default():
    queue = result_projection_queue_from_settings(ApiSettings(queue_backend="redis"))
    assert isinstance(queue, RedisRQResultProjectionQueue)
    assert isinstance(
        result_projection_queue_from_settings(ApiSettings(queue_backend="local")),
        DisabledResultProjectionQueue,
    )


def test_execution_supervisor_terminal_commit_publishes_result_wakeup(monkeypatch):
    import mdi_api.research_agent.execution.supervisor as supervisor_module
    import mdi_api.scientific_results.queue as queue_module

    turn_id = uuid4()
    queue = InMemoryResultProjectionQueue()

    class Supervisor:
        def __init__(self, _factory):
            pass

        def sync_for_job(self, _job_id):
            return SimpleNamespace(status=ResearchTurnStatus.RESULT_PENDING, turn_id=turn_id)

    monkeypatch.setattr(supervisor_module, "ResearchExecutionSupervisor", Supervisor)
    monkeypatch.setattr(queue_module, "result_projection_queue_from_settings", lambda _settings: queue)
    QueueWorkerRuntime._notify_agent2_progress("job-1")
    assert queue.pop_next() == turn_id


def test_projection_publish_failure_does_not_change_execution_authority(monkeypatch):
    import mdi_api.research_agent.execution.supervisor as supervisor_module
    import mdi_api.scientific_results.queue as queue_module

    turn_id = uuid4()

    class Supervisor:
        def __init__(self, _factory):
            pass

        def sync_for_job(self, _job_id):
            return SimpleNamespace(status=ResearchTurnStatus.RESULT_PENDING, turn_id=turn_id)

    class FailingQueue:
        def enqueue_turn(self, _turn_id):
            raise ConnectionError("redis unavailable")

    monkeypatch.setattr(supervisor_module, "ResearchExecutionSupervisor", Supervisor)
    monkeypatch.setattr(queue_module, "result_projection_queue_from_settings", lambda _settings: FailingQueue())
    QueueWorkerRuntime._notify_agent2_progress("job-1")


class _Session:
    def __init__(self, status):
        self.agent2 = SimpleNamespace(research_turns=SimpleNamespace(get=lambda _turn_id: {"status": status}))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None


class _Factory:
    def __init__(self, status):
        self.status = status

    def session(self):
        return _Session(self.status)


def test_reconciler_republishes_only_recoverable_result_pending_turns():
    turn_id = uuid4()
    queue = InMemoryResultProjectionQueue()
    reconciler = ScientificResultReconciler(_Factory("RESULT_PENDING"), queue)
    result = reconciler.reconcile_turn(turn_id)
    assert result.enqueued is True
    assert queue.pop_next() == turn_id
    assert ScientificResultReconciler(_Factory("RESULT_READY"), queue).reconcile_turn(turn_id) is None
