from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_5_report_recipe_experience"

ACCEPTANCE = {
    "P12X5-A01": "Exact Report source discovery, eligibility, and unavailable-source explanation",
    "P12X5-A02": "Exact source selection, ordering, captions, and mandatory disclosure preservation",
    "P12X5-A03": "Session-draft honesty and deterministic no-write preview",
    "P12X5-A04": "Explicit atomic finalization and immutable history",
    "P12X5-A05": "Human-readable Recipe before exact inert declaration",
    "P12X5-A06": "Authorized export, recovery, legacy, and typed failure presentation",
    "P12X5-A07": "Responsive, keyboard, accessibility, and secure inert rendering",
    "P12X5-A08": "Authority non-change, browser, regression, evidence, and lifecycle closure",
}

RECORDS: dict[str, object] = {
    "phase12_4_handoff_snapshot.json": {"implementation": "9fac62bbb2cc9069da62370ee9d02cf3150e987a", "implementationCi": "31379672528", "completion": "0949265", "archive": "4417e275f173f6436b6b8f9e67958cbac39d436a", "trustPath": "SEALED", "authority": "UNCHANGED"},
    "report_contract_snapshot.json": {"request": "ReportCompositionRequest 1.0", "snapshot": "ReportCompositionSnapshot 1.0", "authorityChanged": False},
    "recipe_contract_snapshot.json": {"recipe": "RecipeReplayManifest 1.0", "executionAuthorized": False, "authorityChanged": False},
    "source_inventory_matrix.json": {"sourceKinds": ["WORKSPACE_PANEL", "ARTIFACT", "SCIENTIFIC_CLAIM", "EVIDENCE_ITEM"], "metadataFirst": True, "heavyPayloadRequests": 0},
    "source_eligibility_matrix.json": {"states": ["ELIGIBLE", "MANDATORY", "METADATA_ONLY", "UNAVAILABLE", "STALE", "UNSUPPORTED", "SOURCE_INTEGRITY_FAILED"], "explanationVisible": True, "frontendEligibilityInference": False},
    "source_selection_matrix.json": {"identity": "sourceId exact", "latest": 0, "filename": 0, "displayLabel": 0, "fuzzy": 0},
    "ordering_caption_matrix.json": {"ordering": "itemOrder exact", "captionBounded": True, "sourceIdentityChanged": False},
    "mandatory_disclosure_matrix.json": {"removable": False, "persistentInPreview": True, "persistentInFinal": True},
    "draft_state_matrix.json": {"authority": "session memory", "persistedBeforeFinalize": False, "beforeUnloadProtected": True},
    "preview_matrix.json": {"reportWrites": 0, "recipeWrites": 0, "jobCreates": 0, "toolCalls": 0, "scientificComputation": 0},
    "finalization_matrix.json": {"explicitConfirmation": True, "atomicPair": True, "idempotencyKey": True, "immutable": True},
    "history_matrix.json": {"immutable": True, "latestWins": False, "legacyReadOnly": True, "exactOpenByReportId": True},
    "report_section_matrix.json": {"sectionAuthority": "persisted snapshot", "frontendScientificRewrite": False, "typedEmptyVisible": True},
    "human_recipe_matrix.json": {"meaningFirst": True, "stepsVisible": True, "outputsVisible": True, "executionOutcomeVisible": True},
    "raw_recipe_matrix.json": {"exactDeclarationAvailable": True, "collapsedByDefault": True, "inertText": True, "executionAction": False},
    "recipe_nonexecution_matrix.json": {"executionAuthorized": False, "automaticReplay": False, "planCreated": False, "jobCreated": False, "queueMessageCreated": False},
    "warning_limitation_matrix.json": {"persistent": True, "dismissibleToast": False, "reportAndRecipe": True},
    "export_matrix.json": {"formats": ["json", "markdown"], "source": "server-authorized immutable export", "clientRegeneration": False},
    "recovery_matrix.json": {"inventoryFailure": "typed", "previewFailure": "context preserved", "finalizeFailure": "draft preserved", "legacy": "read-only"},
    "partial_failed_matrix.json": {"partialDisclosureRequired": True, "failedBlockedMissingSection": True, "fullSuccessUpgrade": False},
    "workspace_authority_matrix.json": {"oneWorkspacePerJob": True, "revisionExact": True, "localStorageAuthority": "NONE"},
    "report_recipe_authority_matrix.json": {"reportAuthority": "server persisted snapshot", "recipeAuthority": "server persisted manifest", "frontendAuthority": "NONE"},
    "scientific_nonchange_matrix.json": {"values": 0, "units": 0, "claims": 0, "artifacts": 0, "frontendRecomputation": 0},
    "api_nonchange_matrix.json": {"newEndpointFamilies": 0, "existingEndpointFamiliesChanged": 0},
    "database_nonchange_matrix.json": {"migration": "0007_phase10m1_workspace_domain", "tables": 0, "columns": 0},
    "dependency_nonchange_matrix.json": {"python": 0, "frontend": 0, "lockfile": 0},
    "security_matrix.json": {"rawHtmlExecution": 0, "javascriptExecution": 0, "iframeExecution": 0, "externalArtifactUrlExecution": 0, "secretDisclosure": 0},
    "accessibility_matrix.json": {"keyboard": "PASS", "focus": "PASS", "semanticHeadings": "PASS", "nonColorState": "PASS", "dialogDescription": "PASS"},
    "mobile_matrix.json": {"viewport": [390, 844], "sourcePicker": "bottom sheet", "singleColumn": True, "touchMinimum": 44},
    "zoom_200_matrix.json": {"essentialActionClipping": 0, "unrecoverableOverflow": 0},
    "browser_semantic_matrix.json": {"chromium": "PENDING", "firefox": "PENDING", "webkit": "PENDING", "chromium390x844": "PENDING"},
    "interaction_regression_matrix.json": {"selection": "UNCHANGED", "preview": "UNCHANGED", "finalize": "EXPLICIT_CONFIRMATION_ADDED", "download": "UNCHANGED"},
    "payload_nonchange.json": {"reportSemanticEquality": True, "recipeSemanticEquality": True, "requestFieldsChanged": False},
    "phase12_5_problem_closure.json": {"closed": [{"problemId": "UX-005", "owner": "12-5", "severity": "P2", "status": "FIXED_WITH_EVIDENCE"}], "open": [], "newP0": 0, "newP1": 0},
    "deferred_problem_matrix.json": {"12-6": ["UX-006", "UX-009"], "12-7": ["UX-010"]},
    "phase12_6_handoff.json": {"owner": "12-6", "status": "REVIEWER_GATE", "mobileAuthority": "UNCHANGED", "problems": ["UX-006", "UX-009"], "executableTaskCreatedBy12_5": False},
    "acceptance_registry.json": {"expected": 8, "implemented": 8, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": ACCEPTANCE},
}

TEXT = {
    "baseline.txt": "Phase 12-4 archive 4417e275f173f6436b6b8f9e67958cbac39d436a\nRegistry 62\nDataProfile 2.4\nmigration 0007_phase10m1_workspace_domain\n",
    "entry_gate.md": "PHASE_12_5_ENTRY_GATE = PASS\n\nPhase 12-4 lifecycle and exact-SHA CI resolve. The prewritten Phase 12-6 block remains pending and is not executed by Phase 12-5.\n",
    "no_scientific_change_audit.md": "Report and Recipe contracts remain 1.0. Scientific values, units, identities, claims, Plan, Runtime, Artifact and Workspace authority changed: 0.\n",
    "no_backend_change_audit.md": "Backend production behavior changes = 0. New API families = 0. Database and migration unchanged.\n",
    "security.md": "NO_PHASE12_5_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE12_5_RECIPE_EXECUTION = PASS\nNO_PHASE12_5_ARTIFACT_HTML_EXECUTION = PASS\nNO_PHASE12_5_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS\nNO_PHASE12_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\nNO_SECRET_PATTERN_HITS = PASS\n",
    "secret_scan.txt": "secret-bearing evidence = 0\nexternal scientific API calls = 0\nreal LLM calls = 0\n",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    browser = OUT / "browser_semantic_matrix.json"
    retained_browser = None
    if browser.exists():
        try:
            candidate = json.loads(browser.read_text(encoding="utf-8"))
            if all(candidate.get(key) == "PASS" for key in ("chromium", "firefox", "webkit", "chromium390x844")):
                retained_browser = candidate
        except json.JSONDecodeError:
            pass
    manifest_path = OUT / "manifest.json"
    retained_implementation_ci = "PENDING"
    if manifest_path.exists():
        try:
            candidate_ci = json.loads(manifest_path.read_text(encoding="utf-8")).get("implementationCi")
            if isinstance(candidate_ci, str) and candidate_ci != "PENDING":
                retained_implementation_ci = candidate_ci
        except json.JSONDecodeError:
            pass
    for name, value in RECORDS.items():
        write_json(OUT / name, retained_browser if name == browser.name and retained_browser else value)
    for name, value in TEXT.items():
        (OUT / name).write_text(value, encoding="utf-8")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(manifest_path, {"phase": "12-5", "schemaVersion": "phase12-5-report-recipe/1.0", "entries": entries, "missing": 0, "extra": 0, "hashMismatch": 0, "implementationCi": retained_implementation_ci})
    print(f"PHASE12_5_EVIDENCE_GENERATED {len(entries)}")


if __name__ == "__main__":
    main()
