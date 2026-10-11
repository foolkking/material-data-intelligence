from datetime import datetime, timedelta, timezone
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path
import asyncio
import json
import os
import sqlite3
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, insert, update, select, func

from mdi_api.config import ApiSettings
from mdi_api.db import agent2_scientific_report_generations as generations
from mdi_api.research_agent import recovery as recovery_module
from mdi_api.infrastructure.scientific_reports.service import ScientificReportService
from mdi_api.infrastructure.scientific_reports.requests import ScientificReportRequestService
from mdi_api.infrastructure.scientific_reports.queue import InMemoryReportQueue
from mdi_api.infrastructure.scientific_reports.queue import RedisRQReportQueue
from mdi_api.infrastructure.scientific_reports.client import FakeStructuredReportComposerClient
from mdi_api.infrastructure.persistence.agent2_reports import Agent2ScientificReportGenerationRepository
from mdi_api.application.scientific_reports import generate_queued_report
from mdi_api.research_agent.recovery import StaleResearchRecoveryService
from mdi_api.db import analysis_plans, jobs, artifacts, tool_calls, scientific_result_snapshots
from mdi_api.db import metadata
from mdi_api.unit_of_work import RepositoryFactory
from mdi_llm.providers import LLMProviderError
from tests.test_agent2_reports import _bundle, _interpretation, _report
from tests.test_research_worker_loss_recovery import _stalled_turn
from tests.test_research_result_loss_recovery import _saved_result


def _generation(status="COMPOSING", age_minutes=16):
    factory, turn_id = _stalled_turn("COMPLETED")
    snapshot = _saved_result(factory, turn_id)
    old = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    with factory.unit_of_work() as unit:
        generation = unit.agent2.scientific_report_generations.create({
            "id": uuid4(), "project_id": "product", "research_turn_id": turn_id,
            "requested_by": "owner", "status": status, "attempt_count": 1,
            "created_at": old, "updated_at": old,
        })
    return factory, turn_id, generation, snapshot


@pytest.mark.parametrize("status", ["REQUESTED", "COMPOSING"])
def test_watchdog_terminalizes_lost_report_without_changing_science(monkeypatch, status):
    factory, turn_id, generation, snapshot = _generation(status)
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _: factory)
    assert recovery_module._watchdog_cycle(ApiSettings()) == 1
    assert recovery_module._watchdog_cycle(ApiSettings()) == 0
    response = ScientificReportService(factory).status_for_turn(turn_id)
    assert response["status"] == "FAILED"
    assert response["error_code"] == ("REPORT_QUEUE_TIMEOUT" if status == "REQUESTED" else "REPORT_STAGE_TIMEOUT")
    with factory.session() as session:
        assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
        assert session.agent2.scientific_result_snapshots.get(snapshot["id"])["bundle_json"] == snapshot["bundle_json"]
        assert session.agent2.scientific_report_generations.claim(generation["id"]) is None
        assert session.agent2.scientific_reports.get_for_turn(turn_id) is None


@pytest.mark.parametrize("status,age,enabled", [
    ("REQUESTED", 1, True), ("COMPOSING", 1, True),
    ("READY", 60, True), ("FAILED", 60, True), ("COMPOSING", 60, False),
])
def test_report_deadline_preserves_recent_terminal_and_disabled_work(status, age, enabled):
    factory, _, generation, _ = _generation(status, age)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings(agent2_report_enabled=enabled)).expire_stalled_reports() == 0
    with factory.session() as session:
        assert session.agent2.scientific_report_generations.get(generation["id"])["status"] == status


def test_report_expiry_cannot_overwrite_newer_attempt(monkeypatch):
    factory, _, generation, _ = _generation()
    original = Agent2ScientificReportGenerationRepository.compare_status
    def raced(self, identifier, status, **kwargs):
        with factory.engine.begin() as connection:
            connection.execute(update(generations).where(generations.c.id == identifier).values(
                attempt_count=2, updated_at=datetime.now(timezone.utc),
            ))
        return original(self, identifier, status, **kwargs)
    monkeypatch.setattr(Agent2ScientificReportGenerationRepository, "compare_status", raced)
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_reports() == 0
    with factory.session() as session:
        assert session.agent2.scientific_report_generations.get(generation["id"])["status"] == "COMPOSING"


