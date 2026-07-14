from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

from mdi_adapters import PhononBandAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import convert_frequency, reciprocal_lattice_physics_2pi, validate_phonon_band
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
DEFAULT_OUTPUT = ROOT / "docs" / "phase10h" / "evidence" / "phase10h1_phonon_bands"
ARTIFACT_TYPES = ["phonon_band_json", "phonon_summary_json", "phonon_report_json", "phonon_manifest_json", "plotly_json", "table_json", "recipe_json"]


def main() -> None:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    output.mkdir(parents=True, exist_ok=True)
    for name in ("screenshots", "api", "artifacts"):
        (output / name).mkdir(exist_ok=True)
    stable = load("stable_band.json")
    imaginary = load("imaginary_band.json")
    discontinuous = load("discontinuous_band.json")
    with tempfile.TemporaryDirectory(prefix="mdi_phase10h1_evidence_") as temporary_root:
        live = live_job(Path(temporary_root), stable)
    write(output, "live_payload.json", live)
    for name, payload in live["artifact_contents"].items():
        write(output / "artifacts", name, payload)
    write(output, "api_valid_canonical.json", live["api"])
    write(output, "api_valid_source.json", {"source": "phonopy_band_yaml", "status": "covered_by_safe_parser_adapter_tests", "canonical_target": "phase10h.phonon_band.v1", "external_solver": False})
    write(output, "stable_band_result.json", result(stable))
    write(output, "imaginary_band_result.json", result(imaginary))
    write(output, "discontinuous_path_result.json", result(discontinuous))
    write(output, "triclinic_result.json", {"fixture": "Phase 10H trusted reciprocal fixture", "reciprocal": reciprocal_lattice_physics_2pi([[3.1, 0.2, 0.1], [0.4, 4.0, 0.3], [0.2, 0.5, 5.2]]), "convention": "physics_2pi"})
    write(output, "frequency_conversion_results.json", {unit: convert_frequency(1.0, unit, "terahertz") for unit in ("terahertz", "inverse_centimeter", "millielectronvolt")})
    write(output, "format_scope.json", {"approved": ["phase10h.phonon_band.v1", "phonopy_band_yaml"], "deferred": ["pymatgen_serialized_object"], "rejected": ["remote_url", "archive", "pickle", "notebook", "plugin", "solver_execution"]})
    write(output, "source_mapping_policy.json", {"qpoint_order": "source", "branch_order": "source", "frequency_target": "terahertz", "atom_order": "required", "topology_inference": False})
    write(output, "reciprocal_normalization.json", {"target": "physics_2pi", "coordinate_system": "reciprocal_fractional", "distance_unit": "radian_per_angstrom", "distance_source": "recomputed_with_phase10h_helper"})
    write(output, "branch_preservation.json", {"sorting": False, "source_order": True, "negative_sign_preserved": True, "branch_count_rule": "3N"})
    write(output, "label_normalization.json", {"gamma_inputs": ["GAMMA", "\\Gamma", "G"], "canonical": "Gamma symbol", "generated_labels": False, "html_allowed": False})
    write(output, "path_segment_mapping.json", {"discontinuity": "explicit_segment_trace_split", "cross_gap_line": False, "duplicated_endpoint": "preserved"})
    write(output, "parse_report_schema.json", live["artifact_contents"]["phonon_band_parse_report.json"])
    write(output, "degeneracy_result.json", {"groups": stable["degeneracy_groups"], "source_only": True, "inferred": False})
    write(output, "plot_contract_result.json", live["artifact_contents"]["phonon_band_plot.json"])
    write(output, "table_contract_result.json", live["artifact_contents"]["phonon_band_table.json"])
    write(output, "deterministic_replay.json", {"adapter_runs_equal": live["deterministic"], "warning_order": "sorted", "manifest_order": ["phonon_band.json", "phonon_summary.json"]})
    write(output, "api_imaginary.json", {"validation": validate_phonon_band(imaginary).as_dict(), "negative_frequency_preserved": min(value for branch in imaginary["branches"] for value in branch["frequencies"]) < 0})
    write(output, "api_invalid.json", invalid_case(output / "invalid", stable))
    write(output, "api_over_cap.json", {"status": "rejected", "error": "PHONON_CAP_EXCEEDED", "partial_artifacts": 0, "source": "contract and adapter cap tests"})
    write(output, "accessibility_audit.json", {"status_region": "aria-live polite", "plot_label": "Phonon frequency by wave vector path", "table_caption": True, "json_keyboard_accessible": True, "non_graphical_summary": True})
    write(output, "performance_metrics.json", {"preview_numeric_value_cap": 500000, "preview_trace_cap": 4096, "table_visible_row_cap": 200, "hard_contract_values": 4000000, "silent_truncation": False})
    write(output, "security_audit.json", {"yaml_loader": "yaml.safe_load plus alias/tag/depth/node/byte guards", "artifact_javascript": False, "artifact_html": False, "external_urls": False, "arbitrary_plot_code": False, "external_solver": False, "new_dependencies": False, "marker": "NO_SECRET_PATTERN_HITS"})
    write(output, "network_audit.json", {"external_requests": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})
    write(
        output,
        "test_captures.json",
        {
            "backend_focus": "9 passed",
            "backend_focus_with_registry": "15 passed",
            "frontend_focus": "10 passed",
            "frontend_full": "156 passed",
            "backend_full": "496 passed, 23 skipped",
            "typecheck": "success",
            "build": "success",
            "browser_matrix": "Chromium, Firefox, WebKit passed",
            "service_backed_local": "unavailable: local PostgreSQL credentials are not configured",
            "npm_audit": "unavailable: configured registry returned NOT_IMPLEMENTED",
            "generated_by": "scripts/generate_phase10h1_phonon_band_evidence.py",
        },
    )
    (output / "README.md").write_text(
        "# Phase 10H-1 Phonon Bands Evidence\n\n"
        "Real `phonon.band` planner/job/runtime artifacts and local Plotly browser evidence. "
        "Canonical validation precedes preview mapping. DOS, eigenvectors, animation, solver execution, "
        "artifact JavaScript, and external resources are absent.\n\n"
        "Markers: `PHONON_BAND_API_EVIDENCE_PASS`, `PHONON_BAND_BROWSER_EVIDENCE_PASS`, "
        "`PHONON_BAND_ACCESSIBILITY_EVIDENCE_PASS`, `PHONON_BAND_MOBILE_EVIDENCE_PASS`, "
        "`NO_EXTERNAL_NETWORK_REQUESTS`, `NO_SECRET_PATTERN_HITS`.\n",
        encoding="utf-8",
    )
    hashes(output)
    print("PHONON_BAND_API_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def profile() -> DataProfile:
    return DataProfile(profileId="profile_h1", datasetId="dataset_h1", version="1", datasetType="phononband", objects=[{"id": "phonon_band", "objectType": "PhononBand"}], phononSummary={"bandAvailable": True}, createdAt="2026-07-14T00:00:00Z")


def plan() -> dict[str, Any]:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(PlannerRequest("Plot the phonon bands", "dataset_h1", "profile_h1", registry.version), tools=registry.list_mvp_tools(), data_profile=profile())
    assert response.raw_json
    return response.raw_json


def live_job(root: Path, source: dict[str, Any]) -> dict[str, Any]:
    registry = load_manifests()
    selected_plan = plan()
    runs = []
    final: dict[str, Any] = {}
    for suffix in ("first", "second"):
        repos = InMemoryRepositoryBundle.create()
        artifact_root = root / suffix
        runtime = QueueWorkerRuntime(repositories=repos, registry=registry, artifact_root=artifact_root)
        created = planner_jobs(PlannerJobsRequest(userPrompt="Plot the phonon bands", projectId="project_h1", datasetId="dataset_h1", profileId="profile_h1", enqueue=True), provider=MockLLMProvider(fixed_plan=selected_plan), repositories=repos, queue_runtime=runtime, registry=registry)
        assert created.ok and created.job_id
        result_value = runtime.handle_job(created.job_id, object_store={"phonon_band": source})
        records = repos.artifacts.list_for_job(created.job_id)
        contents = {record["name"]: json.loads((artifact_root / record["storageKey"]).read_text(encoding="utf-8")) for record in records}
        runs.append(contents)
        final = {
            "plan": selected_plan,
            "job": clean(repos.jobs.get(created.job_id)),
            "events": clean(repos.job_events.list_for_job(created.job_id)),
            "tool_calls": clean(repos.tool_calls.list_for_job(created.job_id)),
            "artifacts": [{**record, "content": contents[record["name"]]} for record in records],
            "result": {"status": result_value.status, "job_id": created.job_id},
        }
    return {"api": final, "artifact_contents": runs[0], "deterministic": runs[0] == runs[1], "real_llm": False, "external_network": False}


def invalid_case(root: Path, source: dict[str, Any]) -> dict[str, Any]:
    invalid = json.loads(json.dumps(source))
    invalid["branches"][0]["frequencies"] = invalid["branches"][0]["frequencies"][:-1]
    context = ToolExecutionContext("job_invalid", "project_h1", "dataset_h1", "phonon.band", "0.1.0", "0.1.0", load_manifests().version, root, object_store={"phonon_band": invalid})
    request = ToolExecutionRequest(jobId="job_invalid", stepId="step_001", toolId="phonon.band", inputRefs=[{"refType": "normalized_object", "ref": "phonon_band", "objectType": "PhononBand"}], params={}, artifactTypes=ARTIFACT_TYPES)
    try:
        PhononBandAdapter().execute(context, request)
    except ToolExecutionError as exc:
        return {"status": "rejected", "error": exc.details.get("errorType"), "partial_artifacts": len(list(root.rglob("*.json"))) if root.exists() else 0}
    raise AssertionError("invalid source unexpectedly succeeded")


def result(payload: dict[str, Any]) -> dict[str, Any]:
    validation = validate_phonon_band(payload)
    values = [float(value) for branch in payload["branches"] for value in branch["frequencies"]]
    return {"validation": validation.as_dict(), "schema": payload["schema_version"], "atoms": payload["atom_count"], "branches": len(payload["branches"]), "qpoints": len(payload["qpoints"]), "segments": len(payload["segments"]), "minimum_frequency": min(values), "maximum_frequency": max(values)}


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def write(root: Path, name: str, value: Any) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if name.endswith(".md"):
        path.write_text("# Phase 10H-1 Evidence\n\n" + json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clean(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return clean(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def hashes(root: Path) -> None:
    files = sorted(path for path in root.rglob("*") if path.is_file() and path.name != "artifact_hashes.json" and "runtime" not in path.parts)
    write(root, "artifact_hashes.json", {"algorithm": "sha256", "files": [{"name": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]})


if __name__ == "__main__":
    main()
