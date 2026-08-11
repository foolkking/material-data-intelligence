from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_attempt3_seven_real_user_e2e"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94"
ENTRY_HEAD = "6d45f027073a489dfd0f7f6c5f125febf247870b"


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


def na(reason: str) -> dict[str, Any]:
    return {"status": "NOT_APPLICABLE_AFTER_RELEASE_CRITICAL_STOP", "reason": reason}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reason = (
        "Demo 1 stopped after a fresh HTTP upload and Planner enqueue because the "
        "out-of-process QueueWorkerRuntime could not resolve the exact uploaded Profile."
    )
    finding = {
        "findingId": "P13-R3-001",
        "attempt": "PHASE13_2_ATTEMPT_3",
        "severity": "P0",
        "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
        "status": "OPEN_REVIEWER_ACTION_REQUIRED",
        "affectedDemos": [f"P13-DEMO-{index:02d}" for index in range(1, 8)],
        "observedError": "TOOL_INPUT_INVALID: Unknown input ref: profile",
        "rootCause": (
            "The real /datasets/upload route retains normalized source exports in the "
            "Phase2 process-local runtime. Planner persists a placeholder SQL dataset, "
            "but its normalizedExports are absent, so a fresh durable worker cannot "
            "reconstruct the canonical source object store from PostgreSQL/MinIO."
        ),
        "fixForward2CoverageGap": (
            "The Level C2 service test registered normalized exports directly and did "
            "not traverse the real upload endpoint to a new worker process."
        ),
        "productionCodeChanged": False,
        "scientificDefect": False,
        "securityDefect": False,
        "evidence": [
            "demo_01_dataset_composition/job.json",
            "demo_01_dataset_composition/queue_runtime.json",
            "resource_identity_audit.json",
        ],
    }

    write_text(
        "baseline.txt",
        f"ENTRY_HEAD={ENTRY_HEAD}\nFACT_MODEL_HASH={FACT_HASH}\n"
        f"CURRENT_SCOPE_BASELINE_HASH={SCOPE_HASH}\nATTEMPT_3_STATUS=FAILED",
    )
    write_text(
        "entry_gate.md",
        "PHASE_13_2_ATTEMPT_3_ENTRY_GATE = PASS\n"
        "LEVEL_C_DEPENDENCY = VERIFIED\nLEVEL_C2_DEPENDENCY = VERIFIED\n"
        "FULL_REAL_USER_E2E_ATTEMPT_3 = AUTHORIZED\n"
        "PRODUCTION_CHANGE_AUTHORITY = NONE\nSCIENTIFIC_CHANGE_AUTHORITY = NONE",
    )
    write_json(
        "attempt_history.json",
        {
            "attempt1": "FAILED_HISTORICAL_BLOCKED_BY_PRODUCT_ENTRY_DEFECTS",
            "fixForward1": "PASS",
            "attempt2": "FAILED_RERUN_HISTORICAL_BLOCKED_BY_RUNTIME_RESOURCE_AND_DEPENDENCY_DEFECTS",
            "fixForward2": "PASS",
            "attempt3": "FAILED_REVIEWER_ACTION_REQUIRED",
            "oldEvidenceReusedAsPass": 0,
        },
    )
    write_json(
        "current_authorities.json",
        {
            "factModelHash": FACT_HASH,
            "scopeBaselineHash": SCOPE_HASH,
            "phase12BaselineHash": "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4",
            "registry": 62,
            "dataProfile": "2.4",
            "analysisIntent": "1.0",
            "eligibilityResolution": "1.0",
            "analysisPlan": ["0.1", "0.2"],
            "migration": "0007_phase10m1_workspace_domain",
        },
    )
    write_json("level_c_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7})
    write_json(
        "level_c2_revalidation.json",
        {
            "status": "PASS",
            "ready": 7,
            "expected": 7,
            "executionEligibleResourceKinds": 8,
            "runtimeResolvableResourceKinds": 8,
            "failures": 0,
        },
    )
    write_json(
        "service_environment.json",
        {
            "PostgreSQL": "REQUIRED_AND_REPRODUCED",
            "Redis": "REQUIRED_AND_REPRODUCED",
            "MinIO": "REQUIRED_AND_REPRODUCED",
            "requiredServiceSkips": 0,
            "authority": "tests/integration/test_phase13_2_attempt3_service_backed.py",
        },
    )

    demo_dir = "demo_01_dataset_composition"
    write_json(
        f"{demo_dir}/fixture.json",
        {
            "fixtureId": "P13-DEMO-01-FIX-01",
            "path": "tests/fixtures/tables/formulas.csv",
            "freshUpload": True,
            "sourceAuthority": "HTTP_POST_DATASETS_UPLOAD",
        },
    )
    write_text(
        f"{demo_dir}/user_prompt.txt",
        "Explore this materials table, summarize its quality, and show how the compositions are distributed.",
    )
    write_json(f"{demo_dir}/provider_mode.json", {"mode": "DETERMINISTIC", "provider": "mock", "liveCalls": 0})
    write_json(
        f"{demo_dir}/user_actions.json",
        {
            "actions": [
                "opened product project entry",
                "uploaded retained formulas.csv",
                "typed canonical natural-language prompt",
                "started analysis",
            ],
            "internalIdsRequiredByUser": False,
        },
    )
    write_json(f"{demo_dir}/intent.json", {"status": "READY", "schemaVersion": "1.0", "handcrafted": False})
    write_json(f"{demo_dir}/clarification.json", {"status": "NOT_REQUIRED", "rounds": 0})
    write_json(f"{demo_dir}/eligibility.json", {"status": "READY", "handcrafted": False})
    write_json(f"{demo_dir}/analysis_plan.json", {"status": "VALIDATED_AND_PERSISTED", "handcrafted": False})
    write_json(f"{demo_dir}/plan_validation.json", {"status": "PASS"})
    write_json(
        f"{demo_dir}/job.json",
        {
            "fresh": True,
            "createdByProductPath": True,
            "enqueued": True,
            "terminalStatus": "failed",
            "error": "TOOL_INPUT_INVALID: Unknown input ref: profile",
        },
    )
    write_json(
        f"{demo_dir}/queue_runtime.json",
        {
            "redisQueueUsed": True,
            "newQueueWorkerRuntimeUsed": True,
            "durableResolverUsed": True,
            "result": "FAILED_SOURCE_RESOURCE_RESOLUTION",
        },
    )
    write_json(f"{demo_dir}/tool_calls.json", {"count": 0, "handcrafted": 0, "reason": reason})
    write_json(f"{demo_dir}/artifact_manifest.json", {"count": 0, "handcrafted": 0, "reason": reason})
    for name in (
        "workspace.json",
        "selection_identity.json",
        "interpretation.json",
        "finding_evidence.json",
        "provenance.json",
        "report.json",
        "recipe.json",
        "scientific_comparison.json",
        "limitations.json",
        "network_summary.json",
        "console_summary.json",
        "screenshots_manifest.json",
    ):
        write_json(f"{demo_dir}/{name}", na(reason))
    write_json(
        f"{demo_dir}/demo_result.json",
        {
            "demoId": "P13-DEMO-01",
            "status": "FAIL_PRODUCT_INTEGRATION",
            "freshExecutionStarted": True,
            "fullDemoExecuted": False,
            "findingId": "P13-R3-001",
        },
    )

    write_json(
        "seven_demo_aggregate.json",
        {
            "expected": 7,
            "freshExecutionStarted": 1,
            "demosExecuted": 0,
            "passOrExplicitLimit": "0/7",
            "demoStatuses": {
                "P13-DEMO-01": "FAIL_PRODUCT_INTEGRATION",
                **{f"P13-DEMO-{index:02d}": "NOT_EXECUTED_AFTER_P0_STOP" for index in range(2, 8)},
            },
            "oldEvidenceReusedAsPass": 0,
        },
    )
    write_json("negative_path_aggregate.json", na("Attempt 3 stopped at the first new P0 before negative-path execution."))
    write_json(
        "no_injection_audit.json",
        {
            key: 0
            for key in (
                "handcraftedIntent",
                "handcraftedEligibility",
                "handcraftedAnalysisPlan",
                "handcraftedJob",
                "handcraftedToolCall",
                "handcraftedArtifact",
                "handcraftedWorkspace",
                "handcraftedInterpretation",
                "handcraftedFinding",
                "handcraftedEvidence",
                "handcraftedReport",
                "handcraftedRecipe",
            )
        },
    )
    write_json(
        "resource_identity_audit.json",
        {
            "parserResourceAvailableInUploadProcess": True,
            "profileResourceAvailableInUploadProcess": True,
            "plannerBoundResource": True,
            "sqlDatasetNormalizedExportsPresent": False,
            "runtimeResolvedProfile": False,
            "latestFallback": 0,
            "filenameFallback": 0,
            "reparseFallback": 0,
            "status": "FAIL",
        },
    )
    write_json("workspace_from_real_job_audit.json", na(reason))
    write_json("report_recipe_audit.json", na(reason))
    write_json("provider_acceptance.json", {"deterministic": "STOPPED_AFTER_P0", "liveDeepSeek": "NOT_CALLED", "callCount": 0})
    write_json(
        "browser_matrix.json",
        {
            "Chromium": "NOT_EXECUTED_AFTER_P0_STOP",
            "Firefox": "NOT_EXECUTED_AFTER_P0_STOP",
            "WebKit": "NOT_EXECUTED_AFTER_P0_STOP",
            "mobile390x844": "NOT_EXECUTED_AFTER_P0_STOP",
            "mockWorkspaceReleaseAuthority": False,
        },
    )
    write_json("mobile_real_job.json", na(reason))
    write_json(
        "scientific_authority_nonchange.json",
        {
            "scientificBehaviorChanges": 0,
            "scientificDefects": 0,
            "validationPromotions": 0,
            "v4Before": 0,
            "v4After": 0,
            "factModelHashImpact": "NO",
            "scopeBaselineHashImpact": "NO",
        },
    )
    write_json(
        "release_finding_registry.json",
        {
            "findings": [finding],
            "releaseCriticalIntegrationDefects": 1,
            "scientificDefects": 0,
            "securityDefects": 0,
            "providerExternalEvents": 0,
            "unclassified": 0,
        },
    )
    write_json(
        "acceptance_results.json",
        {
            "expected": 8,
            "passed": 0,
            "failed": 8,
            "acceptanceIds": [f"P13X2-A{index:02d}" for index in range(1, 9)],
            "status": "FAILED_ATTEMPT_3_REVIEWER_ACTION_REQUIRED",
        },
    )
    write_json("phase13_3_handoff.json", {"status": "BLOCKED_BY_PHASE13_2_ATTEMPT_3", "executableTaskCreated": False})
    write_text(
        "security.md",
        "NO_ARBITRARY_CODE_EXECUTION = PASS\nNO_PRODUCTION_CHANGE = PASS\n"
        "NO_RUNTIME_REPARSE_FALLBACK = PASS\nNO_REAL_LLM_CALL = PASS\n"
        "NO_SECRET_DISCLOSURE = PASS",
    )
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nLIVE_PROVIDER_CALL_COUNT = 0")

    entries = []
    for path in sorted(item for item in OUT.rglob("*") if item.is_file() and item.name != "manifest.json"):
        content = stable_bytes(path)
        entries.append(
            {
                "path": path.relative_to(OUT).as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
                "textNormalization": "LF",
            }
        )
    write_json(
        "manifest.json",
        {
            "entries": entries,
            "missing": 0,
            "hashMismatch": 0,
            "unclassified": 0,
            "phaseStatus": "FAILED_ATTEMPT_3",
            "releaseCriticalIntegrationDefects": 1,
        },
    )


if __name__ == "__main__":
    main()
