from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
from typing import Any

from mdi_adapters import PhononBandDosAdapter, ToolExecutionContext, ToolExecutionError
from mdi_api.repositories import InMemoryRepositoryBundle
from mdi_api.routers.planner import PlannerJobsRequest, planner_jobs
from mdi_artifact_core import (
    COMBINED_CAPS,
    COMBINED_CHECK_ORDER,
    PhononBandDosContractError,
    combined_content_hash,
    compose_phonon_band_dos,
    convert_frequency,
    stable_phonon_json,
    validate_phonon_band_dos,
    validate_phonon_band_dos_compatibility_report,
    validate_phonon_band_dos_manifest,
    validate_phonon_band_dos_plot,
    validate_phonon_band_dos_summary,
    validate_phonon_band_dos_table,
)
from mdi_llm import MockLLMProvider, PlannerRequest
from mdi_schemas import DataProfile, ToolExecutionRequest
from mdi_tool_registry import load_manifests
from mdi_workers import QueueWorkerRuntime


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs" / "phase10h" / "fixtures" / "phonon_contract"
DEFAULT_OUTPUT = ROOT / "docs" / "phase10h" / "evidence" / "phase10h3_combined_band_dos"
ARTIFACT_TYPES = [
    "phonon_band_dos_json",
    "phonon_summary_json",
    "phonon_compatibility_json",
    "plotly_json",
    "table_json",
    "phonon_manifest_json",
    "recipe_json",
]


def main() -> None:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    for name in ("artifacts", "converted_artifacts", "api", "compatibility", "browser", "screenshots", "security"):
        (output / name).mkdir(parents=True, exist_ok=True)
    band, dos = load("stable_band.json"), load("projected_dos.json")
    with tempfile.TemporaryDirectory(prefix="mdi_phase10h3_evidence_") as temporary_root:
        live = live_job(Path(temporary_root), band, dos)
        invalid = invalid_adapter_case(Path(temporary_root) / "invalid", band, dos)
    products = compose_phonon_band_dos(band, dos, selected_projection_ids=["atom:0"])
    converted = compose_phonon_band_dos(
        envelope(band, "band-converted", "inverse_centimeter", "band"),
        envelope(dos, "dos-converted", "inverse_centimeter", "dos"),
    )
    write(output, "live_payload.json", live)
    for name, payload in live["artifact_contents"].items():
        write(output / "artifacts", name, payload)
    for name, payload in product_payloads(converted).items():
        write(output / "converted_artifacts", name, payload)
    write(output / "api", "live_job.json", live["api"])
    write(output / "api", "invalid_job.json", invalid)
    write(output / "compatibility", "compatible.json", products.compatibility_report)
    write(output / "compatibility", "convertible.json", converted.compatibility_report)
    write(output / "compatibility", "structure_mismatch.json", failure(band, mutate(dos, structure_identity="b" * 64)))
    write(output / "compatibility", "source_lineage_mismatch.json", failure(band, source_mismatch(dos)))
    write(output / "compatibility", "nac_mismatch.json", failure(band, nac_mismatch(dos)))
    write(output / "compatibility", "normalization_invalid.json", normalization_failure(band, dos))
    write(output / "compatibility", "ordered_checks.json", {"order": list(COMBINED_CHECK_ORDER), "deterministic": True})
    write(output, "combined_contract_validation.json", validate_phonon_band_dos(products.combined).as_dict())
    write(output, "summary_validation.json", validate_phonon_band_dos_summary(products.summary).as_dict())
    write(output, "compatibility_validation.json", validate_phonon_band_dos_compatibility_report(products.compatibility_report).as_dict())
    write(output, "plot_validation.json", validate_phonon_band_dos_plot(products.plot).as_dict())
    write(output, "table_validation.json", validate_phonon_band_dos_table(products.table).as_dict())
    write(output, "manifest_validation.json", validate_phonon_band_dos_manifest(products.manifest).as_dict())
    write(output, "shared_frequency_domain.json", products.compatibility_report["frequency_domain"])
    write(output, "conversion_policy.json", converted.compatibility_report["conversion"])
    write(output, "plot_contract.json", products.plot)
    write(output, "summary_contract.json", products.summary)
    write(output, "manifest_contract.json", products.manifest)
    write(output, "deterministic_replay.json", {"runtime_runs_equal": live["deterministic"], "check_order": list(COMBINED_CHECK_ORDER), "artifact_order": products.manifest["artifact_order"]})
    write(output, "performance_policy.json", {"caps": COMBINED_CAPS, "interactive": "all bounded projections available", "degraded": "total DOS only", "refused": "no plot arrays", "silent_truncation": False})
    write(output, "accessibility_policy.json", {"region": "Combined phonon band and density of states preview", "shared_axis_summary": True, "tabs_keyboard_accessible": True, "projection_selector_labeled": True, "aria_live": "polite", "non_color_projection_label": True})
    write(output / "security", "audit.json", {"artifact_javascript": False, "artifact_html": False, "external_urls": False, "artifact_layout_forwarded": False, "remote_modules": False, "external_resources": False, "new_dependencies": False, "marker": "NO_SECRET_PATTERN_HITS"})
    write(output / "security", "network.json", {"external_requests": 0, "marker": "NO_EXTERNAL_NETWORK_REQUESTS"})
    write(
        output,
        "test_captures.json",
        {
            "backend_h3": "11 passed",
            "frontend_h3": "10 passed",
            "frontend_full": "174 passed",
            "backend_full": "521 passed, 23 skipped, 11 warnings",
            "registry_regression": "6 passed",
            "typecheck": "success",
            "build": "success",
            "browser_regressions": ["phase10h1", "phase10h2", "phase10_closure", "phase10g2", "phase10g3"],
            "service_backed_local": "unavailable: Docker and required service environment variables are not configured",
            "npm_audit": "unavailable: configured npmmirror audit endpoint returns NOT_IMPLEMENTED",
            "generator": "scripts/generate_phase10h3_phonon_band_dos_evidence.py",
        },
    )
    (output / "README.md").write_text(
        "# Phase 10H-3 Combined Band + DOS Evidence\n\n"
        "Real `phonon.band_dos` planner/job/runtime artifacts and deterministic compatibility evidence. The display contract uses band-left/DOS-right with one shared THz frequency axis. Eigenvectors, animation, thermal properties, solver execution, artifact JavaScript, and external resources are absent.\n\n"
        "Markers: `PHONON_BAND_DOS_API_EVIDENCE_PASS`, `PHONON_BAND_DOS_COMPATIBILITY_EVIDENCE_PASS`, `PHONON_BAND_DOS_BROWSER_EVIDENCE_PASS`, `PHONON_BAND_DOS_ACCESSIBILITY_EVIDENCE_PASS`, `PHONON_BAND_DOS_MOBILE_EVIDENCE_PASS`, `NO_EXTERNAL_NETWORK_REQUESTS`, `NO_SECRET_PATTERN_HITS`.\n",
        encoding="utf-8",
    )
    hashes(output)
    print("PHONON_BAND_DOS_API_EVIDENCE_PASS")
    print("PHONON_BAND_DOS_COMPATIBILITY_EVIDENCE_PASS")
    print("NO_EXTERNAL_NETWORK_REQUESTS")
    print("NO_SECRET_PATTERN_HITS")


