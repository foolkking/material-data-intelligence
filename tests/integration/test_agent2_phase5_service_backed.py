from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
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
from sqlalchemy import create_engine, func, insert, select

from mdi_api.db import (
    artifacts,
    auth_sessions,
    jobs,
    research_turns,
    scientific_result_snapshots,
    tool_calls,
    users,
)
from mdi_api.scientific_results.projectors.canonical import resolve_json_pointer


ROOT = Path(__file__).resolve().parents[2]


def _phase4_module():
    path = ROOT / "tests" / "integration" / "test_agent2_phase4_service_backed.py"
    spec = importlib.util.spec_from_file_location("agent2_phase4_service_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def phase5_service_pipeline():
    phase4 = _phase4_module()
    database_url = phase4._postgres_url()
    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    result_queue_name = f"mdi-agent2-phase5-results-{uuid4().hex[:12]}"
    previous = {
        key: os.environ.get(key)
        for key in (
            "MDI_QUEUE_BACKEND",
            "MDI_AGENT2_RESULT_PROJECTION_ENABLED",
            "MDI_AGENT2_RESULT_QUEUE_NAME",
            "MDI_AGENT2_INTERPRETATION_ENABLED",
        )
    }
    os.environ.update({
        "MDI_QUEUE_BACKEND": "redis",
        "MDI_AGENT2_RESULT_PROJECTION_ENABLED": "1",
        "MDI_AGENT2_RESULT_QUEUE_NAME": result_queue_name,
        # This fixture validates Result projection in isolation. A shared
        # interpretation worker must not consume its wakeup and race the
        # RESULT_READY assertions with an unrelated provider failure.
        "MDI_AGENT2_INTERPRETATION_ENABLED": "0",
    })
    try:
        phase4.test_agent2_phase4_fresh_worker_executes_exact_plan_and_stops_at_result_pending()
        evidence = dict(phase4.LAST_PHASE4_SERVICE_EVIDENCE)
        assert evidence["rdf"]["execution_worker_pid"] != evidence["api_fixture_pid"]
        assert evidence["xrd"]["execution_worker_pid"] != evidence["api_fixture_pid"]

        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        cases = {name: dict(evidence[name]) for name in ("rdf", "xrd")}
        with engine.connect() as connection:
            for case in cases.values():
                case["job_count_before"] = connection.execute(select(func.count()).select_from(jobs)).scalar_one()
                case["tool_count_before"] = connection.execute(select(func.count()).select_from(tool_calls)).scalar_one()
                row = connection.execute(select(research_turns).where(research_turns.c.id == case["turn_id"])).mappings().one()
                assert row["status"] == "RESULT_PENDING"
                assert row["assistant_final_message_id"] is None

        result_queue = Queue(result_queue_name, connection=Redis.from_url(redis_url))
        for case in cases.values():
            task = result_queue.fetch_job(f"agent2-result-{case['turn_id']}")
            assert task is not None
            assert task.args == (case["turn_id"],) and task.kwargs == {}

        environment = phase4._worker_environment(database_url)
        environment.update({
            "MDI_QUEUE_BACKEND": "redis",
            "MDI_REDIS_URL": redis_url,
            "MDI_AGENT2_RESULT_PROJECTION_ENABLED": "1",
            "MDI_AGENT2_RESULT_QUEUE_NAME": result_queue_name,
            "MDI_AGENT2_INTERPRETATION_ENABLED": "0",
        })
        concurrent_script = """
import json, os, sys
from mdi_api.scientific_results.worker import run_queued_result_projection
result = run_queued_result_projection(sys.argv[1])
print(json.dumps(result))
"""
        concurrent_workers = [
            subprocess.Popen(
                [sys.executable, "-c", concurrent_script, cases["rdf"]["turn_id"]],
                cwd=ROOT, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            for _ in range(2)
        ]
        concurrent_pids = set()
        for process in concurrent_workers:
            stdout, stderr = process.communicate(timeout=120)
            assert process.returncode == 0, stderr[-5000:]
            worker_result = json.loads(stdout.splitlines()[-1])
            concurrent_pids.add(int(worker_result["process_id"]))
        assert len(concurrent_pids) == 2
        with engine.connect() as connection:
            assert connection.execute(
                select(func.count()).select_from(scientific_result_snapshots).where(
                    scientific_result_snapshots.c.research_turn_id == cases["rdf"]["turn_id"]
                )
            ).scalar_one() == 1

        result_process = subprocess.run(
            [sys.executable, "-m", "mdi_workers.worker_entrypoint", result_queue_name, "--url", redis_url, "--burst", "--max-jobs", "2", "--name", f"agent2-phase5-result-{uuid4().hex[:8]}"],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=240,
        )
        assert result_process.returncode == 0, result_process.stderr[-6000:]
        result_pids = set()
        for case in cases.values():
            task = result_queue.fetch_job(f"agent2-result-{case['turn_id']}")
            assert task is not None and task.is_finished
            result_pids.add(int(task.return_value()["process_id"]))
        assert result_pids
        result_pids.update(concurrent_pids)
        assert not result_pids.intersection({evidence["api_fixture_pid"], evidence["rdf"]["execution_worker_pid"], evidence["xrd"]["execution_worker_pid"]})

        storage = phase4._minio_storage()
        with engine.connect() as connection:
            for name, case in cases.items():
                turn = connection.execute(select(research_turns).where(research_turns.c.id == case["turn_id"])).mappings().one()
                snapshots = connection.execute(select(scientific_result_snapshots).where(scientific_result_snapshots.c.research_turn_id == case["turn_id"])).mappings().all()
                assert turn["status"] == "RESULT_READY"
                assert turn["assistant_final_message_id"] is None
                assert len(snapshots) == 1
                case["bundle"] = dict(snapshots[0]["bundle_json"])
                case["snapshot_id"] = str(snapshots[0]["id"])
                assert connection.execute(select(func.count()).select_from(jobs)).scalar_one() == case["job_count_before"]
                assert connection.execute(select(func.count()).select_from(tool_calls)).scalar_one() == case["tool_count_before"]

                for fact in case["bundle"]["facts"]:
                    artifact_id = fact["source"]["artifact_id"]
                    artifact = connection.execute(select(artifacts).where(artifacts.c.id == artifact_id)).mappings().one()
                    payload = storage.get_json(str(artifact["storage_key"]))
                    assert resolve_json_pointer(payload, fact["source"]["artifact_locator"]) == fact["value"]

        owner_token = f"phase5-owner-{uuid4().hex}"
        outsider_token = f"phase5-outsider-{uuid4().hex}"
        outsider_id = f"agent2-phase5-outsider-{uuid4().hex[:12]}"
        with engine.begin() as connection:
            connection.execute(insert(users), {"id": outsider_id, "email": f"{outsider_id}@example.invalid", "display_name": "Phase5 outsider", "is_active": True})
            expires = datetime.now(timezone.utc) + timedelta(hours=1)
            connection.execute(insert(auth_sessions), [
                {"id": f"auth-{uuid4().hex}", "user_id": evidence["owner"]["id"], "token_hash": _token_hash(owner_token), "expires_at": expires},
                {"id": f"auth-{uuid4().hex}", "user_id": outsider_id, "token_hash": _token_hash(outsider_token), "expires_at": expires},
            ])

        api_script = """
import json, os, sys
from fastapi.testclient import TestClient
from mdi_api.main import create_app
turn_id, owner_token, outsider_token = sys.argv[1:4]
with TestClient(create_app()) as client:
    owner = client.get(f'/api/research/turns/{turn_id}/result', cookies={'mdi_session': owner_token})
    outsider = client.get(f'/api/research/turns/{turn_id}/result', cookies={'mdi_session': outsider_token})
print(json.dumps({'api_pid': os.getpid(), 'owner_status': owner.status_code, 'outsider_status': outsider.status_code, 'body': owner.json()}))
"""
        api_process = subprocess.run(
            [sys.executable, "-c", api_script, cases["rdf"]["turn_id"], owner_token, outsider_token],
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert api_process.returncode == 0, api_process.stderr[-4000:]
        api_evidence = json.loads(api_process.stdout.splitlines()[-1])
        assert api_evidence["owner_status"] == 200
        assert api_evidence["outsider_status"] == 403
        assert api_evidence["api_pid"] not in result_pids
        assert api_evidence["body"]["research_turn_id"] == cases["rdf"]["turn_id"]
        # The immutable persistence row has its own snapshot primary key. The
        # public Result identity is the deterministic bundle result_id, which
        # is the identifier presentation and provenance consumers must retain.
        assert api_evidence["body"]["result_id"] == cases["rdf"]["bundle"]["result_id"]
        assert api_evidence["body"]["source_object_refs"] == cases["rdf"]["bundle"]["source_object_refs"]
        assert api_evidence["body"]["facts"] == cases["rdf"]["bundle"]["facts"]

        print(json.dumps({
            "phase5_fresh_process_evidence": {
                "api_pid": api_evidence["api_pid"],
                "execution_worker_pids": [evidence["rdf"]["execution_worker_pid"], evidence["xrd"]["execution_worker_pid"]],
                "result_worker_pids": sorted(result_pids),
                "rdf": "PASS",
                "xrd_two_step": "PASS",
                "selected_skip": 0,
            }
        }, sort_keys=True))
        yield cases
        for case in cases.values():
            task = result_queue.fetch_job(f"agent2-result-{case['turn_id']}")
            if task is not None:
                task.delete()
        result_queue.delete(delete_jobs=True)
        engine.dispose()
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@pytest.mark.integration
@pytest.mark.agent2_phase5_service
def test_agent2_phase5_rdf_fresh_process_auto_projection(phase5_service_pipeline):
    bundle = phase5_service_pipeline["rdf"]["bundle"]
    assert bundle["execution_status"] == "SUCCESS"
    assert bundle["source_object_refs"]
    assert {item["result_type"] for item in bundle["result_items"]} == {"structure.rdf"}
    assert {fact["predicate"] for fact in bundle["facts"]} >= {"rdf.structure_count", "rdf.bin_count", "rdf.number_density"}
    assert bundle["provenance"]["artifact_ids"]


@pytest.mark.integration
@pytest.mark.agent2_phase5_service
def test_agent2_phase5_xrd_two_step_fresh_process_auto_projection(phase5_service_pipeline):
    bundle = phase5_service_pipeline["xrd"]["bundle"]
    assert bundle["execution_status"] == "SUCCESS"
    assert len(bundle["source_object_refs"]) == 2
    assert {item["result_type"] for item in bundle["result_items"]} == {"diffraction.xrd.theoretical", "diffraction.xrd.comparison"}
    assert len(bundle["provenance"]["tool_call_ids"]) == 2
    assert {fact["predicate"] for fact in bundle["facts"]} >= {"xrd.peak_count", "xrd.matched_peak_count"}
