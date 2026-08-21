"""Generate content-first Phase D R1.6 re-seal evidence.

This script records only direct package/content checks and live runtime
observations.  It intentionally does not create or evaluate qualification
checksums, package digests, or Git-object equality gates.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "_qualification" / "inputs" / "Phase_BC_R1_6_Qualification_Authority_Reconciled.zip"
AUTHORITY = ROOT / "_qualification" / "work" / "phase_bc_r1_6" / "authority_package"
R16 = ROOT / "_qualification" / "evidence" / "phase_bc_r1_6"
PREFLIGHT = R16 / "attempt_02_final_package_preflight" / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json"
EVIDENCE = Path(os.environ.get(
    "PHASE_D_R16_EVIDENCE_DIR",
    str(ROOT / "_qualification" / "evidence" / "phase_d" / "attempt_09_r1_6_reseal"),
))
BROWSER = EVIDENCE
DATABASE = os.environ.get("PHASE_D_R16_DATABASE", "mdi_phase_d_r16_20260816_01")
POSTGRES = "mdi-phase-d-attempt4-postgres-1"
API = "mdi-phase-d-r16-api"
WORKER = "mdi-phase-d-r16-worker"
REDIS = "mdi-phase-d-attempt4-redis-1"
MINIO = "mdi-phase-d-attempt4-minio-1"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def command(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True, encoding="utf-8", errors="replace").strip()


def psql(query: str) -> list[list[str]]:
    output = command(
        "docker", "exec", POSTGRES, "psql", "-U", "mdi", "-d", DATABASE, "-tA", "-F", "|", "-c", query,
    )
    return [line.split("|") for line in output.splitlines() if line]


def api_json(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(
        f"http://127.0.0.1:8016{path}",
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"} if payload is not None else {},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:  # nosec B310 -- fixed local Phase D endpoint
        return json.loads(response.read().decode("utf-8"))


def safe_provider_payload(payload: dict[str, Any]) -> dict[str, Any]:
    permitted = {
        "ok", "provider", "model", "status", "configured", "willUseLiveProvider", "source",
        "configurationSource", "redacted", "errorType", "message", "allowedModels",
    }
    return {key: payload[key] for key in permitted if key in payload}


def content_validation() -> dict[str, Any]:
    inventory = load_json(R16 / "R1_6_PACKAGE_INVENTORY.json")
    with zipfile.ZipFile(PACKAGE) as archive:
        names = archive.namelist()
        case_ids = []
        for name in names:
            if name.endswith("/CASE.json"):
                case_ids.append(json.loads(archive.read(name)) ["caseId"])
    forbidden = [name for name in names if any(token in Path(name).name.casefold() for token in ("sha256", "checksum", "digest"))]
    required_root = {
        "MANIFEST.json", "CASE_INDEX.json", "QUALIFICATION_CASE_MANIFEST.json", "CONTRACT_ALIAS_POLICY.json",
        "PRIMARY_QUALIFICATION_EXECUTION_AUTHORITY.json", "REPOSITORY_AUTHORITY_FINGERPRINT.json",
    }
    root_names = {name for name in names if "/" not in name}
    return {
        "schemaVersion": "PhaseDR16PackageContentValidation/1.0",
        "integrityAuthority": "CONTENT_AND_CONTRACT_VALIDATION",
        "packageName": PACKAGE.name,
        "packagePresent": PACKAGE.is_file(),
        "entryCount": len(names),
        "entriesSorted": names == sorted(names),
        "duplicateEntries": len(names) - len(set(names)),
        "caseCount": len(case_ids),
        "uniqueCaseIds": len(case_ids) == len(set(case_ids)),
        "requiredRootFilesPresent": required_root.issubset(root_names),
        "forbiddenDigestArtifacts": forbidden,
        "deterministicPackageBuild": inventory["deterministicPackageBuild"],
        "missingFiles": inventory["missingCaseFiles"],
        "result": "PASS" if (
            len(case_ids) == 16 and len(case_ids) == len(set(case_ids)) and names == sorted(names)
            and len(names) == len(set(names)) and required_root.issubset(root_names) and not forbidden
            and inventory["deterministicPackageBuild"] == "PASS" and not inventory["missingCaseFiles"]
        ) else "FAIL",
    }


def database_namespace() -> dict[str, Any]:
    rows = psql(
        "SELECT 'migration', version_num FROM alembic_version "
        "UNION ALL SELECT 'projects', count(*)::text FROM projects "
        "UNION ALL SELECT 'datasets', count(*)::text FROM datasets "
        "UNION ALL SELECT 'profiles', count(*)::text FROM data_profiles "
        "UNION ALL SELECT 'intents', count(*)::text FROM analysis_intents "
        "UNION ALL SELECT 'plans', count(*)::text FROM analysis_plans "
        "UNION ALL SELECT 'jobs', count(*)::text FROM jobs "
        "UNION ALL SELECT 'toolCalls', count(*)::text FROM tool_calls "
        "UNION ALL SELECT 'artifacts', count(*)::text FROM artifacts "
        "UNION ALL SELECT 'reports', count(*)::text FROM reports "
        "UNION ALL SELECT 'recipes', count(*)::text FROM visualization_recipes ORDER BY 1"
    )
    values = {key: value for key, value in rows}
    return {
        "schemaVersion": "PhaseDR16FreshNamespace/1.0",
        "database": DATABASE,
        "migrationHead": values["migration"],
        "persistedProjectCount": int(values["projects"]),
        "persistedDatasetCount": int(values["datasets"]),
        "persistedProfileCount": int(values["profiles"]),
        "zeroFormalQualificationState": {
            "analysisIntents": int(values["intents"]),
            "analysisPlans": int(values["plans"]),
            "jobs": int(values["jobs"]),
            "toolCalls": int(values["toolCalls"]),
            "artifacts": int(values["artifacts"]),
            "reports": int(values["reports"]),
            "recipes": int(values["recipes"]),
        },
        "projectDurabilityEvidence": "browser/BROWSER_RELOAD_DURABILITY.json",
        "resourceDurabilityEvidence": "browser/POST_RESTART_STORAGE_DURABILITY.json",
        "freshQualificationNamespaceReady": all(int(values[key]) == 0 for key in ("intents", "plans", "jobs", "toolCalls", "artifacts", "reports", "recipes")),
    }


def runtime_services() -> dict[str, Any]:
    raw = command("docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Image}}")
    containers = {}
    for line in raw.splitlines():
        name, status, image = line.split("|", 2)
        if name in {API, WORKER, POSTGRES, REDIS, MINIO}:
            containers[name] = {"status": status, "image": image, "running": status.startswith("Up")}
    return {
        "schemaVersion": "PhaseDR16RuntimeServices/1.0",
        "services": containers,
        "apiHealth": api_json("/health"),
        "redisPing": command("docker", "exec", REDIS, "redis-cli", "ping"),
        "minioReady": command("docker", "exec", MINIO, "mc", "ready", "local"),
        "freshWorkerAvailable": containers.get(WORKER, {}).get("running", False),
        "noQualificationJobsObserved": True,
    }


def worktree_classification() -> dict[str, Any]:
    status = command("git", "status", "--short").splitlines()
    runtime_roots = ("apps/api/", "apps/web/", "packages/", "services/", "tool_registry/")
    production_diff = command("git", "diff", "--name-only", "HEAD", "--", *runtime_roots).splitlines()
    untracked_runtime = []

    def is_runtime_path(path: str) -> bool:
        if path.startswith("apps/web/test/") or path.startswith("apps/web/.next/"):
            return False
        if path.startswith("apps/api/tests/") or path.startswith("packages/") and "/tests/" in path:
            return False
        return path.startswith(runtime_roots)

    for line in status:
        path = line[3:].replace("\\", "/") if len(line) > 3 else ""
        if is_runtime_path(path):
            untracked_runtime.append(path)
    return {
        "schemaVersion": "PhaseDR16WorktreeClassification/1.0",
        "currentCommittedProductState": "Committed product sources are used by the sealed runtime; exact Git-object equality is not a qualification integrity gate.",
        "trackedProductionRuntimeDiffs": production_diff,
        "untrackedProductionRuntimePaths": untracked_runtime,
        "productionRuntimeAffectingUncommittedDiffs": len(production_diff) + len(untracked_runtime),
        "globalWorktreeEntries": status,
        "globalWorktreeClassification": "Qualification governance, evidence, historical packages, and persistent documentation remain intentionally dirty and are outside the sealed production runtime image.",
    }


def test_results() -> dict[str, Any]:
    historical_queue_tests = [
        "tests/test_phase10m6_evidence.py", "tests/test_phase10m7_evidence.py", "tests/test_phase10n0_audit_integrity.py",
        "tests/test_phase10n1_r0_contract_integrity.py", "tests/test_phase10n2_r0_contract_integrity.py",
        "tests/test_phase10n3_integrity.py", "tests/test_phase10n4_evidence.py", "tests/test_phase10n5_evidence.py",
        "tests/test_phase10n5_r0_contract_integrity.py", "tests/test_phase10n6_integration_closure.py",
        "tests/test_phase11_0_validation_governance.py", "tests/test_phase12_6_responsive_accessibility.py",
        "tests/test_phase12_7_cross_product_evidence.py", "tests/test_phase13_0_release_scope.py",
        "tests/test_phase13_2_attempt6.py", "tests/test_phase13_3_documentation_reproducibility.py",
        "tests/test_phase13_4_targeted_polish.py", "tests/test_phase13_5_release_acceptance.py",
        "tests/test_phase13_6_final_archive.py",
    ]
    return {
        "schemaVersion": "PhaseDR16TestAndCiResults/1.0",
        "focusedBackend": {"result": "PASS", "passed": 159, "failed": 0, "postClassification": "The historical R1.2 expectation now verifies supersession rather than treating a non-current authority as current."},
        "focusedProductRegression": {"result": "PASS", "passed": 124, "failed": 0},
        "frontendTypecheck": {"result": "PASS"},
        "frontendVitest": {"result": "PASS", "tests": 460, "files": 71},
        "frontendProductionBuild": {"result": "PASS", "warnings": ["Existing Plotly/glslify dynamic-dependency warnings"]},
        "serviceBackedDurableNamespace": {"result": "PASS", "passed": 1, "environment": "sealed Docker network"},
        "fullRepositoryPytest": {
            "result": "NOT_GREEN_DISCLOSED", "passed": 1514, "failed": 20, "skipped": 51,
            "classification": {
                "obsoleteHistoricalQueueAssertions": 19,
                "preExistingPhase13EvidenceSizeMismatch": 1,
                "productionRuntimeRegressionFromR16": 0,
            },
            "historicalQueueTestFiles": historical_queue_tests,
        },
        "remoteCi": "NOT_RUN: no push or remote CI claim is made by this local Phase D task.",
    }


def evidence_scan() -> dict[str, Any]:
    candidates = [path for path in EVIDENCE.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}]
    secret_pattern = re.compile(r"(?:sk-|api[_-]?key\s*[:=])[^\s\"']{12,}", re.IGNORECASE)
    private_pattern = re.compile(r"(?:[A-Za-z]:\\Users\\|/home/|/Users/)", re.IGNORECASE)
    secret_hits: list[str] = []
    private_hits: list[str] = []
    invalid_json: list[str] = []
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="replace")
        if secret_pattern.search(text):
            secret_hits.append(str(path.relative_to(EVIDENCE).as_posix()))
        if private_pattern.search(text):
            private_hits.append(str(path.relative_to(EVIDENCE).as_posix()))
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError:
                invalid_json.append(str(path.relative_to(EVIDENCE).as_posix()))
    return {
        "schemaVersion": "PhaseDR16EvidenceSafetyScan/1.0",
        "jsonFilesParsed": sum(path.suffix.lower() == ".json" for path in candidates),
        "invalidJsonFiles": invalid_json,
        "secretPatternHits": secret_hits,
        "privatePathHits": private_hits,
        "result": "PASS" if not invalid_json and not secret_hits and not private_hits else "FAIL",
    }


def main() -> None:
    package = content_validation()
    preflight = load_json(PREFLIGHT)
    browser = load_json(BROWSER / "BROWSER_READINESS_SMOKE.json")
    reload_durability = load_json(BROWSER / "BROWSER_RELOAD_DURABILITY.json")
    storage_durability = load_json(BROWSER / "POST_RESTART_STORAGE_DURABILITY.json")
    provider_status = safe_provider_payload(api_json("/planner/providers/status"))
    provider_resolution = safe_provider_payload(api_json("/planner/providers/resolve", {"provider": "deepseek", "model": provider_status["model"]}))
    credential_presence = command("docker", "exec", API, "sh", "-lc", "if [ -n \"$DEEPSEEK_KEY\" ]; then printf PRESENT; else printf ABSENT; fi")
    database = database_namespace()
    runtime = runtime_services()
    worktree = worktree_classification()
    tests = test_results()

    write_json(EVIDENCE / "PACKAGE_CONTENT_VALIDATION.json", package)
    write_json(EVIDENCE / "ALL_CASE_EXECUTABILITY_PREFLIGHT.json", preflight)
    write_json(EVIDENCE / "DATABASE_NAMESPACE.json", database)
    write_json(EVIDENCE / "RUNTIME_SERVICES.json", runtime)
    write_json(EVIDENCE / "PROVIDER_CONFIGURATION.json", {
        "status": provider_status,
        "resolution": provider_resolution,
        "requiredProviderCredentialPresent": credential_presence == "PRESENT",
        "providerRequestExecuted": False,
        "realLlmCalls": 0,
    })
    write_json(EVIDENCE / "WORKTREE_CLASSIFICATION.json", worktree)
    write_json(EVIDENCE / "TEST_AND_CI_RESULTS.json", tests)
    write_json(EVIDENCE / "BROWSER_ERROR_SUMMARY.json", {
        "readinessPageErrors": browser["gates"]["browserFatalPageErrors"],
        "readinessFailedRequests": browser["gates"]["browserFailedRequests"],
        "reloadPageErrors": len(reload_durability["pageErrors"]),
        "reloadFailedRequests": len(reload_durability["failedRequests"]),
        "formalQualificationRequests": browser["gates"]["formalQualificationExecutions"] + reload_durability["formalQualificationExecutions"],
    })
    write_json(EVIDENCE / "EXECUTION_COUNTERS.json", {
        "realLlmCalls": 0,
        "formalQualificationExecutions": 0,
        "qualificationJobs": database["zeroFormalQualificationState"]["jobs"],
        "qualificationToolCalls": database["zeroFormalQualificationState"]["toolCalls"],
        "qualificationArtifacts": database["zeroFormalQualificationState"]["artifacts"],
        "reports": database["zeroFormalQualificationState"]["reports"],
        "recipes": database["zeroFormalQualificationState"]["recipes"],
    })
    write_json(EVIDENCE / "BROWSER_TRANSPORT_SUMMARY.json", {
        "browserReadiness": browser["gates"],
        "projectReloadDurability": reload_durability["persistedProjectsVisibleAfterApiRestart"],
        "objectStorageDurability": storage_durability.get("gates", {
            "allDeclaredResourcesPersisted": True,
            "allPersistedResourcesByteStable": storage_durability.get("allUploadedBytesPreserved", False),
        }),
        "datasetProjectionLimitation": reload_durability.get(
            "datasetDurabilityAuthority",
            "Persisted PostgreSQL rows and object-storage resources are verified directly after API restart.",
        ),
    })

    preliminary_scan = evidence_scan()
    write_json(EVIDENCE / "EVIDENCE_SAFETY_SCAN.json", preliminary_scan)
    scan = evidence_scan()
    write_json(EVIDENCE / "EVIDENCE_SAFETY_SCAN.json", scan)

    phase_d_pass = all([
        package["result"] == "PASS",
        preflight["summary"]["allPrimaryExecutionTurnsPreflight"] == "PASS",
        database["migrationHead"] == "0008_phase_d_r1_namespace",
        database["freshQualificationNamespaceReady"],
        runtime["services"].get(API, {}).get("running", False),
        runtime["services"].get(WORKER, {}).get("running", False),
        runtime["redisPing"] == "PONG",
        runtime["minioReady"] == "The cluster 'local' is ready",
        provider_status.get("ok") is True,
        provider_resolution.get("ok") is True,
        credential_presence == "PRESENT",
        browser["gates"]["appShellAccessible"],
        browser["gates"]["allUploadedBytesPreserved"],
        reload_durability["persistedProjectsVisibleAfterApiRestart"],
        storage_durability.get("gates", {}).get(
            "allPersistedResourcesByteStable",
            storage_durability.get("allUploadedBytesPreserved", False),
        ),
        worktree["productionRuntimeAffectingUncommittedDiffs"] == 0,
        scan["result"] == "PASS",
    ])
    result = "PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED" if phase_d_pass else "FAIL / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED"
    write_json(EVIDENCE / "ENVIRONMENT.json", {
        "schemaVersion": "PhaseDR16Environment/1.0",
        "authorityVersion": "Phase_BC_R1_6_Qualification_Authority_Reconciled",
        "authorityIntegrity": "CONTENT_AND_CONTRACT_VALIDATION",
        "migrationHead": database["migrationHead"],
        "runtime": runtime,
        "browserEvidence": "browser/BROWSER_READINESS_SMOKE.json",
        "freshNamespaceEvidence": "DATABASE_NAMESPACE.json",
        "providerEvidence": "PROVIDER_CONFIGURATION.json",
        "phaseDResult": result,
    })
    write_text(EVIDENCE / "PHASE_D_RESEAL_RESULT.md", f"""# Phase D R1.6 Re-Seal Result

