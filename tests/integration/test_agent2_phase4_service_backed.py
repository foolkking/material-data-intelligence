from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any
from uuid import uuid4

import pytest
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from pymatgen.core import Lattice, Structure
from redis import Redis
from rq import Queue
from sqlalchemy import create_engine, func, insert, inspect, select
from sqlalchemy.engine import make_url

from mdi_api.artifact_storage import S3CompatibleArtifactStorage
from mdi_api.db import (
    artifacts, data_profiles, datasets, job_events, jobs, organizations, projects,
    research_execution_summaries, research_turn_events, research_turns,
    scientific_result_snapshots, sessions, tool_calls, users,
)
from mdi_api.research_agent.execution.dispatcher import ResearchExecutionDispatcher
from mdi_api.research_agent.llm.schemas import StructuredLLMResult
from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
from mdi_api.research_agent.registry_validation import build_default_agent2_registries
from mdi_api.research_agent.schemas import CreateResearchTurnRequest
from mdi_api.research_agent.service import ResearchTurnService
from mdi_api.routers.auth import CurrentUser
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, ScientificObjectRef, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory, transaction_active
from mdi_workers.queue_runtime import RedisRQQueueBackend
from mdi_artifact_core import content_hash, stable_json_dumps


ROOT = Path(__file__).resolve().parents[2]
LAST_PHASE4_SERVICE_EVIDENCE: dict[str, Any] = {}


