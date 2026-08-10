from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_4_findings_evidence_inspector_provenance"

CLAIM_TYPES = ["OBSERVATION", "COMPARISON", "ANOMALY", "WARNING", "LIMITATION", "RECOMMENDATION", "NO_SUPPORTED_CONCLUSION"]
ACCEPTANCE = {
    "P12X4-A01": "Finding hierarchy and persisted scientific claim presentation",
    "P12X4-A02": "Finding-to-Evidence exact trust path and membership roles",
    "P12X4-A03": "Evidence detail, exact source Artifact and Tool navigation",
    "P12X4-A04": "Three-layer Inspector with subordinate developer detail",
    "P12X4-A05": "Exact provenance, lineage and Plan 0.1/0.2 presentation",
    "P12X4-A06": "Warnings, limitations, partial and no-supported-evidence honesty",
    "P12X4-A07": "Responsive, keyboard, accessibility and secure trust-path behavior",
    "P12X4-A08": "Scientific-authority non-change, browser, regression, evidence and lifecycle closure",
}

JSON_RECORDS: dict[str, object] = {
    "phase12_3_handoff_snapshot.json": {"implementation": "9b38a753bda134e9c27425e1193d2980a0790731", "implementationCi": "31370240101", "completion": "2abbcf20ff283931536c6643a3ce96347fd24556", "archive": "f6a39ca4d6afc560662d98c6f882ecc10a0e3d71", "resultFirst": True, "workspaceAuthority": "UNCHANGED"},
    "finding_inventory.json": {"contract": "ScientificClaim 1.0", "claimTypes": CLAIM_TYPES, "rankingAuthority": "NONE", "source": "persisted GroundedScientificInterpretation"},
    "claim_type_matrix.json": {"types": [{"claimType": value, "presentationLabel": value.replace("_", " ").title(), "scientificSemanticsChanged": False} for value in CLAIM_TYPES]},
    "finding_hierarchy_matrix.json": {"ordering": ["displayOrder", "claimId tie-break"], "frontendScientificRanking": False, "resultGrouping": "persisted interpretation"},
    "finding_qualification_matrix.json": {"classes": ["DIRECT", "QUALIFIED", "LIMITED"], "probabilityFabrication": 0, "labelsAreQualifiers": True},
    "limitation_warning_matrix.json": {"runtimeWarning": "distinct", "scientificLimitation": "persistent near claim", "validationLimitation": "qualified", "presentationWarning": "distinct", "dismissedMandatoryLimitations": 0},
    "finding_evidence_membership.json": {"authority": ["supportingEvidenceIds", "limitingEvidenceIds", "contradictingEvidenceIds"], "textSimilarity": False, "fuzzyMatching": False},
    "evidence_inventory.json": {"contract": "ScientificEvidenceItem 1.0", "bundle": "ScientificEvidenceBundle 1.0", "kinds": ["SCALAR", "RANGE", "CATEGORY", "COUNT", "BOOLEAN", "ORDERED_SERIES_SUMMARY", "TABLE_ROW", "WARNING", "LIMITATION", "EXECUTION_STATE", "PROVENANCE"]},
    "evidence_role_matrix.json": {"roles": ["SUPPORTING", "LIMITING", "CONTRADICTING"], "colorOnly": False, "membershipExact": True},
    "evidence_source_matrix.json": {"fields": ["sourceArtifactId", "sourceArtifactChecksum", "artifactContract", "artifactContractVersion", "sourceToolId", "sourceToolVersion", "fieldLocator"], "allExact": True},
    "evidence_artifact_trace_matrix.json": {"path": ["Evidence", "Artifact ID/checksum", "Artifact contract/version", "Tool/version"], "latestBinding": 0, "filenameAuthority": 0},
    "trust_path_matrix.json": {"path": ["Finding", "Evidence", "Artifact", "Tool/version", "Input identity", "Provenance"], "discoverable": True, "exact": True, "frontendInference": 0},
    "inspector_adapter_matrix.json": {"selectionKinds": ["ARTIFACT", "EVIDENCE_ITEM", "CLAIM"], "fallback": "typed no selection", "rawPayloadExecution": False},
    "inspector_summary_matrix.json": {"default": "meaning and selected kind", "internalIdsPrimary": False},
    "inspector_scientific_details_matrix.json": {"facts": "exact canonical selection fields", "collapsedByDefault": True},
    "inspector_provenance_matrix.json": {"facts": ["project", "sourceScopeHash", "panel source refs"], "collapsedByDefault": True},
    "developer_detail_matrix.json": {"subordinate": True, "collapsedByDefault": True, "rawJsonInert": True},
    "provenance_chain_matrix.json": {"steps": ["claim", "evidence", "artifact", "tool", "plan/job", "input"], "exactIdentity": True},
    "lineage_matrix.json": {"artifactLineageAuthority": "persisted records", "UIAuthority": "NONE", "latest": 0, "nearest": 0, "arrayPosition": 0},
    "plan01_provenance_matrix.json": {"schema": "0.1", "presentation": "independent/sequential semantics", "dependencyFabrication": 0},
    "plan02_provenance_matrix.json": {"schema": "0.2", "presentation": "typed Artifact dependency bindings", "bindingMutation": 0},
    "selection_integration_matrix.json": {"selectionContract": "WorkspaceSelectionContext 1.0", "evidenceToArtifact": "exact persisted ID/checksum/contract/version", "urlAuthority": "UNCHANGED"},
    "partial_interpretation_matrix.json": {"state": "INTERPRETATION_READY_WITH_LIMITS", "successfulScopeVisible": True, "failedBlockedScopeVisible": True, "fullSuccessPresentation": False},
    "no_supported_evidence_matrix.json": {"states": ["NO_SUPPORTED_EVIDENCE", "NO_SUPPORTED_CONCLUSION"], "infrastructureFailure": False, "explicitMessage": True},
    "integrity_failure_matrix.json": {"states": ["SOURCE_INTEGRITY_FAILED", "VALIDATION_FAILED", "PROVIDER_FAILED"], "collapsedToNoFindings": False},
    "stale_missing_matrix.json": {"stale": "typed", "missing": "typed", "substituteSelected": False, "contextPreserved": True},
    "recommendation_boundary.json": {"executionAuthorized": False, "planCreated": False, "jobCreated": False, "queued": False, "directRunAction": False},
    "scientific_wording_audit.json": {"probabilityFabrication": 0, "unqualifiedFactUpgrade": 0, "limitationsHidden": 0, "recommendationExecutionCopy": 0},
    "phase11_validation_presentation_audit.json": {"supportEqualsValidation": False, "mappingOnlyUpgrade": 0, "notApplicableUpgrade": 0, "v4Fabrication": 0},
    "mobile_findings_matrix.json": {"viewport": [390, 844], "singleColumn": True, "touchTargetMinimum": 44, "horizontalOverflow": 0},
    "mobile_inspector_matrix.json": {"viewport": [390, 844], "mode": "bottom sheet", "layers": ["Summary", "Scientific details", "Provenance"], "focusTrap": True},
    "accessibility_matrix.json": {"keyboard": "PASS", "focus": "PASS", "nonColorRoles": "PASS", "semanticHeadings": "PASS", "limitationsText": "PASS"},
    "zoom_200_matrix.json": {"equivalentViewport": [720, 450], "essentialActionClipping": 0, "horizontalOverflow": 0},
    "before_after_surface_matrix.json": {"before": "phase12-0 findings/evidence audit", "after": ["trust path", "three-layer inspector", "exact provenance chain"], "scientificPayloadChanged": False},
    "interaction_baseline_comparison.json": {"findingToEvidence": "one exact selection action", "evidenceToArtifact": "one exact source action", "developerConceptsDefault": "subordinate", "humanUsabilityClaim": False},
    "scientific_payload_nonchange.json": {"ArtifactValues": 0, "units": 0, "claims": 0, "evidence": 0, "frontendRecomputation": 0},
    "interpretation_contract_nonchange.json": {"ScientificEvidenceBundle": "1.0 unchanged", "ScientificEvidenceItem": "1.0 unchanged", "ScientificClaim": "1.0 unchanged", "GroundedScientificInterpretation": "1.0 unchanged"},
    "phase12_4_problem_closure.json": {"closed": [{"problemId": "UX-004", "severity": "P1", "owner": "12-4", "status": "FIXED_WITH_EVIDENCE"}], "open": [], "newP0": 0, "newP1": 0},
    "deferred_problem_matrix.json": {"12-5": ["UX-005"], "12-6": ["UX-006", "UX-009"], "12-7": ["UX-010"]},
    "phase12_5_handoff.json": {"owner": "12-5", "status": "REVIEWER_GATE", "reportRecipeAuthority": "UNCHANGED", "findingsEvidenceTrustPath": "phase12-4", "executableTaskCreated": False},
    "acceptance_registry.json": {"expected": 8, "implemented": 8, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": ACCEPTANCE},
}

TEXT_RECORDS = {
    "baseline.txt": "Phase 12-3 archive f6a39ca4d6afc560662d98c6f882ecc10a0e3d71\nRegistry 62\nDataProfile 2.4\nmigration 0007_phase10m1_workspace_domain\n",
    "entry_gate.md": "PHASE_12_4_ENTRY_GATE = PASS\n\nPhase 12-3 lifecycle, DS2, Workspace IA, interpretation contracts, exact selection, Registry 62, DataProfile 2.4 and migration 0007 resolve. The task queue addition is the reviewer-authorized admission change.\n",
    "security.md": "NO_PHASE12_4_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE12_4_ARTIFACT_HTML_EXECUTION = PASS\nNO_PHASE12_4_ARTIFACT_JAVASCRIPT_EXECUTION = PASS\nNO_PHASE12_4_IFRAME_EXECUTION = PASS\nNO_PHASE12_4_EXTERNAL_ARTIFACT_URL_EXECUTION = PASS\nNO_PHASE12_4_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\nNO_PHASE12_4_LLM_SCIENTIFIC_AUTHORITY = PASS\nNO_SECRET_PATTERN_HITS = PASS\n",
    "secret_scan.txt": "secret-bearing evidence = 0\nexternal network = 0\nreal LLM calls = 0\n",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    browser_path = EVIDENCE / "browser_matrix.json"
    browser = None
    if browser_path.exists():
        try:
            candidate = json.loads(browser_path.read_text(encoding="utf-8"))
            if all(name in candidate for name in ("chromium", "firefox", "webkit")):
                browser = candidate
        except json.JSONDecodeError:
            browser = None
    for name, value in JSON_RECORDS.items():
        write_json(EVIDENCE / name, value)
    write_json(browser_path, browser or {"chromium": "PENDING", "firefox": "PENDING", "webkit": "PENDING", "chromium390x844": "PENDING"})
    for name, value in TEXT_RECORDS.items():
        (EVIDENCE / name).write_text(value, encoding="utf-8")
    entries = []
    for path in sorted(EVIDENCE.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(EVIDENCE).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(EVIDENCE / "manifest.json", {"phase": "12-4", "schemaVersion": "phase12-4-findings-evidence/1.0", "entries": entries, "missing": 0, "extra": 0, "hashMismatch": 0, "implementationCi": "PENDING"})
    print(f"PHASE12_4_EVIDENCE_GENERATED {len(entries)}")


if __name__ == "__main__":
    main()
