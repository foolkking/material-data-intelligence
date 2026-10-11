from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from mdi_schemas import AnalysisPlanV02, AnalysisPlanV03, parse_analysis_plan, parse_dependency_plan
from mdi_schemas.dependency_planning import (
    compute_dependency_graph_hash,
    dependency_semantic_hash,
    make_dependency_binding,
)


V1 = "11111111-1111-4111-8111-111111111111"
V2 = "22222222-2222-4222-8222-222222222222"


def payload():
    return {
        "schemaVersion": "0.3", "goal": "Compare independent material RDF results.",
        "datasetId": "dataset_a", "profileId": "profile_a", "toolRegistryVersion": "1.0",
        "graphHash": compute_dependency_graph_hash([]),
        "sourceContexts": [
            {"datasetId": "dataset_a", "profileId": "profile_a"},
            {"datasetId": "dataset_b", "profileId": "profile_b"},
        ],
        "sourceVersions": [
            {"objectId": V1, "versionId": V1, "datasetId": "dataset_a", "objectType": "Structure"},
            {"objectId": V2, "versionId": V2, "datasetId": "dataset_b", "objectType": "Structure"},
        ],
        "steps": [
            {"stepId": f"s{index}", "toolId": "structure.rdf", "purpose": "RDF", "reason": "Material comparison",
             "inputRefs": [{"refType": "normalized_object", "ref": version, "objectType": "Structure"}],
             "params": {}, "output": {"sourceObjectVersionIds": [version]}}
            for index, version in enumerate([V1, V2], 1)
        ],
    }


def test_independent_datasets_keep_exact_version_and_profile_ownership():
    original = payload()
    plan = AnalysisPlanV03.model_validate(original)
    assert plan.sourceVersions[1].datasetId == "dataset_b"
    assert plan.sourceContexts[1].profileId == "profile_b"
    assert plan.steps[1].inputRefs[0].ref == V2
    assert original == payload()
    assert dependency_semantic_hash(plan) == dependency_semantic_hash(plan.model_dump(mode="json"))
    changed = deepcopy(original)
    changed["sourceVersions"][0]["objectId"] = "33333333-3333-4333-8333-333333333333"
    assert dependency_semantic_hash(AnalysisPlanV03.model_validate(changed)) != dependency_semantic_hash(plan)


@pytest.mark.parametrize("change", [
    lambda p: p["sourceContexts"].reverse(),
    lambda p: p["sourceContexts"][1].update(datasetId="dataset_a"),
    lambda p: p["sourceContexts"][1].update(profileId="profile_a"),
    lambda p: p.update(profileId="profile_b"),
    lambda p: p["sourceVersions"][1].update(datasetId="foreign_dataset"),
    lambda p: p["sourceVersions"][1].update(versionId=V1),
    lambda p: p["sourceVersions"][1].update(versionId="https://example.invalid/file"),
    lambda p: p["sourceContexts"][1].update(datasetId="../../source"),
    lambda p: p["sourceVersions"][1].update(payload="untrusted"),
    lambda p: p["steps"][1]["inputRefs"][0].update(ref="dataset_alias"),
    lambda p: p["steps"][1]["inputRefs"][0].update(objectType="Trajectory"),
    lambda p: p["steps"][1]["inputRefs"][0].update(datasetId="invented"),
    lambda p: p["steps"][1].update(sourceScope="invented"),
    lambda p: p["steps"][1]["output"].update(sourceObjectVersionIds=[V1]),
    lambda p: p["steps"][1]["output"].update(sourceObjectVersionIds=[V1, V2]),
    lambda p: p["steps"].pop(),
])
def test_invalid_or_ambiguous_source_inventory_is_rejected(change):
    draft = payload()
    change(draft)
    with pytest.raises(ValidationError):
        AnalysisPlanV03.model_validate(draft)