def _run_execution_worker_with_timeline(
    *,
    engine,
    database_url: str,
    job_id: str,
    startup_timeout_seconds: float = 120.0,
    timeout_seconds: float = 180.0,
) -> tuple[str, str, dict[str, Any]]:
    """Run a fresh worker with separate startup and execution timing bounds."""

    with tempfile.TemporaryDirectory(prefix="agent2-phase4-worker-") as marker_dir:
        ready_path = Path(marker_dir) / "ready"
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "import os, sys, time; "
                    "from mdi_workers.queue_runtime import run_queued_job; "
                    "Path(sys.argv[2]).write_text(str(time.time()), encoding='utf-8'); "
                    "print(f'EXECUTION_WORKER_PID={os.getpid()}', flush=True); "
                    "result = run_queued_job(sys.argv[1]); "
                    "print(result.status, flush=True)"
                ),
                job_id,
                str(ready_path),
            ],
            cwd=ROOT,
            env=_worker_environment(database_url),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        spawned = time.monotonic()
        while not ready_path.exists() and process.poll() is None and time.monotonic() - spawned < startup_timeout_seconds:
            time.sleep(0.05)
        if not ready_path.exists():
            stdout, stderr = process.communicate(timeout=5)
            raise AssertionError(
                "fresh execution worker readiness timeout; "
                + json.dumps({
                    "startup_timeout_seconds": startup_timeout_seconds,
                    "process_id": process.pid,
                    "stdout": stdout[-2000:],
                    "stderr": stderr[-4000:],
                }, ensure_ascii=False, sort_keys=True)
            )
        execution_started = time.monotonic()
    last_state: tuple[Any, ...] | None = None
    timeline: list[dict[str, Any]] = []
    while process.poll() is None and time.monotonic() - execution_started < timeout_seconds:
        with engine.connect() as connection:
            job = connection.execute(
                select(jobs.c.status).where(jobs.c.id == job_id)
            ).scalar_one()
            calls = connection.execute(
                select(tool_calls.c.step_id, tool_calls.c.status)
                .where(tool_calls.c.job_id == job_id)
                .order_by(tool_calls.c.created_at, tool_calls.c.id)
            ).all()
            artifact_count = connection.execute(
                select(func.count()).select_from(artifacts).where(
                    artifacts.c.job_id == job_id
                )
            ).scalar_one()
            events = connection.execute(
                select(job_events.c.event_type).where(job_events.c.job_id == job_id)
                .order_by(job_events.c.seq)
            ).scalars().all()
        state = (
            str(job),
            tuple((str(step), str(status)) for step, status in calls),
            int(artifact_count),
            tuple(str(item) for item in events),
        )
        if state != last_state:
            timeline.append({
                "elapsed_seconds": round(time.monotonic() - execution_started, 3),
                "job_status": state[0],
                "tool_calls": list(state[1]),
                "artifact_count": state[2],
                "job_events": list(state[3]),
            })
            last_state = state
        time.sleep(0.1)
    if process.poll() is None:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate(timeout=5)
        raise AssertionError(
            "fresh execution worker timeout; "
            + json.dumps(
                {
                    "timeout_seconds": timeout_seconds,
                    "startup_seconds": round(execution_started - spawned, 3),
                    "process_id": process.pid,
                    "stdout": stdout[-2000:],
                    "stderr": stderr[-4000:],
                    "timeline": timeline,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    stdout, stderr = process.communicate(timeout=5)
    execution_wall_seconds = time.monotonic() - execution_started
    first_running = next(
        (item["elapsed_seconds"] for item in timeline if item["job_status"] == "running"),
        None,
    )
    first_tool_running = next(
        (
            item["elapsed_seconds"]
            for item in timeline
            if any(status == "running" for _step, status in item["tool_calls"])
        ),
        None,
    )
    first_artifact = next(
        (item["elapsed_seconds"] for item in timeline if item["artifact_count"] > 0),
        None,
    )
    return stdout, stderr, {
        "returncode": process.returncode,
        "startup_seconds": round(execution_started - spawned, 3),
        "queued_to_terminal_seconds": round(execution_wall_seconds, 3),
        "queued_to_running_seconds": first_running,
        "running_to_tool_seconds": (
            round(first_tool_running - first_running, 3)
            if first_tool_running is not None and first_running is not None
            else None
        ),
        "first_artifact_seconds": first_artifact,
        "timeline": timeline,
    }


class RdfOrchestratorFixture:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.calls = 0

    async def generate_structured(self, **_kwargs: Any) -> StructuredLLMResult:
        assert transaction_active() is False
        with self._lock:
            self.calls += 1
        return StructuredLLMResult(
            provider="fake",
            model="phase4-service-fixture",
            parsed={
                "contract_version": "1.0",
                "action": "ANALYZE",
                "assistant_message": "I will calculate the RDF for the selected structure.",
                "research_objective": "Compute the radial distribution function for the selected structure.",
                "selected_scope_ref_keys": ["obj_1"],
                "scientific_requirements": [{
                    "requirement_id": "structure.compute_rdf",
                    "criticality": "REQUIRED",
                    "subject_ref_keys": ["obj_1"],
                    "constraints": {},
                }],
                "reusable_result_ref_keys": [],
                "clarification": None,
                "confidence": "HIGH",
            },
            latency_ms=1,
            prompt_version="research-orchestrator/1.0",
        )


class XrdOrchestratorFixture:
    async def generate_structured(self, **kwargs: Any) -> StructuredLLMResult:
        assert transaction_active() is False
        objects = kwargs["input_payload"]["research_context"]["objects"]
        structure_key = next(item["ref_key"] for item in objects if item["object_type"] == "structure.crystal")
        experimental_key = next(
            item["ref_key"]
            for item in objects
            if item["object_type"] == "diffraction.xrd.experimental"
        )
        return StructuredLLMResult(
            provider="fake",
            model="phase4-service-fixture",
            parsed={
                "contract_version": "1.0",
                "action": "ANALYZE",
                "assistant_message": "I will generate a theoretical XRD pattern and compare it with the selected experiment.",
                "research_objective": "Generate and compare theoretical and experimental XRD patterns.",
                "selected_scope_ref_keys": [structure_key, experimental_key],
                "scientific_requirements": [
                    {
                        "requirement_id": "diffraction.generate_theoretical_pattern",
                        "criticality": "REQUIRED",
                        "subject_ref_keys": [structure_key],
                        "constraints": {},
                    },
                    {
                        "requirement_id": "diffraction.compare_experimental_theoretical",
                        "criticality": "REQUIRED",
                        "subject_ref_keys": [structure_key, experimental_key],
                        "constraints": {},
                    },
                ],
                "reusable_result_ref_keys": [],
                "clarification": None,
                "confidence": "HIGH",
            },
            latency_ms=1,
            prompt_version="research-orchestrator/1.0",
        )


def _postgres_url() -> str:
    value = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not value or not make_url(value).get_backend_name().startswith("postgresql"):
        if os.getenv("MDI_RUN_INTEGRATION") == "1":
            raise RuntimeError("PostgreSQL is required for the enabled Agent2 Phase4 integration gate")
        pytest.skip("A PostgreSQL MDI_TEST_DATABASE_URL or DATABASE_URL is required")
    parsed = make_url(value)
    # Docker Desktop can publish the test database on IPv4 only while Windows
    # resolves localhost to ::1 first. Fresh worker processes then wait on the
    # unreachable IPv6 address before psycopg can try IPv4.
    if os.name == "nt" and parsed.host == "localhost":
        return parsed.set(host="127.0.0.1").render_as_string(hide_password=False)
    return value


def _minio_storage() -> S3CompatibleArtifactStorage:
    try:
        import boto3

        endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
        access = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
        secret = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
        bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
        client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access,
            aws_secret_access_key=secret,
            region_name="us-east-1",
        )
        try:
            client.head_bucket(Bucket=bucket)
        except Exception:
            client.create_bucket(Bucket=bucket)
        return S3CompatibleArtifactStorage(
            bucket=bucket,
            endpoint_url=endpoint,
            access_key_id=access,
            secret_access_key=secret,
            client=client,
        )
    except Exception as exc:
        if os.getenv("MDI_RUN_INTEGRATION") == "1":
            raise RuntimeError("MinIO is required for the enabled Agent2 Phase4 integration gate") from exc
        pytest.skip("MinIO is not available")


def _worker_environment(database_url: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update({
        "DATABASE_URL": database_url,
        "MDI_DATABASE_URL": database_url,
        "MDI_ARTIFACT_BACKEND": "minio",
        "MDI_RUNTIME_BACKEND": "postgresql",
    })
    python_paths = [
        ROOT / "apps" / "api",
        ROOT / "services" / "workers",
        ROOT / "packages" / "schemas",
        ROOT / "packages" / "tool-registry",
        ROOT / "packages" / "adapters",
        ROOT / "packages" / "artifact-core",
        ROOT / "packages" / "material-parsers",
        ROOT / "packages" / "llm-client",
    ]
    environment["PYTHONPATH"] = os.pathsep.join(
        [*(str(path) for path in python_paths), environment.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)
    return environment


@pytest.mark.integration
def test_agent2_phase4_fresh_worker_executes_exact_plan_and_stops_at_result_pending():
    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    alembic_command.upgrade(config, "head")
    engine = create_engine(database_url, future=True, pool_pre_ping=True)
    assert "research_execution_summaries" in inspect(engine).get_table_names()

    suffix = uuid4().hex[:12]
    owner = CurrentUser(
        id=f"agent2-phase4-owner-{suffix}",
        email=f"agent2-phase4-{suffix}@example.invalid",
        displayName="Agent2 Phase4 Owner",
        roles=[],
    )
    org_id = f"agent2-phase4-org-{suffix}"
    project_id = f"agent2-phase4-project-{suffix}"
    session_id = f"agent2-phase4-session-{suffix}"
    dataset_id = f"agent2-phase4-dataset-{suffix}"
    profile_id = f"agent2-phase4-profile-{suffix}"
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": owner.id, "email": owner.email, "display_name": owner.displayName, "is_active": True})
        connection.execute(insert(organizations), {"id": org_id, "name": f"Agent2 Phase4 {suffix}"})
        connection.execute(insert(projects), {"id": project_id, "organization_id": org_id, "name": f"Agent2 Phase4 {suffix}", "created_by": owner.id})
        connection.execute(insert(datasets), {"id": dataset_id, "project_id": project_id, "name": "Phase4 RDF Dataset", "status": "profile_ready", "metadata_json": {}, "created_by": owner.id})
        connection.execute(insert(data_profiles), {"id": profile_id, "dataset_id": dataset_id, "version": "2.0", "profile_json": {"id": profile_id, "datasetId": dataset_id}})
        connection.execute(insert(sessions), {"id": session_id, "project_id": project_id, "dataset_id": dataset_id, "mode": "project", "status": "active", "created_by": owner.id})

    storage = _minio_storage()
    structure_payload = Structure(
        Lattice.cubic(5.43),
        ["Si", "Si"],
        [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
    ).as_dict()
    stored = storage.put_json(
        f"projects/{project_id}/agent2/sources/structure-v1.json",
        structure_payload,
    )
    factory = RepositoryFactory(engine)
    objects = ScientificObjectService(factory, build_default_object_type_registry())
    logical = objects.create_object(
        project_id=project_id,
        kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal",
        display_name="Phase4 exact silicon structure",
        created_by_user_id=owner.id,
    )
    version = objects.create_version(
        logical["id"],
        object_type="structure.crystal",
        object_schema_version="1.0",
        source_resource_refs=[{"project_id": project_id, "dataset_id": dataset_id}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="minio",
            object_key=stored.storage_key,
            checksum=stored.sha256,
            media_type="application/json",
            byte_size=stored.size_bytes,
        ),
        content_hash=stored.sha256,
        semantic_hash=f"phase4-semantic-{suffix}",
        canonical_metadata={"formula": "Si2"},
        created_by_user_id=owner.id,
    )
    object_ref = ScientificObjectRef(
        object_id=logical["id"],
        version_id=version["id"],
        project_id=project_id,
        object_type="structure.crystal",
        display_name=logical["display_name"],
    )
    turn_service = ResearchTurnService(factory)
    received = turn_service.receive_turn(
        project_id=project_id,
        session_id=session_id,
        request=CreateResearchTurnRequest(
            message="Calculate the RDF for this structure.",
            ui_context={"active_object_refs": [object_ref], "selection_refs": []},
        ),
        current_user=owner,
    )
    orchestrator = RdfOrchestratorFixture()
    assert asyncio.run(AgentTurnProcessor(
        repository_factory=factory,
        registries=build_default_agent2_registries(),
        llm_client=orchestrator,
    ).process(received.turn_id)).status == "READY_TO_PLAN"
    planned = CapabilityPlanningProcessor(
        factory,
        registries=build_default_agent2_registries(),
    ).process(received.turn_id)
    assert planned["status"] == "PLAN_READY"
    assert orchestrator.calls == 1

    redis_url = os.getenv("MDI_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    queue_name = f"mdi-agent2-phase4-{suffix}"
    queue = Queue(queue_name, connection=Redis.from_url(redis_url))
    dispatcher = ResearchExecutionDispatcher(
        factory,
        queue=RedisRQQueueBackend(redis_url=redis_url, queue_name=queue_name),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        dispatches = list(pool.map(lambda _index: dispatcher.dispatch_turn(received.turn_id), range(2)))
    assert len({item.job_id for item in dispatches}) == 1
    dispatched = dispatches[0]
    queued_job = queue.fetch_job(dispatched.job_id)
    assert any(item.queued for item in dispatches)
    assert queued_job is not None
    assert queued_job.args == (dispatched.job_id,) and queued_job.kwargs == {}
    with engine.connect() as connection:
        assert connection.execute(select(func.count()).select_from(jobs).where(jobs.c.id == dispatched.job_id)).scalar_one() == 1

    before = {
        "results": 0,
        "tools": 0,
        "artifacts": 0,
    }
    with engine.connect() as connection:
        before = {
            "results": connection.execute(select(func.count()).select_from(scientific_result_snapshots).where(scientific_result_snapshots.c.research_turn_id == received.turn_id)).scalar_one(),
            "tools": connection.execute(select(func.count()).select_from(tool_calls).where(tool_calls.c.job_id == dispatched.job_id)).scalar_one(),
            "artifacts": connection.execute(select(func.count()).select_from(artifacts).where(artifacts.c.job_id == dispatched.job_id)).scalar_one(),
        }

    stdout, stderr, rdf_timing = _run_execution_worker_with_timeline(
        engine=engine,
        database_url=database_url,
        job_id=dispatched.job_id,
    )
    assert stdout.strip().endswith("completed"), json.dumps(
        {
            "returncode": rdf_timing.get("returncode"),
            "stdout": stdout[-4000:],
            "stderr": stderr[-4000:],
            "timing": rdf_timing,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    rdf_worker_pid = int(next(line.split("=", 1)[1] for line in stdout.splitlines() if line.startswith("EXECUTION_WORKER_PID=")))
    assert rdf_worker_pid != os.getpid()

    with engine.connect() as connection:
        turn = connection.execute(select(research_turns).where(research_turns.c.id == received.turn_id)).mappings().one()
        job = connection.execute(select(jobs).where(jobs.c.id == dispatched.job_id)).mappings().one()
        calls = connection.execute(select(tool_calls).where(tool_calls.c.job_id == dispatched.job_id)).mappings().all()
        output_rows = connection.execute(select(artifacts).where(artifacts.c.job_id == dispatched.job_id)).mappings().all()
        summary = connection.execute(select(research_execution_summaries).where(research_execution_summaries.c.research_turn_id == received.turn_id)).mappings().one()
        result_count = connection.execute(select(func.count()).select_from(scientific_result_snapshots).where(scientific_result_snapshots.c.research_turn_id == received.turn_id)).scalar_one()
        events = connection.execute(select(research_turn_events).where(research_turn_events.c.turn_id == received.turn_id).order_by(research_turn_events.c.sequence_no)).mappings().all()

    assert job["status"] == "completed"
    assert turn["status"] == "RESULT_PENDING"
    assert turn["assistant_final_message_id"] is None
    assert summary["execution_outcome"] == "SUCCESS"
    assert len(calls) == before["tools"] + 1
    assert len(output_rows) > before["artifacts"]
    assert result_count == before["results"] == 0
    event_types = [item["event_type"] for item in events]
    assert event_types.index("EXECUTION_OUTPUT_AVAILABLE") < event_types.index("RESULT_PENDING")
    assert not any(item["event_type"] == "TURN_COMPLETED" for item in events)

    experimental_resource = {
        "schemaVersion": "phase10n3.experimental_xrd_resource.v1",
        "resourceId": f"experimental-xrd-{suffix}",
        "resourceVersion": "1",
        "xAxis": {"kind": "two_theta", "unit": "degree"},
        "twoTheta": [19.8, 20.0, 20.2, 39.8, 40.0, 40.2, 59.8, 60.0, 60.2],
        "intensity": [0.0, 10.0, 0.0, 0.0, 8.0, 0.0, 0.0, 6.0, 0.0],
        "intensitySemantic": "counts",
        "wavelength": {"value": 1.54184, "unit": "angstrom"},
    }
    experimental_resource["resourceHash"] = content_hash(stable_json_dumps(experimental_resource))
    experimental_rows = [
        {"two_theta": two_theta, "intensity": intensity}
        for two_theta, intensity in zip(
            experimental_resource["twoTheta"],
            experimental_resource["intensity"],
            strict=True,
        )
    ]
    stored_experimental = storage.put_json(
        f"projects/{project_id}/agent2/sources/experimental-xrd-v1.json",
        experimental_rows,
    )
    experimental_object = objects.create_object(
        project_id=project_id,
        kind=ScientificObjectKind.DIFFRACTION,
        object_type="diffraction.xrd.experimental",
        display_name="Phase4 experimental XRD",
        created_by_user_id=owner.id,
    )
    experimental_version = objects.create_version(
        experimental_object["id"],
        object_type="diffraction.xrd.experimental",
        object_schema_version="1.0",
        source_resource_refs=[{"project_id": project_id, "dataset_id": dataset_id}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="minio",
            object_key=stored_experimental.storage_key,
            checksum=stored_experimental.sha256,
            media_type="application/json",
            byte_size=stored_experimental.size_bytes,
        ),
        content_hash=stored_experimental.sha256,
        semantic_hash=f"phase4-xrd-semantic-{suffix}",
        canonical_metadata={"experimentalXrd": experimental_resource},
        created_by_user_id=owner.id,
    )
    experimental_ref = ScientificObjectRef(
        object_id=experimental_object["id"],
        version_id=experimental_version["id"],
        project_id=project_id,
        object_type="diffraction.xrd.experimental",
        display_name=experimental_object["display_name"],
    )
    xrd_received = turn_service.receive_turn(
        project_id=project_id,
        session_id=session_id,
        request=CreateResearchTurnRequest(
            message="Generate theoretical XRD and compare it with this experiment.",
            ui_context={
                "active_object_refs": [object_ref, experimental_ref],
                "selection_refs": [object_ref, experimental_ref],
            },
        ),
        current_user=owner,
    )
    assert asyncio.run(AgentTurnProcessor(
        repository_factory=factory,
        registries=build_default_agent2_registries(),
        llm_client=XrdOrchestratorFixture(),
    ).process(xrd_received.turn_id)).status == "READY_TO_PLAN"
    xrd_planned = CapabilityPlanningProcessor(
        factory,
        registries=build_default_agent2_registries(),
    ).process(xrd_received.turn_id)
    assert xrd_planned["status"] == "PLAN_READY"

    xrd_queue_name = f"mdi-agent2-phase4-xrd-{suffix}"
    xrd_queue = Queue(xrd_queue_name, connection=Redis.from_url(redis_url))
    xrd_dispatch = ResearchExecutionDispatcher(
        factory,
        queue=RedisRQQueueBackend(redis_url=redis_url, queue_name=xrd_queue_name),
    ).dispatch_turn(xrd_received.turn_id)
    assert xrd_dispatch.queued is True

    with tempfile.TemporaryDirectory(prefix="agent2-phase4-xrd-") as barrier_dir:
        signal_path = Path(barrier_dir) / "output-visible"
        release_path = Path(barrier_dir) / "continue"
        worker_script = """
from pathlib import Path
import sys
import time
import os
from mdi_workers.queue_runtime import QueueWorkerRuntime, run_queued_job

print(f"EXECUTION_WORKER_PID={os.getpid()}")

signal_path = Path(sys.argv[2])
release_path = Path(sys.argv[3])
original = QueueWorkerRuntime._notify_agent2_progress

def notify_with_barrier(job_id):
    original(job_id)
    from mdi_api.database import create_repository_factory
    with create_repository_factory().session() as session:
        events = session.agent2.research_turn_events.list_for_turn(sys.argv[4])
    if any(item["event_type"] == "EXECUTION_OUTPUT_AVAILABLE" for item in events) and not signal_path.exists():
        signal_path.write_text("visible", encoding="utf-8")
        deadline = time.monotonic() + 15
        while not release_path.exists() and time.monotonic() < deadline:
            time.sleep(0.02)

QueueWorkerRuntime._notify_agent2_progress = staticmethod(notify_with_barrier)
result = run_queued_job(sys.argv[1])
print(result.status)
"""
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                worker_script,
                xrd_dispatch.job_id,
                str(signal_path),
                str(release_path),
                str(xrd_received.turn_id),
            ],
            cwd=ROOT,
            env=_worker_environment(database_url),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.monotonic() + 30
        while not signal_path.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.02)
        assert signal_path.exists(), (process.stderr.read()[-4000:] if process.poll() is not None else "barrier timeout")
        with engine.connect() as connection:
            live_job = connection.execute(select(jobs).where(jobs.c.id == xrd_dispatch.job_id)).mappings().one()
            live_events = connection.execute(
                select(research_turn_events)
                .where(research_turn_events.c.turn_id == xrd_received.turn_id)
                .order_by(research_turn_events.c.sequence_no)
            ).mappings().all()
        assert live_job["status"] == "running"
        assert any(item["event_type"] == "EXECUTION_OUTPUT_AVAILABLE" for item in live_events)
        assert not any(item["event_type"] == "RESULT_PENDING" for item in live_events)
        release_path.write_text("continue", encoding="utf-8")
        stdout, stderr = process.communicate(timeout=180)
        assert process.returncode == 0, stderr[-4000:]
        assert stdout.strip().endswith("completed")
        xrd_worker_pid = int(next(line.split("=", 1)[1] for line in stdout.splitlines() if line.startswith("EXECUTION_WORKER_PID=")))
        assert xrd_worker_pid != os.getpid()

    with engine.connect() as connection:
        xrd_turn = connection.execute(select(research_turns).where(research_turns.c.id == xrd_received.turn_id)).mappings().one()
        xrd_calls = connection.execute(
            select(tool_calls)
            .where(tool_calls.c.job_id == xrd_dispatch.job_id)
            .order_by(tool_calls.c.step_id)
        ).mappings().all()
        xrd_summary = connection.execute(select(research_execution_summaries).where(research_execution_summaries.c.research_turn_id == xrd_received.turn_id)).mappings().one()
        xrd_events = connection.execute(
            select(research_turn_events)
            .where(research_turn_events.c.turn_id == xrd_received.turn_id)
            .order_by(research_turn_events.c.sequence_no)
        ).mappings().all()
    assert xrd_turn["status"] == "RESULT_PENDING"
    assert xrd_turn["assistant_final_message_id"] is None
    assert xrd_summary["execution_outcome"] == "SUCCESS"
    assert [item["tool_id"] for item in xrd_calls] == [
        "structure.xrd",
        "structure.experimental_xrd_comparison",
    ]
    xrd_event_types = [item["event_type"] for item in xrd_events]
    assert xrd_event_types.index("EXECUTION_OUTPUT_AVAILABLE") < xrd_event_types.index("RESULT_PENDING")

    LAST_PHASE4_SERVICE_EVIDENCE.clear()
    LAST_PHASE4_SERVICE_EVIDENCE.update({
        "api_fixture_pid": os.getpid(),
        "rdf": {
            "turn_id": str(received.turn_id),
            "job_id": dispatched.job_id,
            "execution_worker_pid": rdf_worker_pid,
            "timing": rdf_timing,
        },
        "xrd": {"turn_id": str(xrd_received.turn_id), "job_id": xrd_dispatch.job_id, "execution_worker_pid": xrd_worker_pid},
        "owner": {"id": owner.id, "email": owner.email},
        "project_id": project_id,
    })
    print(json.dumps({
        "phase4_fresh_worker_timing": {
            "rdf": rdf_timing,
            "execution_timeout_seconds": 180.0,
            "startup_timeout_seconds": 120.0,
        }
    }, sort_keys=True))

    queued_job.delete()
    queued_xrd_job = xrd_queue.fetch_job(xrd_dispatch.job_id)
    if queued_xrd_job is not None:
        queued_xrd_job.delete()
    engine.dispose()