def test_report_watchdog_also_runs_when_new_research_orchestration_is_disabled(monkeypatch):
    factory, turn_id, _, _ = _generation()
    monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _: factory)
    assert recovery_module._watchdog_cycle(ApiSettings(agent2_orchestration_enabled=False)) == 1
    assert ScientificReportService(factory).status_for_turn(turn_id)["status"] == "FAILED"


def _prepared_generation():
    factory, turn_id, generation, snapshot = _generation("REQUESTED", 0)
    job_id = "job_report_loss"
    payload = _bundle().model_dump(mode="json")
    payload.update(project_id="product", research_session_id="session", research_turn_id=str(turn_id), source_object_refs=[])
    payload["result_items"][0]["scientific_object_refs"] = []
    payload["methods"][0]["source_object_refs"] = []
    payload["provenance"]["job_id"] = job_id
    with factory.engine.begin() as connection:
        connection.execute(insert(analysis_plans), {
            "id": "plan_report_loss", "project_id": "product", "job_id": job_id,
            "plan_source": "agent2", "planner_provider": "fixture", "analysis_plan_json": {},
            "plan_hash": "a" * 64, "validation_status": "validated", "created_by": "owner",
        })
        connection.execute(insert(jobs), {"id": job_id, "project_id": "product", "plan_id": "plan_report_loss", "kind": "agent2", "status": "completed", "created_by": "owner"})
        connection.execute(update(scientific_result_snapshots).where(scientific_result_snapshots.c.id == snapshot["id"]).values(bundle_json=payload, job_id=job_id))
    with factory.unit_of_work() as unit:
        unit.agent2.interpretations.add({
            "id": uuid4(), "research_turn_id": turn_id, "result_snapshot_id": snapshot["id"],
            "project_id": "product", "contract_version": "1.0", "prompt_version": "fixture",
            "provider": "fake", "model": "fixture", "provider_request_id": None, "repair_attempted": False,
            "input_fingerprint": "c" * 64, "grounding_status": "VALID", "output_json": _interpretation(),
        })
    report_payload = _report().model_dump(mode="json")
    report_payload["data_sources"] = []
    return factory, turn_id, generation, report_payload


@pytest.mark.parametrize("outcome", ["success", "failure", "repair"])
def test_late_report_attempt_cannot_publish_or_overwrite_explicit_retry(outcome):
    factory, turn_id, generation, payload = _prepared_generation()
    identifier = generation["id"]
    with factory.engine.connect() as connection:
        before = [connection.execute(select(func.count()).select_from(table)).scalar_one() for table in (jobs, artifacts, tool_calls, scientific_result_snapshots)]

    class InterruptedClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            with factory.engine.begin() as connection:
                connection.execute(update(generations).where(generations.c.id == identifier).values(
                    updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
                ))
            assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_reports() == 1
            retried = ScientificReportRequestService(factory, queue=InMemoryReportQueue()).request(turn_id, requested_by="owner")
            assert retried["status"] == "REQUESTED" and retried["queue"]["enqueued"]
            if outcome == "failure":
                raise LLMProviderError("PROVIDER_TIMEOUT", "late provider failure")
            return await super().generate_structured(**kwargs)

    old_client = InterruptedClient({} if outcome == "repair" else payload)
    old = generate_queued_report(str(identifier), repository_factory=factory,
        report_generator=ScientificReportService(factory, client=old_client), expected_attempt=2)
    assert old["status"] == "REQUESTED"
    with factory.session() as session:
        assert session.agent2.scientific_reports.get_for_turn(turn_id) is None
        assert session.agent2.scientific_report_generations.get(identifier)["attempt_count"] == 2
    fresh_client = FakeStructuredReportComposerClient(payload)
    # A replay from the retired attempt cannot claim the user's retry.
    replay = generate_queued_report(str(identifier), repository_factory=factory,
        report_generator=ScientificReportService(factory, client=fresh_client), expected_attempt=2)
    assert replay["status"] == "REQUESTED" and fresh_client.calls == 0
    fresh = generate_queued_report(str(identifier), repository_factory=factory,
        report_generator=ScientificReportService(factory, client=fresh_client), expected_attempt=3)
    assert fresh["status"] == "READY" and fresh_client.calls == 1
    with factory.session() as session:
        assert session.agent2.scientific_report_generations.get(identifier)["attempt_count"] == 3
        assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
        after = [session.connection.execute(select(func.count()).select_from(table)).scalar_one() for table in (jobs, artifacts, tool_calls, scientific_result_snapshots)]
        assert after == before


