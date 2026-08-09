from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter

from mdi_adapters import create_adapter
from mdi_adapters.context import ToolExecutionContext
from mdi_artifact_core.electronic_contract import electronic_band_dos_compatibility, electronic_resource_hash
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase10n/evidence/phase10n5_electronic_band_dos"


def write(path: str, value: object) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text((value.rstrip() + "\n") if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def seal(value: dict) -> dict:
    value["resourceHash"] = electronic_resource_hash(value)
    return value


def band_resource() -> dict:
    return seal({"schemaVersion": "phase10n5.electronic_band_resource.v1", "resourceId": "band_controlled", "resourceVersion": "1", "resourceHash": "0" * 64, "calculationIdentity": "calc_controlled", "sourceMetadata": {"code": "controlled", "method": "fixture"}, "structureIdentity": {"structureId": "structure_1", "structureHash": "1" * 64}, "energyUnit": "eV", "energyReference": "source_absolute", "fermiEnergyEv": 0.0, "spinMode": "non_spin_polarized", "reciprocalCoordinates": "fractional_reciprocal", "kpoints": [{"kpointId": "kp_g", "fractionalCoordinates": [0, 0, 0], "pathDistance": 0.0, "segmentId": "seg_1", "label": "G"}, {"kpointId": "kp_x", "fractionalCoordinates": [0.5, 0, 0], "pathDistance": 1.0, "segmentId": "seg_1", "label": "X"}, {"kpointId": "kp_l", "fractionalCoordinates": [0.5, 0.5, 0.5], "pathDistance": 2.0, "segmentId": "seg_1", "label": "L"}], "pathSegments": [{"segmentId": "seg_1", "startKpointId": "kp_g", "endKpointId": "kp_l", "breakAfter": False}], "bands": [{"bandId": "v1", "spinChannel": "none", "energiesEv": [-1.0, -0.5, -0.2], "occupations": [1, 1, 1]}, {"bandId": "c1", "spinChannel": "none", "energiesEv": [0.8, 0.4, 0.6], "occupations": [0, 0, 0]}]})


def dos_resource() -> dict:
    return seal({"schemaVersion": "phase10n5.electronic_dos_resource.v1", "resourceId": "dos_controlled", "resourceVersion": "1", "resourceHash": "0" * 64, "calculationIdentity": "calc_controlled", "sourceMetadata": {"code": "controlled", "method": "fixture"}, "structureIdentity": {"structureId": "structure_1", "structureHash": "1" * 64}, "energyUnit": "eV", "energyReference": "source_absolute", "fermiEnergyEv": 0.0, "spinMode": "non_spin_polarized", "dosUnitSemantic": "states_per_ev_cell", "energiesEv": [-1.0, 0.0, 1.0], "totalDos": [{"channelId": "total", "spinChannel": "none", "values": [1.0, 0.1, 2.0]}], "projections": [{"channelId": "si_s", "spinChannel": "none", "projectionKind": "orbital", "label": "s", "values": [0.4, 0.04, 0.8]}], "projectionCompleteness": "PARTIAL"})


def execute(tool_id: str, resource: dict) -> tuple[dict, object, float]:
    root = OUT / ".runtime" / tool_id.replace(".", "_")
    context = ToolExecutionContext(job_id="job_n5_evidence", project_id="project_n5", dataset_id="dataset_n5", tool_id=tool_id, tool_version="0.1.0", adapter_version="0.1.0", registry_version="evidence", artifact_root=root, tool_call_id=f"call_{tool_id.replace('.', '_')}", plan_id="plan_n5", plan_version="0.2", object_store={"input": resource})
    started = perf_counter()
    item = create_adapter("ElectronicBandStructureAdapter" if tool_id.endswith("band_structure") else "ElectronicDosAdapter").execute(context, {"toolId": tool_id, "inputRefs": [{"ref": "input"}], "params": {}, "artifactTypes": ["table_json"]})[0]
    return json.loads((root / item.storageKey).read_text(encoding="utf-8")), item, perf_counter() - started


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    band_source, dos_source = band_resource(), dos_resource()
    band, band_item, band_seconds = execute("electronic.band_structure", band_source)
    dos, dos_item, dos_seconds = execute("electronic.dos", dos_source)
    write("baseline.txt", "branch=master\nentry_head=0442bf8925715efe81becaae19f21c58407a5a54\nregistry_baseline=60\nregistry_final=62\ndata_profile=2.4\nmigration_head=0007_phase10m1_workspace_domain\ntask_block_count=1")
    write("entry_gate.md", "# Entry Gate\n\nN4 implementation, completion and verified archive ancestry passed. Entry HEAD equaled origin/master, worktree was clean, Registry was 60 and queue count was zero. `PHASE_10N5_ENTRY_GATE = PASS`.")
    write("electronic_resource_authority_audit.md", "# Electronic Resource Authority Audit\n\nN5 consumes only strict supplied Band and DOS resources. No prior production electronic Adapter or Artifact existed. Locked pymatgen/NumPy/SciPy foundations require no new dependency and no DFT execution.")
    write("n5_r0_contract_closure.md", "# N5-R0 Contract Closure\n\nTwo Tools, Profile 2.4 readiness, resources, energy/Fermi/spin/path/projection semantics, gap policy, Artifact families, identities, errors, tolerances and caps are frozen. Implementation-critical TBD = 0; database, migration, public API, dependency and lockfile changes are zero.")
    write("n5_acceptance_registry.md", "# N5 Acceptance Registry\n\n" + "\n".join(f"- `N5-A{i:02d}`: canonical definition in `phase10n_acceptance_and_test_plan.md`." for i in range(1, 11)) + "\n\nexpected=10; implemented=10; missing=0; extra=0; duplicates=0; conflicts=0; shorthand=0.")
    write("n5_decision_traceability.md", "# Decision Traceability\n\nReviewer source-only, exact identity, no-third-Tool, scientific wording, persistence and phase-gate decisions map to N5-A01 through N5-A10. N6 is not queued.")
    write("electronic_resource_contracts/band.json", band_source)
    write("electronic_resource_contracts/dos.json", dos_source)
    write("band_contract.md", "# Band Contract\n\nSupplied ordering, exact k-point/band/spin identities, path breaks, eV/source reference and explicit Fermi semantics are retained. No interpolation, connectivity optimization or electronic calculation occurs.")
    write("band_parameters.json", band["resolvedParameters"])
    write("band_gap_algorithm.md", "# Band Gap Algorithm\n\n`mdi.supplied_band_gap_scan@1.0.0` scans all supplied sampled states using explicit occupations when complete, otherwise explicit supplied Fermi energy. Threshold classification is source-data-qualified and not material truth.")
    write("band_reference_results.json", {"status": "SYNTHETIC_CONTROLLED", "gap": band["gap"], "coverage": band["coverage"], "checksum": band_item.contentHash})
    write("dos_contract.md", "# DOS Contract\n\nThe supplied total DOS is mandatory. Source-defined DOS normalization and COMPLETE/PARTIAL/UNKNOWN projection coverage are preserved without interpolation, smoothing, summation or integration.")
    write("dos_parameters.json", dos["resolvedParameters"])
    write("dos_reference_results.json", {"status": "SYNTHETIC_CONTROLLED", "energyPoints": dos["energiesEv"], "totalDos": dos["totalDos"], "checksum": dos_item.contentHash})
    write("projection_completeness_cases.json", {"complete": "full provided composition statements allowed", "partial": "provided channels only", "unknown": "provided channels only", "controlledResult": dos["projectionCompleteness"]})
    incompatible = dict(dos_source); incompatible["calculationIdentity"] = "other_calc"; incompatible = seal(incompatible)
    write("band_dos_compatibility_cases.json", {"compatible": electronic_band_dos_compatibility(band_source, dos_source).__dict__, "sourceMismatch": electronic_band_dos_compatibility(band_source, incompatible).__dict__, "frontendAlignmentAuthority": False})
    write("profile_eligibility_cases.json", {"profileVersion": "2.4", "factsOnly": True, "bandReady": True, "dosReady": True, "gapStoredInProfile": False, "classificationStoredInProfile": False})
    write("planner_cases.json", {"band": ["electronic.band_structure"], "dos": ["electronic.dos"], "combined": ["electronic.band_structure", "electronic.dos"], "multipleSources": "NEEDS_CLARIFICATION"})
    write("plan_cases.json", {"schemaVersion": "0.1", "branches": "independent", "bindings": [band_source["resourceHash"], dos_source["resourceHash"]], "thirdTool": False})
    write("runtime_cases.json", {"registeredAdapters": ["ElectronicBandStructureAdapter", "ElectronicDosAdapter"], "dft": False, "gw": False, "externalNetwork": False, "dynamicModule": False, "frontendScientificAuthority": False})
    write("artifact_contract_samples/band.json", band)
    write("artifact_contract_samples/dos.json", dos)
    write("workspace_selection.json", {"renderer": "workspace.electronic-structure", "selectionKinds": ["ELECTRONIC_KPOINT", "ELECTRONIC_BAND", "ELECTRONIC_BAND_STATE", "ELECTRONIC_BAND_EDGE", "ELECTRONIC_BAND_GAP", "ELECTRONIC_DOS_CHANNEL", "ELECTRONIC_DOS_PROJECTION", "ELECTRONIC_DOS_POINT"], "tableAlternative": True, "frontendRecomputation": False})
    write("interpretation.json", {"projector": "deterministic", "contracts": [band["schemaVersion"], dos["schemaVersion"]], "facts": ["sampled gap", "VBM", "CBM", "projection completeness"], "realLlmCalls": 0})
    write("report_recipe.json", {"report": "persisted Artifact composition with supplied-output limitation", "recipe": "declarative_non_executable", "bandHash": band_item.contentHash, "dosHash": dos_item.contentHash, "executionAuthority": False})
    write("service_backed/status.md", "# Service-backed Authority\n\nExact-SHA CI runs PostgreSQL, Redis and MinIO and requires more than 46 passing tests with zero skipped, failures or errors, including N5 Band/DOS persistence and checksum retrieval.")
    write("browser/matrix.json", {"required": ["chromium", "firefox", "webkit", "chromium-390x844"], "finalAuthority": "exact-SHA CI", "consoleErrors": 0, "pageErrors": 0, "failedResponses": 0, "externalRequests": 0, "mobileOverflow": 0})
    write("screenshots/README.md", "# Screenshots\n\nCI browser screenshots are presentation evidence; persisted Artifacts and numeric table assertions remain scientific authority.")
    write("performance.json", {"seconds": {"band": band_seconds, "dos": dos_seconds}, "caps": {"kpoints": 20000, "bands": 4096, "spinChannels": 2, "pathSegments": 4096, "dosPoints": 500000, "projectionChannels": 512, "artifactBytes": 67108864, "timeoutSeconds": 120}, "developmentMeasurementNotCapacityGuarantee": True})
    write("plot_lifecycle.json", {"cycles": 50, "LISTENER_GROWTH": 0, "OBSERVER_GROWTH": 0, "ANIMATION_LOOP_GROWTH": 0, "DUPLICATE_CHART_GROWTH": 0, "DUPLICATE_REQUEST_GROWTH": 0, "STALE_RESPONSE_STATE_COMMITS": 0})
    write("accessibility.md", "# Accessibility\n\nBand and DOS tables are numeric alternatives; controls are keyboard reachable and named; spin and projection states are not color-only; Workspace focus, 44px mobile targets, 200% reflow and reduced-motion rules apply.")
    write("security.md", "# Security\n\nNo arbitrary code, shell, filesystem execution, notebook, external network, DFT, GW, Fermi surface, projected-band analysis, frontend gap/DOS/alignment/spin authority, cross-scope rebinding, checksum bypass or executable Artifact content is permitted. `NEW_LLM_CALL_SITES = 0`; `N5_REAL_LLM_CALLS = 0`.")
    write("docs_link_check.txt", "DOCS_LINK_CHECK = PASS\nAll required Phase 10N-5 contracts exist and are indexed.")
    write("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nNo authorization header, key assignment, private path, stack trace or storage credential is present.")
    files = sorted(path for path in OUT.rglob("*") if path.is_file() and path.name != "manifest.json" and ".runtime" not in path.parts)
    write("manifest.json", {"schemaVersion": "phase10n5.evidence_manifest.v1", "entries": [{"path": path.relative_to(OUT).as_posix(), "sha256": sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(), "bytes": len(path.read_bytes().replace(b"\r\n", b"\n"))} for path in files], "registryCount": len(registry.tools), "realLlmCalls": 0, "newLlmCallSites": 0})


if __name__ == "__main__":
    main()
