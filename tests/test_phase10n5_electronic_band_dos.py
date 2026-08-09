from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from mdi_adapters import create_adapter
from mdi_adapters.context import ToolExecutionContext
from mdi_artifact_core.electronic_contract import (
    electronic_band_dos_compatibility,
    electronic_resource_hash,
    validate_electronic_band_resource,
    validate_electronic_dos_resource,
)
from mdi_material_parsers import build_data_profile, parse_file
from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder
from mdi_llm.providers import MockLLMProvider, PlannerRequest
from mdi_schemas import AnalysisIntentOutcome, CapabilityNeed, ScientificIntent
from mdi_tool_registry import build_artifact_port_inventory, load_manifests


def _seal(value: dict) -> dict:
    value["resourceHash"] = electronic_resource_hash(value)
    return value


def band_resource() -> dict:
    return _seal({
        "schemaVersion": "phase10n5.electronic_band_resource.v1",
        "resourceId": "band_controlled", "resourceVersion": "1", "resourceHash": "0" * 64,
        "calculationIdentity": "calc_controlled", "sourceMetadata": {"code": "controlled", "method": "fixture"},
        "structureIdentity": {"structureId": "structure_1", "structureHash": "1" * 64},
        "energyUnit": "eV", "energyReference": "source_absolute", "fermiEnergyEv": 0.0,
        "spinMode": "non_spin_polarized", "reciprocalCoordinates": "fractional_reciprocal",
        "kpoints": [
            {"kpointId": "kp_g", "fractionalCoordinates": [0, 0, 0], "pathDistance": 0.0, "segmentId": "seg_1", "label": "G"},
            {"kpointId": "kp_x", "fractionalCoordinates": [0.5, 0, 0], "pathDistance": 1.0, "segmentId": "seg_1", "label": "X"},
            {"kpointId": "kp_l", "fractionalCoordinates": [0.5, 0.5, 0.5], "pathDistance": 2.0, "segmentId": "seg_1", "label": "L"},
        ],
        "pathSegments": [{"segmentId": "seg_1", "startKpointId": "kp_g", "endKpointId": "kp_l", "breakAfter": False}],
        "bands": [
            {"bandId": "v1", "spinChannel": "none", "energiesEv": [-1.0, -0.5, -0.2], "occupations": [1, 1, 1]},
            {"bandId": "c1", "spinChannel": "none", "energiesEv": [0.8, 0.4, 0.6], "occupations": [0, 0, 0]},
        ],
    })


def dos_resource() -> dict:
    return _seal({
        "schemaVersion": "phase10n5.electronic_dos_resource.v1",
        "resourceId": "dos_controlled", "resourceVersion": "1", "resourceHash": "0" * 64,
        "calculationIdentity": "calc_controlled", "sourceMetadata": {"code": "controlled", "method": "fixture"},
        "structureIdentity": {"structureId": "structure_1", "structureHash": "1" * 64},
        "energyUnit": "eV", "energyReference": "source_absolute", "fermiEnergyEv": 0.0,
        "spinMode": "non_spin_polarized", "dosUnitSemantic": "states_per_ev_cell",
        "energiesEv": [-1.0, 0.0, 1.0],
        "totalDos": [{"channelId": "total", "spinChannel": "none", "values": [1.0, 0.1, 2.0]}],
        "projections": [{"channelId": "si_s", "spinChannel": "none", "projectionKind": "orbital", "label": "s", "values": [0.4, 0.04, 0.8]}],
        "projectionCompleteness": "PARTIAL",
    })


def _context(tmp_path: Path, tool_id: str, payload: dict) -> ToolExecutionContext:
    return ToolExecutionContext(job_id="job_n5", project_id="project_n5", dataset_id="dataset_n5", tool_id=tool_id, tool_version="0.1.0", adapter_version="0.1.0", registry_version="0.1.0", artifact_root=tmp_path, tool_call_id=f"call_{tool_id.replace('.', '_')}", plan_id="plan_n5", plan_version="0.2", object_store={"input": payload})


