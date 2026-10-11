from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.pool import StaticPool

from mdi_api.artifact_storage import LocalFileArtifactStorage
from mdi_api.db import data_profiles, datasets, metadata, organizations, projects, users
from mdi_schemas import AnalysisPlanV03
from mdi_schemas.dependency_planning import compute_dependency_graph_hash
from mdi_api.scientific_objects.registry import build_default_object_type_registry
from mdi_api.scientific_objects.schemas import ScientificObjectKind, StorageRef
from mdi_api.scientific_objects.service import ScientificObjectService
from mdi_api.unit_of_work import RepositoryFactory
from mdi_workers.object_store import DurableObjectStoreResolver
from mdi_workers.source_resources import SOURCE_RESOURCE_INDEX_KEY
from mdi_workers.source_resources import preflight_execution_resources


def _fixture(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    metadata.create_all(engine)
    suffix = uuid4().hex[:8]
    project_id, dataset_id = f"project-{suffix}", f"dataset-{suffix}"
    with engine.begin() as connection:
        connection.execute(insert(users), {"id": "owner", "email": "owner@local.invalid", "display_name": "Owner", "is_active": True})
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {"id": project_id, "organization_id": "org", "name": "Project", "created_by": "owner"})
        connection.execute(insert(datasets), {"id": dataset_id, "project_id": project_id, "name": "Dataset", "status": "profile_ready", "metadata_json": {}, "created_by": "owner"})
    factory = RepositoryFactory(engine)
    storage = LocalFileArtifactStorage(tmp_path)
    service = ScientificObjectService(factory, build_default_object_type_registry())
    logical = service.create_object(
        project_id=project_id,
        kind=ScientificObjectKind.STRUCTURE,
        object_type="structure.crystal",
        display_name="Exact historical structure",
        created_by_user_id="owner",
    )
    return engine, factory, storage, service, logical, project_id, dataset_id


def _create_version(service, storage, logical, project_id, dataset_id, *, label, resource_id=None, structure_payload=None):
    payload = structure_payload if structure_payload is not None else {"@module": "pymatgen.core.structure", "@class": "Structure", "label": label}
    stored = storage.put_json(f"projects/{project_id}/agent2/{label}.json", payload)
    version = service.create_version(
        logical["id"],
        object_type="structure.crystal",
        object_schema_version="1.0",
        source_resource_refs=[{"project_id": project_id, "dataset_id": dataset_id}],
        parent_object_version_refs=[],
        normalized_payload_ref=StorageRef(
            storage_backend="local",
            object_key=stored.storage_key,
            checksum=stored.sha256,
            media_type="application/json",
            byte_size=stored.size_bytes,
        ),
        content_hash=stored.sha256,
        semantic_hash=f"semantic-{label}",
        canonical_metadata={"label": label, **({"source_resource_id": resource_id} if resource_id else {})},
        created_by_user_id="owner",
    )
    return version, payload


def _plan(version_id):
    return {
        "steps": [{
            "stepId": "step_1",
            "inputRefs": [{
                "refType": "normalized_object",
                "ref": str(version_id),
                "objectType": "Structure",
            }],
        }],
    }


