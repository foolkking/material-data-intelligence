from __future__ import annotations

import os
import uuid

import pytest
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect

from mdi_api.repositories import SqlAlchemyRepositoryBundle, compute_plan_hash
from mdi_api.routers.planner import (
    PlannerJobsRequest,
    PlannerInterpretationRequest,
    create_planner_job_interpretation,
    get_planner_interpretation_evidence,
    planner_jobs,
)
from mdi_llm import MockLLMProvider
from mdi_schemas import AnalysisPlan, DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

from tests.integration.test_phase10l3_dependency_service_backed import (
    _minio_storage,
    _postgres_url,
    _redis_backend,
    _source,
)
from tests.test_phase10l3_planner_api import _phonon_profile


def _profile(*, profile_id: str, dataset_id: str, dataset_type: str) -> DataProfile:
    return DataProfile.model_validate({
        "profileId": profile_id,
        "datasetId": dataset_id,
        "version": "phase10l4-service-profile-v1",
        "datasetType": dataset_type,
        "files": [],
        "objects": [],
        "qualityIssues": [],
        "recommendedTasks": [],
        "profileContractVersion": "2.0",
        "semanticRulesVersion": "phase10k1.material_profile_semantics.v1",
        "semanticHash": "c" * 64,
        "semanticColumns": [],
        "semanticGroups": [],
        "resourceSemantics": [],
        "analysisReadiness": [],
        "sampleIdentity": {
            "policy": "object_hash_row_index",
            "datasetVersion": "phase10l4-service-dataset-v1",
            "objectIds": [],
        },
        "createdAt": "2026-07-30T00:00:00+00:00",
    })


def _persist_job(
    repos: SqlAlchemyRepositoryBundle,
    *,
    project_id: str,
    dataset_id: str,
    profile_id: str,
    plan_id: str,
    job_id: str,
    plan: AnalysisPlan | AnalysisPlanV02,
    dataset_type: str,
) -> str:
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "phase10l4_ci"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "phase10l4_ci"})
    repos.data_profiles.save(_profile(profile_id=profile_id, dataset_id=dataset_id, dataset_type=dataset_type))
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan({
        "id": plan_id,
        "projectId": project_id,
        "datasetId": dataset_id,
        "profileId": profile_id,
        "planSource": "capability_planner",
        "plannerProvider": "mock",
        "analysisPlan": plan.model_dump(mode="json"),
        "planHash": plan_hash,
        "createdBy": "phase10l4_ci",
    })
    if isinstance(plan, AnalysisPlanV02):
        repos.dependency_execution.save_plan_bindings(plan_id, plan_hash, plan.graphHash, plan.dependencyBindings)
    repos.jobs.save({
        "id": job_id,
        "projectId": project_id,
        "datasetId": dataset_id,
        "planId": plan_id,
        "status": "created",
        "kind": "analysis",
        "createdBy": "phase10l4_ci",
    })
    repos.analysis_plans.attach_plan_to_job(plan_id, job_id)
    return plan_hash


def _single_metrics_plan(*, dataset_id: str, profile_id: str) -> AnalysisPlan:
    return AnalysisPlan.model_validate({
        "schemaVersion": "0.1",
        "goal": "Evaluate exact regression metrics.",
        "datasetId": dataset_id,
        "profileId": profile_id,
        "toolRegistryVersion": load_manifests().version,
        "assumptions": [],
        "warnings": [],
        "steps": [{
            "stepId": "step_metrics",
            "toolId": "ml.basic_metrics",
            "purpose": "Compute exact regression metrics.",
            "reason": "Phase 10L-4 service-backed single-tool interpretation case.",
            "inputRefs": [{"refType": "normalized_object", "ref": "ml_table", "objectType": "DataFrame"}],
            "params": {"targetColumn": "y_true", "predictionColumn": "y_pred"},
            "output": {"artifactTypes": ["metrics_json"]},
        }],
        "expectedArtifacts": [{"name": "metrics.json", "type": "metrics_json", "fromStepId": "step_metrics"}],
    })


def _metrics_table() -> object:
    import pandas as pd

    return pd.DataFrame({
        "formula": ["SiO2", "Al2O3", "CaO", "MgO"],
        "y_true": [2.1, 3.4, 1.8, 4.2],
        "y_pred": [2.0, 3.5, 1.9, 4.0],
    })


def _canonical_phonon_job(
    repos: SqlAlchemyRepositoryBundle,
    *,
    project_id: str,
    dataset_id: str,
    profile_id: str,
) -> object:
    base = _phonon_profile().model_dump(mode="json")
    base["profileId"] = profile_id
    base["datasetId"] = dataset_id
    base["sampleIdentity"]["datasetVersion"] = f"{dataset_id}:v1"
    profile = DataProfile.model_validate(base)
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "phase10l4_ci"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "phase10l4_ci"})
    repos.data_profiles.save(profile)
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Analyze this phonon calculation.",
            projectId=project_id,
            datasetId=dataset_id,
            profileId=profile_id,
            intentSchemaVersion="1.0",
            selectedResourceIds=["phonon_band_1", "phonon_dos_1"],
            provider="mock",
        ),
        provider=MockLLMProvider(fixed_plan={"invalid": "legacy path must not run"}),
        repositories=repos,
    )
    assert result.ok and result.job_id and result.plan_id and result.plan_hash
    assert result.plan_schema_version == "0.2"
    return result