def _execute(tmp_path: Path, tool_id: str, payload: dict, params: dict | None = None) -> dict:
    adapter_name = "ElectronicBandStructureAdapter" if tool_id.endswith("band_structure") else "ElectronicDosAdapter"
    artifacts = create_adapter(adapter_name).execute(_context(tmp_path, tool_id, payload), {"toolId": tool_id, "inputRefs": [{"ref": "input"}], "params": params or {}, "artifactTypes": ["table_json"]})
    return json.loads((tmp_path / artifacts[0].storageKey).read_text(encoding="utf-8"))


def test_registry_has_exact_two_n5_tools_and_ports() -> None:
    registry = load_manifests()
    assert len(registry.tools) == 62
    tools = [item.toolId for item in registry.tools if item.toolId.startswith("electronic.")]
    assert tools == ["electronic.band_structure", "electronic.dos"]
    ports = build_artifact_port_inventory(registry)
    assert ports["electronic.band_structure"].outputPorts[0].contractVersions == ["phase10n5.electronic_band_structure.v1"]
    assert ports["electronic.dos"].outputPorts[0].contractVersions == ["phase10n5.electronic_dos.v1"]


def test_strict_resource_validation_and_compatibility() -> None:
    band, dos = band_resource(), dos_resource()
    assert validate_electronic_band_resource(band).valid
    assert validate_electronic_dos_resource(dos).valid
    assert electronic_band_dos_compatibility(band, dos).valid
    foreign = deepcopy(dos)
    foreign["calculationIdentity"] = "other_calc"
    foreign = _seal(foreign)
    assert electronic_band_dos_compatibility(band, foreign).errors == ("BAND_DOS_SOURCE_MISMATCH",)
    unknown = deepcopy(band)
    unknown["module"] = "os"
    unknown = _seal(unknown)
    assert "ELECTRONIC_RESOURCE_UNSUPPORTED" in validate_electronic_band_resource(unknown).errors


def test_indirect_gap_vbm_cbm_and_source_qualified_classification(tmp_path: Path) -> None:
    result = _execute(tmp_path, "electronic.band_structure", band_resource())
    assert result["schemaVersion"] == "phase10n5.electronic_band_structure.v1"
    assert result["gap"]["valueEv"] == pytest.approx(0.6)
    assert result["gap"]["vbm"]["kpointId"] == "kp_l"
    assert result["gap"]["cbm"]["kpointId"] == "kp_x"
    assert result["gap"]["directness"] == "INDIRECT"
    assert result["gap"]["classification"] == "NONZERO_GAP_UNDER_POLICY"
    assert result["runtimeDiagnostics"]["platformDftExecution"] is False
    assert result["runtimeDiagnostics"]["frontendBandGapRecomputation"] is False


def test_gapless_crossing_is_metal_like_under_policy_not_material_truth(tmp_path: Path) -> None:
    resource = band_resource()
    resource["bands"][1]["energiesEv"] = [-0.1, 0.1, 0.2]
    resource["bands"][1]["occupations"] = [1, 0, 0]
    resource = _seal(resource)
    result = _execute(tmp_path, "electronic.band_structure", resource)
    assert result["gap"]["classification"] == "METAL_LIKE_UNDER_POLICY"
    assert "true" not in " ".join(result["limitations"]).lower()


def test_missing_fermi_preserves_raw_band_but_rejects_fermi_view(tmp_path: Path) -> None:
    resource = band_resource()
    resource.pop("fermiEnergyEv")
    resource = _seal(resource)
    assert _execute(tmp_path, "electronic.band_structure", resource)["gap"]["status"] == "AVAILABLE"
    with pytest.raises(Exception, match="Fermi-referenced"):
        _execute(tmp_path, "electronic.band_structure", resource, {"energy_reference": "fermi"})


def test_dos_preserves_total_partial_projection_and_no_recomputation(tmp_path: Path) -> None:
    result = _execute(tmp_path, "electronic.dos", dos_resource())
    assert result["schemaVersion"] == "phase10n5.electronic_dos.v1"
    assert result["projectionCompleteness"] == "PARTIAL"
    assert result["totalDos"][0]["values"] == [1.0, 0.1, 2.0]
    assert result["projections"][0]["label"] == "s"
    assert result["algorithm"]["projectionSummation"] is False
    assert result["runtimeDiagnostics"]["dosGenerationFromBands"] is False


