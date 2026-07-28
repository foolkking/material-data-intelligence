from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pymatgen.core import Lattice, Structure
from sqlalchemy import create_engine

from mdi_api.artifact_storage import S3CompatibleArtifactStorage
from mdi_api.config import load_settings
from mdi_api.database import create_repository_factory
from mdi_api.db import metadata
from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    VIEWER_SCHEMA_COMPATIBILITY,
    validate_trajectory,
    validate_trajectory_manifest,
    validate_trajectory_summary,
    validate_viewer_scene,
    validate_viewer_scene_manifest,
    validate_volumetric_dataset,
    validate_volumetric_manifest,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import build_data_profile, parse_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from mdi_workers import QueueWorkerRuntime, RedisRQQueueBackend


ROOT = Path(__file__).resolve().parents[2]
TRAJECTORY_FIXTURE = ROOT / "docs" / "phase10g" / "fixtures" / "trajectory_import" / "fixed_lattice_md.extxyz"
VOLUMETRIC_FIXTURE = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser" / "CHGCAR"


PORTFOLIO = (
    ("Analyze numeric distribution statistics", "table.distribution_summary", "table"),
    ("Compare value and reference with a scatter plot", "viz.scatter", "table"),
    ("Summarize element composition from the formula field", "composition.summary", "table"),
    ("Summarize this crystal structure and lattice", "structure.summary", "structure"),
    ("Generate an XRD pattern for this crystal", "structure.xrd", "structure"),
    ("Show this periodic crystal in 3D and allow bond inspection.", "structure.viewer_3d", "structure"),
)


def test_phase10_registry_planner_runtime_artifact_portfolio_closure(tmp_path: Path) -> None:
    observed: dict[str, dict[str, Any]] = {}
    for index, (prompt, expected_tool, profile_kind) in enumerate(PORTFOLIO):
        result = _run_in_memory_product_job(
            prompt,
            _table_profile() if profile_kind == "table" else _structure_profile(),
            _object_store(),
            tmp_path / str(index),
        )
        assert result["tool_id"] == expected_tool
        assert result["worker_status"] == "completed"
        assert result["artifact_names"]
        assert result["tool_call_count"] == 1
        observed[expected_tool] = result

    distribution = _json_artifact(observed["table.distribution_summary"], "distribution_summary.json")
    assert distribution["rowCount"] == 4
    assert list(distribution["numericColumns"]) == ["reference", "value"]
    assert {"scatter.json", "scatter.html"}.issubset(observed["viz.scatter"]["artifact_names"])
    composition = _json_artifact(observed["composition.summary"], "composition_summary.json")
    assert composition["formulaColumn"] == "composition"
    assert composition["parsedFormulaCount"] == 4
    assert _json_artifact(observed["structure.summary"], "structure_summary.json")["artifactType"] == "structure.summary"
    assert _json_artifact(observed["structure.xrd"], "xrd_pattern.json")["schema_version"] == "phase10e4.xrd_pattern.v1"

    viewer = observed["structure.viewer_3d"]
    scene = _json_artifact(viewer, "viewer_scene.json")
    manifest = _json_artifact(viewer, "viewer_scene_manifest.json")
    assert scene["schema_version"] == "phase10f18.viewer_scene.v2"
    assert manifest["schema_version"] == "phase10f19.viewer_assets_manifest.v2"
    assert validate_viewer_scene(scene).valid
    assert validate_viewer_scene_manifest(manifest).valid
    assert manifest["renderer_required"] is False
    assert manifest["external_resources"] == "none"


