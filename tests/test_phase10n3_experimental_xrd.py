from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import pytest

from mdi_adapters import ToolExecutionContext
from mdi_adapters.errors import ToolExecutionError
from mdi_adapters.executor import execute_tool_request
from mdi_artifact_core import content_hash, stable_json_dumps
from mdi_llm.grounded_interpretation import ArtifactProjectionInput, InterpretationSource, project_artifact
from mdi_material_parsers import build_data_profile, parse_file
from mdi_schemas import InputRef, MaterialObjectType, ToolExecutionRequest
from mdi_tool_registry import build_artifact_compatibility_matrix, load_manifests


HASH = "a" * 64
WAVELENGTH = 1.5406


def _resource(two_theta: list[float] | None = None, intensity: list[float] | None = None, *, wavelength: float = WAVELENGTH) -> dict[str, Any]:
    x = two_theta or [19.8, 20.0, 20.2, 39.8, 40.0, 40.2, 59.8, 60.0, 60.2]
    y = intensity or [0.0, 10.0, 0.0, 0.0, 8.0, 0.0, 0.0, 6.0, 0.0]
    result = {
        "schemaVersion": "phase10n3.experimental_xrd_resource.v1",
        "resourceId": "experimental_xrd_1", "resourceVersion": "1",
        "xAxis": {"kind": "two_theta", "unit": "degree"},
        "twoTheta": x, "intensity": y, "intensitySemantic": "counts",
        "wavelength": {"value": wavelength, "unit": "angstrom"},
    }
    result["resourceHash"] = content_hash(stable_json_dumps(result))
    return result


def _theoretical(peaks: list[float] | None = None, *, wavelength: float = WAVELENGTH) -> dict[str, Any]:
    values = peaks or [20.02, 39.97, 80.0]
    return {
        "artifactType": "structure.xrd", "schema_version": "phase10e4.xrd_pattern.v1",
        "tool_id": "structure.xrd", "radiation": {"name": "CuKa", "wavelength_angstrom": wavelength},
        "pattern": {"peak_count": len(values), "intensity_scale": "relative_100", "peaks": [
            {"structureId": "structure_1", "two_theta_deg": value, "intensity": 100.0 - index, "d_spacing_angstrom": 2.0 + index, "hkls": [{"hkl": [index + 1, 0, 0], "multiplicity": 2}]}
            for index, value in enumerate(values)
        ]},
    }


def _run(tmp_path: Path, *, resource: dict[str, Any] | None = None, theory: dict[str, Any] | None = None, params: dict[str, Any] | None = None):
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.experimental_xrd_comparison")
    theory_payload = theory or _theoretical()
    context = ToolExecutionContext(
        job_id="job_n3", project_id="project_n3", dataset_id="dataset_n3",
        tool_id=tool.toolId, tool_version=tool.version, adapter_version="0.1.0",
        registry_version=registry.version, artifact_root=tmp_path, tool_call_id="call_n3",
        plan_id="plan_n3", plan_version="0.2",
        object_store={"experimental": resource or _resource(), "theoretical": theory_payload},
        artifact_bindings={"theoretical": {"artifactId": "artifact_theory", "checksum": HASH, "artifactContractVersion": "phase10e4.xrd_pattern.v1", "projectId": "project_n3", "jobId": "job_n3"}},
        resource_limits=tool.resourceLimits,
    )
    request = ToolExecutionRequest(
        jobId="job_n3", stepId="step_n3", toolId=tool.toolId,
        inputRefs=[
            InputRef(refType="normalized_object", ref="experimental", objectType=MaterialObjectType.DataFrame),
            InputRef(refType="artifact", ref="theoretical", fieldRole="theoretical_xrd_artifact", objectType=MaterialObjectType.Structure),
        ],
        params=params or {}, artifactTypes=tool.artifactTypes,
    )
    result = execute_tool_request(context, request, registry=registry)
    artifact = next(item for item in result.artifacts if item.type.value == "table_json")
    return result, json.loads((tmp_path / artifact.storageKey).read_text(encoding="utf-8"))


def test_registry_adds_one_n3_tool_and_exact_theoretical_dependency() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 57
    tool = registry.get_tool_by_id("structure.experimental_xrd_comparison")
    assert tool.version == "0.1.0" and tool.adapter == "ExperimentalXrdComparisonAdapter"
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=["structure.experimental_xrd_comparison", "structure.xrd"])
    pair = next(item for item in matrix.pairs if item.compatible)
    assert pair.producerToolId == "structure.xrd"
    assert pair.artifactContractVersion == "phase10e4.xrd_pattern.v1"


def test_resource_parser_builds_additive_profile_22(tmp_path: Path) -> None:
    path = tmp_path / "experimental-xrd.json"
    path.write_text(json.dumps(_resource()), encoding="utf-8")
    parsed = parse_file(path, dataset_id="dataset_n3")
    assert parsed.parse_status == "success"
    profile = build_data_profile(dataset_id="dataset_n3", parse_results=[parsed])
    assert profile.profileContractVersion == "2.2"
    assert profile.experimentalXrdReadiness is not None
    assert profile.experimentalXrdReadiness.status == "READY"
    assert profile.experimentalXrdReadiness.resources[0].resourceHash == _resource()["resourceHash"]