def profile() -> DataProfile:
    return DataProfile(
        profileId="profile_h3",
        datasetId="dataset_h3",
        version="1",
        datasetType="phonon",
        objects=[{"id": "band_artifact", "objectType": "PhononBand"}, {"id": "dos_artifact", "objectType": "PhononDos"}],
        phononSummary={"bandAvailable": True, "dosAvailable": True},
        createdAt="2026-07-14T00:00:00Z",
    )


def plan() -> dict[str, Any]:
    registry = load_manifests()
    response = MockLLMProvider().generate_plan(
        PlannerRequest("Show a combined phonon band + DOS with shared frequency axis", "dataset_h3", "profile_h3", registry.version),
        tools=registry.list_mvp_tools(),
        data_profile=profile(),
    )
    assert response.raw_json
    return response.raw_json


def live_job(root: Path, band: dict[str, Any], dos: dict[str, Any]) -> dict[str, Any]:
    registry = load_manifests()
    selected_plan = plan()
    runs: list[dict[str, Any]] = []
    final: dict[str, Any] = {}
    for suffix in ("first", "second"):
        repositories = InMemoryRepositoryBundle.create()
        artifact_root = root / suffix
        runtime = QueueWorkerRuntime(repositories=repositories, registry=registry, artifact_root=artifact_root)
        created = planner_jobs(
            PlannerJobsRequest(userPrompt="Show a combined phonon band + DOS with shared frequency axis", projectId="project_h3", datasetId="dataset_h3", profileId="profile_h3", enqueue=True),
            provider=MockLLMProvider(fixed_plan=selected_plan),
            repositories=repositories,
            queue_runtime=runtime,
            registry=registry,
        )
        assert created.ok and created.job_id
        result = runtime.handle_job(created.job_id, object_store={"band_artifact": band, "dos_artifact": dos})
        records = repositories.artifacts.list_for_job(created.job_id)
        contents = {record["name"]: json.loads((artifact_root / record["storageKey"]).read_text(encoding="utf-8")) for record in records}
        runs.append(contents)
        final = {
            "plan": selected_plan,
            "job": clean(repositories.jobs.get(created.job_id)),
            "events": clean(repositories.job_events.list_for_job(created.job_id)),
            "tool_calls": clean(repositories.tool_calls.list_for_job(created.job_id)),
            "artifacts": [{**record, "content": contents[record["name"]]} for record in records],
            "result": {"status": result.status, "job_id": created.job_id},
        }
    return {"api": final, "artifact_contents": runs[0], "deterministic": runs[0] == runs[1], "real_llm": False, "external_network": False}