def test_phase10_determinism_capability_and_compatibility_closure(tmp_path: Path) -> None:
    first = _run_in_memory_product_job(PORTFOLIO[-1][0], _structure_profile(), _object_store(), tmp_path / "first")
    second = _run_in_memory_product_job(PORTFOLIO[-1][0], _structure_profile(), _object_store(), tmp_path / "second")
    for name in ("viewer_scene.json", "viewer_scene_manifest.json"):
        assert _json_artifact(first, name) == _json_artifact(second, name)
    first_recipe = dict(_json_artifact(first, "recipe.json"))
    second_recipe = dict(_json_artifact(second, "recipe.json"))
    assert first_recipe.pop("recipeId").startswith("recipe_call_job_")
    assert second_recipe.pop("recipeId").startswith("recipe_call_job_")
    assert first_recipe == second_recipe

    registry = load_manifests()
    ids = [tool.toolId for tool in registry.list_tools()]
    assert ids.count("structure.viewer_3d") == 1
    viewer = registry.get_tool_by_id("structure.viewer_3d")
    assert viewer.source["manifest"] == "platform_builtin_manifest.yaml"
    assert viewer.paramsSchema["additionalProperties"] is False
    description = viewer.description.lower()
    for unsupported in ("trajector", "phonon", "brillouin", "volumetric", "editing", "authoritative"):
        assert unsupported in description

    assert VIEWER_SCHEMA_COMPATIBILITY["phase10d1.viewer_scene.v1"]["renderer_supported"] is False
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10d1.viewer_scene.v1"]["new_artifact_generation_allowed"] is False
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f8.viewer_scene.v1"]["periodic_topology_supported"] is False
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f18.viewer_scene.v2"]["status"] == "current"
    assert VIEWER_SCHEMA_COMPATIBILITY["phase10f18.viewer_scene.v2"]["new_artifact_generation_allowed"] is True

    for prompt in ("Animate this trajectory", "Show phonon animation", "Run Bader atomic charge analysis", "Edit this structure"):
        plan = _planner_plan(prompt, _structure_profile())
        assert plan["steps"][0]["toolId"] != "structure.viewer_3d"

    combined = json.dumps(_json_artifact(first, "viewer_scene.json"), sort_keys=True).lower()
    for forbidden in ("<script", "javascript:", "http://", "https://", "callback", "shader", "module_path"):
        assert forbidden not in combined


def test_phase10_formal_trajectory_viewer_product_closure(tmp_path: Path) -> None:
    result = _run_in_memory_product_job(
        "Play this molecular dynamics trajectory.",
        _trajectory_profile(),
        {"trajectory": _trajectory_object()},
        tmp_path / "trajectory-viewer",
    )
    assert result["tool_id"] == "structure.trajectory_viewer"
    assert result["worker_status"] == "completed"
    assert result["tool_call_count"] == 1
    assert result["artifact_names"] == {
        "trajectory.json",
        "trajectory_summary.json",
        "trajectory_parse_report.json",
        "trajectory_manifest.json",
    }
    assert validate_trajectory(_json_artifact(result, "trajectory.json")).valid
    assert validate_trajectory_summary(_json_artifact(result, "trajectory_summary.json")).valid
    assert validate_trajectory_manifest(_json_artifact(result, "trajectory_manifest.json")).valid


@pytest.mark.integration
def test_phase10_service_backed_formal_viewer_product_closure(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not database_url or "postgres" not in database_url or not redis_url:
        pytest.skip("Service-backed Phase 10 closure environment is incomplete")

    engine = create_engine(database_url, future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    suffix = uuid.uuid4().hex[:10]
    project_id = f"project_phase10_closure_{suffix}"
    dataset_id = f"dataset_phase10_closure_{suffix}"
    profile_id = f"profile_phase10_closure_{suffix}"
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "test_user"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "test_user"})

    profile = _structure_profile(dataset_id=dataset_id, profile_id=profile_id)
    plan = _planner_plan(PORTFOLIO[-1][0], profile)
    assert plan["steps"][0]["toolId"] == "structure.viewer_3d"
    storage = _minio_storage(f"phase10-closure-{suffix}")
    runtime = QueueWorkerRuntime(
        repository_factory=create_repository_factory(load_settings()),
        queue_backend=RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase10-closure"),
        artifact_storage=storage,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter-artifacts",
    )
    created = planner_jobs(
        PlannerJobsRequest(userPrompt=PORTFOLIO[-1][0], projectId=project_id, datasetId=dataset_id, profileId=profile_id, enqueue=True),
        provider=MockLLMProvider(fixed_plan=plan), repositories=repos, queue_runtime=runtime, registry=load_manifests(),
    )
    assert created.ok and created.job_id and created.plan_id and created.enqueued
    result = runtime.handle_job(created.job_id, object_store={"structures": [_periodic_structure()]})
    artifacts = repos.artifacts.list_for_job(created.job_id)
    calls = repos.tool_calls.list_for_job(created.job_id)
    assert result.status == "completed"
    assert len(calls) == 1 and calls[0]["toolId"] == "structure.viewer_3d"
    assert {item["name"] for item in artifacts} == {"viewer_scene.json", "viewer_scene_manifest.json", "summary.md", "recipe.json"}
    assert all(item["storageProvider"] == "s3" and storage.exists(item["storageKey"]) for item in artifacts)
    engine.dispose()


