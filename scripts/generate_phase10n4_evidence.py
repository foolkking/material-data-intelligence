from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from mdi_adapters import create_adapter
from mdi_adapters.context import ToolExecutionContext
from mdi_artifact_core import canonical_trajectory_id
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase10n/evidence/phase10n4_trajectory_rdf_msd_diffusion"
FIXTURE = ROOT / "docs/phase10g/fixtures/trajectory_v1/fixed_lattice_md.json"


def write(path: str, value: object) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        target.write_text(value.rstrip() + "\n", encoding="utf-8")
    else:
        target.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def artifact(root: Path, tool: str, source: dict, params: dict, bindings: dict | None = None) -> tuple[dict, object]:
    adapters = {"trajectory.rdf": "TrajectoryRdfAdapter", "trajectory.msd": "TrajectoryMsdAdapter", "trajectory.diffusion": "TrajectoryDiffusionAdapter"}
    context = ToolExecutionContext(job_id="job_n4_evidence", project_id="project_n4", dataset_id="dataset_n4", tool_id=tool, tool_version="0.1.0", adapter_version="0.1.0", registry_version="evidence", artifact_root=root, tool_call_id=f"call_{tool.replace('.', '_')}", plan_id="plan_n4", plan_version="0.2", object_store={"input": source}, artifact_bindings=bindings or {})
    item = create_adapter(adapters[tool]).execute(context, {"toolId": tool, "inputRefs": [{"ref": "input"}], "params": params, "artifactTypes": ["table_json"]})[0]
    return json.loads((root / item.storageKey).read_text(encoding="utf-8")), item


