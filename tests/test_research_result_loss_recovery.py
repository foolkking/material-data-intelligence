from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import subprocess
import sys
from threading import Barrier, Event
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, insert, update

from mdi_api.config import ApiSettings
from mdi_api.agent2_errors import ConcurrentTurnModification
from mdi_api.db import artifacts, research_turns
from mdi_api.infrastructure.interpretation.client import FakeStructuredInterpreterClient
from mdi_api.infrastructure.interpretation.service import ScientificInterpretationService
from mdi_api.infrastructure.scientific_results.service import ScientificResultProjectionService
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.execution.supervisor import ResearchExecutionSupervisor
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.unit_of_work import RepositoryFactory
from tests.test_agent2_execution import CaptureQueue, _factory
from tests.test_agent2_interpretation import _bundle, _output
from tests.test_research_execution_loss_recovery import isolated_postgres_execution
from tests.test_research_worker_loss_recovery import _stalled_turn


def _saved_result(factory, turn_id):
    with factory.unit_of_work() as unit:
        turn = unit.agent2.research_turns.get(turn_id)
        base = _bundle()
        bundle = base.model_copy(update={
            "project_id": turn["project_id"], "research_session_id": turn["research_session_id"],
            "research_turn_id": turn_id, "source_object_refs": [],
            "result_items": [item.model_copy(update={"scientific_object_refs": []}) for item in base.result_items],
        })
        return unit.agent2.scientific_result_snapshots.add({
            "id": uuid4(), "project_id": turn["project_id"], "research_turn_id": turn_id,
            "job_id": None, "schema_version": bundle.schema_version,
            "projection_version": bundle.projection_version,
            "execution_status": bundle.execution_status.value,
            "relevance_status": bundle.relevance_status.value,
            "source_fingerprint": "preserved-result", "bundle_json": bundle.model_dump(mode="json"),
        })


@pytest.mark.parametrize("stage", ["RESULT_PENDING", "RESULT_READY", "INTERPRETING"])
def test_watchdog_ends_stalled_result_stages_once_and_preserves_science(monkeypatch, stage):
    factory, turn_id = _stalled_turn(stage)
    snapshot = _saved_result(factory, turn_id)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda settings: factory)
    assert recovery_module._watchdog_cycle(ApiSettings()) == 1
    assert recovery_module._watchdog_cycle(ApiSettings()) == 0
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        events = session.agent2.research_turn_events.list_for_turn(turn_id)
        assert turn["status"] == "FAILED" and turn["completed_at"] is not None
        assert turn["error_code"] == ("RESULT_PROJECTION_TIMEOUT" if stage == "RESULT_PENDING" else "INTERPRETATION_STAGE_TIMEOUT")
        assert turn["assistant_final_message_id"] is None
        assert session.agent2.research_turns.get_message(turn["user_message_id"])["content_summary"] == "保留这条研究问题"
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        assert sum(event["event_type"] == "TURN_FAILED" for event in events) == 1


@pytest.mark.parametrize("stage", ["RESULT_PENDING", "RESULT_READY", "INTERPRETING"])
def test_recent_result_work_keeps_its_deadline(monkeypatch, stage):
    factory, turn_id = _stalled_turn(stage, age_minutes=2)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda settings: factory)
    assert recovery_module._watchdog_cycle(ApiSettings(agent2_startup_recovery_stale_minutes=1)) == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == []


@pytest.mark.parametrize("new_status", ["INTERPRETING", "COMPLETED", "CANCELED"])
def test_timeout_cannot_overwrite_a_new_claim_or_terminal_result(monkeypatch, new_status):
    factory, turn_id = _stalled_turn("INTERPRETING")
    original = ResearchTurnService.fail_if_active

    def advance_then_fail(self, *args, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                status=new_status, row_version=5, updated_at=datetime.now(timezone.utc),
            ))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(ResearchTurnService, "fail_if_active", advance_then_fail)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == new_status
        assert session.agent2.research_turn_events.list_for_turn(turn_id) == []