@pytest.mark.integration
def test_phase10_service_backed_formal_trajectory_viewer_product_closure(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not database_url or "postgres" not in database_url or not redis_url:
        pytest.skip("Service-backed Phase 10 trajectory environment is incomplete")

    engine = create_engine(database_url, future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    suffix = uuid.uuid4().hex[:10]
    project_id = f"project_phase10_trajectory_{suffix}"
    dataset_id = f"dataset_phase10_trajectory_{suffix}"
    profile_id = f"profile_phase10_trajectory_{suffix}"
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "test_user"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "test_user"})

    profile = _trajectory_profile(dataset_id=dataset_id, profile_id=profile_id)
    plan = _planner_plan("Play this molecular dynamics trajectory.", profile)
    assert plan["steps"][0]["toolId"] == "structure.trajectory_viewer"
    assert validate_plan(plan, registry=load_manifests()).ok
    storage = _minio_storage(f"phase10-trajectory-{suffix}")
    runtime = QueueWorkerRuntime(
        repository_factory=create_repository_factory(load_settings()),
        queue_backend=RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase10-trajectory"),
        artifact_storage=storage,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter-artifacts",
    )
    created = planner_jobs(
        PlannerJobsRequest(
            userPrompt="Play this molecular dynamics trajectory.",
            projectId=project_id,
            datasetId=dataset_id,
            profileId=profile_id,
            enqueue=True,
        ),
        provider=MockLLMProvider(fixed_plan=plan),
        repositories=repos,
        queue_runtime=runtime,
        registry=load_manifests(),
    )
    assert created.ok and created.job_id and created.plan_id and created.enqueued
    result = runtime.handle_job(created.job_id, object_store={"trajectory": _trajectory_object()})
    artifacts = repos.artifacts.list_for_job(created.job_id)
    calls = repos.tool_calls.list_for_job(created.job_id)
    assert result.status == "completed"
    assert len(calls) == 1 and calls[0]["toolId"] == "structure.trajectory_viewer"
    assert {item["name"] for item in artifacts} == {
        "trajectory.json",
        "trajectory_summary.json",
        "trajectory_parse_report.json",
        "trajectory_manifest.json",
    }
    assert all(item["storageProvider"] == "s3" and storage.exists(item["storageKey"]) for item in artifacts)
    trajectory_record = next(item for item in artifacts if item["name"] == "trajectory.json")
    summary_record = next(item for item in artifacts if item["name"] == "trajectory_summary.json")
    manifest_record = next(item for item in artifacts if item["name"] == "trajectory_manifest.json")
    assert validate_trajectory(storage.get_json(trajectory_record["storageKey"])).valid
    assert validate_trajectory_summary(storage.get_json(summary_record["storageKey"])).valid
    assert validate_trajectory_manifest(storage.get_json(manifest_record["storageKey"])).valid
    engine.dispose()


