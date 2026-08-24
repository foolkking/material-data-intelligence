from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, func, select

from mdi_api.db import agent2_scientific_report_generations, agent2_scientific_report_snapshots, analysis_plans, artifacts, jobs, projects, scientific_result_snapshots, tool_calls
from mdi_api.scientific_reports.grounded import DeterministicScientificReportComposer
from mdi_api.scientific_reports.queue import RedisRQReportQueue
from mdi_api.scientific_reports.requests import ScientificReportRequestService
from mdi_api.scientific_results.schemas import ScientificResultBundle
from mdi_api.unit_of_work import RepositoryFactory


ROOT = Path(__file__).resolve().parents[2]


def _phase6_module():
    path = ROOT / "tests" / "integration" / "test_agent2_phase6_service_backed.py"
    spec = importlib.util.spec_from_file_location("agent2_phase6_report_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _report_fixture(bundle_payload: dict, interpretation_payload: dict, relevance: str) -> str:
    report = DeterministicScientificReportComposer().compose(
        bundle=ScientificResultBundle.model_validate(bundle_payload),
        interpretation=interpretation_payload,
        relevance_status=relevance,
    ).model_dump(mode="json")
    for figure in report["primary_figures"]:
        figure["caption"] = "Validated scientific figure"
    return json.dumps(report, ensure_ascii=False)


def _scientific_counts(connection) -> dict[str, int]:
    return {
        "plans": connection.execute(select(func.count()).select_from(analysis_plans)).scalar_one(),
        "jobs": connection.execute(select(func.count()).select_from(jobs)).scalar_one(),
        "tool_calls": connection.execute(select(func.count()).select_from(tool_calls)).scalar_one(),
        "artifacts": connection.execute(select(func.count()).select_from(artifacts)).scalar_one(),
        "result_snapshots": connection.execute(select(func.count()).select_from(scientific_result_snapshots)).scalar_one(),
    }


_REOPEN_PROCESS = r"""
import json
import sys
from mdi_api.database import create_repository_factory
from mdi_api.scientific_reports.service import ScientificReportService
report = ScientificReportService(create_repository_factory()).get_by_report_id(sys.argv[1])
print(json.dumps({"report_id": report["report_id"], "title": report["title"], "process_id": __import__("os").getpid()}))
"""


@pytest.fixture(scope="module")
def phase8_service_pipeline():
    phase6 = _phase6_module()
    generator = phase6.phase6_service_pipeline.__wrapped__()
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    queue_name = f"mdi-agent2-phase8-reports-{uuid4().hex[:12]}"
    previous = {key: os.environ.get(key) for key in ("MDI_ENV", "MDI_AGENT2_REPORT_FIXTURE_JSON", "MDI_AGENT2_REPORT_QUEUE_NAME", "MDI_QUEUE_BACKEND")}
    try:
        phase6_data = next(generator)
        database_url = phase6_data["database_url"]
        phase5 = phase6._phase5_module()
        environment = phase5._phase4_module()._worker_environment(database_url)
        environment.update({"MDI_ENV": "ci", "MDI_QUEUE_BACKEND": "redis", "MDI_REDIS_URL": redis_url, "MDI_AGENT2_REPORT_QUEUE_NAME": queue_name})
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        factory = RepositoryFactory(engine)
        with engine.connect() as connection:
            before = _scientific_counts(connection)
        evidence: dict[str, dict] = {}
        for family in ("rdf", "xrd"):
            case = phase6_data["cases"][family]
            with factory.session() as session:
                interpretation = session.agent2.interpretations.get_for_turn(case["turn_id"])
                snapshot = session.agent2.scientific_result_snapshots.get(case["snapshot_id"])
                project = session.connection.execute(select(projects).where(projects.c.id == snapshot["project_id"])).mappings().one()
            assert interpretation is not None
            environment["MDI_AGENT2_REPORT_FIXTURE_JSON"] = _report_fixture(snapshot["bundle_json"], interpretation["output_json"], str(snapshot["relevance_status"]))
            request = ScientificReportRequestService(factory, queue=RedisRQReportQueue(redis_url=redis_url, queue_name=queue_name)).request(case["turn_id"], requested_by=str(project["created_by"]))
            worker = subprocess.run(
                [sys.executable, "-m", "mdi_workers.worker_entrypoint", queue_name, "--url", redis_url, "--burst", "--max-jobs", "1", "--name", f"agent2-phase8-report-{family}"],
                cwd=ROOT, env=environment, capture_output=True, text=True, timeout=240,
            )
            assert worker.returncode == 0, worker.stderr[-6000:]
            task = Queue(queue_name, connection=Redis.from_url(redis_url)).fetch_job(f"agent2-report-{request['generation_id']}")
            assert task is not None and task.is_finished
            result = task.return_value()
            reopen = subprocess.run([sys.executable, "-c", _REOPEN_PROCESS, result["report_id"]], cwd=ROOT, env=environment, capture_output=True, text=True, timeout=60)
            assert reopen.returncode == 0, reopen.stderr[-3000:]
            reopened = json.loads(reopen.stdout.splitlines()[-1])
            assert reopened["report_id"] == result["report_id"]
            assert int(reopened["process_id"]) not in {os.getpid(), int(result["process_id"])}
            evidence[family] = {**result, "reopen_process_id": reopened["process_id"], "turn_id": str(case["turn_id"]), "snapshot_id": str(case["snapshot_id"])}
        with engine.connect() as connection:
            after = _scientific_counts(connection)
            generations = connection.execute(select(func.count()).select_from(agent2_scientific_report_generations)).scalar_one()
            reports = connection.execute(select(func.count()).select_from(agent2_scientific_report_snapshots)).scalar_one()
        assert after == before
        assert generations >= 2 and reports >= 2
        yield {"before": before, "after": after, "evidence": evidence, "generations": generations, "reports": reports}
        engine.dispose()
    finally:
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
@pytest.mark.agent2_phase8_service
def test_agent2_phase8_rdf_report_is_fresh_process_and_zero_computation(phase8_service_pipeline):
    assert phase8_service_pipeline["evidence"]["rdf"]["status"] == "READY"
    assert phase8_service_pipeline["after"] == phase8_service_pipeline["before"]


@pytest.mark.integration
@pytest.mark.agent2_phase8_service
def test_agent2_phase8_xrd_report_is_not_rdf_specific(phase8_service_pipeline):
    assert phase8_service_pipeline["evidence"]["xrd"]["status"] == "READY"
    assert phase8_service_pipeline["evidence"]["xrd"]["report_id"] != phase8_service_pipeline["evidence"]["rdf"]["report_id"]


@pytest.mark.integration
@pytest.mark.agent2_phase8_service
def test_agent2_phase8_report_reopen_does_not_call_provider(phase8_service_pipeline):
    assert phase8_service_pipeline["evidence"]["rdf"]["reopen_process_id"]
    assert phase8_service_pipeline["evidence"]["xrd"]["reopen_process_id"]


@pytest.mark.integration
@pytest.mark.agent2_phase8_service
def test_agent2_phase8_dedicated_selection_has_no_skips(phase8_service_pipeline):
    assert phase8_service_pipeline["generations"] >= 2
    assert phase8_service_pipeline["reports"] >= 2
