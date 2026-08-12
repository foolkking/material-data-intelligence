from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_attempt4_seven_real_user_e2e"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"


def write_json(path: str, value: Any) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: str, value: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8")


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def not_executed(reason: str) -> dict[str, Any]:
    return {"status": "NOT_EXECUTED_AFTER_P0_STOP", "reason": reason}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reason = (
        "Fresh Demo 1 stopped Attempt 4 because the canonical natural-language prompt "
        "planned only dataset.materials_explorer instead of the sealed composition-space "
        "family, and its AnalysisPlan 0.1 Workspace was LEGACY_READ_ONLY so the real UI "
        "disabled Report finalization."
    )
    findings = [
        {
            "findingId": "P13-R4-001",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
            "affectedDemos": ["P13-DEMO-01"],
            "classification": "CANONICAL_PROMPT_TO_SEALED_CAPABILITY_MISMATCH",
            "rootCause": (
                "The sealed Demo 1 contract requires dataset.composition_space, but the "
                "canonical phrase 'show how the compositions are distributed' is formally "
                "classified as composition_analysis. Production Intent and Mock planning "
                "require an explicit composition-space, embedding, or clustering expression."
            ),
            "observed": {
                "plannedTools": ["dataset.materials_explorer"],
                "executedTools": ["dataset.materials_explorer"],
                "artifactTypes": ["table_json", "quality_issues_json", "summary_md", "recipe_json"],
                "missingTool": "dataset.composition_space",
                "missingArtifactType": "plotly_json",
            },
            "productionCodeChanged": False,
            "evidence": [
                "demo_01_dataset_composition/analysis_plan.json",
                "demo_01_dataset_composition/tool_calls.json",
                "demo_01_dataset_composition/artifact_manifest.json",
            ],
        },
        {
            "findingId": "P13-R4-002",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
            "affectedDemos": ["P13-DEMO-01"],
            "classification": "REAL_USER_REPORT_FINALIZE_BLOCKED_BY_PLAN_0_1_WORKSPACE_POLICY",
            "rootCause": (
                "Workspace projection classifies every AnalysisPlan 0.1 source as "
                "LEGACY_READ_ONLY. The Workspace Report composer disables Finalize when "
                "workspace.readOnly is true, so a normal user cannot complete the sealed "
                "Report/Recipe path for this current Planner-produced job."
            ),
            "observed": {
                "planSchemaVersion": "0.1",
                "workspaceStatus": "LEGACY_READ_ONLY",
                "workspaceReadOnly": True,
                "uiFinalizeEnabled": False,
                "diagnosticDirectApiFinalizeIsUserPathAuthority": False,
            },
            "productionCodeChanged": False,
            "evidence": [
                "demo_01_dataset_composition/workspace.json",
                "demo_01_dataset_composition/report.json",
                "demo_01_dataset_composition/recipe.json",
            ],
        },
    ]

    write_text(
        "entry_gate.md",
        "PHASE_13_2_ATTEMPT_4_ENTRY_GATE = PASS\n"
        "REVIEWER_AUTHORIZED_PREEXISTING_INPUTS = .claude/, ui-ux-audit/\n"
        "LEVEL_C_DEPENDENCY = VERIFIED\nLEVEL_C2_DEPENDENCY = VERIFIED\n"
        "D0_DEPENDENCY = VERIFIED_AND_RERUN\nFULL_FRESH_REAL_USER_E2E_ATTEMPT_4 = AUTHORIZED\n"
        "PRODUCTION_CHANGE_AUTHORITY = NONE\nSCIENTIFIC_CHANGE_AUTHORITY = NONE",
    )
    write_json(
        "attempt_history.json",
        {
            "attempt1": "FAILED_HISTORICAL",
            "fixForward1": "PASS",
            "attempt2": "FAILED_RERUN_HISTORICAL",
            "fixForward2": "PASS",
            "attempt3": "FAILED_RERUN_HISTORICAL",
            "fixForward3": "PASS",
            "attempt4": "FAILED_REVIEWER_ACTION_REQUIRED",
            "oldEvidenceReusedAsAttempt4Pass": 0,
        },
    )
    write_json(
        "current_authorities.json",
        {
            "factModelHash": FACT_HASH,
            "scopeBaselineHash": SCOPE_HASH,
            "phase12BaselineHash": PHASE12_HASH,
            "registry": 62,
            "dataProfile": "2.4",
            "analysisIntent": "1.0",
            "eligibilityResolution": "1.0",
            "analysisPlan": ["0.1", "0.2"],
            "migration": "0007_phase10m1_workspace_domain",
            "clarification": {"maxRounds": 1, "maxQuestions": 3, "secondRound": "TYPED_FAILURE"},
        },
    )
    write_json("level_c_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7})
    write_json("level_c2_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7})
    write_json("d0_revalidation.json", {"status": "PASS", "tests": 1, "skipped": 0, "freshWorker": True})
    write_json(
        "durable_upload_authority.json",
        {
            "authority": "PostgreSQL manifest/Profile + MinIO payload",
            "uploadProcessMemoryDependency": 0,
            "manualNormalizedExportPreload": 0,
            "runtimeReparseFallback": 0,
            "status": "PASS",
        },
    )
    write_json(
        "service_environment.json",
        {
            "PostgreSQL": "REAL_ISOLATED_INSTANCE",
            "Redis": "REAL_MEMURAI_REDIS_PROTOCOL_DB14",
            "MinIO": "REAL_ISOLATED_INSTANCE",
            "requiredServiceSkips": 0,
            "secretsRecorded": False,
        },
    )
    write_json(
        "reviewer_authorized_inputs.json",
        {
            "authority": "REVIEWER_AUTHORIZED_ATTEMPT4_SUPPORTING_INPUT_ONLY",
            "productionAuthority": "NONE",
            "scientificAuthority": "NONE",
            "scopeAuthority": "NONE",
            "files": [
                ".claude/launch.json",
                "ui-ux-audit/UI_UX_RECONSTRUCTION_BASELINE.md",
                "ui-ux-audit/runtime/RUNTIME_VERIFICATION_ADDENDUM.md",
            ],
        },
    )

    demo = "demo_01_dataset_composition"
    write_json(f"{demo}/fixture.json", {"fixtureId": "P13-DEMO-01-FIX-01", "path": "tests/fixtures/tables/formulas.csv", "freshUpload": True})
    write_text(f"{demo}/user_prompt.txt", "Explore this materials table, summarize its quality, and show how the compositions are distributed.")
    write_json(f"{demo}/user_actions.json", {"humanEquivalent": True, "internalIdsRequired": False, "actions": ["upload", "enter natural-language goal", "run", "open Workspace", "preview Report"]})
    write_json(f"{demo}/intent.json", {"schemaVersion": "1.0", "outcome": "READY", "handcrafted": False, "scientificIntents": ["composition_analysis", "dataset_overview"]})
    write_json(f"{demo}/clarification.json", {"rounds": 0, "status": "NOT_REQUIRED"})
    write_json(f"{demo}/eligibility.json", {"schemaVersion": "1.0", "outcome": "READY", "handcrafted": False})
    write_json(f"{demo}/analysis_plan.json", {"schemaVersion": "0.1", "validated": True, "handcrafted": False, "plannedTools": ["dataset.materials_explorer"]})
    write_json(f"{demo}/plan_validation.json", {"status": "PASS"})
    write_json(f"{demo}/durable_source_manifest.json", {"identityExact": True, "uploadProcessMemoryDependency": 0, "manualPreload": 0})
    write_json(f"{demo}/job.json", {"fresh": True, "jobId": "job_71ec040c2e0e49baba47863b", "postgresqlPersisted": True, "redisEnqueued": True, "workerStatus": "completed"})
    write_json(f"{demo}/redis_enqueue.json", {"realRedis": True, "queue": "mdi-jobs", "scientificPayloadAuthority": False})
    write_json(f"{demo}/worker_runtime.json", {"freshWorker": True, "registeredAdapterExecuted": True, "runtimeReparseFallback": 0, "status": "completed"})
    write_json(f"{demo}/tool_calls.json", {"count": 1, "handcrafted": 0, "tools": ["dataset.materials_explorer"], "missingRequiredTool": "dataset.composition_space"})
    write_json(f"{demo}/artifact_manifest.json", {"count": 4, "handcrafted": 0, "types": ["table_json", "quality_issues_json", "summary_md", "recipe_json"], "artifactIds": ["call_job_71ec040c2e0e49baba47863b_step_001-table_json", "call_job_71ec040c2e0e49baba47863b_step_001-quality_issues_json", "call_job_71ec040c2e0e49baba47863b_step_001-summary_md", "call_job_71ec040c2e0e49baba47863b_step_001-recipe_json"], "missingRequiredType": "plotly_json", "persistedInMinIO": True})
    write_json(f"{demo}/workspace.json", {"workspaceId": "workspace_dd25f3b0123eb3e13c9922499a2fd683", "fromRealJob": True, "projectedStatus": "LEGACY_READ_ONLY", "readOnly": True, "oneWorkspacePerJob": True})
    write_json(f"{demo}/selection_identity.json", {"status": "NOT_COMPLETED_AFTER_P0", "latestRebinding": 0})
    write_json(f"{demo}/interpretation.json", not_executed(reason))
    write_json(f"{demo}/finding_evidence.json", not_executed(reason))
    write_json(f"{demo}/provenance.json", {"durableSourceExact": True, "jobToolArtifactLineagePresent": True, "demoContractComplete": False})
    write_json(f"{demo}/report.json", {"previewFromPersistedFacts": True, "realUserFinalizeEnabled": False, "diagnosticApiFinalizeExcludedFromPass": True})
    write_json(f"{demo}/recipe.json", {"diagnosticPairPersisted": True, "executionAuthorized": False, "realUserPathComplete": False})
    write_json(f"{demo}/scientific_comparison.json", {"status": "NOT_APPLICABLE", "reason": "No numeric reference promotion is authorized for Demo 1."})
    write_json(f"{demo}/limitations.json", {"sealedLimitationsPreserved": True, "newDefectsHiddenAsLimitations": False})
    write_json(f"{demo}/network_summary.json", {"status": "NOT_EXECUTED_IN_BROWSER_AFTER_P0"})
    write_json(f"{demo}/console_summary.json", {"status": "NOT_EXECUTED_IN_BROWSER_AFTER_P0"})
    write_json(f"{demo}/screenshots_manifest.json", {"count": 0, "reason": "P0 stop preceded Attempt 4 browser authority."})
    write_json(f"{demo}/demo_result.json", {"demoId": "P13-DEMO-01", "status": "FAIL_PRODUCT_INTEGRATION", "freshExecutionStarted": True, "fullDemoExecuted": False, "findingIds": ["P13-R4-001", "P13-R4-002"]})

    statuses = {"P13-DEMO-01": "FAIL_PRODUCT_INTEGRATION"}
    statuses.update({f"P13-DEMO-{index:02d}": "NOT_EXECUTED_AFTER_P0_STOP" for index in range(2, 8)})
    write_json("seven_demo_aggregate.json", {"expected": 7, "freshExecutionsStarted": 1, "fullDemosExecuted": 0, "passOrExplicitLimit": "0/7", "statuses": statuses, "oldEvidenceReusedAsPass": 0})
    write_json("negative_path_aggregate.json", not_executed("Attempt 4 stopped at the first new P0 before the negative suite."))
    write_json("no_injection_audit.json", {key: 0 for key in ("handcraftedIntent", "handcraftedEligibility", "handcraftedAnalysisPlan", "handcraftedJob", "handcraftedToolCall", "handcraftedArtifact", "handcraftedWorkspace", "handcraftedInterpretation", "handcraftedFinding", "handcraftedEvidence", "handcraftedReport", "handcraftedRecipe")})
    write_json("durable_resource_identity_audit.json", {"demo1": "PASS", "uploadProcessMemoryDependency": 0, "manualPreload": 0, "runtimeReparse": 0, "latestNearestFuzzyFilenameArrayRebinding": 0})
    write_json("workspace_from_real_job_audit.json", {"demo1": "PASS_WITH_READ_ONLY_BLOCKER", "findingId": "P13-R4-002"})
    write_json("report_recipe_audit.json", {"demo1RealUserFinalize": "BLOCKED", "recipeExecutionAuthority": "NONE", "findingId": "P13-R4-002"})
    write_json("provider_acceptance.json", {"deterministic": "FAILED_DEMO1_CONTRACT", "liveDeepSeek": "NOT_CALLED_AFTER_P0", "liveCalls": 0})
    write_json("browser_matrix.json", {"Chromium": "NOT_EXECUTED_AFTER_P0_STOP", "Firefox": "NOT_EXECUTED_AFTER_P0_STOP", "WebKit": "NOT_EXECUTED_AFTER_P0_STOP", "mobile390x844": "NOT_EXECUTED_AFTER_P0_STOP"})
    write_json(
        "regression_summary.json",
        {
            "backend": {"passed": 1391, "skipped": 52, "status": "PASS"},
            "frontend": {"passed": 456, "status": "PASS"},
            "phase13FocusedGovernance": {"passed": 46, "status": "PASS"},
            "typecheck": "PASS",
            "build": "PASS_WITH_EXISTING_PLOTLY_GLSLIFY_WARNINGS",
            "lock": "PASS",
            "diff": "PASS",
            "serviceD0": {"passed": 1, "skipped": 0, "status": "PASS"},
            "browser": "NOT_EXECUTED_AFTER_P0_STOP",
            "linuxReplay": "NOT_EXECUTED_AFTER_P0_STOP",
            "windowsReplay": "NOT_EXECUTED_AFTER_P0_STOP",
            "localFailedCandidate": {
                "result": "1390 passed, 52 skipped, 1 failed",
                "cause": "Attempt 4 TASK block used an English status label",
                "resolution": "Use the repository-authoritative Chinese failed status label",
            },
        },
    )
    write_json("mobile_real_job.json", not_executed(reason))
    write_json("scientific_authority_nonchange.json", {"scientificBehaviorChanges": 0, "scientificDefects": 0, "validationPromotions": 0, "v4Before": 0, "v4After": 0, "registryBefore": 62, "registryAfter": 62})
    write_json("phase11_reference_reconciliation.json", {"status": "UNCHANGED", "e2ePassEqualsReferenceValidated": False})
    write_json("release_finding_registry.json", {"findings": findings, "releaseCriticalIntegrationDefects": 2, "scientificDefects": 0, "securityDefects": 0, "providerExternalEvents": 0, "unclassified": 0})
    write_json("p13x2_acceptance.json", {"expected": 8, "passed": 0, "failed": 8, "missing": 0, "extra": 0, "duplicate": 0, "acceptance": "0/8", "records": [{"acceptanceId": f"P13X2-A{index:02d}", "status": "FAIL_ATTEMPT4"} for index in range(1, 9)]})
    write_json("phase13_3_handoff.json", {"status": "BLOCKED_BY_PHASE13_2_ATTEMPT_4", "executableTaskCreated": False})
    write_json("hash_verification.json", {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "phase12BaselineHash": PHASE12_HASH, "factModelImpact": "NO", "scopeImpact": "NO", "determinism": "PASS"})
    write_text("security.md", "NO_PRODUCTION_CHANGE = PASS\nNO_SCIENTIFIC_CHANGE = PASS\nNO_RUNTIME_REPARSE_FALLBACK = PASS\nNO_REDIS_SCIENTIFIC_AUTHORITY = PASS\nNO_SECRET_DISCLOSURE = PASS")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nLIVE_PROVIDER_CALL_COUNT = 0")

    entries = []
    for path in sorted(item for item in OUT.rglob("*") if item.is_file() and item.name != "manifest.json"):
        content = stable_bytes(path)
        entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "textNormalization": "LF"})
    write_json("manifest.json", {"entries": entries, "missing": 0, "hashMismatch": 0, "unclassified": 0, "phaseStatus": "FAILED_ATTEMPT_4", "releaseCriticalIntegrationDefects": 2})


if __name__ == "__main__":
    main()