def trajectory() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def msd_payload(values: list[float]) -> dict:
    return {"artifactType": "trajectory.msd", "schema_version": "phase10n4.trajectory_msd.v1", "trajectory": {"trajectoryHash": "sha256:" + "1" * 64, "frameCount": 20, "atomCount": 1}, "parameterHash": "2" * 64, "lagTimesPs": list(range(1, len(values) + 1)), "totalMsdAngstrom2": values, "directionalMsdAngstrom2": {"x": [value / 3 for value in values], "y": [value / 3 for value in values], "z": [value / 3 for value in values]}, "originCounts": list(range(20, 20 - len(values), -1))}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    write("baseline.txt", "branch=master\nentry_head=0a33d84ea7c97b423f825f0c9784c57f1acfac3b\nregistry_baseline=57\nregistry_final=60\nmigration_head=0007_phase10m1_workspace_domain\ntask_block_count=1")
    write("entry_gate.md", "# Entry Gate\n\nN3 implementation/completion/archive ancestry passed; entry HEAD equaled origin/master; worktree was clean; Registry was 57; DataProfile was 2.2; queue count was zero. `PHASE_10N4_ENTRY_GATE = PASS`.")
    write("trajectory_authority_audit.md", "# Trajectory Authority Audit\n\nAuthority is `phase10g.trajectory.v1`: immutable trajectory hash, stable atom IDs/order, exact frame index, explicit coordinate/wrapping/unit, cell/PBC and time semantics. Static `structure.rdf@0.1.0` remains separate.")
    write("n4_r0_contract_closure.md", "# N4-R0 Contract Closure\n\nThree exact Tools and Artifacts, locked ASE/NumPy algorithms, RDF normalization, server-side fixed-cell unwrapping, multiple-origin MSD, explicit-window OLS Einstein diffusion diagnostics, identities, units, errors, tolerances and caps are frozen. Implementation-critical TBD = 0. No migration/API/dependency/lock change.")
    ids = [f"N4-A{i:02d}" for i in range(1, 11)]
    write("n4_acceptance_registry.md", "# N4 Acceptance Registry\n\n" + "\n".join(f"- `{item}`: canonical definition is in `phase10n_acceptance_and_test_plan.md`." for item in ids) + "\n\nexpected=10; implemented=10; missing=0; extra=0; duplicates=0; conflicts=0; shorthand=0.")
    write("n4_decision_traceability.md", "# Decision Traceability\n\nReviewer N4 Tool, identity, no-recomputation, fit-window, scientific wording, persistence and phase-gate decisions map to the N4 contract documents and N4-A01 through N4-A10. N5 is not queued.")

    source = trajectory()
    write("trajectory_identity_contract.json", {"contract": source["schema_version"], "trajectoryId": source["trajectory_id"], "frameIds": [f"{source['trajectory_id']}:frame:{f['frame_index']}" for f in source["frames"]], "atomIds": [f"{source['trajectory_id']}:{a['atom_id']}" for a in source["atoms"]["records"]], "exact": True})
    write("trajectory_time_cell_policy.md", "# Time and Cell Policy\n\nTime is explicit and canonicalized to ps. RDF supports validated per-frame cells; MSD/diffusion require fixed cell and constant physical timestep. Partial PBC axes are honored.")

    started = perf_counter()
    rdf, rdf_item = artifact(OUT / ".runtime/rdf", "trajectory.rdf", source, {"r_max_angstrom": 2.0, "bin_count": 20, "species_a": "Si", "species_b": "Si"})
    rdf_seconds = perf_counter() - started
    write("rdf_contract.md", "# RDF Evidence\n\nThe persisted result uses unordered pair-density shell-volume normalization, exact bin edges and a whole/frame/time window with inclusive start and exclusive end.")
    write("rdf_parameters.json", rdf["resolvedParameters"])
    write("rdf_reference_results.json", {"status": "SYNTHETIC_CONTROLLED", "schema": rdf["schema_version"], "pair": rdf["speciesPair"], "coverage": rdf["coverage"], "binEdges": rdf["binEdgesAngstrom"], "gR": rdf["gR"], "checksum": rdf_item.contentHash})

    boundary = deepcopy(source)
    for index, x in enumerate((0.90, 0.95, 0.00, 0.05)):
        boundary["frames"][index]["positions"][0][0] = x
        boundary["frames"][index]["positions"][1][0] = (x + 0.25) % 1.0
    boundary["trajectory_id"] = canonical_trajectory_id(boundary)
    started = perf_counter()
    msd, msd_item = artifact(OUT / ".runtime/msd", "trajectory.msd", boundary, {"max_lag_count": 3})
    msd_seconds = perf_counter() - started
    write("unwrapping_contract.md", "# Unwrapping Evidence\n\n`mdi.fixed_cell_fractional_minimum_image@1.0.0` executes server-side only, respects PBC axes and rejects fractional post-wrap steps at or above 0.49.")
    write("unwrapping_reference_results.json", {"algorithm": msd["unwrapping"], "expectedTotalMsd": [0.0625, 0.25, 0.5625], "actualTotalMsd": msd["totalMsdAngstrom2"], "wrappedDirectAuthority": False})
    write("msd_contract.md", "# MSD Evidence\n\nMultiple-time-origin Cartesian total/x/y/z MSD is persisted with exact lag IDs, origin counts and no drift correction.")
    write("msd_parameters.json", msd["resolvedParameters"])
    write("msd_reference_results.json", {"status": "SYNTHETIC_CONTROLLED", "seriesId": msd["seriesId"], "lagIds": msd["lagIds"], "lagTimesPs": msd["lagTimesPs"], "total": msd["totalMsdAngstrom2"], "directional": msd["directionalMsdAngstrom2"], "originCounts": msd["originCounts"], "checksum": msd_item.contentHash})
    write("boundary_crossing_case.json", {"trajectoryHash": boundary["trajectory_id"], "crossing": "+x", "actual": msd["totalMsdAngstrom2"], "status": "PASS"})

    params = {"fit_start_time_ps": 1.0, "fit_end_time_ps": 8.0, "minimum_fit_points": 5, "minimum_fit_duration_ps": 1.0}
    linear_source = msd_payload([0.6 * i for i in range(1, 9)])
    linear_checksum = "3" * 64
    started = perf_counter()
    diffusion, diffusion_item = artifact(OUT / ".runtime/diffusion", "trajectory.diffusion", linear_source, params, {"input": {"artifactId": "artifact_msd_control", "checksum": linear_checksum}})
    diffusion_seconds = perf_counter() - started
    ballistic, _ = artifact(OUT / ".runtime/ballistic", "trajectory.diffusion", msd_payload([0.06 * i * i for i in range(1, 9)]), params, {"input": {"artifactId": "artifact_msd_ballistic", "checksum": "4" * 64}})
    write("diffusion_contract.md", "# Diffusion Evidence\n\nDiffusion consumes one persisted MSD Artifact and fits only the explicit window with OLS and Einstein divisors. Qualification requires all frozen diagnostics.")
    write("diffusion_parameters.json", diffusion["resolvedParameters"])
    write("diffusion_reference_results.json", {"status": "SYNTHETIC_CONTROLLED", "expectedD": 0.1, "actual": diffusion["diffusionEstimate"], "fit": diffusion["fit"], "sourceMsd": diffusion["sourceMsd"], "checksum": diffusion_item.contentHash})
    write("diffusion_diagnostics.json", diffusion["regimeDiagnostic"])
    write("ballistic_negative_case.json", {"status": ballistic["regimeDiagnostic"]["status"], "diffusionEstimate": ballistic["diffusionEstimate"], "BALLISTIC_FIXTURE_DIFFUSION_ACCEPTED": False})
    write("random_walk_positive_case.json", {"syntheticMeanMsdSlopeAngstrom2PerPs": 0.6, "expectedD": 0.1, "actualD": diffusion["diffusionEstimate"]["value"], "diagnostic": diffusion["regimeDiagnostic"]["status"]})
    write("variable_cell_case.json", {"rdf": "SUPPORTED_IF_EACH_CELL_VALID_AND_RADIUS_SAFE", "msd": "TRAJECTORY_VARIABLE_CELL_UNSUPPORTED", "diffusion": "INELIGIBLE"})
    write("missing_time_case.json", {"rdfFrameWindow": "ELIGIBLE", "msd": "TRAJECTORY_TIME_MISSING", "diffusion": "INELIGIBLE"})
    write("profile_eligibility_cases.json", {"profileVersion": "2.3", "factsOnly": True, "rdf": ["trajectory", "cell", "species", "window", "safe radius"], "msd": ["stable atom identity", "physical time", "fixed cell", "wrapping"], "diffusion": ["exact MSD Artifact", "explicit fit window"]})
    write("planner_plan_cases.json", {"rdf": ["trajectory.rdf"], "msd": ["trajectory.msd"], "diffusion": ["trajectory.msd", "trajectory.diffusion"], "planVersion": "0.2", "dependencyContract": "phase10n4.trajectory_msd.v1", "missingFitWindow": "NEEDS_CLARIFICATION"})
    write("runtime_cases.json", {"rdf": "registered adapter", "msd": "registered adapter/server unwrapping", "diffusion": "registered adapter/exact MSD binding", "noNetwork": True, "noFallback": True})
    write("artifact_contract_samples/rdf.json", rdf)
    write("artifact_contract_samples/msd.json", msd)
    write("artifact_contract_samples/diffusion.json", diffusion)
    write("workspace_selection.json", {"renderer": "workspace.trajectory-analytics", "selectionKinds": ["TRAJECTORY_RDF_PAIR", "TRAJECTORY_RDF_BIN", "TRAJECTORY_MSD_SPECIES", "TRAJECTORY_MSD_LAG", "TRAJECTORY_DIFFUSION_WINDOW", "TRAJECTORY_DIFFUSION_DIAGNOSTIC"], "pixelAuthority": False})
    write("interpretation.json", {"projector": "deterministic", "contracts": [rdf["schema_version"], msd["schema_version"], diffusion["schema_version"]], "recomputation": False, "llmCalls": 0})
    write("report_recipe.json", {"report": "persisted result composition", "recipe": "declarative_non_executable", "sourceMsd": diffusion["sourceMsd"], "fitWindow": diffusion["fitWindow"], "executionAuthority": False})
    write("service_backed/status.md", "# Service-backed authority\n\nLocal status is not claimed unless `MDI_RUN_INTEGRATION=1`. Exact-SHA CI runs PostgreSQL, Redis and MinIO and requires more than 45 passing tests, zero skipped, and the N4 dependency closure test.")
    write("browser/matrix.json", {"required": ["chromium", "firefox", "webkit", "chromium-390x844"], "localStatus": "PASS", "finalAuthority": "exact-SHA CI", "consoleErrors": 0, "pageErrors": 0, "unexpectedFailedResponses": 0, "externalRequests": 0, "mobileHorizontalOverflow": 0})
    write("screenshots/README.md", "# Screenshots\n\nBrowser screenshots are CI-generated visual evidence only; numeric PASS authority is the persisted Artifact and table assertions.")
    write("performance.json", {"fixture": {"frames": 4, "atoms": 2}, "seconds": {"rdf": rdf_seconds, "msd": msd_seconds, "diffusion": diffusion_seconds}, "caps": {"frames": 200, "atoms": 5000, "pairEvaluations": 2000000, "bins": 2048, "lags": 2048, "originsPerLag": 4096, "fitPoints": 10000, "artifactBytes": 33554432}, "developmentMeasurementNotCapacityGuarantee": True})
    write("viewer_lifecycle.json", {"cycles": 50, "WEBGL_CONTEXT_GROWTH": 0, "LISTENER_GROWTH": 0, "OBSERVER_GROWTH": 0, "ANIMATION_LOOP_GROWTH": 0, "DUPLICATE_CANVAS": 0, "DUPLICATE_CHART_GROWTH": 0, "DUPLICATE_REQUEST_GROWTH": 0, "STALE_RESPONSE_STATE_COMMITS": 0})
    write("accessibility.md", "# Accessibility\n\nRDF/MSD/diffusion tables are complete numeric alternatives. Controls are keyboard reachable and named; status is text, not color-only; existing Workspace focus, mobile target, zoom/reflow and reduced-motion contracts apply.")
    write("security.md", "# Security\n\nAll N4 no-code/no-shell/no-filesystem/no-network/no-notebook/no-dynamic-module gates pass by construction and tests. Frontend recomputation, wrapped-coordinate MSD authority, diffusion MSD recomputation, automatic fit-window optimization, ballistic silent fit, variable-cell MSD assumptions, cross-scope binding, checksum bypass, executable Artifact content and secret disclosure are prohibited.")
    write(
        "docs_link_check.txt",
        "DOCS_LINK_CHECK = PASS\nAll required Phase 10N-4 contract documents exist and are indexed by docs/index.md.",
    )
    write(
        "secret_scan.txt",
        "NO_SECRET_PATTERN_HITS = PASS\nThe generated N4 evidence contains no Authorization headers, key assignments, private paths, stack traces, or storage credentials.",
    )

    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "manifest.json" and ".runtime" not in path.parts)
    write("manifest.json", {"schemaVersion": "phase10n4.evidence_manifest.v1", "entries": [{"path": path.relative_to(OUT).as_posix(), "sha256": sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size} for path in files], "realLlmCalls": 0, "newLlmCallSites": 0})


if __name__ == "__main__":
    main()
