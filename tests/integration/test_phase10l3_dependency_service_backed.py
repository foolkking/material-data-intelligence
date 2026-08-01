from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect

from mdi_api.artifact_storage import S3CompatibleArtifactStorage
from mdi_api.repositories import SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_schemas import AnalysisPlanV02, compute_dependency_graph_hash, make_dependency_binding
from mdi_tool_registry import load_manifests, validate_dependency_plan
from mdi_workers import QueueWorkerRuntime, RedisRQQueueBackend


ROOT = Path(__file__).resolve().parents[2]
PHONON_FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"


def _source(name: str) -> dict[str, Any]:
    return json.loads((PHONON_FIXTURES / name).read_text(encoding="utf-8"))


def _step(
    step_id: str,
    tool_id: str,
    *,
    refs: list[dict[str, Any]],
    artifacts: list[str],
) -> dict[str, Any]:
    return {
        "stepId": step_id,
        "toolId": tool_id,
        "purpose": f"Execute {tool_id}",
        "reason": "Phase 10L-3 live typed dependency integration fixture.",
        "inputRefs": refs,
        "params": {},
        "output": {"artifactTypes": artifacts, "displayTarget": "phonon"},
    }


def _plan(*, dataset_id: str, profile_id: str) -> AnalysisPlanV02:
    band_binding = make_dependency_binding(
        producerStepId="step_band",
        producerOutputPort="canonical-band",
        consumerStepId="step_combined",
        consumerInputPort="band",
        artifactKind="phonon_band_json",
        artifactContractVersion="phase10h.phonon_band.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    dos_binding = make_dependency_binding(
        producerStepId="step_dos",
        producerOutputPort="canonical-dos",
        consumerStepId="step_combined",
        consumerInputPort="dos",
        artifactKind="phonon_dos_json",
        artifactContractVersion="phase10h.phonon_dos.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    bindings = [band_binding, dos_binding]
    registry = load_manifests()
    return AnalysisPlanV02.model_validate(
        {
            "schemaVersion": "0.2",
            "goal": "Build a typed phonon band and DOS linked product.",
            "datasetId": dataset_id,
            "profileId": profile_id,
            "toolRegistryVersion": registry.version,
            "assumptions": [],
            "warnings": [],
            # Consumer-first storage order proves runtime topology is authoritative.
            "steps": [
                _step(
                    "step_combined",
                    "phonon.band_dos",
                    refs=[],
                    artifacts=["phonon_band_dos_json"],
                ),
                _step(
                    "step_dos",
                    "phonon.dos",
                    refs=[
                        {
                            "refType": "normalized_object",
                            "ref": "source_dos",
                            "objectType": "PhononDos",
                        }
                    ],
                    artifacts=["phonon_dos_json"],
                ),
                _step(
                    "step_band",
                    "phonon.band",
                    refs=[
                        {
                            "refType": "normalized_object",
                            "ref": "source_band",
                            "objectType": "PhononBand",
                        }
                    ],
                    artifacts=["phonon_band_json"],
                ),
            ],
            "expectedArtifacts": [
                {"name": "phonon_band.json", "type": "phonon_band_json", "fromStepId": "step_band"},
                {"name": "phonon_dos.json", "type": "phonon_dos_json", "fromStepId": "step_dos"},
                {
                    "name": "phonon_band_dos.json",
                    "type": "phonon_band_dos_json",
                    "fromStepId": "step_combined",
                },
            ],
            "graphHash": compute_dependency_graph_hash(bindings),
            "dependencyBindings": [item.model_dump(mode="json") for item in bindings],
        }
    )


def _postgres_url() -> str:
    url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url or "postgres" not in url:
        if os.getenv("MDI_RUN_INTEGRATION") == "1":
            raise RuntimeError("PostgreSQL DATABASE_URL is required for the enabled integration gate")
        pytest.skip("No PostgreSQL DATABASE_URL configured")
    return url


def _redis_backend(*, queue_name: str) -> tuple[RedisRQQueueBackend, Any]:
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not redis_url:
        pytest.skip("No REDIS_URL configured")
    try:
        from redis import Redis
        from rq import Queue

        connection = Redis.from_url(redis_url)
        connection.ping()
        return RedisRQQueueBackend(redis_url=redis_url, queue_name=queue_name), Queue(
            queue_name,
            connection=connection,
        )
    except Exception as exc:
        if os.getenv("MDI_RUN_INTEGRATION") == "1":
            raise RuntimeError("Redis/RQ is not reachable for the enabled integration gate") from exc
        pytest.skip("Redis/RQ not reachable")


def _minio_storage(*, prefix: str) -> S3CompatibleArtifactStorage:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
    secret = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    try:
        import boto3

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
    except Exception as exc:
        if os.getenv("MDI_RUN_INTEGRATION") == "1":
            raise RuntimeError("MinIO is not reachable for the enabled integration gate") from exc
        pytest.skip("MinIO not reachable")
    return S3CompatibleArtifactStorage(
        bucket=bucket,
        endpoint_url=endpoint,
        prefix=prefix,
        access_key_id=access,
        secret_access_key=secret,
        client=client,
    )


@pytest.mark.integration
def test_phase10l3_postgres_redis_minio_typed_dependency_execution() -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic_upgrade(config, "head")

    suffix = uuid.uuid4().hex[:12]
    ids = {
        "project": f"project_l3_service_{suffix}",
        "dataset": f"dataset_l3_service_{suffix}",
        "profile": f"profile_l3_service_{suffix}",
        "plan": f"plan_l3_service_{suffix}",
        "job": f"job_l3_service_{suffix}",
    }
    plan = _plan(dataset_id=ids["dataset"], profile_id=ids["profile"])
    registry = load_manifests()
    validation = validate_dependency_plan(plan, registry=registry)
    assert validation.ok
    assert validation.topological_order == ["step_band", "step_dos", "step_combined"]
    assert plan.steps[0].stepId == "step_combined"

    engine = create_engine(database_url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    expected_tables = {
        "plan_dependency_bindings",
        "runtime_artifact_binding_resolutions",
        "dependency_execution_records",
        "artifact_lineage_records",
    }
    assert expected_tables.issubset(inspect(engine).get_table_names())

    repos.projects.save({"id": ids["project"], "name": ids["project"], "createdBy": "phase10l3_ci"})
    repos.datasets.save(
        {
            "id": ids["dataset"],
            "projectId": ids["project"],
            "name": ids["dataset"],
            "createdBy": "phase10l3_ci",
        }
    )
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan(
        {
            "id": ids["plan"],
            "projectId": ids["project"],
            "datasetId": ids["dataset"],
            "profileId": ids["profile"],
            "planSource": "capability_planner",
            "plannerProvider": "mock",
            "analysisPlan": plan.model_dump(mode="json"),
            "planHash": plan_hash,
            "createdBy": "phase10l3_ci",
        }
    )
    persisted = repos.analysis_plans.get_plan(ids["plan"])
    assert persisted["analysisPlan"]["schemaVersion"] == "0.2"
    assert persisted["planHash"] == plan_hash
    planned_bindings = repos.dependency_execution.save_plan_bindings(
        ids["plan"],
        plan_hash,
        plan.graphHash,
        plan.dependencyBindings,
    )
    assert len(planned_bindings) == 2
    repos.jobs.save(
        {
            "id": ids["job"],
            "projectId": ids["project"],
            "datasetId": ids["dataset"],
            "planId": ids["plan"],
            "status": "created",
            "kind": "analysis",
            "createdBy": "phase10l3_ci",
        }
    )
    repos.analysis_plans.attach_plan_to_job(ids["plan"], ids["job"])

    queue_name = f"mdi-test-phase10l3-{suffix}"
    queue_backend, redis_queue = _redis_backend(queue_name=queue_name)
    storage = _minio_storage(prefix=f"phase10l3-{suffix}")
    runtime = QueueWorkerRuntime(
        repositories=repos,
        queue_backend=queue_backend,
        artifact_storage=storage,
        registry=registry,
    )
    submitted = runtime.submit_job(ids["job"])
    assert submitted.enqueued is True
    assert submitted.backend == "rq"
    assert redis_queue.fetch_job(ids["job"]) is not None

    result = runtime.handle_job(
        ids["job"],
        object_store={
            "source_band": _source("stable_band.json"),
            "source_dos": _source("projected_dos.json"),
        },
    )
    assert result.status == "completed"
    assert result.plan_id == ids["plan"]
    assert result.plan_hash == plan_hash

    calls = repos.tool_calls.list_for_job(ids["job"])
    calls_by_step = {item["stepId"]: item for item in calls}
    assert {
        step_id: (item["toolId"], item["status"])
        for step_id, item in calls_by_step.items()
    } == {
        "step_band": ("phonon.band", "completed"),
        "step_dos": ("phonon.dos", "completed"),
        "step_combined": ("phonon.band_dos", "completed"),
    }
    started_steps = [
        event.payload["stepId"]
        for event in repos.job_events.list_for_job(ids["job"])
        if event.eventType == "tool.started"
    ]
    assert started_steps == validation.topological_order
    artifacts = repos.artifacts.list_for_job(ids["job"])
    assert {item["type"] for item in artifacts} == {
        "phonon_band_json",
        "phonon_dos_json",
        "phonon_band_dos_json",
    }
    assert all(item["storageProvider"] == "s3" for item in artifacts)
    assert all(item["bucket"] == os.getenv("MINIO_BUCKET", "mdi-artifacts") for item in artifacts)
    assert all(storage.exists(item["storageKey"]) for item in artifacts)
    assert all(len(storage.get_bytes(item["storageKey"])) == item["sizeBytes"] for item in artifacts)

    resolutions = repos.dependency_execution.list_binding_resolutions(ids["job"])
    assert len(resolutions) == 2
    assert {item["validationOutcome"] for item in resolutions} == {"RESOLVED"}
    assert {item["consumerInputPort"] for item in resolutions} == {"band", "dos"}
    assert all(item["resolvedArtifactInputRef"]["jobId"] == ids["job"] for item in resolutions)
    assert all(item["resolvedArtifactInputRef"]["planHash"] == plan_hash for item in resolutions)

    execution = repos.dependency_execution.get_execution_for_job(ids["job"])
    assert execution["outcome"] == "ALL_SUCCEEDED"
    assert execution["topologicalOrder"] == validation.topological_order
    assert execution["succeededCount"] == 3
    assert execution["failedCount"] == 0
    assert execution["blockedCount"] == 0

    lineage = repos.dependency_execution.list_lineage_for_job(ids["job"])
    assert len(lineage) == 3
    combined = next(item for item in lineage if item["producerToolId"] == "phonon.band_dos")
    assert combined["outputPort"] == "combined-band-dos"
    assert len(combined["upstreamArtifactIds"]) == 2
    assert len(combined["upstreamArtifactHashes"]) == 2
    assert len(combined["bindingIds"]) == 2
    assert {item["artifactId"] for item in lineage} == {item["id"] for item in artifacts}

    before_replay = (
        len(calls),
        len(artifacts),
        len(resolutions),
        len(lineage),
        len(repos.job_events.list_for_job(ids["job"])),
    )
    replay = runtime.handle_job(
        ids["job"],
        object_store={
            "source_band": _source("stable_band.json"),
            "source_dos": _source("projected_dos.json"),
        },
    )
    assert replay.status == "completed"
    assert before_replay == (
        len(repos.tool_calls.list_for_job(ids["job"])),
        len(repos.artifacts.list_for_job(ids["job"])),
        len(repos.dependency_execution.list_binding_resolutions(ids["job"])),
        len(repos.dependency_execution.list_lineage_for_job(ids["job"])),
        len(repos.job_events.list_for_job(ids["job"])),
    )
    engine.dispose()
