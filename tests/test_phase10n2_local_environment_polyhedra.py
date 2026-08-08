from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import ToolExecutionContext
from mdi_adapters.context import hashable_material
from mdi_adapters.errors import ToolExecutionError
from mdi_adapters.executor import execute_tool_request
from mdi_artifact_core import content_hash, stable_json_dumps
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_llm.grounded_interpretation import ArtifactProjectionInput, InterpretationSource, project_artifact
from mdi_schemas import AnalysisPlan, InputRef, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import build_artifact_compatibility_matrix, load_manifests

from tests.test_phase10n1_coordination import _profile


def _structure(vectors: list[tuple[float, float, float]]) -> Structure:
    scale = 0.08
    center = (0.5, 0.5, 0.5)
    sites = [center, *[(center[0] + scale * x, center[1] + scale * y, center[2] + scale * z) for x, y, z in vectors]]
    return Structure(Lattice.cubic(10), ["Si", *(["O"] * len(vectors))], sites)


def _n1_payload(structure: Structure, *, algorithm: str = "crystalnn") -> dict[str, Any]:
    structure_hash = content_hash(stable_json_dumps(hashable_material(structure)))
    tool_id = f"structure.coordination_{algorithm}"
    algorithm_id = f"pymatgen.{algorithm}"
    schema = f"phase10n1.{algorithm}_coordination.v1"
    semantics = "crystalnn_weight_sum" if algorithm == "crystalnn" else "voronoinn_solid_angle_weight_sum"
    center = structure[0]
    neighbors = []
    parameter_hash = "b" * 64
    for index in range(1, len(structure)):
        distance = float(center.distance(structure[index]))
        identity = f"neighbor:{algorithm_id}:{parameter_hash}:{structure_hash}:0:{index}:0,0,0"
        neighbors.append({
            "neighborIdentity": identity,
            "neighborSiteId": f"site:{structure_hash}:{index}",
            "neighborSiteIndex": index,
            "periodicImage": [0, 0, 0],
            "distance": round(distance, 12),
            "distanceUnit": "angstrom",
            "weight": 1.0,
        })
    return {
        "artifactType": tool_id,
        "schema_version": schema,
        "tool": {"toolId": tool_id, "toolVersion": "0.1.0", "adapterVersion": "0.1.0"},
        "algorithm": {"algorithmId": algorithm_id, "algorithmVersion": "2026.5.4"},
        "library": {"name": "pymatgen", "version": "2026.5.4", "coreVersion": "2026.5.18", "license": "MIT"},
        "resolvedParameters": {},
        "fixedParameters": {},
        "parameterHash": parameter_hash,
        "scope": {"projectId": "project_n2", "datasetId": "dataset_n2", "jobId": "job_n2", "planId": "plan_n2", "planVersion": "0.2", "toolCallId": "call_n1", "sourceResourceId": "structure", "sourceResourceHash": content_hash(stable_json_dumps(hashable_material(structure)))},
        "structures": [{"structureId": "structure", "structureHash": structure_hash, "formula": structure.composition.reduced_formula, "siteCount": len(structure), "sourceResourceId": "structure", "sourceResourceHash": content_hash(stable_json_dumps(hashable_material(structure)))}],
        "siteResults": [{"structureHash": structure_hash, "siteId": f"site:{structure_hash}:0", "siteIndex": 0, "species": "Si", "fractionalCoordinates": [0.5, 0.5, 0.5], "coordinationSemantics": semantics, "coordinationValue": float(len(neighbors)), "neighborCount": len(neighbors), "neighbors": neighbors}],
        "coverage": {"status": "COMPLETE", "totalSites": 1, "eligibleSites": 1, "successfulSites": 1, "unsupportedSites": 0, "failedSites": 0, "zeroNeighborSites": 0, "retainedNeighborRows": len(neighbors), "ratio": 1.0},
        "warnings": [], "unsupportedSites": [], "runtimeDiagnostics": {}, "provenance": {}, "limits": {}, "security": {},
    }


def _run(tmp_path: Path, structure: Structure, payload: dict[str, Any], params: dict[str, Any] | None = None):
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.local_environment_polyhedra")
    checksum = content_hash(stable_json_dumps(payload))
    context = ToolExecutionContext(
        job_id="job_n2", project_id="project_n2", dataset_id="dataset_n2",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="0.1.0",
        registry_version=registry.version, artifact_root=tmp_path, tool_call_id="call_n2",
        plan_id="plan_n2", plan_version="0.2",
        object_store={"structure": structure, "coordination": payload},
        artifact_bindings={"coordination": {"artifactId": "artifact_n1", "checksum": checksum, "artifactContractVersion": payload["schema_version"]}},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_n2", stepId="step_n2", toolId=tool.toolId,
        inputRefs=[
            InputRef(refType="normalized_object", ref="structure", objectType=MaterialObjectType.Structure),
            InputRef(refType="artifact", ref="coordination", fieldRole="coordination_artifact", objectType=MaterialObjectType.Structure),
        ],
        params=params or {}, artifactTypes=tool.artifactTypes,
    )
    result = execute_tool_request(context, request, registry=registry)
    artifact = next(item for item in result.artifacts if item.type.value == "table_json")
    return result, json.loads((tmp_path / artifact.storageKey).read_text(encoding="utf-8"))


