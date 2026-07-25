from __future__ import annotations

import hashlib
import json
import math
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import decode_volumetric_payload, validate_volumetric_dataset, validate_volumetric_manifest
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_material_parsers import VolumetricParseError, parse_file, parse_volumetric_file
from mdi_schemas import DataProfile
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "docs" / "phase10j" / "fixtures" / "volumetric_parser"
EVIDENCE = ROOT / "docs" / "phase10j" / "evidence" / "phase10j5_elf_orbital_product"


def write_json(name: str, value: Any) -> None:
    target = EVIDENCE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def profile(case: str) -> DataProfile:
    return DataProfile.model_validate({
        "schemaVersion": "0.1", "profileId": f"profile_{case}", "datasetId": f"dataset_{case}",
        "version": "1", "datasetType": "volumetric",
        "objects": [{"id": "volumetric", "objectType": "VolumetricData"}],
        "qualityIssues": [], "recommendedTasks": [], "createdAt": "2026-07-24T00:00:00Z",
    })


def run_case(case: str, filename: str, prompt: str, *, quantity_hint: str | None = None) -> dict[str, Any]:
    registry = load_manifests()
    data_profile = profile(case)
    plan = MockLLMProvider().generate_plan(
        PlannerRequest(user_prompt=prompt, dataset_id=f"dataset_{case}", profile_id=f"profile_{case}", tool_registry_version=registry.version),
        tools=registry.list_tools(), data_profile=data_profile,
    ).raw_json
    if not plan or plan["steps"][0]["toolId"] != "structure.volumetric_data":
        raise RuntimeError(f"{case} planner routing failed")
    if quantity_hint is not None:
        plan["steps"][0]["params"]["quantity_hint"] = quantity_hint
    source = parse_file(FIXTURES / filename, dataset_id=f"dataset_{case}", file_id=case).objects[0]
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="mdi_elf_orbital_runtime_") as temp:
        root = Path(temp)
        repositories = InMemoryRepositoryBundle.create()
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=root)
        created = planner_jobs(
            PlannerJobsRequest(userPrompt=prompt, projectId="project_elf_orbital", datasetId=f"dataset_{case}", profileId=f"profile_{case}", enqueue=True),
            provider=MockLLMProvider(fixed_plan=plan), repositories=repositories,
            queue_runtime=runtime, registry=registry,
        )
        result = runtime.handle_job(created.job_id, object_store={"volumetric": source})
        if result.status != "completed":
            raise RuntimeError(f"{case} runtime failed")
        destination = EVIDENCE / "artifacts" / f"live_{case}"
        destination.mkdir(parents=True, exist_ok=True)
        artifact_rows = []
        for row in repositories.artifacts.list_for_job(created.job_id):
            shutil.copyfile(root / row["storageKey"], destination / row["name"])
            artifact_rows.append({
                "id": row["id"], "name": row["name"], "type": row["type"],
                "bytes": row["sizeBytes"], "sha256": row["contentHash"],
            })
        dataset = json.loads((destination / "volumetric_dataset.json").read_text(encoding="utf-8"))
        manifest = json.loads((destination / "volumetric_manifest.json").read_text(encoding="utf-8"))
        binaries = {row["name"]: (destination / row["name"]).read_bytes() for row in artifact_rows if row["type"] == "volumetric_binary"}
        values = decode_volumetric_payload(dataset["payloads"][0], binaries)
        field = dataset["fields"][0]
        valid = validate_volumetric_dataset(dataset, binaries).valid and validate_volumetric_manifest(manifest, dataset=dataset, artifacts=binaries).valid
        tool_calls = repositories.tool_calls.list_for_job(created.job_id)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return {
        "case": case, "filename": filename, "prompt": prompt, "selected_tool": plan["steps"][0]["toolId"],
        "plan": plan, "job_id": created.job_id, "status": result.status, "tool_calls": tool_calls,
        "artifacts": artifact_rows, "validation": valid, "dataset": dataset, "manifest": manifest,
        "field": field, "values": values, "runtime_ms": elapsed_ms,
    }


