from __future__ import annotations

from copy import deepcopy

import pytest

from mdi_api.phase2_runtime import build_object_store
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_llm import (
    AnalysisIntentRequest,
    DeterministicAnalysisIntentBuilder,
    MockLLMProvider,
    plan_capabilities,
)
from mdi_tool_registry import load_manifests
from mdi_workers import (
    QueueWorkerRuntime,
    SOURCE_RESOURCE_INDEX_KEY,
    preflight_execution_resources,
    register_runtime_source_resource,
)
from mdi_workers.object_store import DurableObjectStoreResolver
from scripts.generate_phase13_1_product_entry_fix_forward import DEMO_SPECS, FIXED_CREATED_AT, _parse_demo


def _canonical_c2(spec: dict[str, object]):
    registry = load_manifests()
    parsed, profile = _parse_demo(spec, {tool.toolId for tool in registry.tools})
    objects = [obj for result in parsed for obj in result.objects]
    selected = tuple(sorted(obj.id for obj in objects))
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal=str(spec["prompt"]),
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=selected,
        ),
        profile=profile,
        created_at=FIXED_CREATED_AT,
    )
    planning = plan_capabilities(intent, profile=profile, registry=registry, provider=MockLLMProvider())
    assert planning.plan is not None
    store, _ = build_object_store(objects, profile=profile)
    result = preflight_execution_resources(
        planning.plan,
        object_store=store,
        registry=registry,
        dataset_id=profile.datasetId,
    )
    return result, store, planning.plan, profile, objects


@pytest.mark.parametrize("spec", DEMO_SPECS, ids=lambda spec: str(spec["demoId"]))
def test_all_seven_canonical_execution_preflights_are_ready(spec: dict[str, object]) -> None:
    result, _, _, _, _ = _canonical_c2(spec)
    assert result.ok, result.issues


def test_phonon_and_electronic_resources_are_registered_by_exact_id() -> None:
    for spec in (DEMO_SPECS[4], DEMO_SPECS[6]):
        result, store, _, profile, objects = _canonical_c2(spec)
        assert result.ok
        index = store[SOURCE_RESOURCE_INDEX_KEY]
        for obj in objects:
            if obj.object_type.value in {"PhononBand", "PhononDos", "ElectronicBand", "ElectronicDos"}:
                assert store[obj.id] == obj.payload
                assert index[obj.id] == {
                    "objectId": obj.id,
                    "objectType": obj.object_type.value,
                    "objectHash": obj.hash,
                    "datasetId": profile.datasetId,
                }


def test_c2_rejects_missing_scope_hash_and_kind_mismatches() -> None:
    result, store, plan, profile, _ = _canonical_c2(DEMO_SPECS[6])
    assert result.ok
    ref = next(step.inputRefs[0].ref for step in plan.steps if step.inputRefs)

    missing = deepcopy(store)
    missing.pop(ref)
    assert "ROOT_RESOURCE_UNRESOLVED" in {
        item.code for item in preflight_execution_resources(plan, object_store=missing, registry=load_manifests(), dataset_id=profile.datasetId).issues
    }

    wrong_scope = deepcopy(store)
    wrong_scope[SOURCE_RESOURCE_INDEX_KEY][ref]["datasetId"] = "foreign_dataset"
    assert "ROOT_RESOURCE_SCOPE_MISMATCH" in {
        item.code for item in preflight_execution_resources(plan, object_store=wrong_scope, registry=load_manifests(), dataset_id=profile.datasetId).issues
    }

    wrong_hash = deepcopy(store)
    wrong_hash[SOURCE_RESOURCE_INDEX_KEY][ref]["objectHash"] = "0" * 64
    assert "ROOT_RESOURCE_HASH_MISMATCH" in {
        item.code for item in preflight_execution_resources(plan, object_store=wrong_hash, registry=load_manifests(), dataset_id=profile.datasetId).issues
    }

    wrong_kind = deepcopy(store)
    wrong_kind[SOURCE_RESOURCE_INDEX_KEY][ref]["objectType"] = "Structure"
    assert "ROOT_RESOURCE_KIND_MISMATCH" in {
        item.code for item in preflight_execution_resources(plan, object_store=wrong_kind, registry=load_manifests(), dataset_id=profile.datasetId).issues
    }