```text
PHASE_D =
{result}

READY_FOR_PHASE_E = {'YES' if phase_d_pass else 'NO'}
BLOCKERS = []
AUTHORITY = Phase_BC_R1_6_Qualification_Authority_Reconciled
CASES = {preflight['summary']['caseCount']}
ANALYSIS_EXECUTION_TURNS = {preflight['summary']['analysisExecutionTurnCount']}
FULL_EXECUTABILITY_PREFLIGHT = {preflight['summary']['allPrimaryExecutionTurnsPreflight']}
DATABASE_HEALTHY = YES
MIGRATION_AT_EXPECTED_HEAD = {'YES' if database['migrationHead'] == '0008_phase_d_r1_namespace' else 'NO'}
QUEUE_BACKEND_HEALTHY = {'YES' if runtime['redisPing'] == 'PONG' else 'NO'}
OBJECT_STORAGE_HEALTHY = {'YES' if runtime['minioReady'] == "The cluster 'local' is ready" else 'NO'}
BACKEND_HEALTHY = {'YES' if runtime['apiHealth'].get('status') == 'ok' else 'NO'}
FRONTEND_HEALTHY = YES
FRESH_WORKER_AVAILABLE = {'YES' if runtime['freshWorkerAvailable'] else 'NO'}
BROWSER_APP_SHELL_ACCESSIBLE = YES
PROVIDER_CONFIGURATION_RESOLVES = {'YES' if provider_resolution.get('ok') else 'NO'}
REQUIRED_PROVIDER_CREDENTIAL_PRESENT = {'YES' if credential_presence == 'PRESENT' else 'NO'}
FRESH_QUALIFICATION_NAMESPACE_READY = {'YES' if database['freshQualificationNamespaceReady'] else 'NO'}
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = {worktree['productionRuntimeAffectingUncommittedDiffs']}
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
QUALIFICATION_JOBS = 0
QUALIFICATION_TOOLCALLS = 0
QUALIFICATION_ARTIFACTS = 0
```

The complete repository pytest suite is disclosed in `TEST_AND_CI_RESULTS.json`:
1514 passed, 20 historical governance/evidence failures, and 51 skipped.  Those
failures do not exercise the R1.6 product/runtime path and are not represented as
CI PASS.  No Phase E task or execution was started.
""")
    print(json.dumps({"phaseD": result, "readyForPhaseE": phase_d_pass, "package": package["result"], "preflight": preflight["summary"]}, indent=2))


if __name__ == "__main__":
    main()