def test_expired_report_queue_message_cannot_claim_the_users_retry():
    factory, turn_id, generation, payload = _prepared_generation()
    with factory.engine.begin() as connection:
        connection.execute(update(generations).where(generations.c.id == generation["id"]).values(
            updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
        ))
    assert StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_reports() == 1
    retry = ScientificReportRequestService(factory, queue=InMemoryReportQueue()).request(turn_id, requested_by="owner")
    assert retry["status"] == "REQUESTED"
    client = FakeStructuredReportComposerClient(payload)
    retired = generate_queued_report(str(generation["id"]), repository_factory=factory,
        report_generator=ScientificReportService(factory, client=client), expected_attempt=2)
    assert retired["status"] == "REQUESTED" and client.calls == 0
    current = generate_queued_report(str(generation["id"]), repository_factory=factory,
        report_generator=ScientificReportService(factory, client=client), expected_attempt=3)
    assert current["status"] == "READY" and client.calls == 1


@pytest.mark.integration
def test_report_queue_attempt_identity_and_concurrent_publication():
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    from redis import Redis
    from rq import Queue
    connection = Redis.from_url(redis_url)
    queue = Queue(f"mdi-test-report-loss-{uuid4().hex}", connection=connection)
    producer = RedisRQReportQueue(redis_url=redis_url, queue_name=queue.name)
    identifier = uuid4()
    barrier = Barrier(2)
    def enqueue():
        barrier.wait()
        return producer.enqueue_generation(identifier, attempt=1)
    try:
        with ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: enqueue(), range(2)))
        assert sum(result.enqueued for result in results) == 1
        old_id = f"agent2-report-{identifier}-1"
        assert queue.job_ids == [old_id]
        assert queue.fetch_job(old_id).kwargs == {"expected_attempt": 1}
        assert queue.fetch_job(old_id).timeout == 300
        assert producer.enqueue_generation(identifier, attempt=2).enqueued
        assert queue.job_ids == [old_id, f"agent2-report-{identifier}-2"]
        foreign = RedisRQReportQueue(redis_url=redis_url, queue_name=f"{queue.name}-foreign")
        with pytest.raises(RuntimeError, match="ownership"):
            foreign.enqueue_generation(identifier, attempt=1)
        assert queue.fetch_job(old_id).origin == queue.name
    finally:
        for job in queue.jobs:
            job.delete()
        queue.delete()
        connection.close()


