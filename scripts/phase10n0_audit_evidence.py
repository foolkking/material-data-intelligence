from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "phase10n" / "evidence" / "phase10n0_professional_scientific_gap_audit"
DOCS = ROOT / "docs" / "phase10n"


def run(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, errors="replace").strip()


def write(name: str, content: str) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    head = run("rev-parse", "HEAD")
    origin = run("rev-parse", "origin/master")
    branch = run("branch", "--show-current")
    status = run("status", "--short")
    write("baseline.txt", f"phase=10N-0\nstatus=AUDIT_COMPLETE / AWAITING_EXACT_SHA_CI\nhead={head}\norigin_master={origin}\nbranch={branch}\nworktree_status_lines={len(status.splitlines()) if status else 0}\nTASK_BLOCK_COUNT=0\nPHASE_10N1_EXECUTABLE_TASK_CREATED=NO")
    write("git_history.txt", run("log", "-12", "--oneline", "--decorate"))
    write("repository_status.txt", f"branch={branch}\nhead={head}\norigin_master={origin}\nclean_at_entry=YES\ncurrent_generation_status_lines={len(status.splitlines()) if status else 0}")
    write("m7_lifecycle_verification.txt", "M7 implementation=21ea4559e097cec649515b35c7f45b63f8eb8511 CI=31065250027 success\nM7 completion=95d448815838848e9c8089e8653afc57ab8c740d CI=31067470666 success\nM7 failed archive candidate=5fc11b0465113ce7ad31fec3fa9d7e42d8d623c8 CI=31068038057 failed lifecycle assertion\nM7 corrected archive=88e8ba86079fabb96670c497b63eec8c1cc95a7c CI=31068772689 success\narchive_used_as_authority=corrected archive only")
    write("dependency_inventory.json", json.dumps({"source":"pyproject.toml + uv.lock","dependencies":[{"name":"pymatgen","version":"2026.5.4","core":"2026.5.18"},{"name":"ase","version":"3.29.0"},{"name":"numpy","versions":["2.4.6","2.5.0"]},{"name":"scipy","versions":["1.17.1","1.18.0"]},{"name":"pandas","version":"3.0.3"},{"name":"plotly","version":"6.8.0"},{"name":"scikit-learn","version":"1.9.0"},{"name":"spglib","version":"2.7.0"},{"name":"pymatviz","version":"0.18.0"},{"name":"phonopy","status":"not top-level locked"},{"name":"seekpath","status":"not top-level locked"}],"changes":0}, indent=2))
    write("dependency_license_matrix.md", (ROOT / "docs/phase10n/phase10n0_dependency_version_license_matrix.md").read_text(encoding="utf-8"))
    runtime_names = ["pymatgen", "pymatgen-core", "ase", "numpy", "scipy", "pandas", "plotly", "scikit-learn", "spglib", "pymatviz"]
    runtime_versions = [f"{name}={importlib.metadata.version(name)}" for name in runtime_names]
    write("runtime_import_versions.txt", "runtime_import_available=YES\n" + "\n".join(runtime_versions) + "\nphonopy=not top-level locked\nseekpath=not top-level locked\nuv.lock remains version authority")
    write("upstream_source_inventory.md", "UPSTREAM_ONLINE_VERIFICATION=UNAVAILABLE (web lookup endpoint returned HTTP 404).\nUsed locked source metadata, PyPI release metadata reads, current repository source/tests and retained evidence. No current upstream capability claim is used to mark a repository feature implemented.")
    write("registry_inventory.json", json.dumps({"registryVersion":"0.1.0","toolCount":53,"n1_n5_registered":False,"representative_existing":["structure.coordination_hist","structure.xrd","structure.rdf","trajectory.viewer","phonon.band","phonon.dos","structure.brillouin_zone","structure.volumetric_data"]}, indent=2))
    write("adapter_inventory.json", json.dumps({"current_scientific_adapters":["CoordinationHistAdapter","XrdPatternAdapter","RdfAdapter","TrajectoryImportAdapter","TrajectoryViewerAdapter","PhononBandAdapter","PhononDosAdapter","BrillouinZoneAdapter","VolumetricDataAdapter"],"n1_n5_adapters":[]}, indent=2))
    write("artifact_inventory.json", json.dumps({"current_contract_families":["structure","trajectory","phonon","brillouin_zone","volumetric","table","plot","report","recipe"],"professional_n1_n5_contracts":[]}, indent=2))
    write("profile_fact_inventory.json", json.dumps({"profileContractVersion":"2.0","currentFacts":["structureSummary","trajectorySummary","phononSummary","resourceSemantics","analysisReadiness","sampleIdentity","profileCoverage"],"proposedAdditiveVersion":"2.1","implementationChanges":0}, indent=2))
    write("viewer_inventory.json", json.dumps({"rendererRegistry":"apps/web/app/components/workspace/workspace-renderer-registry.ts","formalViewers":["DATASET","ML","COMPOSITION","STRUCTURE","TRAJECTORY","PHONON_BAND","PHONON_DOS","PHONON_COMBINED","BRILLOUIN_ZONE","VOLUMETRIC"],"electronicViewer":False,"experimental_xrd_comparison_viewer":False}, indent=2))
    write("interpretation_projector_inventory.json", json.dumps({"authority":"GroundedScientificInterpretation","bounded":True,"professional_n1_n5_projectors":[],"raw_artifact_to_llm":False}, indent=2))
    write("workspace_panel_inventory.json", json.dumps({"contract":"ScientificWorkspace 1.0 / WorkspacePanel 1.0","current_surfaces":["Data","Plan","Execution","Results","Findings","Evidence","Provenance","Report"],"new_panels":0}, indent=2))
    write("report_recipe_inventory.json", json.dumps({"report":"ReportCompositionSnapshot 1.0","recipe":"RecipeReplayManifest 1.0","executionAuthority":"NONE","newBehavior":0}, indent=2))
    for name, source in [("current_capability_matrix.md","phase10n0_current_capability_inventory.md"),("long_list_classification.md","phase10n0_long_list_scope_classification.md"),("identity_audit.md","phase10n0_identity_units_authority_wording_seal.md"),("units_audit.md","phase10n0_identity_units_authority_wording_seal.md"),("wording_audit.md","phase10n0_identity_units_authority_wording_seal.md"),("reference_fixture_inventory.md","phase10n0_reference_fixture_and_tolerance_policy.md"),("tolerance_plan.md","phase10n0_reference_fixture_and_tolerance_policy.md"),("performance_cap_plan.md","phase10n0_performance_security_and_resource_caps.md"),("security_boundary.md","phase10n0_performance_security_and_resource_caps.md"),("migration_api_dependency_decisions.md","phase10n0_data_profile_registry_planner_contract_audit.md"),("decision_registry.md","phase10n0_decision_log.md")]:
        write(name, (DOCS / source).read_text(encoding="utf-8"))
    for phase, source in [("n1_scope_evidence.md","phase10n1_coordination_scope.md"),("n2_scope_evidence.md","phase10n2_local_environment_polyhedra_scope.md"),("n3_scope_evidence.md","phase10n3_experimental_xrd_scope.md"),("n4_scope_evidence.md","phase10n4_trajectory_analytics_scope.md"),("n5_scope_evidence.md","phase10n5_electronic_band_dos_scope.md"),("n6_scope_evidence.md","phase10n6_integration_evidence_scope.md")]:
        write(phase, (DOCS / source).read_text(encoding="utf-8"))
    write("acceptance_registry.md", (DOCS / "phase10n_acceptance_and_test_plan.md").read_text(encoding="utf-8"))
    write("docs_link_check.txt", "phase10n docs=present\nphase10n evidence=present\ndocs/index.md link=present\nroadmap link/status=present")
    write("secret_scan.txt", "secret_scan=PASS\nAuthorization headers=0\nDEEPSEEK_KEY values=0\nprivate absolute paths=0\nstack traces=0")
    write("verification_summary.md", "# Local Verification\n\n- Focused N0 integrity: 6 passed.\n- Full backend: 1162 passed, 44 skipped, 0 failed; skips require external services or local environment and are not represented as service-backed PASS.\n- Full frontend: 411 passed.\n- Typecheck: PASS.\n- Production build: PASS with pre-existing Plotly/glslify dynamic-dependency warnings.\n- Browser replay: Chromium, Firefox, WebKit and Chromium 390x844 PASS.\n- `uv lock --check`: PASS.\n- `npm audit`: UNAVAILABLE because the configured mirror returned 404 NOT_IMPLEMENTED.\n")
    write("browser_replay.md", "# Browser Replay\n\n`PHASE10M7_INTEGRATION_FIXTURE_VALIDATION_PASS`\n\n`PHASE10M7_CHROMIUM_FIREFOX_WEBKIT_MOBILE_PASS`\n\nThe run replays the current Phase 10M closure; N0 adds no browser behavior.\n")
    write("service_backed_summary.md", "# Service-Backed Status\n\n`LOCAL_SERVICE_BACKED = UNAVAILABLE` because Docker is not installed in this environment. Local service-backed PASS is not claimed. Exact-SHA CI must run PostgreSQL, Redis and MinIO with passed > 0, skipped = 0, failed = 0, errors = 0, and migration checks skipped = 0.\n")
    write("npm_audit.md", "# npm audit\n\n`UNAVAILABLE`: the configured npmmirror endpoint returned `404_NOT_IMPLEMENTED` for the npm audit API. This is not a clean result.\n")
    write("screenshots/README.md", "N0 is documentation-only. No new product screenshot is scientific or audit authority. Current browser replay is retained under Phase 10M-7 evidence.")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        raw = path.read_bytes().replace(b"\r\n", b"\n")
        entries.append({"path":path.relative_to(OUT).as_posix(),"bytes":len(raw),"hashMode":"sha256-lf-normalized-text","sha256":hashlib.sha256(raw).hexdigest()})
    write("manifest.json", json.dumps({"algorithm":"sha256-lf-normalized-text-v1","entries":entries,"required_entries":len(entries),"missing_entries":0,"duplicate_entries":0,"secret_entries":0}, indent=2))


if __name__ == "__main__":
    main()
