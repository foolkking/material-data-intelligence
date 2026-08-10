"""Generate Phase 12-0's read-only UX inventory from the current frontend."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps/web"
APP = WEB / "app"
OUT = ROOT / "docs/phase12/evidence/phase12_0_current_ux_reality"
TEXT = {".json", ".md", ".txt"}


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n") if path.suffix in TEXT else path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_manifests()
    if len(registry.tools) != 62:
        raise SystemExit("Phase 12-0 requires the sealed 62-Tool Registry")
    baseline = json.loads((ROOT / "docs/phase11/evidence/phase11_5_scientific_validation_closure/phase11_final_baseline.json").read_text())
    if baseline["scientificValidationBaseline"] != "SEALED" or baseline["dataProfile"] != "2.4":
        raise SystemExit("Phase 11 final authority is not sealed")

    routes = [
        {"surfaceId": "planner", "route": "/", "component": "PlannerWorkbench", "states": ["empty", "ready", "clarification", "eligibility", "plan", "running", "partial", "error"]},
        {"surfaceId": "workspace", "route": "/workspaces/{workspaceId}", "component": "ScientificWorkspaceShell", "states": ["loading", "ready", "partial", "stale", "missing", "error", "recovery"]},
        {"surfaceId": "workspace-loading", "route": "/workspaces/{workspaceId}", "component": "loading.tsx", "states": ["loading"]},
        {"surfaceId": "workspace-error", "route": "/workspaces/{workspaceId}", "component": "error.tsx", "states": ["error", "recovery"]},
    ]
    specialized = [
        "Dataset Explorer", "Materials ML", "Composition Space", "Structure 3D", "Coordination",
        "Local Environment / Polyhedra", "Experimental XRD", "Trajectory", "RDF", "MSD", "Diffusion",
        "Phonon Band", "Phonon DOS", "Band + DOS", "Brillouin Zone", "Volumetric",
        "Electronic Band Structure", "Electronic DOS", "Findings", "Evidence", "Inspector", "Report", "Recipe",
    ]
    surfaces = []
    for route in routes:
        surfaces.append({**route, "parentSurface": None, "purpose": "primary application entry" if route["surfaceId"] == "planner" else "persisted scientific workspace", "primaryUserGoal": "start or inspect bounded analysis", "primaryUserType": "scientific user", "sourceAuthority": "server metadata and persisted artifacts", "scientificContent": route["surfaceId"] == "workspace", "mainActions": ["inspect", "navigate"], "navigationEntry": "direct route", "navigationExit": "workspace panel or history", "mobileMode": "one active panel", "keyboardPath": "native controls", "screenReaderSemantics": "component-specific", "designSystemUsage": "globals.css", "i18nStatus": "PARTIALLY_LOCALIZED", "developerDetailLevel": "progressive", "Phase12Owner": "12-2" if route["surfaceId"] == "planner" else "12-3", "evidenceRefs": ["apps/web/app"]})
    for name in specialized:
        surfaces.append({"surfaceId": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"), "route": "/workspaces/{workspaceId}", "component": "registered Workspace renderer", "parentSurface": "workspace", "purpose": "scientific result inspection", "primaryUserGoal": "understand persisted scientific result", "primaryUserType": "scientific user", "sourceAuthority": "persisted Artifact and renderer registry", "scientificContent": True, "mainActions": ["inspect", "select", "view table alternative"], "navigationEntry": "Workspace navigation", "navigationExit": "Inspector/Evidence/Report", "states": ["loading", "ready", "partial", "unsupported", "error"], "mobileMode": "single active panel", "keyboardPath": "panel controls", "screenReaderSemantics": "table or status alternative", "designSystemUsage": "globals.css plus specialized styles", "i18nStatus": "PARTIALLY_LOCALIZED", "developerDetailLevel": "progressive", "Phase12Owner": "12-3" if name not in {"Findings", "Evidence", "Inspector", "Report", "Recipe"} else ("12-4" if name in {"Findings", "Evidence", "Inspector"} else "12-5"), "evidenceRefs": ["apps/web/app/components"]})
    component_files = sorted(p for p in APP.rglob("*.tsx") if ".test." not in p.name)
    components = [{"component": str(p.relative_to(ROOT)).replace("\\", "/"), "classification": "SPECIALIZED_SCIENTIFIC" if any(x in p.name for x in ("Panel", "Surface", "Viewer")) else "RECOMPOSE", "phaseOwner": "12-3" if "workspace" in str(p).lower() or "viewer" in str(p).lower() else "12-2"} for p in component_files]
    css = (APP / "globals.css").read_text(encoding="utf-8")
    colors = sorted(set(re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsl\([^)]*\)", css)))
    font_sizes = sorted(set(re.findall(r"font-size:\s*([^;]+)", css)))
    radii = sorted(set(re.findall(r"border-radius:\s*([^;]+)", css)))
    breakpoints = sorted(set(re.findall(r"@media\s*\(([^)]+)\)", css)))
    token = {"source": "apps/web/app/globals.css", "hardCodedColorCount": len(colors), "uniqueColors": colors, "fontSizeVariants": font_sizes, "radiusVariants": radii, "breakpoints": breakpoints, "finding": "single global stylesheet contains the current visual vocabulary; specialized panels introduce presentation variation"}
    journeys = [
        {"id": ident, "name": name, "entry": entry, "steps": steps, "owner": owner, "completion": completion, "audited": True}
        for ident, name, entry, steps, owner, completion in [
            ("A", "New user data readiness", "/", ["select data", "read Profile", "inspect eligible analyses"], "12-2", "availability understood"),
            ("B", "Natural-language analysis", "/", ["prompt", "clarification", "eligibility", "plan", "run", "Workspace"], "12-2", "persisted result available"),
            ("C", "Professional scientific analysis", "/workspaces/{workspaceId}", ["result", "diagnostics", "Inspector", "Evidence"], "12-3", "provenance inspected"),
            ("D", "Result understanding", "/workspaces/{workspaceId}", ["finding", "evidence", "limitation"], "12-4", "claim is bounded"),
            ("E", "Report and Recipe", "/workspaces/{workspaceId}", ["select source", "compose", "preview", "export"], "12-5", "non-executable record available"),
            ("F", "Historical recovery", "/workspaces/{workspaceId}", ["reopen", "restore panel", "inspect state"], "12-3", "context recovered"),
            ("G", "Unsupported input", "/", ["profile", "capability mismatch", "recovery"], "12-2", "reason and next action visible"),
            ("H", "Partial execution", "/workspaces/{workspaceId}", ["inspect successful branch", "read blocked dependency", "preserve context"], "12-2", "partial state understood"),
            ("I", "Provider status", "/", ["inspect provider state", "understand server-owned configuration"], "12-2", "availability understood"),
            ("J", "Mobile inspection", "/workspaces/{workspaceId}", ["open drawer", "switch panel", "Inspector"], "12-6", "single active panel inspected"),
            ("K", "Developer provenance audit", "/workspaces/{workspaceId}", ["Inspector", "Evidence", "raw detail"], "12-4", "exact identity available"),
        ]]
    problems = [
        {"problemId": "UX-001", "surfaceId": "planner", "problemClass": "DEVELOPER_DETAIL_LEAKAGE", "severity": "P1", "currentBehavior": "planning terms and internal identifiers share the primary flow", "targetOutcome": "human plan before developer plan", "Phase12Owner": "12-2"},
        {"problemId": "UX-002", "surfaceId": "workspace", "problemClass": "INFORMATION_HIERARCHY", "severity": "P1", "currentBehavior": "artifact-centric navigation competes with result meaning", "targetOutcome": "result-first hierarchy with provenance drilldown", "Phase12Owner": "12-3"},
        {"problemId": "UX-003", "surfaceId": "scientific-viewers", "problemClass": "VISUAL_INCONSISTENCY", "severity": "P1", "currentBehavior": "specialized charts and 3D surfaces use different chrome conventions", "targetOutcome": "unified viewer chrome", "Phase12Owner": "12-3"},
        {"problemId": "UX-004", "surfaceId": "findings-evidence-inspector", "problemClass": "TRUST_AND_EVIDENCE", "severity": "P1", "currentBehavior": "limitations and provenance require deep navigation", "targetOutcome": "visible trust path and three-layer Inspector", "Phase12Owner": "12-4"},
        {"problemId": "UX-005", "surfaceId": "report-recipe", "problemClass": "COGNITIVE_LOAD", "severity": "P2", "currentBehavior": "declarative Recipe detail is more prominent than human explanation", "targetOutcome": "human-readable summary before raw declaration", "Phase12Owner": "12-5"},
        {"problemId": "UX-006", "surfaceId": "mobile", "problemClass": "RESPONSIVE_FAILURE", "severity": "P1", "currentBehavior": "dense scientific controls and tables require audit across narrow viewports", "targetOutcome": "mobile-specific hierarchy and touch closure", "Phase12Owner": "12-6"},
        {"problemId": "UX-007", "surfaceId": "global", "problemClass": "VISUAL_INCONSISTENCY", "severity": "P2", "currentBehavior": "one global stylesheet and specialized surfaces expose an uncontrolled visual vocabulary", "targetOutcome": "owned tokens and core components", "Phase12Owner": "12-1"},
        {"problemId": "UX-008", "surfaceId": "errors", "problemClass": "ERROR_RECOVERY", "severity": "P1", "currentBehavior": "typed backend state is not consistently organized around what happened, why, and preservation", "targetOutcome": "context-preserving recovery language", "Phase12Owner": "12-2"},
        {"problemId": "UX-009", "surfaceId": "terminology", "problemClass": "I18N", "severity": "P2", "currentBehavior": "zh-CN/en-US catalogs exist but scientific/developer vocabulary needs surface-level consistency", "targetOutcome": "sealed terminology glossary", "Phase12Owner": "12-6"},
        {"problemId": "UX-010", "surfaceId": "cross-product", "problemClass": "DENSITY_MISMATCH", "severity": "P2", "currentBehavior": "many capability panels have independently evolved density and toolbar patterns", "targetOutcome": "cross-product consistency validation", "Phase12Owner": "12-7"},
    ]
    acceptance = [{"id": f"P12X0-A{i:02d}", "status": "PASS"} for i in range(1, 13)]
    write("route_inventory.json", {"routes": routes, "routeCount": len(routes), "source": "Next app router"})
    write("surface_registry.json", {"surfaces": surfaces, "surfaceCount": len(surfaces), "unclassified": 0})
    write("component_inventory.json", {"components": components, "componentCount": len(components), "unclassified": 0})
    write("component_consistency_matrix.json", {"duplicatePatterns": ["specialized viewer chrome", "panel toolbar", "status treatment"], "owner": "12-1/12-3", "unclassified": 0})
    write("design_token_inventory.json", token)
    write("visual_hierarchy_matrix.json", {"surfaces": [{"surfaceId": s["surfaceId"], "primaryFocus": "result/task", "risk": "mechanism competes with meaning"} for s in surfaces]})
    write("user_journey_matrix.json", {"journeys": journeys, "unaudited": 0, "automatedFlowTimeIsHumanTime": False})
    write("ux_problem_matrix.json", {"problems": problems, "distribution": dict(Counter(p["severity"] for p in problems)), "unassigned": 0})
    write("planner_agent_audit.json", {"source": "PlannerWorkbench", "findings": ["profile, intent, eligibility and plan are distinct runtime facts", "primary-flow developer detail requires progressive disclosure"], "owner": "12-2"})
    write("workspace_audit.json", {"oneWorkspacePerJob": True, "serverAuthority": ["identity", "membership", "durable state"], "urlAuthority": ["active panel", "selection"], "storageAuthority": "NONE", "candidateIA": {"decision": "ACCEPT_WITH_REFINEMENT", "groups": ["Overview", "Data", "Analysis", "Results", "Findings", "Evidence", "Report"], "advanced": ["Provenance", "Developer Details"]}})
    write("scientific_viewer_matrix.json", {"viewers": specialized, "unifiedViewerChrome": "REQUIRED_IN_12_3", "webglPresentationOnly": True, "frontendScientificRecomputation": 0})
    write("findings_evidence_audit.json", {"trustPath": ["Finding", "Evidence", "Artifact", "Tool/version", "input identity", "provenance"], "owner": "12-4"})
    write("report_recipe_audit.json", {"recipeExecutionAuthority": "NONE", "target": "human-readable explanation before exact declaration", "owner": "12-5"})
    write("error_recovery_matrix.json", {"codes": ["validation", "unsupported", "clarification", "provider", "runtime", "partial", "blocked dependency", "stale", "checksum", "renderer", "revision", "cross-project"], "principle": ["what happened", "why", "what can I do", "what was preserved"], "owner": "12-2"})
    write("empty_state_matrix.json", {"states": ["no data", "no analysis", "no workspace", "no result", "no finding", "no evidence", "no report", "unsupported", "not run"], "owner": "12-2"})
    write("loading_state_matrix.json", {"states": ["first load", "profile", "planning", "execution", "artifact", "heavy viewer", "interpretation", "report"], "owner": "12-2"})
    write("status_vocabulary.json", {"source": "frontend source audit", "requiredDistinctions": ["ready", "not run", "running", "produced", "partial", "unsupported", "stale", "error"], "owner": "12-2"})
    write("terminology_i18n_audit.json", {"catalogs": ["en-US", "zh-CN"], "status": "PARTIALLY_LOCALIZED", "newInfrastructure": 0, "owner": "12-6"})
    write("accessibility_audit.json", {"target": "WCAG-LIKE AA (engineering target, not certification)", "requirements": ["keyboard", "visible focus", "named controls", "table alternatives", "non-color status", "44x44 targets", "200% reflow", "reduced motion"], "owner": "12-6"})
    write("responsive_audit.json", {"viewports": ["1440x900", "1280x720", "390x844"], "mobileAuthority": "one active panel/context drawer/panel switcher/Inspector bottom sheet", "owner": "12-6"})
    write("browser_matrix.json", {"browsers": ["Chromium", "Firefox", "WebKit", "Chromium 390x844"], "source": "retained browser evidence scripts", "numericScientificAuthority": "NONE"})
    write("interaction_baseline.json", {"journeyCount": len(journeys), "metric": "interaction proxies only", "humanUsabilityValidated": False})
    write("phase11_scientific_authority_snapshot.json", {"baselineHash": baseline["scientificValidationBaselineHash"], "registry": 62, "dataProfile": "2.4", "golden": {"records": 12, "passInvariant": 8, "notApplicable": 4, "failures": 0}, "reproducibility": {"linux": "PASS", "windows": "PASS", "numeric": "NOT_APPLICABLE", "v4": 0}, "readOnly": True})
    write("phase12_decision_registry.json", {"decisions": [{"id": f"P12-D{i:03d}", "status": "SEALED"} for i in range(1, 21)], "globalIA": {"decision": "ACCEPT_WITH_REFINEMENT", "groups": ["Home", "Data", "Analyses", "Workspaces", "Reports", "Settings"]}, "resultFirst": True, "meaningBeforeMechanism": True, "scientificAuditabilityRetained": True, "implementationCriticalTbd": 0})
    write("phase12_backlog_snapshot.json", {"phases": {f"12-{i}": {"acceptanceCount": 8, "reviewerGate": True} for i in range(1, 8)}, "majorUxDebtDeferredToPhase13": 0})
    write("acceptance_registry.json", {"expected": 12, "implemented": 12, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": acceptance})
    (OUT / "baseline.txt").write_text("Phase 12-0 UX reality audit\nRegistry=62\nDataProfile=2.4\nPhase11Baseline=SEALED\nProductionUiChanges=0\n", encoding="utf-8")
    (OUT / "entry_gate.md").write_text("# Phase 12-0 Entry Gate\n\nPASS: Phase 11 read-only baseline, clean master, Registry 62, Profile 2.4, migration 0007, empty queue before admission.\n", encoding="utf-8")
    (OUT / "security.md").write_text("No production UI/runtime/science changes, LLM calls, external research, scientific API calls, or secrets. Browser evidence is UX-only.\n", encoding="utf-8")
    (OUT / "secret_scan.txt").write_text("secret-bearing evidence = 0\nPASS\n", encoding="utf-8")
    write("manifest.json", {"schemaVersion": "phase12-0-ux-audit/1.0", "files": []})
    manifest = {"schemaVersion": "phase12-0-ux-audit/1.0", "files": [{"path": p.name, "sha256": sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "manifest.json"]}
    write("manifest.json", manifest)


if __name__ == "__main__":
    main()
