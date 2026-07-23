from __future__ import annotations

import json
from pathlib import Path

import pytest

from mdi_adapters import ToolExecutionContext, VolumetricDataAdapter
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"


def _execute(root: Path, fixture: str = "LOCPOT", quantity_hint: str = "auto"):
    source = parse_file(FIXTURES / fixture, dataset_id="dataset").objects[0]
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.volumetric_data")
    context = ToolExecutionContext(job_id="job", project_id="project", dataset_id="dataset", tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.1.0", registry_version=registry.version, artifact_root=root, tool_call_id="call", object_store={"volumetric": source}, resource_limits=tool.resourceLimits)
    params = {"format":"auto","quantity_hint":quantity_hint,"field_selection":"all_supported","stored_dtype":"source_or_float64","compression":"contract_default","include_statistics":True,"include_histogram":False,"verify_integrals":True,"allow_partial_dataset":False}
    request = ToolExecutionRequest(jobId="job",stepId="step",toolId=tool.toolId,inputRefs=[{"refType":"normalized_object","ref":"volumetric","objectType":"VolumetricData"}],params=params,artifactTypes=["volumetric_grid_json","volumetric_payload_json","volumetric_field_json","volumetric_dataset_json","volumetric_manifest_json","volumetric_binary","volumetric_structure_overlay_json","summary_md","recipe_json"])
    artifacts = VolumetricDataAdapter().execute(context, request)
    dataset = json.loads((root / next(item.storageKey for item in artifacts if item.name == "volumetric_dataset.json")).read_text(encoding="utf-8"))
    binaries = {item.name:(root/item.storageKey).read_bytes() for item in artifacts if item.type.value == "volumetric_binary"}
    return artifacts, dataset, binaries


def test_locpot_remains_source_defined_local_potential(tmp_path: Path) -> None:
    artifacts, dataset, binaries = _execute(tmp_path)
    assert validate_volumetric_dataset(dataset, binaries).valid
    field = dataset["fields"][0]
    assert field["field_name"] == field["quantity"] == "local_potential"
    assert field["unit"]["source_unit"] == field["unit"]["canonical_unit"] == "electronvolt"
    assert field["normalization_semantics"] == "source_native"
    assert field["integral_semantics"] == "cell_average"
    assert field["potential_reference"] == {"kind":"source_defined","reference_value":0.0,"reference_unit":"electronvolt","shift_applied":False,"shift_amount":0.0,"source_metadata":"No alignment or mean shift was applied."}
    values = decode_volumetric_payload(dataset["payloads"][0], binaries)
    assert sorted(values) == pytest.approx([-1,-.5,0,.5,1,1.5,2,2.5])
    stats = field["statistics"]["stored_components"][0]
    assert stats["mean"] == pytest.approx(.75)
    assert stats["integral"] == pytest.approx(6.0)
    summary = (tmp_path / next(item.storageKey for item in artifacts if item.name == "summary.md")).read_text(encoding="utf-8")
    recipe = json.loads((tmp_path / next(item.storageKey for item in artifacts if item.name == "recipe.json")).read_text(encoding="utf-8"))
    assert "## Potential Reference" in summary
    assert "No vacuum, Fermi, work-function, or absolute-zero reference is inferred." in summary
    assert recipe["scientificContract"]["potentialFields"] == [{"fieldId":field["field_id"],"quantity":"local_potential","unit":"electronvolt","reference":field["potential_reference"]}]


def test_explicit_cube_potential_does_not_change_locpot_semantics(tmp_path: Path) -> None:
    _, dataset, _ = _execute(tmp_path, "orthogonal.cube", "electrostatic_potential")
    assert dataset["fields"][0]["quantity"] == "electrostatic_potential"
    assert dataset["fields"][0]["unit"]["canonical_unit"] == "hartree"
    _, locpot, _ = _execute(tmp_path / "locpot", "LOCPOT", "electrostatic_potential")
    assert locpot["fields"][0]["quantity"] == "local_potential"
    assert "VOLUME_QUANTITY_HINT_CONFLICT" in locpot["warnings"]


def test_planner_routes_potential_product_but_rejects_calculation_claims() -> None:
    registry=load_manifests(); profile=DataProfile.model_validate({"schemaVersion":"0.1","profileId":"p","datasetId":"d","version":"1","datasetType":"volumetric","objects":[{"id":"volumetric","objectType":"VolumetricData"}],"qualityIssues":[],"recommendedTasks":[],"createdAt":"2026-07-22T00:00:00Z"})
    def tool(prompt: str) -> str:
        result=MockLLMProvider().generate_plan(PlannerRequest(user_prompt=prompt,dataset_id="d",profile_id="p",tool_registry_version=registry.version),tools=registry.list_tools(),data_profile=profile).raw_json
        return result["steps"][0]["toolId"] if result and result.get("steps") else ""
    for prompt in ("Visualize the local potential from this LOCPOT","Plot the planar-averaged potential along the third lattice axis","Show equipotential surfaces","Compare the potential at two selected points","显示这个LOCPOT的局域势","把这个LOCPOT设为胞平均零点显示"):
        assert tool(prompt) == "structure.volumetric_data", prompt
    for prompt in ("Calculate the work function and vacuum level","Run VASP to calculate LOCPOT","Align two LOCPOT calculations","Calculate the electric field","做宏观平均","计算费米能级"):
        assert tool(prompt) != "structure.volumetric_data", prompt