@pytest.mark.parametrize("stage", ["RESULT_PENDING", "RESULT_READY", "INTERPRETING"])
def test_disabled_result_stage_is_not_expired(stage):
    factory, turn_id = _stalled_turn(stage)
    settings = ApiSettings(agent2_result_projection_enabled=False, agent2_interpretation_enabled=False)
    assert StaleResearchRecoveryService(factory, settings=settings).expire_stalled_results() == 0
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == stage


def test_interpretation_handoff_has_deadline_but_query_handoff_is_preserved():
    for action, expected in [("INTERPRET_RESULT", 1), ("QUERY_DATA", 0)]:
        factory, turn_id = _stalled_turn("ORCHESTRATING")
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(action_type=action))
        assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results() == expected
        with factory.session() as session:
            turn = session.agent2.research_turns.get(turn_id)
            assert turn["status"] == ("FAILED" if expected else "ORCHESTRATING")


@pytest.mark.parametrize("late_outcome", ["success", "failure"])
def test_expired_interpreter_cannot_publish_its_late_provider_outcome(late_outcome):
    factory, turn_id = _stalled_turn("RESULT_READY", age_minutes=0)
    snapshot = _saved_result(factory, turn_id)
    started, release = Event(), Event()

    class GatedClient(FakeStructuredInterpreterClient):
        async def generate_structured(self, **kwargs):
            started.set()
            assert release.wait(10)
            if late_outcome == "failure":
                raise RuntimeError("test late provider failure")
            return await super().generate_structured(**kwargs)

    interpreter = ScientificInterpretationService(factory, client=GatedClient(_output()))
    with ThreadPoolExecutor(max_workers=1) as pool:
        try:
            future = pool.submit(interpreter.process_turn, turn_id)
            assert started.wait(5), future.exception(timeout=1)
            with factory.engine.begin() as connection:
                connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                    updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
                ))
            assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results() == 1
            release.set()
            assert future.exception(timeout=10) is not None
        finally:
            release.set()
    with factory.session() as session:
        turn = session.agent2.research_turns.get(turn_id)
        assert turn["status"] == "FAILED" and turn["error_code"] == "INTERPRETATION_STAGE_TIMEOUT"
        assert turn["assistant_final_message_id"] is None
        assert session.agent2.interpretations.get_for_turn(turn_id) is None
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        assert sum(e["event_type"] == "TURN_FAILED" for e in session.agent2.research_turn_events.list_for_turn(turn_id)) == 1


def test_late_projection_rolls_back_snapshot_and_ready_events_after_timeout():
    factory, turn_id = _stalled_turn("RESULT_PENDING")
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results() == 1
    bundle = _bundle().model_copy(update={"project_id": "product", "research_turn_id": turn_id})
    with pytest.raises(ConcurrentTurnModification):
        ScientificResultProjectionService(factory)._persist(turn_id, bundle, "late-projection", None)
    with factory.session() as session:
        assert session.agent2.scientific_result_snapshots.list_for_turn(turn_id) == []
        assert session.agent2.research_turns.get(turn_id)["error_code"] == "RESULT_PROJECTION_TIMEOUT"
        assert [e["event_type"] for e in session.agent2.research_turn_events.list_for_turn(turn_id)] == ["TURN_FAILED"]


@pytest.mark.integration
def test_postgres_concurrent_result_watchdogs_publish_one_failure(isolated_postgres_execution):
    factory, turn_id, _job_id, _lease = isolated_postgres_execution
    with factory.engine.begin() as connection:
        connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="RESULT_READY"))
    snapshot = _saved_result(factory, turn_id)
    barrier = Barrier(2)

    def expire():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_results()

    with ThreadPoolExecutor(max_workers=2) as pool:
        left, right = pool.submit(expire), pool.submit(expire)
        assert left.result(timeout=10) + right.result(timeout=10) == 1
    with factory.session() as session:
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        assert sum(e["event_type"] == "TURN_FAILED" for e in session.agent2.research_turn_events.list_for_turn(turn_id)) == 1


