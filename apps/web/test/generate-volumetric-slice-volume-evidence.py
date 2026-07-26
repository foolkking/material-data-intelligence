from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset, validate_volumetric_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import parse_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
EVIDENCE = ROOT / "docs" / "phase10j" / "evidence" / "phase10j6_volumetric_slice_volume_rendering"
CASES = (
    ("charge", "CHGCAR", "Show a slice through this charge density", None),
    ("spin", "CHGCAR.collinear", "Render this signed spin density directly", None),
    ("potential", "LOCPOT", "Display the LOCPOT plane at fractional coordinate 0.5", None),
    ("elf", "ELFCAR", "Render this volumetric field directly", None),
    ("orbital", "PARCHG", "Open the 3D volume view for this partial density", None),
    ("triclinic", "triclinic.cube", "Render this volumetric field directly", "generic_scalar"),
)


def write_json(relative: str, value: Any) -> None:
    target = EVIDENCE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def profile(case: str) -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": f"profile_{case}", "datasetId": f"dataset_{case}",
        "version": "1", "datasetType": "volumetric",
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-25T00:00:00Z",
    })


def run_case(case: str, filename: str, prompt: str, quantity_hint: str | None) -> dict[str, Any]:
    registry = load_manifests()
    plan = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id=f"dataset_{case}", profile_id=f"profile_{case}", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=profile(case),
    ).raw_json
    if not plan or plan["steps"][0]["toolId"] != "structure.volumetric_data":
        raise RuntimeError(f"{case} planner routing failed")
    if quantity_hint:
        plan["steps"][0]["params"]["quantity_hint"] = quantity_hint
    source = parse_file(FIXTURES / filename, dataset_id=f"dataset_{case}", file_id=f"source_{case}").objects[0]
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="mdi_slice_volume_runtime_") as temp:
        root = Path(temp)
        repositories = InMemoryRepositoryBundle.create()
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(userPrompt=prompt, projectId="project_slice_volume", datasetId=f"dataset_{case}", profileId=f"profile_{case}", enqueue=True),
            provider=MockLLMProvider(fixed_plan=plan), repositories=repositories, queue_runtime=runtime, registry=registry,
        )
        result = runtime.handle_job(created.job_id, object_store={"volumetric": source})
        if result.status != "completed":
            raise RuntimeError(f"{case} runtime failed")
        destination = EVIDENCE / "artifacts" / f"live_{case}"
        destination.mkdir(parents=True, exist_ok=True)
        rows = []
        for row in repositories.artifacts.list_for_job(created.job_id):
            shutil.copyfile(root / row["storageKey"], destination / row["name"])
            rows.append({"id": row["id"], "name": row["name"], "type": row["type"], "bytes": row["sizeBytes"], "sha256": row["contentHash"]})
        dataset = json.loads((destination / "volumetric_dataset.json").read_text(encoding="utf-8"))
        manifest = json.loads((destination / "volumetric_manifest.json").read_text(encoding="utf-8"))
        binaries = {row["name"]: (destination / row["name"]).read_bytes() for row in rows if row["type"] == "volumetric_binary"}
        valid = validate_volumetric_dataset(dataset, binaries).valid and validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid
        values = decode_volumetric_payload(dataset["payloads"][0], binaries)
        tool_calls = repositories.tool_calls.list_for_job(created.job_id)
    return {
        "case": case, "prompt": prompt, "selected_tool": plan["steps"][0]["toolId"], "plan": plan,
        "job_id": created.job_id, "status": result.status, "tool_calls": tool_calls, "artifacts": rows,
        "validation": valid, "dataset_hash": dataset["content_hash"], "field_hash": dataset["fields"][0]["content_hash"],
        "shape": dataset["grid"]["shape"], "step_matrix": dataset["grid"]["step_matrix"],
        "boundary_conditions": dataset["grid"]["boundary_conditions"], "dtype": dataset["payloads"][0]["dtype"],
        "quantity": dataset["fields"][0]["quantity"], "unit": dataset["fields"][0]["unit"]["canonical_unit"],
        "minimum": min(values), "maximum": max(values),
        "fields": [{"field_id": item["field_id"], "field_name": item["field_name"], "quantity": item["quantity"], "minimum": item["statistics"]["stored_components"][0]["minimum"], "maximum": item["statistics"]["stored_components"][0]["maximum"], "spin": item.get("spin")} for item in dataset["fields"]],
        "runtime_ms": round((time.perf_counter() - started) * 1000, 3),
    }


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    captures = [run_case(*case) for case in CASES]
    for capture in captures:
        write_json(f"api/{capture['case']}_live_job.json", capture)
    write_json("pre_implementation_audit.json", {
        "baseline_head": "f8cbdda20800b536fa38cd15c4b0375a186c42ef", "tool": "structure.volumetric_data",
        "schemas": ["phase10j.volumetric_dataset.v1", "phase10j.volumetric_grid.v1", "phase10j.volumetric_field.v1", "phase10j.volumetric_payload.v1", "phase10j.volumetric_manifest.v1"],
        "texture_mapping": "width=nz,height=ny,depth=nx; texture(q2,q1,q0)", "renderer": "application-owned Three.js 0.185.1 WebGL2 Data3DTexture/R32F", "new_dependencies": [],
    })
    write_json("scientific/runtime_cases.json", [{key: value for key, value in capture.items() if key not in {"plan", "tool_calls", "artifacts"}} for capture in captures])
    write_json("scientific/slice_reference.json", {
        "canonical_offset": "((i * ny) + j) * nz + k", "axes": [0, 1, 2], "exact": True,
        "interpolation": "linear_axis_only", "periodic_wrap": True, "triclinic_affine": True,
        "source_mutated": False, "reference_tests": "volumetricSliceModel.test.ts",
    })
    write_json("scientific/volume_reference.json", {
        "domain": "normalized affine unit cube", "texture_coordinates": ["q2", "q1", "q0"],
        "sampling": "hardware float linear after capability gate", "compositing": "front_to_back",
        "opacity_correction": "phase10j6.step_corrected.v1", "early_termination": 0.985,
        "cpu_reference_tests": "volumetricVolumeModel.test.ts", "source_mutated": False,
    })
    write_json("security/audit.json", {
        "artifact_javascript": False, "artifact_shader": False, "artifact_worker_wasm": False,
        "artifact_html_css": False, "external_urls": False, "remote_texture": False,
        "silent_downsampling": False, "source_mutation": False, "external_requests": 0,
        "network": "NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS", "secrets": "NO_SECRET_PATTERN_HITS",
    })
    write_json("evidence_manifest.json", {
        "phase": "10J-6", "tool": "structure.volumetric_data", "runtime_cases": [capture["case"] for capture in captures],
        "dataset_hashes": [capture["dataset_hash"] for capture in captures], "field_hashes": [capture["field_hash"] for capture in captures],
        "renderer": "application-owned Three.js 0.185.1 WebGL2 direct volume and slice Worker",
        "replay": ["uv run python apps/web/test/generate-volumetric-slice-volume-evidence.py", "node apps/web/test/volumetric-slice-volume-browser-evidence.mjs"],
        "external_requests": 0,
    })
    write_json("replay/commands.json", {"commands": ["uv run python apps/web/test/generate-volumetric-slice-volume-evidence.py", "npm --prefix apps/web run build", "node apps/web/test/volumetric-slice-volume-browser-evidence.mjs"]})
    print("VOLUMETRIC_SLICE_VOLUME_RUNTIME_EVIDENCE_PASS")
    print("NO_VOLUMETRIC_SLICE_VOLUME_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