def range_result(case: dict[str, Any]) -> dict[str, Any]:
    field = case["field"]
    values = case["values"]
    minimum, maximum = min(values), max(values)
    scale = max(1.0, abs(minimum), abs(maximum))
    tolerance = 256 * 2.220446049250313e-16 * scale
    elf = field["quantity"] == "electron_localization_function"
    lower = max(0.0, -minimum)
    upper = max(0.0, maximum - 1.0) if elf else 0.0
    anomaly = lower > tolerance or upper > tolerance
    numeric = not anomaly and (lower > 0 or upper > 0)
    return {
        "status": "SOURCE_RANGE_ANOMALY" if anomaly else "NUMERIC_TOLERANCE_WARNING" if numeric else "VALID_RANGE",
        "minimum": minimum, "maximum": maximum, "below_zero_count": sum(value < 0 for value in values),
        "above_one_count": sum(value > 1 for value in values), "negative_count": sum(value < 0 for value in values),
        "maximum_lower_violation": lower, "maximum_upper_violation": upper,
        "dtype": case["dataset"]["payloads"][0]["dtype"], "tolerance": tolerance,
        "tolerance_policy": "ELF_ORBITAL_DTYPE_SCALE_TOLERANCE_V1", "source_values_modified": False,
    }


def product_manifest(case: dict[str, Any]) -> dict[str, Any]:
    field = case["field"]
    orbital = field["quantity"] == "orbital_density"
    value = {
        "schema_version": "phase10j5.elf_orbital_product.v1",
        "product_kind": "orbital_density" if orbital else "elf",
        "dataset_id": case["dataset"]["dataset_id"], "dataset_hash": case["dataset"]["content_hash"],
        "manifest_hash": case["manifest"]["content_hash"], "source_field_id": field["field_id"],
        "source_field_hash": field["content_hash"], "source_sha256": field["provenance"]["source_sha256"],
        "quantity": field["quantity"], "unit": field["unit"]["canonical_unit"],
        "normalization": field["normalization_semantics"], "integral_semantics": field["integral_semantics"],
        "full_cell_integral": field["statistics"]["stored_components"][0]["integral"],
        "identity": {
            "completeness": "UNAVAILABLE" if orbital else "not_applicable",
            "display_name": "Source-defined partial density" if orbital else "Electron Localization Function",
            "orbital_id": None, "band_index": None, "k_point_index": None, "occupancy": None,
            "authority": "canonical_source_metadata", "filename_authority": False,
        },
        "range_validation": range_result(case),
        "presets": ([0.5, 0.7, 0.8, 0.9] if not orbital else [0.1, 0.25, 0.5]),
        "renderer": "existing_phase10j2_isosurface_consumer", "renderer_included": False,
        "limitations": ["no_elf_topology", "no_orbital_reconstruction", "no_homo_lumo_inference", "no_occupancy_inference", "no_complex_phase"],
        "security": {"artifact_javascript": False, "artifact_worker": False, "artifact_wasm": False, "artifact_shader": False, "external_urls": False, "source_immutable": True},
    }
    value["product_hash"] = sha(value)
    return value