@pytest.mark.integration
@pytest.mark.parametrize("local_control", [False, True])
def test_production_report_worker_recovers_queued_retry_in_fresh_process(tmp_path, local_control):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    from redis import Redis
    from rq import Queue
    factory, turn_id, generation, payload = _prepared_generation()
    database_path = tmp_path / "report-retry.sqlite3"
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    database_url = f"sqlite:///{database_path.as_posix()}"
    durable = RepositoryFactory(create_engine(database_url))
    connection = Redis.from_url(redis_url)
    queue = Queue(f"mdi-test-report-retry-{uuid4().hex}", connection=connection)
    producer = RedisRQReportQueue(redis_url=redis_url, queue_name=queue.name)
    requests = ScientificReportRequestService(durable, queue=producer)
    queued_ids = []
    tables = (analysis_plans, jobs, artifacts, tool_calls, scientific_result_snapshots)
    with durable.engine.connect() as database:
        before = [database.execute(select(func.count()).select_from(table)).scalar_one() for table in tables]
    environment = {
        **os.environ, "DATABASE_URL": database_url, "MDI_DATABASE_URL": database_url,
        "MDI_RUNTIME_PROFILE": "local", "MDI_ENV": "test",
        "MDI_AGENT2_REPORT_FIXTURE_JSON": json.dumps(payload),
        "PYTHONPATH": os.pathsep.join(path for path in sys.path if path),
    }
    try:
        original = requests.request(turn_id, requested_by="owner")
        assert original["queue"]["enqueued"]
        queued_ids.append(f"agent2-report-{generation['id']}-2")
        with durable.engine.begin() as database:
            database.execute(update(generations).where(generations.c.id == generation["id"]).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
            ))
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_reports() == 1
        retry = requests.request(turn_id, requested_by="owner")
        assert retry["queue"]["enqueued"]
        queued_ids.append(f"agent2-report-{generation['id']}-3")
        assert queue.job_ids == queued_ids
        assert queue.fetch_job(queued_ids[1]).func_name == "mdi_workers.report_worker.run_queued_report_generation"
        child = subprocess.run([
            sys.executable, "-m", "mdi_workers.worker_entrypoint", queue.name,
            "--url", redis_url, "--burst", "--max-jobs", "2", "--name", queue.name,
            "--logging-level", "CRITICAL",
        ] + (["--local-control"] if local_control else []), cwd=Path(__file__).resolve().parents[1], env=environment,
            capture_output=True, text=True, timeout=60)
        assert child.returncode == 0, child.stderr[-3000:]
        retired, current = [queue.fetch_job(identifier) for identifier in queued_ids]
        assert retired.is_finished and current.is_finished
        assert retired.return_value()["status"] == "REQUESTED"
        result = current.return_value()
        assert result["status"] == "READY" and result["process_id"] != os.getpid()
        with durable.session() as session:
            assert session.agent2.scientific_report_generations.get(generation["id"])["attempt_count"] == 3
            assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
            after = [session.connection.execute(select(func.count()).select_from(table)).scalar_one() for table in tables]
        assert after == before
        environment.pop("MDI_AGENT2_REPORT_FIXTURE_JSON")
        reopen = subprocess.run([
            sys.executable, "-c",
            "import sys; from mdi_api.bootstrap.repository_factory import create_repository_factory; "
            "from mdi_api.infrastructure.scientific_reports.service import ScientificReportService; "
            "print(ScientificReportService(create_repository_factory()).get_by_report_id(sys.argv[1])['report_id'])",
            result["report_id"],
        ], cwd=Path(__file__).resolve().parents[1], env=environment,
            capture_output=True, text=True, timeout=30)
        assert reopen.returncode == 0, reopen.stderr[-3000:]
        assert reopen.stdout.strip() == result["report_id"]
    finally:
        for identifier in queued_ids:
            job = queue.fetch_job(identifier)
            if job is not None:
                queue.remove(identifier)
                job.delete()
        queue.delete()
        connection.close()
        durable.engine.dispose()


def _exit_during_report(database_path: str, generation_id: str):
    factory = RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}"))
    class ExitingClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            os._exit(84)
    generate_queued_report(generation_id, repository_factory=factory,
        report_generator=ScientificReportService(factory, client=ExitingClient({})), expected_attempt=2)