TETRAHEDRAL = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
OCTAHEDRAL = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
SQUARE_PLANAR = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]


def test_registry_adds_exactly_one_n2_tool_and_exact_n1_ports() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 56
    tool = registry.get_tool_by_id("structure.local_environment_polyhedra")
    assert tool.version == "0.1.0"
    assert tool.adapter == "LocalEnvironmentPolyhedraAdapter"
    assert not any(item.toolId in {"structure.polyhedron_only", "structure.environment_only", "structure.chemenv"} for item in registry.tools)
    for producer in ("structure.coordination_crystalnn", "structure.coordination_voronoinn"):
        matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=sorted([producer, tool.toolId]))
        pair = next(item for item in matrix.pairs if item.compatible)
        assert pair.producerOutputPort == "coordination-table"
        assert pair.consumerInputPort == "coordination"


def test_planner_preserves_explicit_n1_source_and_never_silently_selects_one() -> None:
    registry = load_manifests()
    provider = MockLLMProvider()
    tools = registry.list_mvp_tools()
    for algorithm, producer in (
        ("CrystalNN", "structure.coordination_crystalnn"),
        ("VoronoiNN", "structure.coordination_voronoinn"),
    ):
        response = provider.generate_plan(
            PlannerRequest(
                user_prompt=f"Analyze the local environment using {algorithm} coordination.",
                dataset_id="dataset_n2",
                profile_id="profile_n2",
                tool_registry_version=registry.version,
            ),
            tools=tools,
            data_profile=_profile(),
        )
        plan = AnalysisPlan.model_validate(response.raw_json)
        assert [step.toolId for step in plan.steps] == [producer, "structure.local_environment_polyhedra"]
        assert all(step.inputRefs[0].ref == "structures" for step in plan.steps)

    ambiguous = provider.generate_plan(
        PlannerRequest(
            user_prompt="Analyze the local environment and construct coordination polyhedra.",
            dataset_id="dataset_n2",
            profile_id="profile_n2",
            tool_registry_version=registry.version,
        ),
        tools=tools,
        data_profile=_profile(),
    )
    assert "structure.local_environment_polyhedra" not in {
        step.toolId for step in AnalysisPlan.model_validate(ambiguous.raw_json).steps
    }


@pytest.mark.parametrize(("vectors", "expected"), [(TETRAHEDRAL, "tetrahedral"), (OCTAHEDRAL, "octahedral")])
@pytest.mark.parametrize("algorithm", ["crystalnn", "voronoinn"])
def test_exact_n1_artifact_produces_reference_class_and_persisted_faces(tmp_path: Path, vectors, expected, algorithm) -> None:
    structure = _structure(vectors)
    _, payload = _run(tmp_path, structure, _n1_payload(structure, algorithm=algorithm))
    site = payload["siteResults"][0]
    assert site["classification"]["status"] == "CLASSIFIED"
    assert site["classification"]["referenceGeometryId"] == expected
    assert site["polyhedron"]["status"] == "AVAILABLE"
    assert site["polyhedron"]["faces"]
    assert all(vertex["neighborIdentity"] in site["neighborRelationIdentities"] for vertex in site["polyhedron"]["vertices"])
    assert payload["runtimeDiagnostics"] == {
        "boundedPairwiseMatching": True,
        "coordinationAlgorithmFallback": False,
        "independentNeighborSearch": False,
        "n1NeighborRecomputation": False,
        "resultSubstitution": False,
    }


def test_coplanar_environment_remains_classified_while_faces_are_typed_unavailable(tmp_path: Path) -> None:
    structure = _structure(SQUARE_PLANAR)
    _, payload = _run(tmp_path, structure, _n1_payload(structure))
    site = payload["siteResults"][0]
    assert site["classification"]["referenceGeometryId"] == "square_planar"
    assert site["polyhedron"] == {
        "status": "UNAVAILABLE", "vertices": site["polyhedron"]["vertices"], "faces": [], "unavailableReason": "COPLANAR_POLYHEDRON"
    }
    assert site["distortionMetrics"]["polyhedronVolume"] is None


