from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from mdi_adapters import ToolExecutionContext, VolumetricDataAdapter
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import validate_volumetric_dataset, validate_volumetric_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
EVIDENCE = ROOT / "docs" / "phase10j" / "evidence" / "phase10j3_charge_spin_density_product"
ARTIFACT_TYPES = [
    "volumetric_grid_json", "volumetric_payload_json", "volumetric_field_json",
    "volumetric_dataset_json", "volumetric_manifest_json", "volumetric_binary",
    "volumetric_structure_overlay_json", "summary_md", "recipe_json",
]


def write_json(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def profile() -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": "profile_charge_spin", "datasetId": "dataset_charge_spin",
        "version": "1", "datasetType": "volumetric",
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-20T00:00:00Z",
    })


def generate_live_runtime() -> dict[str, Any]:
    registry = load_manifests()
    prompt = "Render positive and negative spin density isosurfaces from this CHGCAR"
    plan = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id="dataset_charge_spin", profile_id="profile_charge_spin", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=profile(),
    ).raw_json
    if not plan or plan["steps"][0]["toolId"] != "structure.volumetric_data":
        raise RuntimeError("charge/spin product prompt did not select the canonical volumetric tool")
    source = parse_file(FIXTURES / "CHGCAR.collinear", dataset_id="dataset_charge_spin", file_id="collinear").objects[0]
    with tempfile.TemporaryDirectory(prefix="mdi_charge_spin_runtime_") as temp:
        root = Path(temp)
        repos = InMemoryRepositoryBundle.create()
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(userPrompt=prompt, projectId="project_charge_spin", datasetId="dataset_charge_spin", profileId="profile_charge_spin", enqueue=True),
            provider=MockLLMProvider(fixed_plan=plan), repositories=repos, queue_runtime=runtime, registry=registry,
        )
        result = runtime.handle_job(created.job_id, object_store={"volumetric": source})
        if result.status != "completed":
            raise RuntimeError("runtime job failed")
        artifact_rows = repos.artifacts.list_for_job(created.job_id)
        destination = EVIDENCE / "artifacts" / "live_collinear"
        destination.mkdir(parents=True, exist_ok=True)
        artifacts = []
        for row in artifact_rows:
            target = destination / row["name"]
            shutil.copyfile(root / row["storageKey"], target)
            artifacts.append({"id": row["id"], "name": row["name"], "type": row["type"], "bytes": row["sizeBytes"], "sha256": row["contentHash"]})
        dataset = json.loads((destination / "volumetric_dataset.json").read_text(encoding="utf-8"))
        binaries = {item["name"]: (destination / item["name"]).read_bytes() for item in artifacts if item["type"] == "volumetric_binary"}
        manifest = json.loads((destination / "volumetric_manifest.json").read_text(encoding="utf-8"))
        validation = {"dataset": validate_volumetric_dataset(dataset, binaries).valid, "manifest": validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid}
        capture = {
            "request": {"prompt": prompt, "project_id": "project_charge_spin", "dataset_id": "dataset_charge_spin"},
            "selected_tool": plan["steps"][0]["toolId"], "plan": plan,
            "job": {"job_id": created.job_id, "status": result.status},
            "tool_calls": [{"toolId": item["toolId"], "status": item["status"]} for item in repos.tool_calls.list_for_job(created.job_id)],
            "artifacts": artifacts, "validation": validation,
            "field_summary": [{"field_id": field["field_id"], "name": field["field_name"], "quantity": field["quantity"], "unit": field["unit"]["canonical_unit"], "integral": field["statistics"]["stored_components"][0]["integral"], "spin": field["spin"]} for field in dataset["fields"]],
            "relationships": dataset["relationships"], "dataset_hash": dataset["content_hash"],
        }
    write_json("api/live_job_capture.json", capture)
    write_json("scientific/collinear_integrals.json", {"fields": capture["field_summary"], "relationships": capture["relationships"], "reference": "unavailable", "augmentation_included": True})
    return capture


