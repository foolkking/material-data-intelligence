from __future__ import annotations

import json
from pathlib import Path

import pytest
from pymatgen.core import Lattice, Structure

from mdi_adapters import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_adapters.executor import execute_tool_request
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_llm.grounded_interpretation import ArtifactProjectionInput, InterpretationSource, project_artifact
from mdi_schemas import AnalysisPlan, DataProfile, InputRef, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import load_manifests


def _structure() -> Structure:
    return Structure(
        Lattice.cubic(3.57),
        ["Si", "Si"],
        [[0, 0, 0], [0.25, 0.25, 0.25]],
    )


def _run(tmp_path: Path, tool_id: str, params: dict | None = None):
    registry = load_manifests()
    tool = registry.get_tool_by_id(tool_id)
    context = ToolExecutionContext(
        job_id="job_n1",
        project_id="project_n1",
        dataset_id="dataset_n1",
        tool_id=tool_id,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=registry.version,
        artifact_root=tmp_path,
        tool_call_id=f"call_{tool_id.rsplit('_', 1)[-1]}",
        plan_id="plan_n1",
        plan_version="0.1",
        object_store={"structure_resource": _structure()},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_n1",
        stepId="step_n1",
        toolId=tool_id,
        inputRefs=[InputRef(refType="normalized_object", ref="structure_resource", objectType=MaterialObjectType.Structure)],
        params=params or {},
        artifactTypes=tool.artifactTypes,
    )
    result = execute_tool_request(context, request, registry=registry)
    table = next(artifact for artifact in result.artifacts if artifact.type.value == "table_json")
    payload = json.loads((tmp_path / table.storageKey).read_text(encoding="utf-8"))
    return result, payload


def _profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1",
        "profileId": "profile_n1",
        "datasetId": "dataset_n1",
        "version": "1",
        "datasetType": "structure_collection",
        "files": [{"path": "structure.cif", "format": "cif", "sizeBytes": 512}],
        "objects": [{"objectType": "Structure", "count": 1, "source": "structure.cif"}],
        "structureSummary": {"nStructures": 1, "elements": ["Si"], "formulaStats": {"total": 1, "uniqueCount": 1}},
        "qualityIssues": [],
        "recommendedTasks": [],
        "createdAt": "2026-01-01T00:00:00Z",
    })


def test_planner_selects_exact_n1_tool_and_preserves_comparison_identity() -> None:
    registry = load_manifests()
    provider = MockLLMProvider()
    for prompt, expected in (
        ("analyze coordination using CrystalNN", ["structure.coordination_crystalnn"]),
        ("analyze coordination using VoronoiNN", ["structure.coordination_voronoinn"]),
        ("compare CrystalNN and VoronoiNN", ["structure.coordination_crystalnn", "structure.coordination_voronoinn"]),
    ):
        response = provider.generate_plan(
            PlannerRequest(user_prompt=prompt, dataset_id="dataset_n1", profile_id="profile_n1", tool_registry_version=registry.version),
            tools=registry.list_mvp_tools(),
            data_profile=_profile(),
        )
        plan = AnalysisPlan.model_validate(response.raw_json)
        assert [step.toolId for step in plan.steps] == expected
        assert all(step.inputRefs[0].ref == "structures" for step in plan.steps)
        assert all("max_retained_rows" in step.params for step in plan.steps)


def test_coordination_projector_exposes_bounded_algorithm_facts(tmp_path: Path) -> None:
    result, payload = _run(tmp_path, "structure.coordination_crystalnn")
    artifact = next(item for item in result.artifacts if item.type.value == "table_json")
    source = InterpretationSource(
        project_id="project_n1", dataset_id="dataset_n1", dataset_version="1", profile_id="profile_n1",
        profile_semantic_hash=None, intent_id=None, intent_hash=None, resolution_id=None, resolution_hash=None,
        decision_id=None, decision_hash=None, plan_id="plan_n1", plan_hash="a" * 64, plan_schema_version="0.1",
        graph_hash=None, job_id="job_n1", job_status="completed", execution_outcome="ALL_SUCCEEDED",
        failed_step_count=0, blocked_step_count=0,
    )
    items = project_artifact(
        source,
        ArtifactProjectionInput(
            artifact={"artifactId": "artifact_n1", "type": "table_json", "contentHash": artifact.contentHash},
            payload=payload,
            tool_call={"toolId": "structure.coordination_crystalnn", "stepId": "step_n1", "id": "call_n1"},
            lineage={"producerToolVersion": "0.1.0"}, raw_checksum=artifact.contentHash, raw_size_bytes=artifact.sizeBytes,
        ),
    )
    roles = {item.semanticRole for item in items}
    assert {"coordination.algorithm", "coordination.coverage", "coordination.value_range", "coordination.distance_range"} <= roles