def test_worker_hydrates_the_exact_historical_version_not_current(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version_1, payload_1 = _create_version(service, storage, logical, project_id, dataset_id, label="v1")
    version_2, _payload_2 = _create_version(service, storage, logical, project_id, dataset_id, label="v2")

    hydrated = DurableObjectStoreResolver(
        artifact_storage=storage,
        repository_factory=factory,
    ).hydrate_agent2_sources(
        {},
        job={"projectId": project_id, "datasetId": dataset_id},
        plan_payload=_plan(version_1["id"]),
    )

    assert hydrated[str(version_1["id"])] == payload_1
    assert str(version_2["id"]) not in hydrated
    identity = hydrated[SOURCE_RESOURCE_INDEX_KEY][str(version_1["id"])]
    assert identity["objectType"] == "Structure"
    assert identity["datasetId"] == dataset_id


def test_worker_rejects_tampered_exact_version_payload(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version, _payload = _create_version(service, storage, logical, project_id, dataset_id, label="v1")
    storage.put_json(f"projects/{project_id}/agent2/v1.json", {"label": "tampered"})

    with pytest.raises(ValueError, match="checksum mismatch"):
        DurableObjectStoreResolver(
            artifact_storage=storage,
            repository_factory=factory,
        ).hydrate_agent2_sources(
            {},
            job={"projectId": project_id, "datasetId": dataset_id},
            plan_payload=_plan(version["id"]),
        )


def test_worker_rejects_cross_project_exact_version(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version, _payload = _create_version(service, storage, logical, project_id, dataset_id, label="v1")

    with pytest.raises(ValueError, match="another Project"):
        DurableObjectStoreResolver(
            artifact_storage=storage,
            repository_factory=factory,
        ).hydrate_agent2_sources(
            {},
            job={"projectId": "foreign-project", "datasetId": dataset_id},
            plan_payload=_plan(version["id"]),
        )


def test_worker_never_relabels_a_foreign_dataset_as_the_jobs_dataset(tmp_path):
    _engine, factory, storage, service, logical, project_id, dataset_id = _fixture(tmp_path)
    version, _payload = _create_version(service, storage, logical, project_id, dataset_id, label="v1")
    with pytest.raises(ValueError, match="source dataset differs"):
        DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources(
            {}, job={"projectId": project_id, "datasetId": "another-dataset"}, plan_payload=_plan(version["id"]),
        )


def _multi_source_fixture(tmp_path, *, real_structures=False):
    engine, factory, storage, service, logical, project_id, dataset_a = _fixture(tmp_path)
    dataset_b = f"dataset-{uuid4().hex[:8]}"
    with engine.begin() as connection:
        connection.execute(insert(datasets), {"id": dataset_b, "project_id": project_id, "name": "Second material", "status": "profile_ready", "metadata_json": {}, "created_by": "owner"})
        for dataset_id, profile_id in [(dataset_a, "profile_a"), (dataset_b, "profile_b")]:
            connection.execute(insert(data_profiles), {
                "id": profile_id, "dataset_id": dataset_id, "version": "1.0",
                "profile_json": {"profileId": profile_id, "datasetId": dataset_id, "version": "1.0", "datasetType": "structure"},
            })
    other = service.create_object(project_id=project_id, kind=ScientificObjectKind.STRUCTURE,
                                  object_type="structure.crystal", display_name="Second material", created_by_user_id="owner")
    structures = [None, None]
    if real_structures:
        from pymatgen.core import Lattice, Structure
        structures = [Structure(Lattice.cubic(3), ["Si"], [[0, 0, 0]]).as_dict(),
                      Structure(Lattice.cubic(4), ["Cu"], [[0, 0, 0]]).as_dict()]
    va, pa = _create_version(service, storage, logical, project_id, dataset_a, label="material_a", resource_id="shared-parser-id", structure_payload=structures[0])
    vb, pb = _create_version(service, storage, other, project_id, dataset_b, label="material_b", resource_id="shared-parser-id", structure_payload=structures[1])
    with engine.begin() as connection:
        for version, dataset_id, profile_id in [(va, dataset_a, "profile_a"), (vb, dataset_b, "profile_b")]:
            connection.execute(update(data_profiles).where(data_profiles.c.id == profile_id).values(profile_json={
                "profileId": profile_id, "datasetId": dataset_id, "version": "1.0", "datasetType": "structure",
                "resourceSemantics": [{"objectId": "shared-parser-id", "objectType": "Structure", "kind": "structure",
                                       "objectHash": version["semantic_hash"]}],
            }))
    draft = {
        "schemaVersion": "0.3", "goal": "Compare material sources", "datasetId": dataset_a, "profileId": "profile_a",
        "toolRegistryVersion": "1.0", "graphHash": compute_dependency_graph_hash([]),
        "sourceContexts": sorted([{"datasetId": dataset_a, "profileId": "profile_a"}, {"datasetId": dataset_b, "profileId": "profile_b"}], key=lambda x: x["datasetId"]),
        "sourceVersions": sorted([
            {"objectId": str(logical["id"]), "versionId": str(va["id"]), "datasetId": dataset_a, "objectType": "Structure"},
            {"objectId": str(other["id"]), "versionId": str(vb["id"]), "datasetId": dataset_b, "objectType": "Structure"},
        ], key=lambda x: x["versionId"]),
        "steps": [
            {"stepId": f"s{i}", "toolId": "structure.rdf", "purpose": "RDF", "reason": "Compare sources",
             "inputRefs": [{"refType": "normalized_object", "ref": str(v["id"]), "objectType": "Structure"}],
             "output": {"sourceObjectVersionIds": [str(v["id"])]}}
            for i, v in enumerate([va, vb], 1)
        ],
    }
    return factory, storage, {"projectId": project_id, "datasetId": dataset_a}, draft, [(va, pa, dataset_a), (vb, pb, dataset_b)]


def test_multi_source_hydration_keeps_materials_and_profiles_separate_even_with_repeated_parser_ids(tmp_path):
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    plan = AnalysisPlanV03.model_validate(draft)
    hydrated = DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources(
        {"unrelated": "must not leak into source scope"}, job=job, plan_payload=plan.model_dump(mode="json"),
    )
    assert "profile" not in hydrated and "shared-parser-id" not in hydrated and "unrelated" not in hydrated
    for version, payload, dataset_id in sources:
        key = str(version["id"])
        assert hydrated[key] == payload
        assert hydrated[SOURCE_RESOURCE_INDEX_KEY][key]["datasetId"] == dataset_id
        assert hydrated[SOURCE_RESOURCE_INDEX_KEY][key]["profileObjectId"] == "shared-parser-id"
        assert hydrated[SOURCE_RESOURCE_INDEX_KEY][key]["profileObjectHash"] == version["semantic_hash"]
        assert hydrated[SOURCE_RESOURCE_INDEX_KEY][key]["objectHash"] == version["content_hash"]
        assert version["semantic_hash"] != version["content_hash"]
    assert hydrated["profile:profile_a"].datasetId == sources[0][2]
    assert hydrated["profile:profile_b"].datasetId == sources[1][2]
    from mdi_tool_registry import load_manifests
    preflight = preflight_execution_resources(plan, object_store=hydrated, registry=load_manifests(), dataset_id=job["datasetId"])
    assert preflight.ok, preflight.issues


@pytest.mark.parametrize("mismatch", ["routing", "source_dataset", "profile"])
def test_multi_source_preflight_rejects_misrouted_runtime_sources(tmp_path, mismatch):
    from mdi_tool_registry import load_manifests
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    hydrated = dict(DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources(
        {}, job=job, plan_payload=draft))
    if mismatch == "routing":
        job["datasetId"] = "foreign_dataset"
    elif mismatch == "source_dataset":
        hydrated[SOURCE_RESOURCE_INDEX_KEY][str(sources[1][0]["id"])]["datasetId"] = sources[0][2]
    else:
        hydrated["profile:profile_b"] = hydrated["profile:profile_a"]
    result = preflight_execution_resources(draft, object_store=hydrated, registry=load_manifests(), dataset_id=job["datasetId"])
    assert not result.ok
    assert any("SCOPE_MISMATCH" in issue.code for issue in result.issues)


@pytest.mark.parametrize("mismatch", ["hash", "missing", "duplicate", "type"])
@pytest.mark.parametrize("reused", [False, True])
def test_multi_source_hydration_rejects_mismatched_profile_before_loading_payloads(tmp_path, monkeypatch, mismatch, reused):
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    if reused:
        draft["steps"][1]["inputRefs"] = [{"refType": "artifact", "ref": "saved-result", "objectType": "DataFrame"}]
    with factory.session() as session:
        profile = dict(session.connection.execute(select(data_profiles.c.profile_json).where(data_profiles.c.id == "profile_b")).scalar_one())
        resource = profile["resourceSemantics"][0]
        if mismatch == "hash":
            resource["objectHash"] = sources[0][0]["semantic_hash"]
        elif mismatch == "missing":
            profile["resourceSemantics"] = []
        elif mismatch == "duplicate":
            profile["resourceSemantics"].append(dict(resource))
        else:
            resource["objectType"] = "Trajectory"
        session.connection.execute(update(data_profiles).where(data_profiles.c.id == "profile_b").values(profile_json=profile))
        session.commit()
    reads = []
    read = storage.get_bytes_bounded

    def track(key, **kwargs):
        reads.append(key)
        return read(key, **kwargs)

    monkeypatch.setattr(storage, "get_bytes_bounded", track)
    with pytest.raises(ValueError, match="Profile"):
        DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources({}, job=job, plan_payload=draft)
    assert reads == []


@pytest.mark.parametrize("mismatch", ["hash", "hash_missing", "resource_missing"])
def test_multi_source_preflight_rechecks_profile_semantic_identity(tmp_path, mismatch):
    from mdi_tool_registry import load_manifests
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    hydrated = dict(DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources({}, job=job, plan_payload=draft))
    identity = hydrated[SOURCE_RESOURCE_INDEX_KEY][str(sources[1][0]["id"])]
    if mismatch == "hash":
        identity["profileObjectHash"] = sources[1][0]["content_hash"]
    elif mismatch == "hash_missing":
        identity.pop("profileObjectHash")
    else:
        identity["profileObjectId"] = "missing"
    result = preflight_execution_resources(draft, object_store=hydrated, registry=load_manifests(), dataset_id=job["datasetId"])
    assert not result.ok
    assert result.issues[0].code in {"ROOT_RESOURCE_HASH_MISMATCH", "ROOT_PROFILE_RESOURCE_MISSING"}


def test_planning_context_loads_separate_persisted_profiles_for_each_material(tmp_path):
    from types import SimpleNamespace
    from mdi_tool_registry import load_manifests
    from mdi_api.research_agent.planning.processor import CapabilityPlanningProcessor
    from mdi_api.scientific_objects.schemas import ScientificObjectRef

    factory, _storage, job, _draft, sources = _multi_source_fixture(tmp_path)
    refs = {f"obj_{i}": ScientificObjectRef(object_id=version["scientific_object_id"], version_id=version["id"],
            project_id=job["projectId"], object_type="structure.crystal") for i, (version, _payload, _dataset) in enumerate(sources, 1)}
    # Call the real context builder with real persisted source/profile records.
    processor = SimpleNamespace(tool_registry=load_manifests(), _is_bounded_resource_fact=CapabilityPlanningProcessor._is_bounded_resource_fact)
    with factory.unit_of_work() as unit:
        context = CapabilityPlanningProcessor._plan_context(processor, unit, job["projectId"], refs)
    assert context["source_contexts"][sources[0][2]]["profile_id"] == "profile_a"
    assert context["source_contexts"][sources[1][2]]["profile_id"] == "profile_b"
    assert context["source_versions"]["obj_2"]["datasetId"] == sources[1][2]


def test_queued_cross_dataset_rdf_uses_real_sources_and_persists_exact_lineage(tmp_path, monkeypatch):
    from mdi_api.repositories import compute_plan_hash
    from mdi_tool_registry import load_manifests
    from mdi_workers import QueueWorkerRuntime
    from mdi_api.routers.planner import get_planner_job_dependencies

    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path, real_structures=True)
    for step in draft["steps"]:
        step["output"]["artifactTypes"] = ["table_json"]
        step["params"] = {"r_max_angstrom": 6.0, "bin_width_angstrom": 0.1}
    plan = AnalysisPlanV03.model_validate(draft)
    repos = factory.create_repositories()
    repos.analysis_plans.save_plan({"id": "multi_plan", "projectId": job["projectId"], "analysisPlan": draft})
    repos.jobs.create({"jobId": "multi_job", **job, "planId": "multi_plan", "status": "created", "kind": "analysis", "createdBy": "owner"})
    repos.analysis_plans.attach_plan_to_job("multi_plan", "multi_job")
    runtime = QueueWorkerRuntime(repository_factory=factory, registry=load_manifests(), artifact_storage=storage,
        artifact_root=tmp_path / "adapter", object_store_resolver=DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory))
    observed = []
    execute = runtime._execute_tool

    def capture(request, context, *, object_store):
        observed.append((context.dataset_id, set(object_store)))
        return execute(request, context, object_store=object_store)

    monkeypatch.setattr(runtime, "_execute_tool", capture)
    result = runtime.handle_job("multi_job")
    assert result.status == "completed", repos.job_events.list_for_job("multi_job")
    assert result.plan_hash == compute_plan_hash(plan)
    assert [item[0] for item in observed] == [sources[0][2], sources[1][2]]
    assert str(sources[1][0]["id"]) not in observed[0][1]
    assert str(sources[0][0]["id"]) not in observed[1][1]
    artifacts = repos.artifacts.list_for_job("multi_job")
    assert len(artifacts) == 2
    import json
    tables = []
    for artifact in artifacts:
        lineage = repos.dependency_execution.get_lineage_for_artifact(artifact["id"])
        assert lineage["schemaVersion"] == "1.1" and lineage["planSchemaVersion"] == "0.3"
        assert artifact["datasetId"] == lineage["datasetId"] == lineage["sourceVersions"][0]["datasetId"]
        assert len(lineage["sourceVersions"]) == 1
        assert artifact["metadata"]["provenance"]["sourceVersions"] == lineage["sourceVersions"]
        tables.append(json.loads(storage.get_bytes(artifact["storageKey"])))
    assert tables[0] != tables[1]
    details = get_planner_job_dependencies("multi_job", repositories=repos)
    assert details["execution"]["outcome"] == "ALL_SUCCEEDED" and len(details["artifactLineage"]) == 2
    assert runtime.handle_job("multi_job").status == "completed"
    assert len(observed) == 2 and len(repos.artifacts.list_for_job("multi_job")) == 2


def test_reused_artifact_provenance_does_not_reload_unused_source_payloads(tmp_path, monkeypatch):
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    draft["steps"][0]["inputRefs"] = [{"refType": "artifact", "ref": "saved-result", "objectType": "DataFrame"}]
    reads = []
    read = storage.get_bytes_bounded

    def tracked_read(key, **kwargs):
        reads.append(key)
        return read(key, **kwargs)

    monkeypatch.setattr(storage, "get_bytes_bounded", tracked_read)
    hydrated = DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources(
        {}, job=job, plan_payload=draft,
    )
    assert str(sources[0][0]["id"]) not in hydrated
    assert hydrated[str(sources[1][0]["id"])] == sources[1][1]
    assert len(reads) == 1 and reads[0].endswith("material_b.json")


@pytest.mark.parametrize("mismatch", ["dataset", "object", "profile", "type", "routing"])
def test_multi_source_hydration_reauthorizes_declared_source_scope(tmp_path, mismatch):
    factory, storage, job, draft, sources = _multi_source_fixture(tmp_path)
    if mismatch == "dataset":
        for source in draft["sourceVersions"]:
            source["datasetId"] = sources[1][2] if source["datasetId"] == sources[0][2] else sources[0][2]
    elif mismatch == "object":
        draft["sourceVersions"][0]["objectId"] = str(uuid4())
    elif mismatch == "profile":
        next(item for item in draft["sourceContexts"] if item["profileId"] == "profile_b")["profileId"] = "missing-profile"
    elif mismatch == "type":
        for source in draft["sourceVersions"]:
            source["objectType"] = "Trajectory"
        for step in draft["steps"]:
            step["inputRefs"][0]["objectType"] = "Trajectory"
    else:
        job["datasetId"] = "wrong-routing-dataset"
    # The JSON is structurally valid; durable state must still reject it.
    plan = AnalysisPlanV03.model_validate(draft)
    with pytest.raises(ValueError):
        DurableObjectStoreResolver(artifact_storage=storage, repository_factory=factory).hydrate_agent2_sources(
            {}, job=job, plan_payload=plan.model_dump(mode="json"),
        )