@pytest.mark.parametrize("profile_ref", ["profile", "profile:profile_a", "profile:missing"])
def test_step_cannot_borrow_another_materials_profile(profile_ref):
    draft = payload()
    draft["steps"][1]["inputRefs"].append({"refType": "profile", "ref": profile_ref, "fieldRole": "profile"})
    with pytest.raises(ValidationError, match="Profile input"):
        AnalysisPlanV03.model_validate(draft)


def test_exact_profile_and_dependency_sources_are_explicit():
    draft = payload()
    draft["steps"][1]["inputRefs"].append({"refType": "profile", "ref": "profile:profile_b", "fieldRole": "profile"})
    draft["steps"].append({
        "stepId": "compare", "toolId": "comparison", "purpose": "Compare", "reason": "Bound outputs",
        "inputRefs": [], "output": {"sourceObjectVersionIds": [V1, V2]},
    })
    bindings = [make_dependency_binding(
        producerStepId=f"s{index}", producerOutputPort="rdf", consumerStepId="compare", consumerInputPort=f"input{index}",
        artifactKind="table_json", artifactContractVersion="rdf/1.0", mediaType="application/json", cardinality="EXACTLY_ONE",
    ) for index in [1, 2]]
    draft["dependencyBindings"] = [item.model_dump(mode="json") for item in bindings]
    draft["graphHash"] = compute_dependency_graph_hash(bindings)
    plan = AnalysisPlanV03.model_validate(draft)
    assert plan.steps[-1].output["sourceObjectVersionIds"] == [V1, V2]
    draft["steps"][-1]["output"]["sourceObjectVersionIds"] = [V1]
    with pytest.raises(ValidationError, match="source coverage"):
        AnalysisPlanV03.model_validate(draft)


def test_legacy_plan_contract_does_not_silently_accept_multi_source_authority():
    draft = payload()
    with pytest.raises(ValidationError):
        AnalysisPlanV02.model_validate(draft)
    draft["schemaVersion"] = "0.2"
    with pytest.raises(ValidationError, match="Extra inputs"):
        AnalysisPlanV02.model_validate(draft)


def test_published_json_schema_matches_the_executable_contract():
    schema = json.loads((Path(__file__).resolve().parents[1] / "packages/schemas/json/analysis-plan-v0.3.schema.json").read_text(encoding="utf-8"))
    assert schema == AnalysisPlanV03.model_json_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload())


def test_version_dispatch_revalidates_models_and_keeps_source_authority_in_plan_hash():
    from mdi_api.application.research.planning.integrity import compute_plan_hash

    plan = parse_analysis_plan(payload())
    assert isinstance(plan, AnalysisPlanV03)
    assert isinstance(parse_dependency_plan(plan), AnalysisPlanV03)
    assert compute_plan_hash(plan) == compute_plan_hash(payload()) == dependency_semantic_hash(plan)
    changed = deepcopy(payload())
    changed["sourceContexts"][1]["profileId"] = "profile_b_revision2"
    assert compute_plan_hash(changed) != compute_plan_hash(plan)
    plan.steps[1].output["sourceObjectVersionIds"] = [V1]
    with pytest.raises(ValueError, match="source coverage"):
        parse_analysis_plan(plan)


@pytest.mark.parametrize("version", ["0.1", "0.2", "0.4", None])
def test_dispatch_never_downgrades_multi_source_authority(version):
    draft = payload()
    draft["schemaVersion"] = version
    with pytest.raises(ValueError):
        parse_analysis_plan(draft)


def test_registry_validation_checks_multi_source_plans_and_tool_parameters():
    from mdi_tool_registry import load_manifests, validate_dependency_plan
    from mdi_tool_registry.plan_validator import validate_plan

    registry = load_manifests()
    draft = payload()
    assert validate_plan(draft, registry=registry).ok
    assert validate_dependency_plan(draft, registry=registry).ok
    draft["steps"][1]["params"] = {"unexpected_execution_argument": "forbidden"}
    result = validate_plan(draft, registry=registry)
    assert not result.ok
    assert any(item.code == "PARAMS_SCHEMA_INVALID" for item in result.errors)
    draft["steps"][1]["output"]["sourceObjectVersionIds"] = [V1]
    assert not validate_dependency_plan(draft, registry=registry).ok