def test_ambiguity_is_retained_and_never_silently_resolved(tmp_path: Path) -> None:
    distorted = [(1, 1, 0.45), (1, -1, -0.45), (-1, 1, -0.45), (-1, -1, 0.45)]
    structure = _structure(distorted)
    _, payload = _run(tmp_path, structure, _n1_payload(structure), {"classification_tie_tolerance": 0.25})
    classification = payload["siteResults"][0]["classification"]
    assert classification["status"] == "AMBIGUOUS"
    assert classification["alternatives"]
    assert "LOCAL_ENVIRONMENT_AMBIGUOUS" in payload["siteResults"][0]["warnings"]


def test_result_is_deterministic_and_parameter_hash_is_stable(tmp_path: Path) -> None:
    structure = _structure(TETRAHEDRAL)
    first, payload_a = _run(tmp_path / "a", structure, _n1_payload(structure))
    second, payload_b = _run(tmp_path / "b", structure, _n1_payload(structure))
    artifact_a = next(item for item in first.artifacts if item.type.value == "table_json")
    artifact_b = next(item for item in second.artifacts if item.type.value == "table_json")
    assert payload_a == payload_b
    assert artifact_a.contentHash == artifact_b.contentHash
    assert payload_a["siteResults"][0]["polyhedron"]["faces"] == sorted(payload_a["siteResults"][0]["polyhedron"]["faces"], key=lambda item: item["faceIdentity"])


def test_strict_params_identity_and_distance_mismatch_are_rejected(tmp_path: Path) -> None:
    structure = _structure(TETRAHEDRAL)
    source = _n1_payload(structure)
    with pytest.raises(ToolExecutionError, match="paramsSchema"):
        _run(tmp_path / "unknown", structure, source, {"unknown": True})
    with pytest.raises(ToolExecutionError, match="classification_tie_tolerance is outside its bounded range"):
        _run(tmp_path / "nan", structure, source, {"classification_tie_tolerance": float("nan")})
    tampered = json.loads(json.dumps(source))
    tampered["siteResults"][0]["neighbors"][0]["distance"] += 0.01
    _, partial = _run(tmp_path / "distance", structure, tampered)
    assert partial["coverage"]["status"] == "FAILED"
    assert partial["coverage"]["unavailable"][0]["reason"] == "COORDINATION_STRUCTURE_MISMATCH"


def test_missing_exact_persisted_binding_is_rejected_before_geometry(tmp_path: Path) -> None:
    structure = _structure(TETRAHEDRAL)
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.local_environment_polyhedra")
    payload = _n1_payload(structure)
    context = ToolExecutionContext(
        job_id="job", project_id="project_n2", dataset_id="dataset_n2", tool_id=tool.toolId,
        tool_version=tool.version, adapter_version="0.1.0", registry_version=registry.version,
        artifact_root=tmp_path, object_store={"s": structure, "a": payload}, resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(jobId="job", stepId="n2", toolId=tool.toolId, inputRefs=[
        InputRef(refType="normalized_object", ref="s", objectType=MaterialObjectType.Structure),
        InputRef(refType="artifact", ref="a", objectType=MaterialObjectType.Structure),
    ], params={}, artifactTypes=tool.artifactTypes)
    with pytest.raises(ToolExecutionError, match="binding metadata"):
        execute_tool_request(context, request, registry=registry)


def test_local_environment_projector_exposes_only_bounded_persisted_facts(tmp_path: Path) -> None:
    structure = _structure(TETRAHEDRAL)
    result, payload = _run(tmp_path, structure, _n1_payload(structure))
    artifact = next(item for item in result.artifacts if item.type.value == "table_json")
    source = InterpretationSource(
        project_id="project_n2", dataset_id="dataset_n2", dataset_version="1", profile_id="profile_n2",
        profile_semantic_hash=None, intent_id=None, intent_hash=None, resolution_id=None, resolution_hash=None,
        decision_id=None, decision_hash=None, plan_id="plan_n2", plan_hash="a" * 64, plan_schema_version="0.2",
        graph_hash="b" * 64, job_id="job_n2", job_status="completed", execution_outcome="ALL_SUCCEEDED",
        failed_step_count=0, blocked_step_count=0,
    )
    items = project_artifact(
        source,
        ArtifactProjectionInput(
            artifact={"artifactId": "artifact_n2", "type": "table_json", "contentHash": artifact.contentHash},
            payload=payload,
            tool_call={"toolId": "structure.local_environment_polyhedra", "stepId": "step_n2", "id": "call_n2"},
            lineage={"producerToolVersion": "0.1.0"}, raw_checksum=artifact.contentHash, raw_size_bytes=artifact.sizeBytes,
        ),
    )
    roles = {item.semanticRole for item in items}
    assert {
        "local_environment.source_algorithm", "local_environment.coverage",
        "local_environment.classified_sites", "local_environment.reference_count",
        "local_environment.geometry_distance_range",
    } <= roles
    assert all("neighbor" not in item.fieldLocator.fieldId and "faces" not in item.fieldLocator.fieldId for item in items)