def _completed_execution():
    engine, factory, turn_id = _factory()
    dispatch = ResearchExecutionDispatcher(factory, queue=CaptureQueue()).dispatch_turn(turn_id)
    with factory.unit_of_work() as unit:
        unit.repositories.jobs.set_status(dispatch.job_id, "running")
        unit.repositories.jobs.set_status(dispatch.job_id, "completed")
        unit.repositories.tool_calls.save({
            "id": "call-output", "jobId": dispatch.job_id, "stepId": "step_1",
            "toolId": "structure.xrd", "status": "completed", "params": {},
        })
    with engine.begin() as connection:
        connection.execute(insert(artifacts), {
            "id": "saved-output", "project_id": "project", "dataset_id": "dataset",
            "job_id": dispatch.job_id, "tool_call_id": "call-output", "type": "table_json",
            "name": "Saved XRD output", "version": "1", "storage_key": "test/xrd.json",
            "storage_provider": "local", "size_bytes": 42, "content_type": "application/json",
            "content_hash": "saved-hash", "sha256": "saved-hash", "metadata_json": {},
        })
    assert ResearchExecutionSupervisor(factory).sync_for_job(dispatch.job_id).status.value == "RESULT_PENDING"
    return factory, turn_id, dispatch.job_id


def _exit_during_result_stage(database_path: str, turn_id: str, stage: str):
    """Lose only the isolated test process inside a real result/provider boundary."""
    factory = RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}"))
    if stage == "RESULT_READY":
        os._exit(83)  # Queue execution was received, but interpretation was not claimed.
    if stage == "RESULT_PENDING":
        def interrupted_artifact_read(_artifact):
            os._exit(83)
        ScientificResultProjectionService(factory, artifact_loader=interrupted_artifact_read).project_turn(UUID(turn_id))
    else:
        class ExitingClient(FakeStructuredInterpreterClient):
            async def generate_structured(self, **kwargs):
                os._exit(83)
        ScientificInterpretationService(factory, client=ExitingClient(_output())).process_turn(UUID(turn_id))


@pytest.mark.integration
@pytest.mark.parametrize("stage", ["RESULT_PENDING", "RESULT_READY", "INTERPRETING"])
def test_real_result_worker_exit_reaches_durable_failure(tmp_path, monkeypatch, stage):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; isolated queue and SQLite database only")
    from redis import Redis
    from rq import Queue, Worker

    factory, turn_id, job_id = _completed_execution()
    snapshot = None
    if stage != "RESULT_PENDING":
        snapshot = _saved_result(factory, turn_id)
        with factory.engine.begin() as connection:
            connection.execute(update(research_turns).where(research_turns.c.id == turn_id).values(status="RESULT_READY"))
    database_path = tmp_path / "result-loss.sqlite3"
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-result-loss-{suffix}", connection=connection)
    worker_name = f"mdi-test-result-loss-{suffix}"
    wakeup = queue.enqueue(_exit_during_result_stage, str(database_path), str(turn_id), stage, job_timeout=30)
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
    try:
        child = subprocess.run([sys.executable, "-c", command, redis_url, queue.name, worker_name],
            env=environment, cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
        assert child.returncode == 83, child.stderr
        assert wakeup.get_status(refresh=True).value == "started"
        with durable.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == stage
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_results() == 0
        with durable.engine.begin() as database:
            database.execute(update(research_turns).where(research_turns.c.id == turn_id).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
            ))
        monkeypatch.setattr(recovery_module, "create_repository_factory", lambda settings: durable)
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
            assert session.repositories.jobs.get(job_id)["status"] == "completed"
            assert session.repositories.artifacts.list_for_job(job_id)[0]["sha256"] == "saved-hash"
            assert session.agent2.research_turns.get_message("message")["content_summary"] == "Run the analysis"
            if snapshot:
                assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
            assert sum(e["event_type"] == "TURN_FAILED" for e in session.agent2.research_turn_events.list_for_turn(turn_id)) == 1
        progress = ResearchExecutionSupervisor(durable).sync_for_job(job_id)
        assert progress.status.value == "FAILED"
        assert progress.incremental_outputs[0].artifact_id == "saved-output"
    finally:
        queue.remove(wakeup.id)
        wakeup.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        durable.engine.dispose()