@pytest.mark.integration
def test_phase10l4_postgres_redis_minio_phonon_chain_interpretation() -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic_upgrade(config, "head")

    suffix = uuid.uuid4().hex[:12]
    project_id = f"project_l4_service_{suffix}"
    dataset_id = f"dataset_l4_service_{suffix}"
    profile_id = f"profile_l4_service_{suffix}"
    registry = load_manifests()

    engine = create_engine(database_url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    assert {
        "scientific_evidence_bundles",
        "scientific_interpretation_runs",
        "scientific_interpretations",
        "scientific_interpretation_claims",
        "scientific_interpretation_evidence_links",
    }.issubset(inspect(engine).get_table_names())
    planned = _canonical_phonon_job(
        repos, project_id=project_id, dataset_id=dataset_id, profile_id=profile_id
    )
    job_id = planned.job_id
    plan_hash = planned.plan_hash

    queue_backend, redis_queue = _redis_backend(queue_name=f"mdi-test-phase10l4-{suffix}")
    storage = _minio_storage(prefix=f"phase10l4-{suffix}")
    runtime = QueueWorkerRuntime(
        repositories=repos,
        queue_backend=queue_backend,
        artifact_storage=storage,
        registry=registry,
    )
    assert runtime.submit_job(job_id).enqueued is True
    assert redis_queue.fetch_job(job_id) is not None
    executed = runtime.handle_job(
        job_id,
        object_store={"phonon_band_1": _source("stable_band.json"), "phonon_dos_1": _source("projected_dos.json")},
    )
    assert executed.status == "completed"
    queued_before = redis_queue.fetch_job(job_id)
    assert queued_before is not None
    queue_snapshot_before = (queued_before.id, queued_before.origin, queued_before.get_status(refresh=True))
    minio_client = storage._require_client()
    minio_snapshot_before = sorted(
        (item["Key"], item["ETag"], item["Size"])
        for item in minio_client.list_objects_v2(Bucket=storage.bucket, Prefix=storage.prefix).get("Contents", [])
    )
    before = (
        len(repos.jobs.list_by_project(project_id)),
        len(repos.tool_calls.list_for_job(job_id)),
        len(repos.artifacts.list_for_job(job_id)),
    )

    interpretation_request = PlannerInterpretationRequest(
        mode="DETERMINISTIC", expectedPlanHash=plan_hash, idempotencyKey=f"l4-{suffix}"
    )
    interpreted = create_planner_job_interpretation(
        job_id,
        interpretation_request,
        repositories=repos,
        queue_runtime=runtime,
    )
    assert interpreted["outcome"] == "INTERPRETATION_READY"
    assert interpreted["noExecution"] == {
        "toolCallCreated": False,
        "planCreated": False,
        "jobCreated": False,
        "enqueued": False,
        "recommendationExecutionAuthorized": False,
    }
    assert before == (
        len(repos.jobs.list_by_project(project_id)),
        len(repos.tool_calls.list_for_job(job_id)),
        len(repos.artifacts.list_for_job(job_id)),
    )
    evidence = get_planner_interpretation_evidence(interpreted["interpretationId"], repositories=repos)
    assert set(evidence["sourceArtifactIds"]) == {
        artifact["id"] for artifact in repos.artifacts.list_for_job(job_id)
    }
    assert {item["sourceToolId"] for item in evidence["evidenceItems"]} == {
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
    }
    assert all(item["sourceArtifactChecksum"] for item in evidence["evidenceItems"])
    assert len(repos.interpretations.list_for_job(job_id)) == 1
    assert create_planner_job_interpretation(
        job_id,
        interpretation_request,
        repositories=repos,
        queue_runtime=runtime,
    )["interpretationId"] == interpreted["interpretationId"]
    assert len(repos.interpretations.list_runs_for_job(job_id)) == 1
    queued_after = redis_queue.fetch_job(job_id)
    assert queued_after is not None
    assert (queued_after.id, queued_after.origin, queued_after.get_status(refresh=True)) == queue_snapshot_before
    minio_snapshot_after = sorted(
        (item["Key"], item["ETag"], item["Size"])
        for item in minio_client.list_objects_v2(Bucket=storage.bucket, Prefix=storage.prefix).get("Contents", [])
    )
    assert minio_snapshot_after == minio_snapshot_before
    engine.dispose()


@pytest.mark.integration
def test_phase10l4_postgres_redis_minio_single_tool_interpretation() -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic_upgrade(config, "head")
    suffix = uuid.uuid4().hex[:12]
    ids = {name: f"{name}_l4_single_{suffix}" for name in ("project", "dataset", "profile", "plan", "job")}
    plan = _single_metrics_plan(dataset_id=ids["dataset"], profile_id=ids["profile"])
    engine = create_engine(database_url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    plan_hash = _persist_job(
        repos,
        project_id=ids["project"], dataset_id=ids["dataset"], profile_id=ids["profile"],
        plan_id=ids["plan"], job_id=ids["job"], plan=plan, dataset_type="table",
    )
    queue_backend, redis_queue = _redis_backend(queue_name=f"mdi-test-phase10l4-single-{suffix}")
    storage = _minio_storage(prefix=f"phase10l4-single-{suffix}")
    runtime = QueueWorkerRuntime(
        repositories=repos, queue_backend=queue_backend, artifact_storage=storage, registry=load_manifests()
    )
    assert runtime.submit_job(ids["job"]).enqueued is True
    assert runtime.handle_job(ids["job"], object_store={"ml_table": _metrics_table()}).status == "completed"
    before = (
        len(repos.jobs.list_by_project(ids["project"])),
        len(repos.tool_calls.list_for_job(ids["job"])),
        len(repos.artifacts.list_for_job(ids["job"])),
        redis_queue.fetch_job(ids["job"]).get_status(refresh=True),
    )
    interpreted = create_planner_job_interpretation(
        ids["job"], PlannerInterpretationRequest(mode="DETERMINISTIC", expectedPlanHash=plan_hash),
        repositories=repos, queue_runtime=runtime,
    )
    assert interpreted["outcome"] == "INTERPRETATION_READY"
    evidence = get_planner_interpretation_evidence(interpreted["interpretationId"], repositories=repos)
    assert {item["sourceToolId"] for item in evidence["evidenceItems"]} == {"ml.basic_metrics"}
    assert before == (
        len(repos.jobs.list_by_project(ids["project"])),
        len(repos.tool_calls.list_for_job(ids["job"])),
        len(repos.artifacts.list_for_job(ids["job"])),
        redis_queue.fetch_job(ids["job"]).get_status(refresh=True),
    )
    engine.dispose()


@pytest.mark.integration
def test_phase10l4_postgres_redis_minio_partial_execution_interpretation() -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")

    database_url = _postgres_url()
    config = AlembicConfig("apps/api/alembic.ini")
    config.set_main_option("script_location", "apps/api/alembic")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic_upgrade(config, "head")
    suffix = uuid.uuid4().hex[:12]
    ids = {name: f"{name}_l4_partial_{suffix}" for name in ("project", "dataset", "profile", "plan", "job")}
    engine = create_engine(database_url, future=True)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    planned = _canonical_phonon_job(
        repos, project_id=ids["project"], dataset_id=ids["dataset"], profile_id=ids["profile"]
    )
    ids["job"] = planned.job_id
    plan_hash = planned.plan_hash
    queue_backend, redis_queue = _redis_backend(queue_name=f"mdi-test-phase10l4-partial-{suffix}")
    storage = _minio_storage(prefix=f"phase10l4-partial-{suffix}")
    runtime = QueueWorkerRuntime(
        repositories=repos, queue_backend=queue_backend, artifact_storage=storage, registry=load_manifests()
    )
    assert runtime.submit_job(ids["job"]).enqueued is True
    executed = runtime.handle_job(
        ids["job"],
        object_store={"phonon_band_1": {}, "phonon_dos_1": _source("projected_dos.json")},
    )
    assert executed.status in {"failed", "partial_success"}
    dependency_execution = repos.dependency_execution.get_execution_for_job(ids["job"])
    assert dependency_execution is not None
    assert dependency_execution["outcome"] == "PARTIAL_RESULTS"
    assert dependency_execution["blockedCount"] >= 1
    before = (
        len(repos.jobs.list_by_project(ids["project"])),
        len(repos.tool_calls.list_for_job(ids["job"])),
        len(repos.artifacts.list_for_job(ids["job"])),
        redis_queue.fetch_job(ids["job"]).get_status(refresh=True),
    )
    interpreted = create_planner_job_interpretation(
        ids["job"], PlannerInterpretationRequest(mode="DETERMINISTIC", expectedPlanHash=plan_hash),
        repositories=repos, queue_runtime=runtime,
    )
    assert interpreted["outcome"] == "INTERPRETATION_READY_WITH_LIMITS"
    assert interpreted["partialResultState"] is True
    evidence = get_planner_interpretation_evidence(interpreted["interpretationId"], repositories=repos)
    source_tools = {item["sourceToolId"] for item in evidence["evidenceItems"]}
    assert "phonon.dos" in source_tools
    assert "phonon.band" not in source_tools
    assert "phonon.band_dos" not in source_tools
    assert before == (
        len(repos.jobs.list_by_project(ids["project"])),
        len(repos.tool_calls.list_for_job(ids["job"])),
        len(repos.artifacts.list_for_job(ids["job"])),
        redis_queue.fetch_job(ids["job"]).get_status(refresh=True),
    )
    engine.dispose()