@pytest.mark.integration
def test_phase10k3_service_backed_materials_ml_product_closure(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not database_url or "postgres" not in database_url or not redis_url:
        pytest.skip("Service-backed Phase 10K-3 environment is incomplete")

    engine = create_engine(database_url, future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    suffix = uuid.uuid4().hex[:10]
    project_id = f"project_phase10k3_{suffix}"
    dataset_id = f"dataset_phase10k3_{suffix}"
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "test_user"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "test_user"})

    profile, objects = _materials_ml_profile(tmp_path, dataset_id)
    object_store, _ = build_object_store(objects, profile=profile)
    registry = load_manifests()
    storage = _minio_storage(f"phase10k3-ml-{suffix}")
    runtime = QueueWorkerRuntime(
        repository_factory=create_repository_factory(load_settings()),
        queue_backend=RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase10k3-ml"),
        artifact_storage=storage,
        registry=registry,
        artifact_root=tmp_path / "adapter-artifacts",
    )
    cases = (
        ("Analyze model performance and prediction error.", "ml.regression_evaluation", "materials_ml_regression.json"),
        ("Analyze uncertainty calibration and error filtering.", "ml.uncertainty_evaluation", "materials_ml_uncertainty.json"),
        ("Analyze classification performance and confusion matrix.", "ml.classification_evaluation", "materials_ml_classification.json"),
    )
    for prompt, tool_id, product_name in cases:
        plan = _planner_plan(prompt, profile)
        assert plan["steps"][0]["toolId"] == tool_id
        assert validate_plan(plan, registry=registry).ok
        created = planner_jobs(
            PlannerJobsRequest(
                userPrompt=prompt,
                projectId=project_id,
                datasetId=dataset_id,
                profileId=profile.profileId,
                enqueue=True,
            ),
            provider=MockLLMProvider(fixed_plan=plan),
            repositories=repos,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id and created.plan_id and created.enqueued
        result = runtime.handle_job(created.job_id, object_store=object_store)
        artifacts = repos.artifacts.list_for_job(created.job_id)
        calls = repos.tool_calls.list_for_job(created.job_id)
        assert result.status == "completed"
        assert len(calls) == 1 and calls[0]["toolId"] == tool_id
        assert {item["name"] for item in artifacts} == {product_name, "summary.md", "recipe.json"}
        assert all(item["storageProvider"] == "s3" and storage.exists(item["storageKey"]) for item in artifacts)
        product = storage.get_json(next(item["storageKey"] for item in artifacts if item["name"] == product_name))
        assert product["dataset"]["profileContractVersion"] == "2.0"
        assert product["schemaVersion"].startswith("phase10k3.materials_ml_")
    engine.dispose()


@pytest.mark.integration
def test_phase10j1_service_backed_volumetric_parser_adapter_closure(tmp_path: Path) -> None:
    if os.getenv("MDI_RUN_INTEGRATION") != "1":
        pytest.skip("Set MDI_RUN_INTEGRATION=1 with PostgreSQL, Redis, and MinIO running")
    database_url = os.getenv("MDI_TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL") or os.getenv("MDI_REDIS_URL")
    if not database_url or "postgres" not in database_url or not redis_url:
        pytest.skip("Service-backed Phase 10J-1 environment is incomplete")

    engine = create_engine(database_url, future=True)
    metadata.create_all(engine)
    repos = SqlAlchemyRepositoryBundle.create(engine)
    suffix = uuid.uuid4().hex[:10]
    project_id = f"project_phase10j1_{suffix}"
    dataset_id = f"dataset_phase10j1_{suffix}"
    profile_id = f"profile_phase10j1_{suffix}"
    repos.projects.save({"id": project_id, "name": project_id, "createdBy": "test_user"})
    repos.datasets.save({"id": dataset_id, "projectId": project_id, "name": dataset_id, "createdBy": "test_user"})

    profile = _volumetric_profile(dataset_id=dataset_id, profile_id=profile_id)
    prompt = "Parse this CHGCAR into canonical volumetric artifacts."
    plan = _planner_plan(prompt, profile)
    assert plan["steps"][0]["toolId"] == "structure.volumetric_data"
    assert validate_plan(plan, registry=load_manifests()).ok
    storage = _minio_storage(f"phase10j1-volume-{suffix}")
    runtime = QueueWorkerRuntime(
        repository_factory=create_repository_factory(load_settings()),
        queue_backend=RedisRQQueueBackend(redis_url=redis_url, queue_name="mdi-test-phase10j1-volume"),
        artifact_storage=storage,
        registry=load_manifests(),
        artifact_root=tmp_path / "adapter-artifacts",
    )
    created = planner_jobs(
        PlannerJobsRequest(userPrompt=prompt, projectId=project_id, datasetId=dataset_id, profileId=profile_id, enqueue=True),
        provider=MockLLMProvider(fixed_plan=plan), repositories=repos, queue_runtime=runtime, registry=load_manifests(),
    )
    assert created.ok and created.job_id and created.plan_id and created.enqueued
    source = parse_file(VOLUMETRIC_FIXTURE, dataset_id=dataset_id, file_id="volumetric").objects[0]
    result = runtime.handle_job(created.job_id, object_store={"volumetric": source})
    artifacts = repos.artifacts.list_for_job(created.job_id)
    calls = repos.tool_calls.list_for_job(created.job_id)
    assert result.status == "completed"
    assert len(calls) == 1 and calls[0]["toolId"] == "structure.volumetric_data"
    assert all(item["storageProvider"] == "s3" and storage.exists(item["storageKey"]) for item in artifacts)
    by_name = {item["name"]: item for item in artifacts}
    dataset = storage.get_json(by_name["volumetric_dataset.json"]["storageKey"])
    manifest = storage.get_json(by_name["volumetric_manifest.json"]["storageKey"])
    binaries = {
        item["name"]: storage.get_bytes(item["storageKey"])
        for item in artifacts if item["type"] == "volumetric_binary"
    }
    assert validate_volumetric_dataset(dataset, binaries).valid
    assert validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid
    engine.dispose()


def _run_in_memory_product_job(prompt: str, profile: DataProfile, object_store: dict[str, Any], root: Path) -> dict[str, Any]:
    registry = load_manifests()
    plan = _planner_plan(prompt, profile)
    assert validate_plan(plan, registry=registry).ok
    repos = InMemoryRepositoryBundle.create()
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
    created = planner_jobs(
        PlannerJobsRequest(userPrompt=prompt, projectId="project_phase10", datasetId=profile.datasetId, profileId=profile.profileId, enqueue=True),
        provider=MockLLMProvider(fixed_plan=plan), repositories=repos, queue_runtime=runtime, registry=registry,
    )
    assert created.ok and created.job_id and created.plan_id
    worker = runtime.handle_job(created.job_id, object_store=object_store)
    records = repos.artifacts.list_for_job(created.job_id)
    contents: dict[str, Any] = {}
    for record in records:
        path = root / record["storageKey"]
        raw = path.read_text(encoding="utf-8")
        contents[record["name"]] = json.loads(raw) if path.suffix == ".json" else raw
    return {
        "tool_id": plan["steps"][0]["toolId"],
        "worker_status": worker.status,
        "tool_call_count": worker.tool_call_count,
        "artifact_names": {item["name"] for item in records},
        "contents": contents,
    }


def _planner_plan(prompt: str, profile: DataProfile) -> dict[str, Any]:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id=profile.datasetId, profile_id=profile.profileId, tool_registry_version=registry.version),
        tools=registry.list_mvp_tools(), data_profile=profile,
    )
    assert response.raw_json is not None
    return response.raw_json


