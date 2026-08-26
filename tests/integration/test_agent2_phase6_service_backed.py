from __future__ import annotations

import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

import pytest
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, func, select

from mdi_api.db import agent2_scientific_interpretations, artifacts, jobs, research_turns, scientific_result_snapshots, tool_calls
from mdi_api.interpretation.queue import RedisRQInterpretationQueue


ROOT = Path(__file__).resolve().parents[2]


def _phase5_module():
    phase5_path = ROOT / "tests" / "integration" / "test_agent2_phase5_service_backed.py"
    spec = importlib.util.spec_from_file_location("agent2_phase5_service_fixture", phase5_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _interpreter_fixture(bundle: dict) -> str:
    fact = bundle["facts"][0]
    item = bundle["result_items"][0]
    return json.dumps({
        "contract_version": "1.0",
        "title": "已验证的科学结果",
        "answer_lead": "执行结果可以在已提交证据范围内解释。",
        "primary_findings": [{
            "finding_id": "finding-1", "statement": f"结果包含 {fact['value']} {fact.get('unit') or ''} 的已记录科学量。",
            "importance": "MEDIUM", "confidence": "HIGH", "fact_refs": [fact["fact_id"]],
            "evidence_refs": [], "result_item_refs": [item["id"]],
        }],
        "supporting_findings": [], "limitations": [], "primary_result_refs": [item["id"]],
        "supporting_result_refs": [], "follow_up_suggestions": [],
    }, ensure_ascii=False)


@pytest.fixture(scope="module")
def phase6_service_pipeline():
    phase5 = _phase5_module()
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    database_url = phase5._phase4_module()._postgres_url()
    queue_name = f"mdi-agent2-phase6-interpretations-{os.getpid()}"
    previous = {key: os.environ.get(key) for key in ("MDI_ENV", "MDI_AGENT2_INTERPRETATION_FIXTURE_JSON", "MDI_AGENT2_INTERPRETATION_QUEUE_NAME", "MDI_AGENT2_INTERPRETATION_ENABLED")}
    phase5_fixture = phase5.phase5_service_pipeline.__wrapped__
    generator = None
    try:
        os.environ["MDI_ENV"] = "ci"
        os.environ["MDI_AGENT2_INTERPRETATION_ENABLED"] = "1"
        os.environ["MDI_AGENT2_INTERPRETATION_QUEUE_NAME"] = queue_name
        generator = phase5_fixture()
        cases = next(generator)
        # Phase 5 intentionally disables interpretation while proving the
        # RESULT_READY projection boundary.  Re-enable the production
        # interpretation queue only after that fixture has yielded its
        # durable result identities, then republish those identities through
        # the real queue authority.  This keeps the two qualification
        # boundaries separate without manually invoking the projector.
        os.environ["MDI_AGENT2_INTERPRETATION_ENABLED"] = "1"
        os.environ["MDI_AGENT2_INTERPRETATION_QUEUE_NAME"] = queue_name
        interpretation_queue = RedisRQInterpretationQueue(redis_url=redis_url, queue_name=queue_name)
        for case in (cases["rdf"], cases["xrd"]):
            queued = interpretation_queue.enqueue_turn(UUID(case["turn_id"]))
            assert queued.enqueued, queued.message
        rdf = cases["rdf"]
        xrd = cases["xrd"]
        environment = phase5._phase4_module()._worker_environment(database_url)
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        with engine.connect() as connection:
            counts_before = {
                "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
                "tool_calls": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
                "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
                "result_snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
            }
        worker_outputs = []
        interpretation_pids: set[int] = set()
        for name, case in (("rdf", rdf), ("xrd", xrd)):
            environment["MDI_AGENT2_INTERPRETATION_FIXTURE_JSON"] = _interpreter_fixture(case["bundle"])
            target_job_id = f"agent2-interpretation-{case['turn_id']}"
            task = None
            for attempt in range(3):
                task = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(target_job_id)
                if task is not None and task.is_finished:
                    break
                result = subprocess.run(
                    [sys.executable, "-m", "mdi_workers.worker_entrypoint", queue_name, "--url", redis_url, "--burst", "--max-jobs", "1", "--name", f"agent2-phase6-interpretation-{name}-{attempt}"],
                    cwd=ROOT, env=environment, capture_output=True, text=True, timeout=240,
                )
                assert result.returncode == 0, result.stderr[-6000:]
                worker_outputs.append(result.stdout[-1000:])
            task = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(target_job_id)
            assert task is not None and task.is_finished
            interpretation_pids.add(int(task.return_value()["process_id"]))
        assert len(interpretation_pids) == 2
        phase5_pids = {
            int(rdf["execution_worker_pid"]),
            int(xrd["execution_worker_pid"]),
        }
        assert not interpretation_pids.intersection(phase5_pids | {os.getpid()})
        with engine.connect() as connection:
            rows = {name: connection.execute(select(research_turns).where(research_turns.c.id == case["turn_id"])).mappings().one() for name, case in (("rdf", rdf), ("xrd", xrd))}
            counts_after = {
                "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
                "tool_calls": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
                "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
                "result_snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
            }
            assert counts_after == counts_before
            yield {
                "cases": cases,
                "rows": rows,
                "counts_before": counts_before,
                "counts_after": counts_after,
                "database_url": database_url,
                "interpretation_worker_output": worker_outputs,
                "interpretation_worker_pids": sorted(interpretation_pids),
            }
        engine.dispose()
    finally:
        if generator is not None:
            try:
                next(generator)
            except StopIteration:
                pass
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.mark.integration
@pytest.mark.agent2_phase6_service
def test_agent2_phase6_rdf_fresh_interpreter_process(phase6_service_pipeline):
    case = phase6_service_pipeline["cases"]["rdf"]
    row = phase6_service_pipeline["rows"]["rdf"]
    assert row["status"] == "COMPLETED"
    assert row["assistant_final_message_id"]
    with create_engine(phase6_service_pipeline["database_url"], future=True).connect() as connection:
        assert connection.execute(select(func.count()).select_from(agent2_scientific_interpretations).where(agent2_scientific_interpretations.c.research_turn_id == case["turn_id"])).scalar_one() == 1


@pytest.mark.integration
@pytest.mark.agent2_phase6_service
def test_agent2_phase6_xrd_fresh_interpreter_process(phase6_service_pipeline):
    row = phase6_service_pipeline["rows"]["xrd"]
    assert row["status"] in {"COMPLETED", "PARTIAL"}
    assert row["assistant_final_message_id"]