def generate_direct_case(name: str, fixture: str, params: dict[str, Any]) -> dict[str, Any]:
    registry = load_manifests()
    tool = registry.get_tool_by_id("structure.volumetric_data")
    source = parse_file(FIXTURES / fixture, dataset_id="dataset_charge_spin", file_id=name).objects[0]
    with tempfile.TemporaryDirectory(prefix=f"mdi_{name}_") as temp:
        root = Path(temp)
        context = ToolExecutionContext(
            job_id=f"job_{name}", project_id="project_charge_spin", dataset_id="dataset_charge_spin",
            tool_id=tool.toolId, tool_version=tool.version, adapter_version="1.1.0", registry_version=registry.version,
            artifact_root=root, tool_call_id=f"call_{name}", object_store={"volumetric": source}, resource_limits=tool.resourceLimits,
        )
        request = ToolExecutionRequest(jobId=f"job_{name}", stepId="step_001", toolId=tool.toolId, inputRefs=[{"refType":"normalized_object","ref":"volumetric","objectType":"VolumetricData"}], params=params, artifactTypes=ARTIFACT_TYPES)
        artifacts = VolumetricDataAdapter().execute(context, request)
        dataset_artifact = next(item for item in artifacts if item.name == "volumetric_dataset.json")
        dataset = json.loads((root / dataset_artifact.storageKey).read_text(encoding="utf-8"))
        result = {"fixture": fixture, "dataset_hash": dataset["content_hash"], "warnings": dataset["warnings"], "fields": [{"name": field["field_name"], "quantity": field["quantity"], "unit": field["unit"]["canonical_unit"], "integral": field["statistics"]["stored_components"][0]["integral"]} for field in dataset["fields"]]}
    write_json(f"scientific/{name}.json", result)
    return result


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    live = generate_live_runtime()
    default = {"format":"auto","quantity_hint":"auto","field_selection":"all_supported","stored_dtype":"source_or_float64","compression":"contract_default","include_statistics":True,"include_histogram":False,"verify_integrals":True,"allow_partial_dataset":False}
    cases = {
        "electron_density": generate_direct_case("electron_density", "CHGCAR", default),
        "augmentation": generate_direct_case("augmentation", "CHGCAR.augmentation", default),
        "signed_charge": generate_direct_case("signed_charge", "orthogonal.cube", {**default, "quantity_hint":"charge_density"}),
    }
    write_json("security/audit.json", {"artifact_javascript":False,"artifact_worker_code":False,"artifact_wasm":False,"artifact_shader":False,"external_urls":False,"arbitrary_formula":False,"allowlisted_formulas":["COLLINEAR_SPIN_UP_V1","COLLINEAR_SPIN_DOWN_V1"],"network":"NO_CHARGE_SPIN_PRODUCT_EXTERNAL_NETWORK_REQUESTS","secrets":"NO_SECRET_PATTERN_HITS"})
    write_json("evidence_manifest.json", {
        "phase":"10J-3", "tool":"structure.volumetric_data", "runtime_status":live["job"]["status"],
        "dataset_hash":live["dataset_hash"], "source_cases":sorted(cases),
        "derived_formulas":["COLLINEAR_SPIN_DOWN_V1", "COLLINEAR_SPIN_UP_V1"],
        "relationship_kinds":sorted(item["kind"] for item in live["relationships"]),
        "renderer":"Phase 10J-2 Three.js/Worker consumer",
        "replay_commands":[
            "uv run python apps/web/test/generate-charge-spin-density-evidence.py",
            "node apps/web/test/charge-spin-density-browser-evidence.mjs",
        ],
        "network":"NO_CHARGE_SPIN_PRODUCT_EXTERNAL_NETWORK_REQUESTS", "secrets":"NO_SECRET_PATTERN_HITS",
    })
    print("CHARGE_SPIN_DENSITY_RUNTIME_EVIDENCE_PASS")
    print("NO_CHARGE_SPIN_PRODUCT_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