def _json_artifact(result: dict[str, Any], name: str) -> dict[str, Any]:
    value = result["contents"][name]
    assert isinstance(value, dict)
    return value


def _object_store() -> dict[str, Any]:
    return {
        "ml_table": pd.DataFrame({
            "composition": ["SiO2", "Al2O3", "NaCl", "MgO"],
            "value": [1.0, 2.0, 3.0, 4.0],
            "reference": [1.1, 1.9, 3.1, 3.8],
        }),
        "structures": [_periodic_structure()],
    }


def _periodic_structure() -> Structure:
    return Structure(Lattice.cubic(10.0), ["H", "H"], [[0.98, 0.0, 0.0], [0.02, 0.0, 0.0]])


def _table_profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_table", "datasetId": "dataset_table", "version": "1", "datasetType": "table",
        "files": [], "objects": [], "tableSummary": {"nRows": 4, "columns": [
            {"name": "composition", "dtype": "string", "missingCount": 0},
            {"name": "value", "dtype": "number", "missingCount": 0},
            {"name": "reference", "dtype": "number", "missingCount": 0},
        ]}, "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-13T00:00:00+00:00",
    })


def _structure_profile(*, dataset_id: str = "dataset_structure", profile_id: str = "profile_structure") -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": profile_id, "datasetId": dataset_id, "version": "1", "datasetType": "structure_collection",
        "files": [{"path": "periodic.cif", "format": "cif", "sizeBytes": 512}],
        "objects": [{"objectType": "Structure", "count": 1, "source": "periodic.cif"}],
        "structureSummary": {"nStructures": 1, "elements": ["H"], "formulaStats": {"total": 1, "uniqueCount": 1}},
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-13T00:00:00+00:00",
    })