def test_registry_has_exactly_two_n1_tools_and_no_comparison_tool() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 55
    assert {tool.toolId for tool in registry.tools if "coordination_" in tool.toolId} == {
        "structure.coordination_hist",
        "structure.coordination_crystalnn",
        "structure.coordination_voronoinn",
    }
    assert not any("comparison" in tool.toolId and "coordination" in tool.toolId for tool in registry.tools)


@pytest.mark.parametrize("tool_id, schema, semantics", [
    ("structure.coordination_crystalnn", "phase10n1.crystalnn_coordination.v1", "crystalnn_weight_sum"),
    ("structure.coordination_voronoinn", "phase10n1.voronoinn_coordination.v1", "voronoinn_solid_angle_weight_sum"),
])
def test_algorithm_produces_inert_algorithm_specific_artifact(tmp_path: Path, tool_id: str, schema: str, semantics: str) -> None:
    result, payload = _run(tmp_path, tool_id)
    assert len(result.artifacts) == 3
    assert payload["artifactType"] == tool_id
    assert payload["schema_version"] == schema
    assert payload["algorithm"]["algorithmVersion"] == "2026.5.4"
    assert payload["scope"]["planId"] == "plan_n1"
    assert payload["coverage"]["status"] == "COMPLETE"
    assert payload["siteResults"][0]["coordinationSemantics"] == semantics
    assert payload["siteResults"][0]["neighbors"]
    assert all(len(item["periodicImage"]) == 3 for item in payload["siteResults"][0]["neighbors"])
    assert payload["security"]["arbitraryCodeExecution"] is False


def test_periodic_image_and_checksum_order_are_deterministic(tmp_path: Path) -> None:
    first, payload_a = _run(tmp_path / "a", "structure.coordination_crystalnn")
    second, payload_b = _run(tmp_path / "b", "structure.coordination_crystalnn")
    table_a = next(item for item in first.artifacts if item.type.value == "table_json")
    table_b = next(item for item in second.artifacts if item.type.value == "table_json")
    assert payload_a == payload_b
    assert table_a.contentHash == table_b.contentHash


def test_algorithm_parameters_are_strict_and_bounded(tmp_path: Path) -> None:
    with pytest.raises(ToolExecutionError, match="paramsSchema"):
        _run(tmp_path, "structure.coordination_crystalnn", {"unknown": 1})
    with pytest.raises(ToolExecutionError, match="between 0.0 and 5.0"):
        _run(tmp_path, "structure.coordination_crystalnn", {"distance_cutoff_low": float("nan")})
    with pytest.raises(ToolExecutionError, match="greater than or equal"):
        _run(tmp_path, "structure.coordination_crystalnn", {"distance_cutoff_low": 2.0, "distance_cutoff_high": 1.0})


def test_disorder_is_typed_and_never_coerced(tmp_path: Path) -> None:
    structure = Structure(
        Lattice.cubic(4),
        [{"Na": 0.5, "K": 0.5}],
        [[0, 0, 0]],
    )
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.coordination_crystalnn")
    context = ToolExecutionContext(
        job_id="job",
        project_id="project",
        dataset_id="dataset",
        tool_id=tool.toolId,
        tool_version=tool.version,
        adapter_version="0.1.0",
        registry_version=registry.version,
        artifact_root=tmp_path,
        object_store={"source": structure},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job",
        stepId="step",
        toolId=tool.toolId,
        inputRefs=[InputRef(refType="normalized_object", ref="source", objectType=MaterialObjectType.Structure)],
        params={},
        artifactTypes=tool.artifactTypes,
    )
    with pytest.raises(ToolExecutionError, match="N1 coordination does not coerce disordered sites"):
        execute_tool_request(context, request, registry=registry)