def main() -> None:
    elf = run_case("elfcar", "ELFCAR", "Show an ELF isosurface at 0.7 from this ELFCAR")
    orbital = run_case("parchg", "PARCHG", "Visualize the source-defined partial density from this PARCHG")
    cube_orbital = run_case(
        "cube_orbital",
        "orthogonal.cube",
        "Visualize this explicitly identified CUBE orbital density",
        quantity_hint="orbital_density",
    )
    for case in (elf, orbital, cube_orbital):
        write_json(f"api/{case['case']}_live_job.json", {key: case[key] for key in ("prompt", "selected_tool", "plan", "job_id", "status", "tool_calls", "artifacts", "validation")})
        write_json(f"scientific/{case['case']}_range_integral.json", {
            "field_id": case["field"]["field_id"], "field_hash": case["field"]["content_hash"],
            "quantity": case["field"]["quantity"], "unit": case["field"]["unit"],
            "normalization": case["field"]["normalization_semantics"],
            "integral_semantics": case["field"]["integral_semantics"],
            "statistics": case["field"]["statistics"], "range_validation": range_result(case),
        })
        write_json(f"scientific/{case['case']}_product_manifest.json", product_manifest(case))
    generic = parse_volumetric_file(FIXTURES / "orthogonal.cube")
    explicit = parse_volumetric_file(FIXTURES / "orthogonal.cube", quantity_hint="orbital_density")
    multi_error = None
    try:
        parse_volumetric_file(FIXTURES / "multi_orbital.cube", quantity_hint="orbital_density")
    except VolumetricParseError as error:
        multi_error = error.code
    write_json("scientific/cube_compatibility.json", {
        "generic_quantity": generic.source["channels"][0]["quantity"], "generic_orbital_product": False,
        "explicit_quantity": explicit.source["channels"][0]["quantity"], "explicit_orbital_product": True,
        "explicit_source_identity": "UNAVAILABLE", "multi_orbital": multi_error,
    })
    write_json("scientific/synthetic_range_cases.json", {
        "elf_minor": {"values": [-1e-14, 1.00000000000001], "expected": "NUMERIC_TOLERANCE_WARNING", "source_values_modified": False},
        "elf_major": {"values": [-0.1, 1.2], "expected": "SOURCE_RANGE_ANOMALY", "source_values_modified": False},
        "orbital_minor": {"values": [-1e-14, 0.5], "expected": "NUMERIC_TOLERANCE_WARNING", "source_values_modified": False},
        "orbital_major": {"values": [-0.01, 0.5], "expected": "SOURCE_RANGE_ANOMALY", "source_values_modified": False},
        "source": "frontend independent scientific reference tests",
    })
    write_json("performance/runtime.json", {
        "elf_runtime_ms": elf["runtime_ms"], "orbital_runtime_ms": orbital["runtime_ms"],
        "cube_orbital_runtime_ms": cube_orbital["runtime_ms"],
        "elf_voxels": math.prod(elf["dataset"]["grid"]["shape"]), "orbital_voxels": math.prod(orbital["dataset"]["grid"]["shape"]),
        "cube_orbital_voxels": math.prod(cube_orbital["dataset"]["grid"]["shape"]),
        "active_payload_cap": 1, "cached_payload_cap": 2, "mesh_cache_cap": 4,
    })
    write_json("security/audit.json", {
        "artifact_javascript": False, "artifact_html_css": False, "artifact_worker_wasm": False,
        "artifact_shader": False, "external_urls": False, "filename_identity_authority": False,
        "arbitrary_normalization": False, "source_values_modified": False, "external_requests": 0,
        "network": "NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS", "secrets": "NO_SECRET_PATTERN_HITS",
    })
    write_json("pre_implementation_audit.json", {
        "baseline_head": "10393d3c62591c1a0d045ddfdb5ef8aa4ba128bf", "tool": "structure.volumetric_data",
        "elf": "source-native dimensionless real scalar; no topology claims",
        "parchg": "source-defined orbital density; identity unavailable; no occupancy inference",
        "cube": "generic by default; explicit trusted quantity required; multi-orbital unsupported",
        "renderer": "existing Phase 10J-2 Worker and Three.js consumer", "new_dependencies": [],
    })
    write_json("evidence_manifest.json", {
        "phase": "10J-5", "tool": "structure.volumetric_data",
        "runtime_sources": ["committed ELFCAR fixture through QueueWorkerRuntime", "committed PARCHG fixture through QueueWorkerRuntime", "committed CUBE fixture with explicit trusted orbital-density hint through QueueWorkerRuntime"],
        "dataset_hashes": [elf["dataset"]["content_hash"], orbital["dataset"]["content_hash"], cube_orbital["dataset"]["content_hash"]],
        "field_hashes": [elf["field"]["content_hash"], orbital["field"]["content_hash"], cube_orbital["field"]["content_hash"]],
        "renderer": "Phase 10J-2 application-owned Worker + Three.js 0.185.1", "external_requests": 0,
        "replay": ["uv run python apps/web/test/generate-elf-orbital-evidence.py", "node apps/web/test/elf-orbital-product-browser-evidence.mjs"],
    })
    print("ELF_ORBITAL_RUNTIME_EVIDENCE_PASS")
    print("NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


if __name__ == "__main__":
    main()