def test_xrd_preflight_preserves_exact_wavelength_rejection() -> None:
    result, store, plan, profile, _ = _canonical_c2(DEMO_SPECS[2])
    assert result.ok
    assert result.scientific_compatibility_checks == ("XRD_WAVELENGTH_EXACT_MATCH",)
    experimental_ref = next(
        ref.ref
        for step in plan.steps
        if step.toolId == "structure.experimental_xrd_comparison"
        for ref in step.inputRefs
    )
    mismatch = deepcopy(store)
    mismatch[experimental_ref]["wavelength"]["value"] = 1.5406
    failed = preflight_execution_resources(plan, object_store=mismatch, registry=load_manifests(), dataset_id=profile.datasetId)
    assert not failed.ok
    assert "XRD_WAVELENGTH_MISMATCH" in {item.code for item in failed.issues}


@pytest.mark.parametrize("spec", (DEMO_SPECS[4], DEMO_SPECS[6]), ids=("phonon", "electronic"))
def test_durable_resolver_restores_typed_specialized_sources(spec: dict[str, object]) -> None:
    _, _, _, profile, objects = _canonical_c2(spec)

    class Storage:
        def __init__(self):
            self.values = {}

        def get_json(self, key):
            return deepcopy(self.values[key])

    class Datasets:
        def get(self, dataset_id):
            return {"id": dataset_id, "projectId": "project", "normalizedExports": exports}

    class Profiles:
        def list_for_dataset(self, dataset_id):
            return [profile.model_dump(mode="json")]

    class Repositories:
        datasets = Datasets()
        data_profiles = Profiles()

    storage = Storage()
    exports = []
    for obj in objects:
        data_key = f"data/{obj.id}.json"
        metadata_key = f"metadata/{obj.id}.json"
        storage.values[data_key] = obj.payload
        storage.values[metadata_key] = {
            "objectId": obj.id,
            "metadata": obj.metadata,
            "provenance": {"objectType": obj.object_type.value},
        }
        exports.append({"objectId": obj.id, "storageKey": data_key, "metadataKey": metadata_key, "contentHash": obj.hash})

    restored = DurableObjectStoreResolver(artifact_storage=storage, repositories=Repositories()).resolve(
        profile.datasetId,
        profile_id=profile.profileId,
    )
    assert restored is not None
    for obj in objects:
        assert restored[obj.id] == obj.payload
        assert restored[SOURCE_RESOURCE_INDEX_KEY][obj.id]["objectHash"] == obj.hash


def test_source_registration_is_idempotent_and_rejects_conflicting_identity() -> None:
    store: dict[str, object] = {}
    kwargs = {
        "object_id": "resource_exact",
        "object_type": "PhononBand",
        "object_hash": "a" * 64,
        "dataset_id": "dataset_exact",
        "value": {"frequencies": [[1.0]]},
    }
    register_runtime_source_resource(store, **kwargs)
    register_runtime_source_resource(store, **kwargs)
    assert len(store[SOURCE_RESOURCE_INDEX_KEY]) == 1

    with pytest.raises(ValueError, match="Conflicting runtime source identity"):
        register_runtime_source_resource(store, **{**kwargs, "object_hash": "b" * 64})


def test_planner_uses_exact_runtime_resolver_and_stops_before_job_creation() -> None:
    _, store, _, profile, objects = _canonical_c2(DEMO_SPECS[6])
    missing = deepcopy(store)
    missing.pop(objects[0].id)

    class Resolver:
        def resolve(self, dataset_id, *, profile_id=None):
            assert dataset_id == profile.datasetId
            assert profile_id == profile.profileId
            return missing

    repositories = InMemoryRepositoryBundle.create()
    repositories.projects.save({"id": "project", "name": "project", "createdBy": "test"})
    repositories.datasets.save({"id": profile.datasetId, "projectId": "project", "name": "dataset", "createdBy": "test"})
    repositories.data_profiles.save(profile)
    runtime = QueueWorkerRuntime(repositories=repositories, object_store_resolver=Resolver())
    result = planner_jobs(
        PlannerJobsRequest(
            userPrompt=str(DEMO_SPECS[6]["prompt"]),
            projectId="project",
            datasetId=profile.datasetId,
            profileId=profile.profileId,
            intentSchemaVersion="1.0",
            selectedResourceIds=tuple(sorted(obj.id for obj in objects)),
            provider="mock",
            enqueue=True,
        ),
        provider=MockLLMProvider(),
        repositories=repositories,
        queue_runtime=runtime,
        registry=load_manifests(),
    )
    assert not result.ok
    assert "ROOT_RESOURCE_UNRESOLVED" in {item["code"] for item in result.validation_errors}
    assert repositories.jobs.records == {}