def test_single_dataset_planner_cannot_admit_unapproved_multi_source_provider_output():
    from mdi_api.repositories import InMemoryRepositoryBundle
    from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
    from mdi_llm import MockLLMProvider

    repos = InMemoryRepositoryBundle.create()
    result = planner_jobs(PlannerJobsRequest(userPrompt="Compare materials", projectId="project", datasetId="dataset_a"),
        provider=MockLLMProvider(fixed_plan=payload()), repositories=repos)
    assert not result.ok and result.plan_id is None and result.job_id is None
    assert result.validation_errors[0]["code"] == "MULTI_SOURCE_REQUIRES_RESEARCH"
    assert repos.jobs.records == {}


def test_xrd_preflight_checks_each_dependency_pair_instead_of_only_the_last_tool():
    from mdi_schemas import DataProfile
    from mdi_tool_registry import build_artifact_port_inventory, load_manifests
    from mdi_workers.source_resources import preflight_execution_resources, register_runtime_source_resource

    registry = load_manifests()
    ports = build_artifact_port_inventory(registry)
    producer = ports["structure.xrd"].outputPorts[0]
    consumer = ports["structure.experimental_xrd_comparison"].inputPorts[0]
    draft = payload()
    draft.update(datasetId="dataset_0", profileId="profile_0", sourceContexts=[], sourceVersions=[], steps=[])
    ids = [f"{i:08d}-1111-4111-8111-111111111111" for i in range(1, 5)]
    store = {}
    for i, version_id in enumerate(ids):
        dataset, profile_id = f"dataset_{i}", f"profile_{i}"
        object_type = "Structure" if i % 2 == 0 else "DataFrame"
        draft["sourceContexts"].append({"datasetId": dataset, "profileId": profile_id})
        draft["sourceVersions"].append({"objectId": version_id, "versionId": version_id, "datasetId": dataset, "objectType": object_type})
        profile = DataProfile(datasetId=dataset, profileId=profile_id, datasetType="structure", version="1.0", createdAt="2026-10-06T00:00:00Z")
        register_runtime_source_resource(store, object_id=f"profile:{profile_id}", object_type="DataProfile", object_hash=profile_id, dataset_id=dataset, value=profile)
        register_runtime_source_resource(store, object_id=version_id, object_type=object_type, object_hash="a"*64, dataset_id=dataset,
            value={"wavelength": {"value": 1.0 if i == 1 else 1.54184, "unit": "angstrom"}})
        draft["steps"].append({"stepId": f"step_{i}", "toolId": "structure.xrd" if i % 2 == 0 else "structure.experimental_xrd_comparison",
            "purpose": "XRD", "reason": "Independent exact material pair", "inputRefs": [{"refType": "normalized_object", "ref": version_id, "objectType": object_type}],
            "output": {"sourceObjectVersionIds": [version_id] if i % 2 == 0 else ids[i-1:i+1]}})
    bindings = [make_dependency_binding(producerStepId=f"step_{i}", producerOutputPort=producer.portId,
        consumerStepId=f"step_{i+1}", consumerInputPort=consumer.portId, artifactKind=producer.artifactKind,
        artifactContractVersion=producer.contractVersions[0], mediaType="application/json", cardinality="EXACTLY_ONE") for i in [0, 2]]
    draft.update(dependencyBindings=[item.model_dump(mode="json") for item in bindings], graphHash=compute_dependency_graph_hash(bindings))
    result = preflight_execution_resources(draft, object_store=store, registry=registry, dataset_id="dataset_0")
    assert [issue.code for issue in result.issues] == ["XRD_WAVELENGTH_MISMATCH"]
    assert result.scientific_compatibility_checks == ("XRD_WAVELENGTH_EXACT_MATCH",)