def test_match_preserves_both_unmatched_sets_and_residuals(tmp_path: Path) -> None:
    _, payload = _run(tmp_path)
    assert payload["coverage"] == {
        "experimentalPoints": 9, "experimentalDetectedPeaks": 3, "theoreticalPeaksConsidered": 3,
        "matchedPairs": 2, "unmatchedExperimentalPeaks": 1, "unmatchedTheoreticalPeaks": 1,
        "experimentalMatchedFraction": pytest.approx(2 / 3), "theoreticalMatchedFraction": pytest.approx(2 / 3), "excludedPoints": 0,
    }
    assert [item["signedDeltaTwoTheta"] for item in payload["matches"]] == [-0.02, 0.03]
    assert payload["residualSummary"]["maeDeltaTwoTheta"] == 0.025
    assert payload["peakDetector"]["independentOfTheoreticalMatching"] is True
    assert payload["runtimeDiagnostics"] == {
        "theoreticalXrdReimplementation": False, "matchOptimizedPeakDetection": False,
        "automaticPatternShift": False, "latticeRefinement": False, "structureRefinement": False,
        "rietveldRefinement": False, "phaseFractionRefinement": False, "automaticPhaseIdentification": False,
    }


def test_zero_match_is_valid_and_deterministic(tmp_path: Path) -> None:
    first_result, first = _run(tmp_path / "first", theory=_theoretical([100.0]))
    second_result, second = _run(tmp_path / "second", theory=_theoretical([100.0]))
    assert first["coverage"]["matchedPairs"] == 0
    assert first["residualSummary"]["maeDeltaTwoTheta"] is None
    assert "XRD_ZERO_MATCHES" in first["warnings"]
    assert first == second
    assert next(item for item in first_result.artifacts if item.type.value == "table_json").contentHash == next(item for item in second_result.artifacts if item.type.value == "table_json").contentHash


@pytest.mark.parametrize("params", [{"unknown": 1}, {"matching_tolerance_deg": float("nan")}, {"matching_tolerance_deg": 3.0}])
def test_unbounded_or_unknown_parameters_are_rejected(tmp_path: Path, params: dict[str, Any]) -> None:
    with pytest.raises(ToolExecutionError) as rejected:
        _run(tmp_path, params=params)
    assert rejected.value.code == "TOOL_PARAM_INVALID"


def test_wavelength_mismatch_and_nonmonotonic_resource_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(ToolExecutionError) as wavelength:
        _run(tmp_path / "wavelength", resource=_resource(wavelength=1.0))
    assert wavelength.value.details["errorType"] == "XRD_WAVELENGTH_MISMATCH"
    invalid = _resource()
    invalid["twoTheta"][2] = invalid["twoTheta"][1]
    invalid["resourceHash"] = content_hash(stable_json_dumps({key: value for key, value in invalid.items() if key != "resourceHash"}))
    with pytest.raises(ToolExecutionError) as axis:
        _run(tmp_path / "axis", resource=invalid)
    assert axis.value.details["errorType"] == "EXPERIMENTAL_XRD_INVALID_AXIS"


def test_checked_schemas_validate_resource_and_runtime_artifact(tmp_path: Path) -> None:
    root = Path("packages/schemas/json")
    resource_schema = json.loads((root / "phase10n3-experimental-xrd-resource.schema.json").read_text(encoding="utf-8"))
    artifact_schema = json.loads((root / "phase10n3-experimental-xrd-comparison.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(resource_schema).validate(_resource())
    _, payload = _run(tmp_path)
    Draft202012Validator(artifact_schema).validate(payload)


def test_interpretation_projector_exposes_only_bounded_comparison_facts(tmp_path: Path) -> None:
    _, payload = _run(tmp_path)
    source = InterpretationSource("project_n3", "dataset_n3", "v1", None, None, None, None, None, None, None, None, "plan_n3", HASH, "0.2", HASH, "job_n3", "completed", "ALL_SUCCEEDED", 0, 0)
    candidate = ArtifactProjectionInput(
        artifact={"id": "artifact_n3", "type": "table_json", "contentHash": HASH}, payload=payload,
        tool_call={"toolId": "structure.experimental_xrd_comparison", "id": "call_n3"}, lineage=None,
        raw_checksum=HASH, raw_size_bytes=len(stable_json_dumps(payload).encode()),
    )
    items = project_artifact(source, candidate)
    roles = {item.semanticRole for item in items}
    assert {"xrd.matched_pairs", "xrd.unmatched_experimental", "xrd.unmatched_theoretical", "xrd.matching_tolerance"}.issubset(roles)
    assert len(items) <= 10
    serialized = stable_json_dumps([item.model_dump(mode="json") for item in items])
    assert "experimentalSeries" not in serialized
    assert "experimental-peak:" not in serialized and "theoretical-peak:" not in serialized