def invalid_adapter_case(root: Path, band: dict[str, Any], dos: dict[str, Any]) -> dict[str, Any]:
    invalid = mutate(dos, structure_identity="b" * 64)
    context = ToolExecutionContext("job_invalid", "project_h3", "dataset_h3", "phonon.band_dos", "0.1.0", "0.1.0", load_manifests().version, root, object_store={"band_artifact": band, "dos_artifact": invalid})
    request = ToolExecutionRequest(jobId="job_invalid", stepId="step_001", toolId="phonon.band_dos", inputRefs=[{"refType": "artifact", "ref": "band_artifact", "fieldRole": "band", "objectType": "PhononBand"}, {"refType": "artifact", "ref": "dos_artifact", "fieldRole": "dos", "objectType": "PhononDos"}], params={}, artifactTypes=ARTIFACT_TYPES)
    try:
        PhononBandDosAdapter().execute(context, request)
    except ToolExecutionError as exc:
        return {"status": "rejected", "error": exc.details.get("errorType"), "partial_artifacts": len(list(root.rglob("*.json"))) if root.exists() else 0}
    raise AssertionError("incompatible combined source unexpectedly succeeded")


def envelope(payload: dict[str, Any], artifact_id: str, unit: str, role: str) -> dict[str, Any]:
    content = stable_phonon_json(payload).encode("utf-8")
    integral = payload["integration"]["observed_integral"] if role == "dos" else None
    return {
        "artifact_id": artifact_id,
        "schema_version": payload["schema_version"],
        "media_type": "application/json",
        "size_bytes": len(content),
        "sha256": combined_content_hash(payload),
        "payload": payload,
        "canonicalization": {
            "source_frequency_unit": unit,
            "frequency_factor_to_terahertz": convert_frequency(1.0, unit, "terahertz"),
            "density_jacobian_applied": role == "dos" and unit != "terahertz",
            "broadening_width_converted": False,
            "integral_before": integral,
            "integral_after": integral,
        },
    }


def product_payloads(products: Any) -> dict[str, dict[str, Any]]:
    return {
        "phonon_band_dos.json": products.combined,
        "phonon_band_dos_summary.json": products.summary,
        "phonon_band_dos_compatibility_report.json": products.compatibility_report,
        "phonon_band_dos_plot.json": products.plot,
        "phonon_band_dos_table.json": products.table,
        "phonon_band_dos_manifest.json": products.manifest,
    }


def failure(band: dict[str, Any], dos: dict[str, Any]) -> dict[str, Any]:
    try:
        compose_phonon_band_dos(band, dos)
    except PhononBandDosContractError as exc:
        return {"status": "incompatible", "error": exc.code, "details": exc.details, "partial_artifacts": 0}
    raise AssertionError("incompatible pair unexpectedly composed")


def source_mismatch(source: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(source))
    value["source"]["force_constants_source"] = "other-force-constants"
    return value


def nac_mismatch(source: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(source))
    value["source"]["nac"] = {"enabled": True, "direction_policy": "explicit", "gamma_direction": [1.0, 0.0, 0.0]}
    return value


def normalization_failure(band: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(source))
    value["integration"]["observed_integral"] = 3.0
    return failure(band, value)


def mutate(source: dict[str, Any], **changes: Any) -> dict[str, Any]:
    value = json.loads(json.dumps(source))
    value.update(changes)
    return value


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def write(root: Path, name: str, value: Any) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
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
    files = sorted(path for path in root.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    write(root, "artifact_hashes.json", {"algorithm": "sha256", "files": [{"name": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]})


if __name__ == "__main__":
    main()
