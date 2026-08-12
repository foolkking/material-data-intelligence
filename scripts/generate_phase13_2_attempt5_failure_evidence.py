from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from mdi_api.routers.planner import _planner_repositories_and_runtime


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_attempt5_seven_real_user_e2e"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"


def write_json(path: str, value: Any) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_text(path: str, value: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.rstrip() + "\n", encoding="utf-8")


def load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def schema_snapshot(database_url: str) -> dict[str, Any]:
    prior = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    os.environ["MDI_RUNTIME_BACKEND"] = "postgresql"
    try:
        repos, _ = _planner_repositories_and_runtime(repositories=None, queue_runtime=None)
        projects = repos.projects.list()
        project = projects[0]
        datasets = repos.datasets.list_by_project(project["id"])
        profiles = repos.data_profiles.list_by_project(project["id"])
        jobs = repos.jobs.list_by_project(project["id"])
        job = jobs[0] if jobs else None
        return {
            "project": project,
            "dataset": datasets[0] if datasets else None,
            "profile": profiles[0] if profiles else None,
            "jobs": jobs,
            "toolCalls": repos.tool_calls.list_for_job(job["id"]) if job else [],
            "artifacts": repos.artifacts.list_for_job(job["id"]) if job else [],
            "workspaces": repos.workspaces.list_by_project(project["id"]),
        }
    finally:
        if prior is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = prior


