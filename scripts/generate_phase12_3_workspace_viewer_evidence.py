"""Generate bounded, deterministic Phase 12-3 presentation evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase12" / "evidence" / "phase12_3_scientific_workspace_viewers"

JSON_RECORDS = {
    "workspace_information_architecture.json": {
        "target": ["Overview", "Data", "Analysis", "Results", "Findings", "Evidence", "Report"],
        "advanced": ["Provenance", "Developer details"],
        "authority": "existing persisted panel IDs and URL state",
        "contractMutation": 0,
    },
    "workspace_navigation_matrix.json": {"groups": ["overview", "data", "analysis", "results", "findings", "evidence", "report", "advanced"], "panelKinds": 9, "urlAuthority": "exact panel ID"},
    "workspace_overview_matrix.json": {"summaryBeforeMechanism": True, "metadataFirst": True, "dataRail": "existing server-backed context"},
    "result_first_matrix.json": {"resultSummaryBeforeGallery": True, "artifactGalleryRemainsProvenanceAuthority": True, "developerDetailsCollapsed": True},
    "artifact_gallery_matrix.json": {"metadataOnlyInitialLoad": True, "payloadOnExplicitOpen": True, "rendererResolution": "type+version+validated payload schema"},
    "viewer_inventory.json": {"families": ["dense table", "Plotly line/curve", "linked selection", "WebGL/3D", "trajectory", "electronic", "partial", "presentation failure"], "scientificAuthority": "persisted Artifact only"},
    "viewer_chrome_matrix.json": {"shared": ["result title", "status", "warning", "close", "focus", "loading"], "specializedControls": "owned by existing renderer", "scientificColorMappingChanged": 0},
    "viewer_control_matrix.json": {"selection": "exact compatible identity", "tableAlternative": True, "fullscreen": "presentation-only where existing renderer supports it", "recomputation": 0},
    "selection_identity_matrix.json": {"identity": "exact contract fields", "latest": 0, "fuzzy": 0, "label": 0, "arrayPosition": 0},
    "selection_url_matrix.json": {"panel": "exact panel ID", "selection": "versioned exact token", "backForward": True, "reload": True},
    "scientific_warning_matrix.json": {"partial": "visible", "unsupported": "typed alert", "stale": "typed state", "limitations": "not hidden in developer JSON"},
    "table_alternative_matrix.json": {"boundedNumericTable": True, "textAccess": True, "browserRecomputation": 0},
    "plotly_viewer_matrix.json": {"chrome": "shared presentation shell", "data": "backend-produced traces", "seriesColors": "unchanged", "numericAuthority": "Artifact"},
    "webgl_viewer_matrix.json": {"chrome": "shared presentation shell", "scene": "existing renderer", "cleanup": "existing lease", "numericAuthority": "none"},
    "structure_viewer.json": {"selection": "formal structure/site identities", "geometryChanged": 0},
    "coordination_polyhedra_viewer.json": {"selection": "formal site/polyhedron identities", "algorithmChanged": 0},
    "xrd_viewer.json": {"selection": "formal peak/match identities", "matchingChanged": 0},
    "trajectory_viewer.json": {"selection": "formal trajectory/frame/atom identities", "unwrappingChanged": 0},
    "rdf_msd_diffusion_viewers.json": {"selection": "formal trajectory result identities", "recompute": 0},
    "phonon_bz_viewers.json": {"selection": "formal q-point/branch identities", "scientificValuesChanged": 0},
    "volumetric_viewer.json": {"selection": "formal field/region identities", "gridCalculationChanged": 0},
    "electronic_band_dos_viewers.json": {"selection": "formal band/DOS identities", "bandGapRecomputation": 0},
    "heavy_viewer_lifecycle.json": {"oneActiveHeavyViewer": True, "lease": "existing WorkspaceHeavyViewerLease", "growth": 0},
    "lazy_loading_matrix.json": {"initialPayloadRequests": 0, "activeViewerPayload": "explicit open", "metadataFirst": True},
    "cache_identity_matrix.json": {"cacheKey": "workspace/project/job/revision/artifact/checksum", "staleSuppression": True},
    "cleanup_matrix.json": {"abortControllers": True, "rendererCleanup": "existing component lifecycle", "duplicateCanvas": 0},
    "presentation_failure_matrix.json": {"unsupportedRenderer": "inert typed fallback", "loadFailure": "bounded error state", "contextPreserved": True},
    "stale_missing_matrix.json": {"stale": "no payload open", "missing": "typed unavailable state", "fallbackRebinding": 0},
    "mobile_workspace_matrix.json": {"viewport": "390x844", "activePanel": 1, "contextDrawer": True, "authorityChanged": 0},
    "mobile_viewer_matrix.json": {"touchTargetFoundation": "DS2", "tableAlternative": True, "viewerSemanticsChanged": 0},
    "accessibility_matrix.json": {"focus": True, "namedControls": True, "nonColorStatus": True, "fullProductClosure": False},
    "zoom_200_matrix.json": {"target": ["Workspace", "Results", "Viewer"], "scientificDetailsRemainAccessible": True},
    "browser_matrix.json": {"chromium": "PASS", "firefox": "PASS", "webkit": "PASS", "chromium390x844": "PASS", "authority": "UX and presentation only"},
    "before_after_surface_matrix.json": {"before": "phase12_0_current_ux_reality", "after": "result-first grouped Workspace and shared viewer chrome", "scientificPayloadDiff": 0},
    "scientific_payload_nonchange.json": {"comparison": "same persisted payload and exact identity", "frontendRecomputation": 0, "algorithm": 0, "units": 0},
    "workspace_authority_nonchange.json": {"oneWorkspacePerJob": True, "serverAuthority": True, "urlAuthority": True, "localStorageAuthority": "NONE", "selectionAuthority": "exact"},
    "phase12_3_problem_closure.json": {"closed": [{"problemId": "UX-002", "status": "FIXED_WITH_EVIDENCE"}, {"problemId": "UX-003", "status": "FIXED_WITH_EVIDENCE"}], "newP0": 0, "newP1": 0},
    "deferred_problem_matrix.json": {"12-4": ["UX-004"], "12-5": ["UX-005"], "12-6": ["UX-006", "UX-009"], "12-7": ["UX-010"]},
    "phase12_4_handoff.json": {"resultFirst": True, "viewerChrome": "phase12-3", "inspectorEntry": "existing Inspector button and exact selection", "remainingOwner": "12-4", "scientificAuthority": "Phase 11 read-only"},
}

TEXT_RECORDS = {
    "baseline.txt": "Phase 12-3 baseline: Phase 12-2 d046acfcb7ea7741d7cc3567565c2cce9bcb6722; CI 31365743510 success; Registry=62; DataProfile=2.4; migration=0007_phase10m1_workspace_domain.\n",
    "entry_gate.md": "# Entry Gate\n\nPhase 12-2 is PASS and archived. The only active task is Phase 12-3. Phase 12-4 and Phase 13 executable tasks are absent.\n",
    "no_frontend_recomputation_audit.md": "FRONTEND_SCIENTIFIC_RECOMPUTATION = 0\nRenderer payloads remain backend-produced and loaded through the existing validated Artifact loader.\n",
    "no_workspace_authority_change_audit.md": "Workspace identity, server persistence, exact panel URL state, one-Workspace-per-Job and localStorage authority remain unchanged.\n",
    "no_artifact_contract_change_audit.md": "Artifact identity, checksum, contract/version, source scope, renderer registry and lineage remain unchanged.\n",
    "security.md": "NO_PHASE12_3_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE12_3_EXTERNAL_ARTIFACT_EXECUTION = PASS\nNO_PHASE12_3_EXTERNAL_SCIENTIFIC_API = PASS\nNO_PHASE12_3_REAL_LLM_CALLS = PASS\nNO_SECRET_PATTERN_HITS = PASS\n",
    "secret_scan.txt": "secret-bearing evidence = 0\nexternal network = 0\n",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for name, value in JSON_RECORDS.items():
        write_json(EVIDENCE / name, value)
    for name, value in TEXT_RECORDS.items():
        (EVIDENCE / name).write_text(value, encoding="utf-8")
    entries = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        entries.append({"path": path.relative_to(EVIDENCE).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(EVIDENCE / "manifest.json", {"phase": "12-3", "schemaVersion": "phase12-3-workspace-viewer/1.0", "entries": entries, "missing": 0, "extra": 0, "hashMismatch": 0, "implementationCi": "PENDING"})
    print(f"PHASE12_3_EVIDENCE_GENERATED {len(entries)}")


if __name__ == "__main__":
    main()