def test_parser_and_dataprofile_24_are_additive(tmp_path: Path) -> None:
    band_path = tmp_path / "band.json"
    dos_path = tmp_path / "dos.json"
    band_path.write_text(json.dumps(band_resource()), encoding="utf-8")
    dos_path.write_text(json.dumps(dos_resource()), encoding="utf-8")
    parsed = [parse_file(band_path, dataset_id="dataset_n5"), parse_file(dos_path, dataset_id="dataset_n5")]
    assert [result.parse_status for result in parsed] == ["success", "success"]
    profile = build_data_profile(dataset_id="dataset_n5", parse_results=parsed)
    assert profile.profileContractVersion == "2.4"
    assert profile.electronicReadiness is not None
    assert profile.electronicReadiness.electronicBandResourcePresent is True
    assert profile.electronicReadiness.electronicDosResourcePresent is True
    dumped = profile.model_dump(mode="json")
    assert "gap" not in json.dumps(dumped["electronicReadiness"]).lower()


def test_planner_routes_exact_supplied_band_and_dos_resources(tmp_path: Path) -> None:
    band_path, dos_path = tmp_path / "band.json", tmp_path / "dos.json"
    band_path.write_text(json.dumps(band_resource()), encoding="utf-8")
    dos_path.write_text(json.dumps(dos_resource()), encoding="utf-8")
    profile = build_data_profile(dataset_id="dataset_n5", parse_results=[parse_file(band_path, dataset_id="dataset_n5"), parse_file(dos_path, dataset_id="dataset_n5")])
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt="show electronic band structure and DOS together", dataset_id=profile.datasetId, profile_id=profile.profileId, tool_registry_version=registry.version),
        tools=registry.list_mvp_tools(), data_profile=profile,
    )
    assert [step["toolId"] for step in response.raw_json["steps"]] == ["electronic.band_structure", "electronic.dos"]
    assert [step["inputRefs"][0]["ref"] for step in response.raw_json["steps"]] == [profile.electronicReadiness.resources[0].objectId, profile.electronicReadiness.resources[1].objectId]
    assert all(step["inputRefs"][0]["refType"] == "normalized_object" for step in response.raw_json["steps"])


def test_analysis_intent_accepts_profile_24_electronic_readiness(tmp_path: Path) -> None:
    band_path = tmp_path / "band.json"
    band_path.write_text(json.dumps(band_resource()), encoding="utf-8")
    profile = build_data_profile(
        dataset_id="dataset_n5",
        parse_results=[parse_file(band_path, dataset_id="dataset_n5")],
    )
    resource_id = profile.electronicReadiness.resources[0].objectId
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal="show the electronic band structure",
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=(resource_id,),
        ),
        profile=profile,
    )
    assert intent.outcome == AnalysisIntentOutcome.ready
    assert ScientificIntent.electronic_structure_analysis in intent.scientificIntents
    assert CapabilityNeed.electronic_resource in intent.requiredCapabilityNeeds


def test_identity_and_checksum_are_deterministic(tmp_path: Path) -> None:
    first = _execute(tmp_path / "first", "electronic.band_structure", band_resource())
    second = _execute(tmp_path / "second", "electronic.band_structure", band_resource())
    for key in ("bands", "states", "gap", "parameterHash"):
        assert first[key] == second[key]


def test_checked_resource_and_artifact_schemas_are_strict(tmp_path: Path) -> None:
    resource_schema = json.loads(Path("packages/schemas/json/phase10n5-electronic-resources.schema.json").read_text(encoding="utf-8"))
    artifact_schema = json.loads(Path("packages/schemas/json/phase10n5-electronic-artifacts.schema.json").read_text(encoding="utf-8"))
    for tool_id, resource in (("electronic.band_structure", band_resource()), ("electronic.dos", dos_resource())):
        assert list(Draft202012Validator(resource_schema).iter_errors(resource)) == []
        artifact = _execute(tmp_path / tool_id.replace(".", "_"), tool_id, resource)
        assert list(Draft202012Validator(artifact_schema).iter_errors(artifact)) == []
        artifact["unknownAuthority"] = True
        assert list(Draft202012Validator(artifact_schema).iter_errors(artifact))