@pytest.mark.integration
def test_actual_report_worker_exit_is_recovered_without_a_provider_replay(tmp_path, monkeypatch):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    from redis import Redis
    from rq import Queue, Worker
    factory, turn_id, generation, _ = _prepared_generation()
    database_path = tmp_path / "report-loss.sqlite3"
    raw = factory.engine.raw_connection()
    with sqlite3.connect(database_path) as destination:
        raw.driver_connection.backup(destination)
    raw.close()
    factory.engine.dispose()
    durable = RepositoryFactory(create_engine(f"sqlite:///{database_path.as_posix()}"))
    connection = Redis.from_url(redis_url)
    name = f"mdi-test-report-loss-{uuid4().hex}"
    queue = Queue(name, connection=connection)
    wakeup = queue.enqueue(_exit_during_report, str(database_path), str(generation["id"]), job_timeout=30)
    command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
    try:
        child = subprocess.run([sys.executable, "-c", command, redis_url, name, name],
            env={**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)},
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
        assert child.returncode == 84, child.stderr
        assert wakeup.get_status(refresh=True).value == "started"
        assert ScientificReportService(durable).status_for_turn(turn_id)["status"] == "COMPOSING"
        assert StaleResearchRecoveryService(durable, settings=ApiSettings()).expire_stalled_reports() == 0
        # Advance only this test record's inactivity; production deadlines are unchanged.
        with durable.engine.begin() as database:
            database.execute(update(generations).where(generations.c.id == generation["id"]).values(
                updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
            ))
        monkeypatch.setattr(recovery_module, "create_repository_factory", lambda _: durable)
        async def exercise():
            settings = ApiSettings(database_url="postgresql://unused", queue_backend="redis", agent2_orchestration_enabled=True)
            async with recovery_module.research_stage_watchdog(settings, interval_seconds=0.01):
                async def completed():
                    while ScientificReportService(durable).status_for_turn(turn_id)["status"] != "FAILED":
                        await asyncio.sleep(0.01)
                await asyncio.wait_for(completed(), timeout=3)
        asyncio.run(exercise())
        assert ScientificReportService(durable).status_for_turn(turn_id)["error_code"] == "REPORT_STAGE_TIMEOUT"
        with durable.session() as session:
            assert session.agent2.research_turns.get(turn_id)["status"] == "COMPLETED"
            assert session.repositories.jobs.get("job_report_loss")["status"] == "completed"
            assert session.agent2.scientific_reports.get_for_turn(turn_id) is None
    finally:
        worker = Worker.find_by_key(f"rq:worker:{name}", connection=connection)
        if worker:
            worker.register_death()
        queue.remove(wakeup.id)
        wakeup.delete()
        queue.delete()
        connection.close()
        durable.engine.dispose()


@pytest.fixture
def report_postgres():
    from sqlalchemy.schema import CreateSchema, DropSchema
    url = os.getenv("MDI_TEST_DATABASE_URL")
    if not url or not url.startswith("postgresql"):
        pytest.skip("Explicit MDI_TEST_DATABASE_URL required")
    source, turn_id, generation, payload = _prepared_generation()
    schema = f"mdi_test_report_loss_{uuid4().hex}"
    server = create_engine(url)
    scoped = server.execution_options(schema_translate_map={None: schema})
    created = False
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
        yield RepositoryFactory(scoped), turn_id, generation, payload
    finally:
        source.engine.dispose()
        if created:
            assert schema.startswith("mdi_test_report_loss_") and len(schema) == len("mdi_test_report_loss_") + 32
            with server.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))
        server.dispose()


@pytest.mark.integration
def test_postgres_report_publication_and_watchdog_choose_one_outcome(report_postgres):
    factory, turn_id, generation, payload = report_postgres
    identifier = generation["id"]
    barrier = Barrier(2)
    class PausedClient(FakeStructuredReportComposerClient):
        async def generate_structured(self, **kwargs):
            with factory.engine.begin() as connection:
                connection.execute(update(generations).where(generations.c.id == identifier).values(
                    updated_at=datetime.now(timezone.utc) - timedelta(minutes=16),
                ))
            barrier.wait(timeout=5)
            return await super().generate_structured(**kwargs)
    def generate():
        return generate_queued_report(str(identifier), repository_factory=factory,
            report_generator=ScientificReportService(factory, client=PausedClient(payload)), expected_attempt=2)
    def expire():
        barrier.wait(timeout=5)
        return StaleResearchRecoveryService(factory, settings=ApiSettings()).expire_stalled_reports()
    with ThreadPoolExecutor(2) as pool:
        tasks = [pool.submit(generate), pool.submit(expire)]
        outcomes = [task.result(timeout=15) for task in tasks]
    with factory.session() as session:
        current = session.agent2.scientific_report_generations.get(identifier)
        saved = session.agent2.scientific_reports.get_for_turn(turn_id)
        assert current["status"] in {"FAILED", "READY"}
        assert (saved is not None) == (current["status"] == "READY")
        assert outcomes[0]["status"] == current["status"]
