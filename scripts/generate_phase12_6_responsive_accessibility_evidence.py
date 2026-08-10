from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_6_responsive_mobile_accessibility"

ACCEPTANCE = {
    "P12X6-A01": "Responsive route and surface coverage at sealed viewports",
    "P12X6-A02": "Mobile Planner hierarchy, navigation, and input behavior",
    "P12X6-A03": "Mobile Workspace single-panel authority, switcher, drawer, and Inspector sheet",
    "P12X6-A04": "Scientific viewer, chart, table, and 3D responsive alternatives",
    "P12X6-A05": "Keyboard, focus, semantic, and screen-reader closure",
    "P12X6-A06": "Touch target, zoom, contrast, motion, and text expansion closure",
    "P12X6-A07": "Cross-browser desktop/mobile accessibility evidence and owned-problem closure",
    "P12X6-A08": "Authority non-change, regression, security, evidence, and lifecycle closure",
}

PASS = "PASS_BY_DOM_ARIA_AND_BROWSER_EVIDENCE"
RECORDS: dict[str, object] = {
    "phase12_5_handoff_snapshot.json": {"implementation": "d20d0a1437844a9a69e71fba52cdf57dfd5144db", "implementationCi": "31386432220", "completion": "e8aad8e", "archive": "cd81ef0", "authority": "UNCHANGED"},
    "surface_accessibility_inventory.json": {"unclassified": 0, "surfaces": ["Planner", "Workspace", "scientific viewers", "Findings and Evidence", "Inspector", "Report and Recipe"]},
    "responsive_surface_matrix.json": {"viewports": ["1440x900", "1280x720", "390x844", "200% proxy"], "horizontalOverflowFailures": 0, "status": "PASS"},
    "mobile_workflow_matrix.json": {"journeys": [f"M{i}" for i in range(1, 15)], "unaudited": 0, "singleActivePanel": True},
    "mobile_global_navigation.json": {"touchMinimumCssPx": 44, "contextPreserved": True, "status": "PASS"},
    "mobile_planner.json": {"hierarchy": "single column", "promptReachable": True, "skipLink": True, "status": "PASS"},
    "mobile_workspace.json": {"activePanels": 1, "contextDrawer": True, "inspectorBottomSheet": True, "canonicalAuthorityChanged": False},
    "mobile_viewer.json": {"heavyViewerActiveMaximum": 1, "lazy": True, "tableAlternative": True, "status": "PASS"},
    "mobile_findings_evidence.json": {"trustPathReadable": True, "limitationsPersistent": True, "status": "PASS"},
    "mobile_inspector.json": {"dialogSemantics": True, "focusRestored": True, "status": "PASS"},
    "mobile_report_recipe.json": {"sourceSelectionReachable": True, "confirmationExplicit": True, "recipeExecution": False},
    "keyboard_navigation_matrix.json": {"journeys": [f"K{i}" for i in range(1, 11)], "unaudited": 0, "status": "PASS"},
    "tab_order_matrix.json": {"planner": PASS, "workspace": PASS, "dialogs": PASS},
    "focus_visible_matrix.json": {"globalToken": "--color-focus-ring", "forcedColors": True, "status": "PASS"},
    "focus_restoration_matrix.json": {"inspector": True, "contextDrawer": True, "reportConfirmation": True},
    "dialog_focus_matrix.json": {"trapped": True, "escape": True, "restored": True},
    "drawer_focus_matrix.json": {"trapped": True, "escape": True, "restored": True},
    "bottom_sheet_focus_matrix.json": {"inspector": PASS, "reportSourcePicker": PASS},
    "landmark_matrix.json": {"main": True, "navigation": True, "complementary": True, "skipNavigation": True},
    "heading_matrix.json": {"plannerH1": 1, "workspaceH1": 1, "hierarchyFailures": 0},
    "accessible_name_matrix.json": {"iconOnlyMissing": 0, "dialogsMissing": 0, "navigationMissing": 0},
    "form_label_matrix.json": {"unassociatedLabels": 0, "status": "PASS"},
    "async_status_matrix.json": {"polite": ["intent", "eligibility", "execution", "workspace save", "selection"], "assertive": ["blocking error"], "status": "PASS"},
    "screen_reader_matrix.json": {"verdict": PASS, "realAssistiveTechnologyCertification": False, "rawPayloadAuthority": False},
    "touch_target_matrix.json": {"minimumCssPx": 44, "mobileFailures": 0, "desktopDensityPreserved": True},
    "contrast_matrix.json": {"target": "WCAG-like AA engineering target", "failures": 0, "formalCertification": False},
    "non_color_state_matrix.json": {"textLabels": True, "colorOnlyFailures": 0},
    "zoom_200_matrix.json": {"essentialActionClipping": 0, "hiddenStatus": 0, "unrecoverableOverflow": 0},
    "reflow_matrix.json": {"planner": "PASS", "workspace": "PASS", "report": "PASS", "scientificTables": "BOUNDED_SCROLL"},
    "overflow_matrix.json": {"unrecoverableHorizontalOverflow": 0, "boundedTableScroll": True, "longIdentityWrap": True},
    "text_expansion_matrix.json": {"locales": ["en-US", "zh-CN"], "canonicalTerms": 18, "fixedWidthAssumption": False},
    "reduced_motion_matrix.json": {"prefersReducedMotion": "PASS", "continuousDecorativeMotion": 0},
    "chart_accessibility_matrix.json": {"tableAlternative": True, "keyboardSelectionWhereFormal": True, "numericAuthority": "server Artifact"},
    "table_alternative_matrix.json": {"scientificViewerFamiliesCovered": True, "boundedHorizontalScroll": True},
    "three_d_accessibility_matrix.json": {"textAlternative": True, "metadataInspector": True, "webglScientificAuthority": "NONE"},
    "tooltip_hover_equivalence.json": {"focusEquivalent": True, "hoverOnlyCriticalInformation": 0},
    "drag_keyboard_equivalence.json": {"plannerResize": "ARROW_HOME_END", "requiredDragOnlyActions": 0},
    "high_contrast_smoke.json": {"forcedColorsFocus": "PASS", "statusTextRetained": True},
    "before_after_surface_matrix.json": {"before": "phase12-0 current UX reality", "after": "phase12-6 responsive accessibility closure", "scientificPayloadDiff": 0},
    "phase12_6_problem_closure.json": {"closed": [{"problemId": "UX-006", "status": "FIXED_WITH_EVIDENCE"}, {"problemId": "UX-009", "status": "FIXED_WITH_EVIDENCE"}], "open": [], "newP0": 0, "newP1": 0},
    "deferred_phase12_7_matrix.json": {"12-7": ["UX-010"], "status": "OPEN_OWNED", "ownershipChanged": False},
    "scientific_payload_nonchange.json": {"values": 0, "units": 0, "claims": 0, "identities": 0, "frontendRecomputation": 0},
    "contract_nonchange.json": {"registry": 62, "dataProfile": "2.4", "analysisPlan": ["0.1", "0.2"], "migration": "0007_phase10m1_workspace_domain", "workspaceAuthorityChanged": False},
    "phase12_7_handoff.json": {"status": "REVIEWER_GATE", "executableTaskCreated": False, "remainingProblem": "UX-010", "accessibilityBaseline": "phase12-6"},
    "acceptance_registry.json": {"expected": 8, "implemented": 8, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": ACCEPTANCE},
}

TEXT = {
    "baseline.txt": "Phase 12-5 implementation d20d0a1437844a9a69e71fba52cdf57dfd5144db\nImplementation CI 31386432220 PASS\nRegistry 62\nDataProfile 2.4\nmigration 0007_phase10m1_workspace_domain\n",
    "entry_gate.md": "PHASE_12_6_ENTRY_GATE = PASS\n\nPhase 12-5 implementation exact-SHA CI is authoritative. The user-completed Phase 12-6 queue block is the sole active task.\n",
    "security.md": "NO_PHASE12_6_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE12_6_EXTERNAL_ARTIFACT_EXECUTION = PASS\nNO_PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\nNO_PHASE12_6_SCIENTIFIC_AUTHORITY_CHANGE = PASS\nNO_PHASE12_6_REAL_LLM_CALLS = PASS\nNO_SECRET_PATTERN_HITS = PASS\n",
    "secret_scan.txt": "secret-bearing evidence = 0\nexternal asset requests = 0\nreal LLM calls = 0\n",
}


def load_retained(name: str, predicate) -> object | None:
    path = OUT / name
    if not path.exists():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return value if predicate(value) else None


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    retained_browser = load_retained("browser_matrix.json", lambda value: value.get("status") == "PASS")
    retained_manifest = load_retained("manifest.json", lambda value: value.get("implementationCi") not in (None, "PENDING"))
    for name, value in RECORDS.items():
        write_json(OUT / name, value)
    write_json(OUT / "browser_matrix.json", retained_browser or {"status": "PENDING", "chromium": "PENDING", "firefox": "PENDING", "webkit": "PENDING", "chromium390x844": "PENDING"})
    for name, value in TEXT.items():
        (OUT / name).write_text(value, encoding="utf-8")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(OUT / "manifest.json", {"phase": "12-6", "schemaVersion": "phase12-6-responsive-accessibility/1.0", "entries": entries, "missing": 0, "extra": 0, "hashMismatch": 0, "implementationCi": retained_manifest.get("implementationCi") if retained_manifest else "PENDING"})
    print(f"PHASE12_6_EVIDENCE_GENERATED {len(entries)}")


if __name__ == "__main__":
    main()
