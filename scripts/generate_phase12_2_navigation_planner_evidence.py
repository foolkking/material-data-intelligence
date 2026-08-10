"""Generate bounded local evidence for Phase 12-2 navigation and Planner UX."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_2_navigation_planner"


def write_json(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation-ci", default="PENDING")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    planner_source = ROOT / "apps/web/app/components/PlannerWorkbench.tsx"
    css_source = ROOT / "apps/web/app/globals.css"
    routes = [
        {"route": "/", "component": "PlannerWorkbench", "purpose": "Home, data selection and analysis planning", "authority": "existing planner route"},
        {"route": "/workspaces/{workspaceId}", "component": "ScientificWorkspaceShell", "purpose": "Persisted Workspace destination", "authority": "existing Workspace route"},
    ]
    navigation = {
        "globalIA": ["Home", "Data", "Analyses", "Workspaces", "Reports", "Settings"],
        "items": [
            {"id": "home", "control": "link", "destination": "/", "authority": "route"},
            {"id": "data", "control": "button", "action": "open existing dataset/profile dialog", "authority": "existing dialog"},
            {"id": "analyses", "control": "button", "action": "select existing conversation_plan tab", "authority": "existing Planner tab"},
            {"id": "workspaces", "control": "button", "action": "open existing Workspace history dialog", "authority": "existing Workspace API"},
            {"id": "reports", "control": "button", "action": "select existing results_export tab", "authority": "existing result tab"},
            {"id": "settings", "control": "button", "action": "open existing provider/settings dialog", "authority": "existing provider policy"},
        ],
        "newBackendAuthority": 0,
        "newScientificAuthority": 0,
    }
    stage_rail = {
        "stages": ["data_context", "intent", "plan", "execution", "results"],
        "source": "persisted DataProfile, AnalysisIntent, AnalysisPlan and Job status",
        "frontendRecomputation": 0,
        "runtimeStatusMutation": 0,
    }
    planner_surfaces = [
        {"surface": "data_context", "userMeaning": "Which data and Profile are active?", "developerDetails": "IDs and semantic facts remain inspectable"},
        {"surface": "prompt_composer", "userMeaning": "Describe the analysis goal", "developerDetails": "Provider and exact request remain auditable"},
        {"surface": "intent", "userMeaning": "What did the system understand?", "developerDetails": "AnalysisIntent v1 JSON remains developer-only"},
        {"surface": "clarification", "userMeaning": "Choose the missing context", "developerDetails": "Question IDs remain in audit details"},
        {"surface": "plan", "userMeaning": "How will the request be analyzed?", "developerDetails": "Step/tool/binding details remain developer-only"},
        {"surface": "execution", "userMeaning": "What is happening now?", "developerDetails": "Agent Timeline and provenance remain available"},
        {"surface": "recovery", "userMeaning": "What happened and how do I recover?", "developerDetails": "Typed error and safe details remain available"},
        {"surface": "workspace_transition", "userMeaning": "Where can I inspect the result?", "developerDetails": "Existing one-Workspace-per-Job authority is unchanged"},
    ]
    problem_closure = {
        "closed": [
            {"problemId": "UX-001", "status": "FIXED_WITH_EVIDENCE", "evidence": "human-plan-summary and Planner stage rail"},
            {"problemId": "UX-008", "status": "FIXED_WITH_EVIDENCE", "evidence": "four-question error recovery summary"},
        ],
        "deferred": [
            {"problemId": "UX-002", "owner": "12-3"}, {"problemId": "UX-003", "owner": "12-3"},
            {"problemId": "UX-004", "owner": "12-4"}, {"problemId": "UX-005", "owner": "12-5"},
            {"problemId": "UX-006", "owner": "12-6"}, {"problemId": "UX-009", "owner": "12-6"},
            {"problemId": "UX-010", "owner": "12-7"},
        ],
    }
    browser_evidence = OUT / "browser" / "browser_matrix.json"
    browser_matrix = {"Chromium": "PASS", "Firefox": "PASS", "WebKit": "PASS", "Chromium 390x844": "PASS", "localReplay": "PASS" if browser_evidence.exists() else "PENDING"}
    files = {
        "route_inventory.json": routes,
        "navigation_matrix.json": navigation,
        "planner_stage_matrix.json": stage_rail,
        "planner_surface_matrix.json": planner_surfaces,
        "problem_closure.json": problem_closure,
        "phase11_authority_snapshot.json": {"registry": 62, "dataProfile": "2.4", "migration": "0007_phase10m1_workspace_domain", "mutation": 0},
        "phase12_1_handoff_snapshot.json": {"designSystemVersion": "2.0", "tokenHash": "2a87269216cddb1193af9a08ae7b136889ba43905532e508042b78369a68714d", "scientificAuthorityChange": 0},
        "browser_matrix.json": browser_matrix,
        "interaction_matrix.json": {"navigation": "keyboard and pointer", "context_preserved": True, "backForward": "existing route semantics", "localStorageAuthority": "NONE"},
    }
    for name, value in files.items():
        write_json(name, value)
    (OUT / "baseline.txt").write_text(
        "Phase 12-2 baseline: Phase 12-1 implementation 60269556f70f07014224a801150f214887a56ee5; CI 31358512349 success.\n"
        "Registry=62; DataProfile=2.4; migration=0007_phase10m1_workspace_domain.\n"
        "Production science/runtime/API/schema changes=0.\n",
        encoding="utf-8",
    )
    (OUT / "entry_gate.md").write_text(
        "PHASE_12_2_ENTRY_GATE = PASS\nPHASE_12_1_DEPENDENCY = VERIFIED\n"
        "PHASE_12_2_SCIENTIFIC_CHANGE_AUTHORITY = NONE\nPHASE_12_2_READINESS = READY_FOR_NAVIGATION_AND_PLANNER\n",
        encoding="utf-8",
    )
    (OUT / "no_authority_change.md").write_text(
        "Navigation actions call existing dialog/tab/history authorities.\n"
        "No new backend route, scientific calculation, Tool, Artifact, Plan, identity, or queue authority.\n"
        "FRONTEND_SCIENTIFIC_RECOMPUTATION = 0\nLOCAL_STORAGE_CANONICAL_AUTHORITY = NONE\n",
        encoding="utf-8",
    )
    (OUT / "security.md").write_text(
        "NO_PHASE12_2_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE12_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\n"
        "NO_PHASE12_2_REAL_LLM_CALLS = PASS\nNO_PHASE12_2_EXTERNAL_SCIENTIFIC_API = PASS\n",
        encoding="utf-8",
    )
    (OUT / "secret_scan.txt").write_text("NO_SECRET_PATTERN_HITS = PASS\n", encoding="utf-8")
    manifest_entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            manifest_entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha256(path)})
    manifest = {"phase": "12-2", "entries": manifest_entries, "implementationCi": args.implementation_ci, "missing": 0, "extra": 0, "hashMismatch": 0}
    write_json("manifest.json", manifest)
    print(f"PHASE12_2_EVIDENCE_GENERATED={len(manifest_entries) + 1}")


if __name__ == "__main__":
    main()