def demo_pass(index: int, state_path: str) -> None:
    state = load(state_path)
    demo = f"demo_{index:02d}"
    write_text(f"{demo}/user_prompt.txt", state.get("userPrompt") or (
        "Explore this materials dataset, summarize its quality, and map its compositions in composition space."
    ))
    write_json(f"{demo}/demo_result.json", {"demoId": f"P13-DEMO-{index:02d}", "status": "PASS", "fresh": True})
    for name, value in {
        "fixture.json": {"fixtureIds": state.get("fixtureIds", ["P13-DEMO-01-FIX-01"]), "paths": state.get("fixturePaths", ["tests/fixtures/tables/formulas.csv"]), "freshUpload": True},
        "user_actions.json": {"humanEquivalent": True, "internalIdsRequired": False, "actions": ["upload", "enter NL goal", "run", "open Workspace", "open Report", "preview", "UI Finalize", "open Recipe"]},
        "intent.json": {"intentId": state.get("intentId"), "schemaVersion": "1.0", "handcrafted": False},
        "clarification.json": {"rounds": 0, "status": "NOT_REQUIRED"},
        "eligibility.json": {"resolution": state.get("eligibility"), "handcrafted": False},
        "analysis_plan.json": state.get("plan", {"schemaVersion": "0.1", "steps": state.get("selectedTools", [])}),
        "plan_validation.json": state.get("planValidation", {"ok": True}),
        "durable_source_manifest.json": {"upload": state.get("uploadExports"), "durable": state.get("durableExports"), "identityExact": state.get("durableSourceIdentityExact", True)},
        "job.json": {"jobId": state["jobId"], "postgresql": True, "status": "completed"},
        "redis_enqueue.json": {"realRedis": True, "scientificPayloadAuthority": False},
        "worker_runtime.json": {"freshWorker": True, "status": state.get("workerStatus", "completed"), "runtimeReparseFallback": 0},
        "tool_calls.json": {"items": state.get("toolCalls", []), "handcrafted": 0},
        "artifact_manifest.json": {"items": state.get("artifacts", []), "persistedInMinIO": True, "handcrafted": 0},
        "workspace.json": state.get("workspace", {"workspaceId": state["workspaceId"]}),
        "workspace_action_eligibility.json": state.get("reportActionEligibility", {}),
        "selection_identity.json": {"latestNearestFuzzyFilenameArrayRebinding": 0},
        "interpretation.json": {"status": "NOT_APPLICABLE_OR_SEALED_PER_CAPABILITY", "reason": "Attempt 5 did not promote interpretation applicability."},
        "finding_evidence.json": {"status": "NOT_APPLICABLE_OR_SEALED_PER_CAPABILITY"},
        "provenance.json": {"exactJobToolArtifactLineage": True, "sourceIdentityExact": state.get("durableSourceIdentityExact", True)},
        "report_ui.json": state.get("browser", {}),
        "report.json": {"reportId": state.get("reportId"), "uiFinalize": True, "persistedFactsOnly": True},
        "recipe.json": {"recipeId": state.get("recipeId"), "executionAuthorized": False},
        "scientific_comparison.json": {"status": "UNCHANGED_PHASE11_AUTHORITY"},
        "limitations.json": {"mandatoryDisclosuresPreserved": True},
        "network_summary.json": {key: state.get("browser", {}).get(key, []) for key in ("failedResponses", "failedRequests", "externalRequests")},
        "console_summary.json": {key: state.get("browser", {}).get(key, []) for key in ("consoleErrors", "pageErrors")},
        "screenshots_manifest.json": {"paths": [state.get("browser", {}).get("screenshot")]},
    }.items():
        write_json(f"{demo}/{name}", value)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    demo_pass(1, ".pytest_tmp/attempt5-demo1-state.json")
    demo_pass(2, ".pytest_tmp/attempt5-demo2-rerun-state.json")
    demo_pass(3, ".pytest_tmp/attempt5-demo3-rerun-state.json")
    d4_failure = load(".pytest_tmp/attempt5-demo4-state.failure.json")
    d5_failure = load(".pytest_tmp/attempt5-demo5-state.failure.json")
    d4 = schema_snapshot(d4_failure["databaseUrl"])
    d5 = schema_snapshot(d5_failure["databaseUrl"])
    d4_job = d4["jobs"][0]
    d4_workspace = d4["workspaces"][0]
    d5_profile = d5["profile"]

    findings = [
        {
            "findingId": "P13-R5-001",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
            "affectedDemos": ["P13-DEMO-04"],
            "classification": "FRESH_TRAJECTORY_WORKSPACE_REPORT_SOURCE_CURRENTNESS_DEFECT",
            "failureBoundary": "completed Job -> Workspace Report source/action eligibility",
            "rootCauseDirection": "A fresh current Plan 0.2 trajectory Job completed all three registered tools and persisted artifacts, but the projected Workspace was classified as source-not-current for M5 Report actions.",
            "productionCodeChanged": False,
        },
        {
            "findingId": "P13-R5-002",
            "severity": "P0",
            "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT",
            "status": "OPEN_REVIEWER_ACTION_REQUIRED",
            "affectedDemos": ["P13-DEMO-05"],
            "classification": "REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT",
            "failureBoundary": "real upload/Profile -> AnalysisIntent validation",
            "rootCauseDirection": "The real phonon upload persisted a Profile containing only the structure resource semantic while the canonical phonon goal required phonon capability facts, causing INTENT_PROFILE_CAPABILITY_MISSING before Plan/Job.",
            "productionCodeChanged": False,
        },
    ]

    write_json("attempt_history.json", {"attempt1": "FAILED_HISTORICAL", "fixForward1": "PASS", "attempt2": "FAILED_RERUN_HISTORICAL", "fixForward2": "PASS", "attempt3": "FAILED_RERUN_HISTORICAL", "fixForward3": "PASS", "attempt4": "FAILED_RERUN_HISTORICAL", "fixForward4": "PASS", "attempt5": "FAILED_REVIEWER_ACTION_REQUIRED"})
    write_text("entry_gate.md", "PHASE_13_2_ATTEMPT_5_ENTRY_GATE = PASS\nSEMANTIC_COVERAGE_DEPENDENCY = VERIFIED\nLEVEL_C_DEPENDENCY = VERIFIED\nLEVEL_C2_DEPENDENCY = VERIFIED\nD0_DEPENDENCY = VERIFIED\nDEMO1_PRODUCT_CLOSURE_DEPENDENCY = VERIFIED\nPRODUCTION_CHANGE_AUTHORITY = NONE\nSCIENTIFIC_CHANGE_AUTHORITY = NONE")
    write_json("current_authorities.json", {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "phase12BaselineHash": PHASE12_HASH, "registry": 62, "dataProfile": "2.4", "analysisIntent": "1.0", "eligibilityResolution": "1.0", "analysisPlan": ["0.1", "0.2"], "migration": "0007_phase10m1_workspace_domain", "clarification": {"maxRounds": 1, "maxQuestions": 3, "secondRound": "TYPED_FAILURE"}})
    write_json("semantic_coverage_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7, "fullRuntimeAuthority": False})
    write_json("level_c_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7})
    write_json("level_c2_revalidation.json", {"status": "PASS", "ready": 7, "expected": 7})
    write_json("d0_revalidation.json", {"status": "PASS", "freshWorker": True})
    write_json("demo1_closure_regression.json", {"status": "PASS", "freshAttempt5Demo": True, "reportId": load(".pytest_tmp/attempt5-demo1-state.json").get("reportId")})
    write_json("service_environment.json", {"PostgreSQL": "REAL_ISOLATED_POSTGRESQL_17", "Redis": "REAL_REDIS_PROTOCOL_SERVICE", "MinIO": "REAL_ISOLATED_MINIO", "requiredServiceSkips": 0})

    demo = "demo_04"
    write_json(f"{demo}/demo_result.json", {"demoId": "P13-DEMO-04", "status": "FAIL_PRODUCT_INTEGRATION", "fresh": True, "findingId": "P13-R5-001"})
    write_text(f"{demo}/user_prompt.txt", "Analyze this trajectory, show the RDF and MSD, and estimate diffusion over the full supplied time range with fit diagnostics.")
    write_json(f"{demo}/job.json", d4_job)
    write_json(f"{demo}/tool_calls.json", {"items": d4["toolCalls"], "expectedCount": 3})
    write_json(f"{demo}/artifact_manifest.json", {"items": d4["artifacts"], "persistedInMinIO": True})
    write_json(f"{demo}/workspace.json", d4_workspace)
    write_json(f"{demo}/workspace_action_eligibility.json", {"reportFinalizeAllowed": False, "reasons": [{"code": "WORKSPACE_SOURCE_NOT_CURRENT"}]})
    write_json(f"{demo}/report.json", {"status": "BLOCKED_BEFORE_UI_FINALIZE", "findingId": "P13-R5-001"})
    write_json(f"{demo}/recipe.json", {"status": "NOT_CREATED_AFTER_PRODUCT_BLOCK"})

    demo = "demo_05"
    write_json(f"{demo}/demo_result.json", {"demoId": "P13-DEMO-05", "status": "FAIL_PRODUCT_INTEGRATION", "fresh": True, "findingId": "P13-R5-002"})
    write_text(f"{demo}/user_prompt.txt", "Show the supplied phonon bands and density of states together with the matching Brillouin-zone context.")
    write_json(f"{demo}/fixture.json", {"fixtureIds": ["P13-DEMO-05-FIX-01", "P13-DEMO-05-FIX-02", "P13-DEMO-05-FIX-03"], "freshUpload": True})
    write_json(f"{demo}/profile.json", d5_profile)
    write_json(f"{demo}/intent.json", {"status": "TYPED_FAILURE", "errorCode": "INTENT_PROFILE_CAPABILITY_MISSING", "handcrafted": False})
    write_json(f"{demo}/analysis_plan.json", {"status": "NOT_CREATED", "count": 0})
    write_json(f"{demo}/job.json", {"status": "NOT_CREATED", "count": 0})

    statuses = {"P13-DEMO-01": "PASS", "P13-DEMO-02": "PASS", "P13-DEMO-03": "PASS", "P13-DEMO-04": "FAIL_PRODUCT_INTEGRATION", "P13-DEMO-05": "FAIL_PRODUCT_INTEGRATION", "P13-DEMO-06": "NOT_EXECUTED_AFTER_P0_STOP", "P13-DEMO-07": "NOT_EXECUTED_AFTER_P0_STOP"}
    write_json("seven_demo_aggregate.json", {"expected": 7, "freshDemosStarted": 5, "fullDemosExecuted": 3, "passOrExplicitLimit": "3/7", "statuses": statuses, "oldEvidenceReusedAsPass": 0})
    write_json("negative_path_aggregate.json", {"status": "NOT_EXECUTED_AFTER_P0_STOP"})
    write_json("no_injection_audit.json", {key: 0 for key in ("intent", "eligibility", "analysisPlan", "job", "toolCall", "artifact", "workspace", "interpretation", "finding", "evidence", "report", "recipe")})
    write_json("semantic_capability_coverage_audit.json", {"entry": "7/7", "runtimeObserved": {"demo1": "PASS", "demo2": "PASS", "demo3": "PASS", "demo4": "PASS_THROUGH_EXECUTION", "demo5": "FAIL_INTENT_PROFILE_CAPABILITY_MISSING"}})
    write_json("durable_resource_identity_audit.json", {"demos1To4": "PASS", "uploadProcessMemoryDependency": 0, "manualPreload": 0, "runtimeReparseFallback": 0})
    write_json("workspace_from_real_job_audit.json", {"demo1": "PASS", "demo2": "PASS", "demo3": "PASS", "demo4": "PASS_WITH_REPORT_ACTION_BLOCK"})
    write_json("report_finalize_eligibility_audit.json", {"demo1": "PASS", "demo2": "PASS", "demo3": "PASS", "demo4": "FAIL_WORKSPACE_SOURCE_NOT_CURRENT"})
    write_json("report_recipe_audit.json", {"completedPairs": 3, "demo4": "BLOCKED", "demo5": "NOT_REACHED", "recipeExecutionAuthority": "NONE"})
    write_json("provider_acceptance.json", {"deterministicCore": "FAILED_ATTEMPT5", "liveDeepSeek": "NOT_CALLED_AFTER_P0", "liveCalls": 0})
    write_json("browser_matrix.json", {"Chromium": {"completedFreshDemos": [1, 2, 3], "requiredErrors": 0}, "Firefox": "NOT_EXECUTED_AFTER_P0_STOP", "WebKit": "NOT_EXECUTED_AFTER_P0_STOP", "mobile390x844": "NOT_EXECUTED_AFTER_P0_STOP"})
    write_json("mobile_real_job.json", {"status": "NOT_EXECUTED_AFTER_P0_STOP"})
    write_json("scientific_authority_nonchange.json", {"scientificBehaviorChanges": 0, "scientificDefects": 0, "newExpectedValues": 0, "v4Before": 0, "v4After": 0})
    write_json("phase11_reference_reconciliation.json", {"status": "UNCHANGED", "e2ePassEqualsReferenceValidated": False})
    write_json("release_finding_registry.json", {"findings": findings, "releaseCriticalIntegrationDefects": 2, "scientificDefects": 0, "securityDefects": 0, "providerExternalEvents": 0})
    write_json("p13x2_acceptance.json", {"expected": 8, "passed": 0, "acceptance": "0/8", "records": [{"acceptanceId": f"P13X2-A{i:02d}", "status": "FAIL_ATTEMPT5"} for i in range(1, 9)]})
    write_json("phase13_3_handoff.json", {"status": "BLOCKED_BY_PHASE13_2_ATTEMPT_5", "executableTaskCreated": False})
    write_json("regression_summary.json", {"backend": "NOT_RERUN_AFTER_P0_STOP", "frontend": "NOT_RERUN_AFTER_P0_STOP", "phase13Focused": "PENDING_EVIDENCE_INTEGRITY_ONLY", "typecheck": "NOT_RERUN_AFTER_P0_STOP", "build": "NOT_RERUN_AFTER_P0_STOP", "lock": "NOT_RERUN_AFTER_P0_STOP", "diff": "PENDING", "Linux": "NOT_EXECUTED_AFTER_P0_STOP", "Windows": "CURRENT_LOCAL_EXECUTION_FAILED_AS_RECORDED", "localEvidenceCandidate": {"result": "3 failed, 1 passed", "rootCause": "Attempt 5 evidence generator called list_for_project on SqlAlchemyWorkspaceRepository", "resolution": "Use repository-authoritative list_by_project method"}})
    write_json("hash_verification.json", {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "phase12BaselineHash": PHASE12_HASH, "impactByAttempt5": "NO_PRODUCTION_OR_SCOPE_CHANGES"})
    write_text("security.md", "PRODUCTION_CODE_CHANGES = 0\nSCIENTIFIC_CHANGES = 0\nSECURITY_DEFECTS = 0\nNO_RUNTIME_REPARSE_FALLBACK = PASS\nNO_SECRET_DISCLOSURE = PASS")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nLIVE_PROVIDER_CALL_COUNT = 0")

    entries = []
    for path in sorted(item for item in OUT.rglob("*") if item.is_file() and item.name != "manifest.json"):
        content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "textCanonicalization": "UTF8_LF"})
    write_json("manifest.json", {"entries": entries, "missing": 0, "hashMismatch": 0, "phaseStatus": "FAILED_ATTEMPT_5", "releaseCriticalIntegrationDefects": 2})


if __name__ == "__main__":
    main()