@pytest.mark.parametrize("backend", ["memory", "sqlite"])
def test_multi_source_plan_and_bindings_persist_without_losing_inventory(tmp_path, backend):
    from sqlalchemy import create_engine
    from mdi_api.db import metadata
    from mdi_api.repositories import InMemoryRepositoryBundle, SqlAlchemyRepositoryBundle, compute_plan_hash

    engine = None
    if backend == "memory":
        repos = InMemoryRepositoryBundle.create()
    else:
        engine = create_engine(f"sqlite:///{(tmp_path / 'multi-source.sqlite').as_posix()}")
        metadata.create_all(engine)
        repos = SqlAlchemyRepositoryBundle.create(engine)
    try:
        repos.projects.save({"projectId": "project", "name": "Sources", "createdBy": "owner"})
        for key in ["dataset_a", "dataset_b"]:
            repos.datasets.save({"datasetId": key, "projectId": "project", "name": key, "createdBy": "owner"})
        draft = payload()
        binding = make_dependency_binding(
            producerStepId="s1", producerOutputPort="rdf", consumerStepId="s2", consumerInputPort="comparison",
            artifactKind="table_json", artifactContractVersion="rdf/1.0", mediaType="application/json", cardinality="EXACTLY_ONE",
        )
        draft["dependencyBindings"] = [binding.model_dump(mode="json")]
        draft["graphHash"] = compute_dependency_graph_hash([binding])
        draft["steps"][1]["output"]["sourceObjectVersionIds"] = [V1, V2]
        plan = parse_dependency_plan(draft)
        plan_hash = compute_plan_hash(plan)
        record = {"id": "plan_multi", "projectId": "project", "analysisPlan": draft, "planHash": plan_hash}
        repos.analysis_plans.save_plan(record)
        saved = repos.analysis_plans.get_plan("plan_multi")
        assert saved["analysisPlan"] == plan.model_dump(mode="json")
        bindings = repos.dependency_execution.save_plan_bindings("plan_multi", plan_hash, plan.graphHash, [binding])
        assert bindings[0]["dependencyBinding"] == binding.model_dump(mode="json")
        assert bindings[0]["planHash"] == plan_hash
        for field in ["datasetId", "profileId"]:
            with pytest.raises(ValueError, match="routing context"):
                repos.analysis_plans.save_plan({**record, "id": "misrouted", field: "unrelated"})
        changed = deepcopy(record)
        changed["analysisPlan"]["sourceVersions"][1]["objectId"] = "33333333-3333-4333-8333-333333333333"
        with pytest.raises(ValueError, match="planHash"):
            repos.analysis_plans.save_plan(changed)
        # A valid replacement hash must not authorize changing the identity of
        # an already persisted plan or its exact source inventory.
        changed["planHash"] = compute_plan_hash(changed["analysisPlan"])
        with pytest.raises(ValueError, match="immutable"):
            repos.analysis_plans.save_plan(changed)
        downgraded = deepcopy(record)
        downgraded["analysisPlan"].update(schemaVersion="0.1")
        for field in ("sourceContexts", "sourceVersions", "graphHash", "dependencyBindings"):
            downgraded["analysisPlan"].pop(field, None)
        downgraded["planHash"] = compute_plan_hash(downgraded["analysisPlan"])
        with pytest.raises(ValueError, match="immutable"):
            repos.analysis_plans.save_plan(downgraded)
        replay = repos.analysis_plans.save_plan(record)
        assert replay["planHash"] == plan_hash
        assert repos.analysis_plans.get_plan("plan_multi")["analysisPlan"] == plan.model_dump(mode="json")
    finally:
        if engine is not None:
            engine.dispose()