def _trajectory_profile(
    *,
    dataset_id: str = "dataset_trajectory",
    profile_id: str = "profile_trajectory",
) -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": profile_id, "datasetId": dataset_id, "version": "1", "datasetType": "trajectory",
        "files": [{"path": "trajectory.extxyz", "format": "extxyz", "sizeBytes": 1024}],
        "objects": [{"id": "trajectory", "objectType": "Trajectory"}],
        "trajectorySummary": {"frames": 3, "atoms": 2},
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-13T00:00:00+00:00",
    })


def _volumetric_profile(*, dataset_id: str, profile_id: str) -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": profile_id, "datasetId": dataset_id, "version": "1", "datasetType": "volumetric",
        "files": [{"path": "CHGCAR", "format": "vasp_volumetric", "sizeBytes": VOLUMETRIC_FIXTURE.stat().st_size}],
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-18T00:00:00+00:00",
    })


def _materials_ml_profile(tmp_path: Path, dataset_id: str) -> tuple[DataProfile, list[Any]]:
    path = tmp_path / f"{dataset_id}.csv"
    path.write_text(
        "material_id,formula,y_true,y_pred,y_std,class_true,class_pred,prob_A,prob_B\n"
        "s1,Si,1.0,1.1,0.10,A,A,0.90,0.10\n"
        "s2,NaCl,2.0,2.3,0.35,B,A,0.65,0.35\n"
        "s3,LiF,3.0,2.9,0.20,B,B,0.20,0.80\n"
        "s4,MgO,4.0,4.2,0.25,A,A,0.75,0.25\n",
        encoding="utf-8",
    )
    parsed = parse_file(path, dataset_id=dataset_id, file_id=f"file_{dataset_id}")
    assert parsed.parse_status == "success"
    registry = load_manifests()
    profile = build_data_profile(
        dataset_id=dataset_id,
        parse_results=[parsed],
        platform_tool_ids={tool.toolId for tool in registry.tools},
    )
    return profile, parsed.objects


def _trajectory_object() -> Any:
    return parse_file(TRAJECTORY_FIXTURE, dataset_id="dataset_trajectory", file_id="trajectory").objects[0]


def _minio_storage(prefix: str) -> S3CompatibleArtifactStorage:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access = os.getenv("MINIO_ACCESS_KEY", "mdi-local")
    secret = os.getenv("MINIO_SECRET_KEY", "mdi-local-dev")
    bucket = os.getenv("MINIO_BUCKET", "mdi-artifacts")
    try:
        import boto3

        client = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=access, aws_secret_access_key=secret, region_name="us-east-1")
        client.head_bucket(Bucket=bucket)
    except Exception:
        pytest.skip("MinIO not reachable")
    return S3CompatibleArtifactStorage(bucket=bucket, endpoint_url=endpoint, prefix=prefix, access_key_id=access, secret_access_key=secret, client=client)
