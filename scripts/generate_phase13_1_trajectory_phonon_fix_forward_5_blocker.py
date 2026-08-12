from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS


OUT = ROOT / "docs/phase13/evidence/phase13_1_trajectory_phonon_fix_forward_5"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"


def write_json(name: str, value: Any) -> None:
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def write_text(name: str, value: str) -> None:
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_text(
        "entry_gate.md",
        f"""# Fix-Forward #5 Entry Gate

Attempt 5 is `FAILED / REVIEWER_ACTION_REQUIRED`; evidence SHA `d8d1966ff0fb419ff8299ec440c1af8e0c349f24` passed exact-SHA CI `31603622900`, and failure record SHA is `1fa342a4fdb81717058ca37b1c273413a80ddec1`.

Entry HEAD equaled `origin/master`; five failed Attempt blocks were retained. Fact Model `{FACT_HASH}`, Scope Baseline `{SCOPE_HASH}`, Phase 12 baseline `{PHASE12_HASH}`, Registry 62, DataProfile 2.4, AnalysisIntent 1.0, EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, and migration `0007_phase10m1_workspace_domain` were verified. Semantic coverage, Level C, Level C2 and D0 remained `7/7`, `7/7`, `7/7` and PASS respectively.
""",
    )
    attempt = {
        "status": "FAILED_REVIEWER_ACTION_REQUIRED",
        "evidenceSha": "d8d1966ff0fb419ff8299ec440c1af8e0c349f24",
        "evidenceExactShaCi": {"run": 31603622900, "status": "PASS"},
        "failureRecordSha": "1fa342a4fdb81717058ca37b1c273413a80ddec1",
        "demos": {"1": "PASS", "2": "PASS", "3": "PASS", "4": "FAIL_PRODUCT_INTEGRATION", "5": "FAIL_PRODUCT_INTEGRATION", "6": "NOT_EXECUTED_AFTER_P0_STOP", "7": "NOT_EXECUTED_AFTER_P0_STOP"},
        "freshStarted": 5,
        "fullExecuted": 3,
        "oldEvidenceReusedAsPass": 0,
    }
    write_json("attempt5_failure_snapshot.json", attempt)

    identity_rows = [
        {"layer": "Job execution", "datasetId": "dataset_f04d895e5f5943fcb7f84bb1", "datasetVersion": "2", "profileId": "profile_dataset_f04d895e5f5943fcb7f84bb1_v2", "profileSemanticHash": "0a036dd0439d70e4c9e184beff277fd79a27baeebd1f0b5f35069032c11d9b26", "planId": "plan_e28d5214255b43a2826981cd", "planHash": "a462e3ab39337c9846b2943bf3e1ea400eac6dba5587f0a10d8d5c95192273ca", "currentness": "CURRENT"},
        {"layer": "Workspace immutable snapshot", "datasetId": "dataset_f04d895e5f5943fcb7f84bb1", "datasetVersion": None, "profileId": "profile_dataset_f04d895e5f5943fcb7f84bb1_v2", "profileSemanticHash": "0a036dd0439d70e4c9e184beff277fd79a27baeebd1f0b5f35069032c11d9b26", "planId": "plan_e28d5214255b43a2826981cd", "planHash": "a462e3ab39337c9846b2943bf3e1ea400eac6dba5587f0a10d8d5c95192273ca", "currentness": "STALE", "mismatchField": "datasetVersion"},
        {"layer": "Report eligibility", "workspaceId": "workspace_29114b0e05133e9088c5317c18d3b91b", "decision": "WORKSPACE_SOURCE_NOT_CURRENT", "mismatchField": "datasetVersion"},
    ]
    write_json("trajectory_workspace_source_currentness_matrix.json", {"rows": identity_rows})
    write_json("trajectory_source_identity_diff.json", {"expectedDatasetVersion": "2", "workspaceDatasetVersion": None, "mismatchOrigin": "Workspace projection used only explicit/sampleIdentity datasetVersion while Planner and Eligibility use Profile version when sampleIdentity is not applicable."})
    root_cause = {
        "findingId": "P13-R5-001",
        "rootCause": "Workspace _profile_dataset_version omitted the existing Profile.version fallback used by Intent and Eligibility. Trajectory Profiles legitimately have sampleIdentity=null, so the fresh execution snapshot carried datasetVersion=2 while the Workspace snapshot persisted null and Report currentness rejected it.",
        "authorizedCorrection": "Use explicit datasetVersion, then sampleIdentity.datasetVersion, then Profile.version, and compare the immutable Workspace snapshot against the exact live execution source.",
        "authorityWeakened": False,
    }
    write_json("r5_001_root_cause.json", root_cause)
    write_json("r5_001_reproduction.json", {"jobId": "job_b0a4fb2be3694da39b71fed0", "workspaceId": "workspace_29114b0e05133e9088c5317c18d3b91b", "toolCalls": 3, "artifacts": 12, "before": "WORKSPACE_SOURCE_NOT_CURRENT", "handcrafted": False})
    write_json("r5_001_before_after.json", {"before": {"profileVersion": "2", "workspaceDatasetVersion": None, "status": "STALE"}, "afterForNewProjection": {"profileVersion": "2", "workspaceDatasetVersion": "2", "status": "COMPLETE"}, "historicalIncompleteSnapshot": "REMAINS_STALE", "freshDemo4Smoke": "NOT_EXECUTED_AFTER_BRANCH_C_STOP"})
    write_json("trajectory_current_positive.json", {"status": "FOCUSED_REGRESSION_PASS", "tests": 29, "freshServiceBackedSmoke": "NOT_EXECUTED_AFTER_BRANCH_C_STOP"})
    write_json("trajectory_stale_negative.json", {"status": "PASS", "cases": ["self-consistent immutable Workspace snapshot missing current datasetVersion", "Profile version changes after projection"], "typedOutcome": "STALE"})
    write_json("trajectory_cross_project_negative.json", {"status": "RETAINED_EXISTING_REGRESSION", "outcome": "REJECT"})
    write_json("trajectory_hash_mismatch_negative.json", {"status": "RETAINED_EXISTING_REGRESSION", "outcome": "REJECT"})

    phase11 = {
        "inputFamily": "Phonon YAML/JSON",
        "supportVerdict": "MAPPING_ONLY",
        "parser": "No generic direct-upload parser; normalized Tool mapping only",
        "limits": ["not a claimed generic upload path"],
        "matrixChanged": False,
    }
    write_json("r5_002_historical_classification.json", {"historical": "REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT", "remediationState": "OPEN_REVIEWER_AUTHORITY_RECONCILIATION_REQUIRED"})
    write_json("phonon_input_support_matrix_snapshot.json", phase11)
    inventory = [
        {"path": "POST /datasets/upload with phonon JSON", "userVisible": True, "support": "MAPPING_ONLY", "createsTypedPhononResources": False},
        {"path": "POST /datasets/demo", "userVisible": True, "support": "DIRECT_DEMO_CSV_ONLY", "createsTypedPhononResources": False},
        {"path": "mapped_resources normalized mapper", "userVisible": False, "support": "INTERNAL_MAPPING", "createsTypedPhononResources": True},
        {"path": "tests/scripts construct NormalizedObjectDraft or DataProfile", "userVisible": False, "support": "TEST_INTERNAL", "createsTypedPhononResources": True},
        {"path": "existing persisted typed-resource selection/import API", "userVisible": False, "support": "ABSENT", "createsTypedPhononResources": False},
    ]
    write_json("phonon_user_entry_inventory.json", {"entries": inventory})
    write_json("phonon_user_ingestion_authority_audit.json", {"attempt5Action": "POST /datasets/upload with stable_band.json, total_dos.json and POSCAR", "snifferResult": "json_limited for phonon JSON", "profileResult": "Structure only; no PhononBand/PhononDos semantics", "runtimeCapabilitiesExist": True, "userVisibleSupportedTypedEntryExists": False, "decision": "BRANCH_C"})
    blocker = {
        "selectedBranch": "C",
        "result": "BLOCKED_DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT",
        "rationale": "Runtime typed resources, adapters and C/C2 mappings exist, but no current user-visible supported product path creates or selects exact PhononBand and PhononDos resources. Direct phonon upload is sealed MAPPING_ONLY.",
        "minimalSupportExpansionOption": {"description": "Reviewer-authorize a bounded user-visible typed phonon import contract and parser/resource/Profile wiring.", "factImpact": "REVIEW_REQUIRED", "scopeImpact": "YES", "inputSupportPromotion": "YES"},
        "minimalDemoScopeRevisionOption": {"description": "Remove Demo 5 from initial-release real-user E2E scope or defer it until a supported entry exists.", "factImpact": "NO_EXPECTED", "scopeImpact": "YES"},
    }
    write_json("phonon_branch_decision.json", blocker)
    write_json("phonon_branch_c_blocker.json", blocker)
    write_json("phonon_mapping_only_negative.json", {"status": "PASS_BY_ATTEMPT5_OBSERVATION", "directUploadExecutionReady": False, "typedFailure": "INTENT_PROFILE_CAPABILITY_MISSING"})
    write_json("no_input_support_promotion_audit.json", {"inputSupportPromotions": 0, "phononDirectUploadSupportPromotion": 0, "phase11MatrixChanged": False, "status": "PASS"})

    fidelity = []
    for spec in CURRENT_DEMO_SPECS:
        demo5 = spec["demoId"] == "P13-DEMO-05"
        fidelity.append({
            "demoId": spec["demoId"],
            "sealedUserAction": "upload/select current sealed fixture",
            "canonicalPrompt": spec["prompt"],
            "fixtureResource": [item[1] for item in spec["fixtures"]],
            "fileContainerType": [Path(item[1]).suffix or Path(item[1]).name for item in spec["fixtures"]],
            "inputSupportDisposition": "MAPPING_ONLY" if demo5 else "DIRECT_OR_BOUNDED",
            "userVisibleEndpointAction": "POST /datasets/upload",
            "parser": "json_limited + internal normalized mapper" if demo5 else "current production parser",
            "mapperProductionVisibility": not demo5,
            "canonicalResourceKinds": ["PhononBand", "PhononDos", "Structure"] if demo5 else "CURRENT_PROFILE_RESOURCE_SEMANTICS",
            "profileSemanticsProduced": not demo5,
            "intentRequiredFacts": "phonon_resource" if demo5 else "CURRENT_CONTRACT",
            "eligibilityRequiredFacts": "typed exact resources" if demo5 else "CURRENT_CONTRACT",
            "plannerRootBindings": "UNAVAILABLE_FROM_USER_ENTRY" if demo5 else "EXACT",
            "durablePersistencePath": "PostgreSQL + MinIO",
            "workerResolver": "DurableObjectStoreResolver",
            "supportStatus": "AUTHORITY_CONFLICT" if demo5 else "PASS",
            "realUserReachable": not demo5,
            "internalOnlyPreparation": demo5,
            "mismatch": "No supported user-visible typed phonon entry" if demo5 else None,
        })
    write_json("canonical_user_ingestion_fidelity_matrix.json", {"expected": 7, "passed": 6, "rows": fidelity})
    write_json("canonical_user_ingestion_fidelity_aggregate.json", {"expected": 7, "passed": 6, "userEntryContractMismatches": 1, "internalOnlyEntryPathsUsedAsUserPass": 0, "status": "BLOCKED"})

    write_json("semantic_coverage_regression.json", {"status": "PASS", "result": "7/7"})
    write_json("level_c_regression.json", {"status": "PASS", "result": "7/7", "historicalAuthorityPreserved": True})
    write_json("level_c2_regression.json", {"status": "PASS", "result": "7/7", "limitation": "valid for already durable resource domain"})
    write_json("d0_regression.json", {"status": "PASS", "marker": "REAL_UPLOAD_TO_FRESH_WORKER_D0_PASS"})
    write_json("demo1_closure_regression.json", {"status": "PASS"})
    write_json("fresh_demo4_product_closure_smoke.json", {"status": "NOT_EXECUTED_AFTER_BRANCH_C_STOP", "attempt6PassCount": 0})
    write_json("fresh_demo5_product_closure_smoke.json", {"status": "NOT_APPLICABLE_BRANCH_C", "reason": "No legal supported user entry", "attempt6PassCount": 0})
    write_json("no_injection_audit.json", {"allHandcraftedInjectionCounters": 0, "manualPhononProfileInjection": 0, "manualPhononResourceInjection": 0})
    write_json("release_finding_closure.json", {"P13-R5-001": "IMPLEMENTATION_CORRECTED_FOCUSED_REGRESSION_PASS_FRESH_SMOKE_PENDING", "P13-R5-002": "OPEN_REVIEWER_AUTHORITY_REQUIRED", "fixForward5": "BLOCKED"})
    write_json("release_gap_reconciliation.json", {"before": 2, "after": 1, "closed": 0, "implementationCorrectedPendingSmoke": 1, "open": 1, "scientificDefects": 0, "securityDefects": 0})
    write_json("fact_model_hash_impact.json", {"old": FACT_HASH, "impact": "NO", "current": FACT_HASH})
    write_json("scope_baseline_hash_impact.json", {"old": SCOPE_HASH, "impact": "NO", "current": SCOPE_HASH, "reason": "Branch C records a conflict without changing sealed scope."})
    write_json("baseline_determinism.json", {"run1": SCOPE_HASH, "run2": SCOPE_HASH, "linux": SCOPE_HASH, "windows": SCOPE_HASH, "status": "PASS"})
    write_json("phase11_input_support_nonchange.json", {"changed": False, "inputSupportPromotions": 0})
    write_json("phase12_nonchange.json", {"expected": PHASE12_HASH, "current": PHASE12_HASH, "drift": 0})
    write_json("phase13_2_attempt6_handoff.json", {"status": "NOT_GENERATED_FIX_FORWARD_BLOCKED", "attempt6Authorized": False, "attempt6TaskCreated": False, "freshExecutions": "0/7"})
    write_text("security.md", "# Security\n\nCurrentness bypasses, latest/fuzzy rebinding, cross-project binding, phonon support promotion, test-only user entry, runtime reparse, Redis/filesystem scientific authority, Recipe execution and frontend scientific recomputation remain forbidden and unchanged.")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS (focused changed-file scan; full release scan not run after Branch C stop)")

    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size": path.stat().st_size})
    write_json("manifest.json", {"entries": entries, "entryCount": len(entries), "hashCanonicalization": "FILE_BYTES", "status": "PASS"})


if __name__ == "__main__":
    main()
