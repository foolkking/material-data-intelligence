from __future__ import annotations

import json
from pathlib import Path

from pymatgen.core import Lattice, Structure

from mdi_api.repositories import InMemoryRepositoryBundle, compute_plan_hash
from mdi_schemas import AnalysisPlanV02, compute_dependency_graph_hash, make_dependency_binding
from mdi_tool_registry import load_manifests, validate_dependency_plan
from mdi_workers import QueueWorkerRuntime


def _plan() -> AnalysisPlanV02:
    binding = make_dependency_binding(
        producerStepId="step_crystalnn",
        producerOutputPort="coordination-table",
        consumerStepId="step_environment",
        consumerInputPort="coordination",
        artifactKind="table_json",
        artifactContractVersion="phase10n1.crystalnn_coordination.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )
    steps = [
        {
            "stepId": "step_environment",
            "toolId": "structure.local_environment_polyhedra",
            "purpose": "Classify exact CrystalNN-derived local environments.",
            "reason": "Consume the persisted exact coordination Artifact without neighbor recomputation.",
            "inputRefs": [{"refType": "normalized_object", "ref": "structure", "objectType": "Structure"}],
            "params": {"site_indices": [0]},
            "output": {"artifactTypes": ["table_json"], "displayTarget": "result"},
        },
        {
            "stepId": "step_crystalnn",
            "toolId": "structure.coordination_crystalnn",
            "purpose": "Produce exact CrystalNN coordination.",
            "reason": "N2 uses this persisted Artifact as its only neighbor authority.",
            "inputRefs": [{"refType": "normalized_object", "ref": "structure", "objectType": "Structure"}],
            "params": {},
            "output": {"artifactTypes": ["table_json"], "displayTarget": "result"},
        },
    ]
    return AnalysisPlanV02.model_validate({
        "schemaVersion": "0.2",
        "goal": "Analyze local environment using CrystalNN coordination.",
        "datasetId": "dataset_n2_runtime",
        "profileId": "profile_n2_runtime",
        "toolRegistryVersion": load_manifests().version,
        "assumptions": [],
        "warnings": [],
        "steps": steps,
        "expectedArtifacts": [
            {"name": "coordination.json", "type": "table_json", "fromStepId": "step_crystalnn"},
            {"name": "local_environment_polyhedra.json", "type": "table_json", "fromStepId": "step_environment"},
        ],
        "graphHash": compute_dependency_graph_hash([binding]),
        "dependencyBindings": [binding.model_dump(mode="json")],
    })


def _seed(plan: AnalysisPlanV02) -> tuple[InMemoryRepositoryBundle, str, str]:
    repos = InMemoryRepositoryBundle.create()
    project_id = "project_n2_runtime"
    job_id = "job_n2_runtime"
    plan_id = "plan_n2_runtime"
    repos.projects.save({"id": project_id, "name": "N2 dependency runtime"})
    repos.datasets.save({"id": plan.datasetId, "projectId": project_id, "name": "Periodic structure"})
    plan_hash = compute_plan_hash(plan)
    repos.analysis_plans.save_plan({
        "id": plan_id, "projectId": project_id, "datasetId": plan.datasetId, "profileId": plan.profileId,
        "planSource": "capability_planner", "plannerProvider": "mock", "analysisPlan": plan.model_dump(mode="json"),
        "planHash": plan_hash, "createdBy": "phase10n2_test",
    })
    repos.dependency_execution.save_plan_bindings(plan_id, plan_hash, plan.graphHash, plan.dependencyBindings)
    repos.jobs.save({
        "id": job_id, "projectId": project_id, "datasetId": plan.datasetId, "planId": plan_id,
        "status": "created", "kind": "analysis", "createdBy": "phase10n2_test",
    })
    repos.analysis_plans.attach_plan_to_job(plan_id, job_id)
    return repos, job_id, plan_hash


def test_n1_to_n2_executes_topologically_with_exact_persisted_binding(tmp_path: Path) -> None:
    registry = load_manifests()
    plan = _plan()
    validation = validate_dependency_plan(plan, registry=registry)
    assert validation.ok
    assert validation.topological_order == ["step_crystalnn", "step_environment"]
    repos, job_id, plan_hash = _seed(plan)
    structure = Structure(Lattice.cubic(3.57), ["Si", "Si"], [[0, 0, 0], [0.25, 0.25, 0.25]])
    runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=tmp_path / "runtime")
    result = runtime.handle_job(job_id, object_store={"structure": structure})

    assert result.status == "completed"
    assert result.plan_hash == plan_hash
    calls = repos.tool_calls.list_for_job(job_id)
    assert [(item["stepId"], item["status"]) for item in calls] == [
        ("step_crystalnn", "completed"), ("step_environment", "completed")
    ]
    artifacts = repos.artifacts.list_for_job(job_id)
    n1 = next(item for item in artifacts if item["metadata"]["provenance"]["schemaVersion"] == "phase10n1.crystalnn_coordination.v1")
    n2 = next(item for item in artifacts if item["metadata"]["provenance"]["schemaVersion"] == "phase10n2.local_environment_polyhedra.v1")
    payload = json.loads(runtime.artifact_storage.get_bytes(n2["storageKey"]).decode("utf-8"))
    assert payload["scope"]["planId"] == "plan_n2_runtime"
    assert payload["scope"]["planVersion"] == "0.2"
    assert payload["sourceCoordination"]["artifactId"] == n1["id"]
    assert payload["sourceCoordination"]["artifactChecksum"] == n1["sha256"]
    assert payload["runtimeDiagnostics"] == {
        "n1NeighborRecomputation": False,
        "independentNeighborSearch": False,
        "coordinationAlgorithmFallback": False,
        "resultSubstitution": False,
        "boundedPairwiseMatching": True,
    }
    execution = repos.dependency_execution.get_execution_for_job(job_id)
    assert execution["outcome"] == "ALL_SUCCEEDED"
    lineage = next(item for item in repos.dependency_execution.list_lineage_for_job(job_id) if item["producerToolId"] == "structure.local_environment_polyhedra")
    assert lineage["upstreamArtifactIds"] == [n1["id"]]
    assert lineage["bindingIds"] == [plan.dependencyBindings[0].bindingId]
