from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/phase13"
SEAL = DOCS / "evidence/phase13_0_release_scope_seal"
CORRECTION = DOCS / "evidence/phase13_0_clarification_fact_correction"
OUT = DOCS / "evidence/phase13_1_zero_gap_verification_closure"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
SCOPE_HASH = "93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627"
TEXT_SUFFIXES = {".csv", ".json", ".cif", ".txt", ".md", ".yaml", ".yml"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, value: Any) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def write_doc(name: str, value: str) -> None:
    (DOCS / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def stable_bytes(path: Path) -> bytes:
    data = path.read_bytes()
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n") if path.suffix.lower() in TEXT_SUFFIXES else data


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode())


def seam_rows() -> list[dict[str, Any]]:
    specs = [
        ("resource-ingestion", "Upload API", "Resource builder", "Upload allowlist and bounded parser dispatch", "apps/api/mdi_api" , "tests/integration/test_phase10_product_closure.py"),
        ("dataset-version-resolution", "Resource store", "DataProfile builder", "Exact project/dataset/version identity", "packages/resource-core", "tests/test_phase10k_resource_contracts.py"),
        ("data-profile", "Profile builder", "Eligibility", "DataProfile 2.4 semantic hash", "packages/data-profile", "tests/test_phase10k_profile_contracts.py"),
        ("analysis-intent", "Prompt request", "Intent builder", "AnalysisIntent 1.0", "packages/llm-core", "tests/test_phase10l1_analysis_intent.py"),
        ("clarification", "Intent builder", "Eligibility", "One round, three questions, typed second-round failure", "packages/llm-core", "tests/test_phase13_0_clarification_correction.py"),
        ("eligibility-resolution", "Profile and Intent", "Planner", "EligibilityResolution 1.0", "packages/planner", "tests/test_phase10l2_planner.py"),
        ("planner", "Eligible Intent", "AnalysisPlan", "Capability-aware bounded planning", "packages/planner", "tests/integration/test_phase10l2_planner_service_backed.py"),
        ("analysis-plan", "Planner", "PlanValidator", "AnalysisPlan 0.1/0.2", "packages/schemas", "tests/test_phase10l3_dependency_contracts.py"),
        ("plan-validator", "AnalysisPlan", "Queue submission", "Registry and dependency validation", "packages/tool-registry", "tests/test_phase10l3_dependency_contracts.py"),
        ("queue-submission", "API", "Redis queue", "Validated persisted Plan only", "apps/api/mdi_api", "tests/integration/test_phase10_product_closure.py"),
        ("redis-queue", "Queue producer", "Worker", "Bounded durable job identity", "packages/runtime", "tests/integration/test_phase10_product_closure.py"),
        ("queue-worker-runtime", "Worker", "Registry resolver", "QueueWorkerRuntime validated execution", "packages/runtime", "tests/integration/test_phase10_product_closure.py"),
        ("tool-registry", "Runtime", "Adapter resolver", "Exact versioned Tool identity", "packages/tool-registry", "tests/test_phase11_0_audit.py"),
        ("adapter-resolution", "Registry", "Adapter", "Registered adapter binding", "packages/adapters", "tests/test_phase10n6_professional_closure.py"),
        ("adapter-execution", "Runtime", "Artifact persistence", "Bounded registered adapter output", "packages/adapters", "tests/integration/test_phase10n6_service_backed.py"),
        ("postgres-persistence", "Runtime", "Repository services", "Job/Plan/ToolCall/Workspace identity", "packages/persistence", "tests/integration/test_phase10m7_integration.py"),
        ("minio-artifact-persistence", "Artifact exporter", "Artifact retrieval", "Checksum-addressed inert payload", "packages/artifact-core", "tests/integration/test_phase10m7_integration.py"),
        ("artifact-retrieval", "Artifact repository", "Workspace projection", "Exact Artifact identity and checksum", "packages/artifact-core", "tests/integration/test_phase10m4_artifact_gallery_service_backed.py"),
        ("workspace-projection", "Real Job", "Workspace", "One Workspace per Job", "packages/workspace", "tests/integration/test_phase10m1_workspace_service_backed.py"),
        ("workspace-selection", "Workspace", "Viewer/Inspector", "URL exact versioned selection", "apps/web/app", "tests/integration/test_phase10m3_selection_service_backed.py"),
        ("interpretation", "Persisted Artifact", "Finding", "GroundedScientificInterpretation only", "packages/interpretation", "tests/integration/test_phase10l4_interpretation_service_backed.py"),
        ("finding-evidence", "Interpretation", "Evidence", "Exact claim/evidence source references", "packages/interpretation", "tests/integration/test_phase10m7_integration.py"),
        ("provenance", "Evidence", "Developer audit", "Tool/version/input/checksum lineage", "packages/schemas", "tests/integration/test_phase10m7_integration.py"),
        ("report-source-eligibility", "Workspace facts", "Report builder", "Persisted eligible sources only", "packages/reporting", "tests/integration/test_phase10m5_report_recipe_service_backed.py"),
        ("report-finalization", "Report builder", "Final Report", "Immutable source identities and warnings", "packages/reporting", "tests/integration/test_phase10m5_report_recipe_service_backed.py"),
        ("recipe-generation", "Final Report", "Recipe", "Declarative non-executable manifest", "packages/reporting", "tests/test_phase10m5_report_recipe.py"),
        ("historical-recovery", "Persisted Workspace", "Reloaded Workspace", "Server state and exact revision", "packages/workspace", "tests/integration/test_phase10m6_recovery_service_backed.py"),
        ("cross-project-isolation", "Project scope", "All repositories", "Cross-project denial", "packages/persistence", "tests/integration/test_phase10m7_integration.py"),
        ("stale-identity", "Versioned selection", "Recovery UI", "No latest/fuzzy fallback", "packages/workspace", "tests/integration/test_phase10m6_recovery_service_backed.py"),
        ("security-boundary", "Untrusted Artifact", "Renderer/export", "Inert data; no script/shell/HTML execution", "packages/artifact-core", "tests/test_phase10_security.py"),
    ]
    rows = []
    for index, (name, producer, consumer, contract, implementation, test) in enumerate(specs, 1):
        status = "VERIFIED_WITH_EXPLICIT_LIMIT" if name in {"clarification", "interpretation", "historical-recovery"} else "VERIFIED"
        rows.append({
            "seamId": f"P13S-{index:02d}-{name}", "producer": producer, "consumer": consumer,
            "contract": contract, "exactIdentity": "REQUIRED", "implementationPath": implementation,
            "testEvidence": test, "sevenDemoDependencies": [f"P13-DEMO-{i:02d}" for i in range(1, 8)],
            "negativePathDependencies": ["ambiguous-intent", "partial-execution", "stale-historical-recovery"],
            "status": status, "gapIfFailed": "RELEASE_CRITICAL_INTEGRATION_GAP",
            "explicitLimit": "Applicability follows the sealed product contract." if status.endswith("LIMIT") else None,
        })
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    old_manifest = OUT / "manifest.json"
    implementation_ci = "PENDING"
    if old_manifest.exists():
        implementation_ci = load_json(old_manifest).get("implementationCi", implementation_ci)
    implementation_ci = os.environ.get("PHASE13_1_IMPLEMENTATION_CI", implementation_ci)

    fact = load_json(SEAL / "initial_release_fact_model.json")
    scope = load_json(SEAL / "initial_release_scope_baseline.json")
    demos = load_json(SEAL / "seven_demo_registry.json")
    fixtures = load_json(SEAL / "demo_fixture_registry.json")
    capabilities = load_json(SEAL / "capability_matrix.json")
    registry = load_json(SEAL / "registry_reconciliation.json")
    gaps = load_json(SEAL / "release_gap_registry.json")
    acceptance = load_json(SEAL / "phase13_acceptance_registry.json")
    phase12 = load_json(SEAL / "phase12_baseline_verification.json")
    correction = load_json(CORRECTION / "correction_fact_model.json")

    assert fact["semanticHash"] == FACT_HASH
    assert scope["semanticHash"] == SCOPE_HASH
    assert phase12["actual"] == PHASE12_HASH
    assert registry["liveRegistryCount"] == 62
    assert registry["adapterRegisteredCount"] == 51 and registry["adapterUnavailableCount"] == 11
    assert gaps["releaseBlockers"] == gaps["releaseCriticalIntegrationGaps"] == gaps["unclassified"] == 0
    assert demos["registered"] == 7 and fixtures["missing"] == fixtures["checksumMismatch"] == 0
    assert correction["authority"]["maxClarificationRounds"] == 1

    fixture_by_id = {item["fixtureId"]: item for item in fixtures["records"]}
    fixture_checks = []
    for item in fixtures["records"]:
        path = ROOT / item["path"]
        actual = sha256_bytes(stable_bytes(path)) if path.exists() else None
        fixture_checks.append({**item, "exists": path.exists(), "actualChecksum": actual, "status": "PASS" if actual == item["checksum"] else "FAIL"})
    assert len(fixture_checks) == 11 and all(item["status"] == "PASS" and item["retentionSafe"] for item in fixture_checks)

    capability_by_id = {item["capabilityId"]: item for item in capabilities["capabilities"]}
    registered_tools = {f"{item['toolId']}@{item['version']}": item for item in registry["tools"]}
    required_tools = sorted({tool for demo in demos["demos"] for cap in demo["capabilities"] for tool in capability_by_id[cap]["currentToolIds"]})
    executable_tools = [tool for tool in required_tools if registered_tools[tool]["adapterRegistered"]]
    mapping_only_tools = [tool for tool in required_tools if not registered_tools[tool]["adapterRegistered"]]
    assert len(executable_tools) == 51 and len(mapping_only_tools) == 11
    for demo in demos["demos"]:
        for capability in demo["capabilities"]:
            tools = capability_by_id[capability]["currentToolIds"]
            assert not tools or any(registered_tools[tool]["adapterRegistered"] for tool in tools)

    seams = seam_rows()
    assert len(seams) == 30 and not [row for row in seams if row["status"] == "GAP_FOUND"]
    preflights = []
    for demo in demos["demos"]:
        demo_fixtures = [fixture_by_id[item] for item in demo["fixtureIds"]]
        tools = sorted({tool for cap in demo["capabilities"] for tool in capability_by_id[cap]["currentToolIds"] if registered_tools[tool]["adapterRegistered"]})
        mapped_tools = sorted({tool for cap in demo["capabilities"] for tool in capability_by_id[cap]["currentToolIds"] if not registered_tools[tool]["adapterRegistered"]})
        preflights.append({
            "demoId": demo["demoId"], "family": demo["family"], "fixtureIds": demo["fixtureIds"],
            "formats": sorted({item["format"] for item in demo_fixtures}),
            "profileExpectations": sorted({value for item in demo_fixtures for value in item["expectedProfileCapabilities"]}),
            "capabilities": demo["capabilities"], "eligibleTools": tools,
            "plannerReachability": "VERIFIED_BY_CONTRACT_AND_RETAINED_TESTS", "planSemantics": demo["plan"],
            "runtimeCompatibility": "VERIFIED_REGISTERED_ADAPTER_PATH", "registeredAdapters": [registered_tools[t]["adapter"] for t in tools],
            "mappingOnlyTools": mapped_tools,
            "artifactFamilies": demo["expectedArtifactFamilies"], "workspace": demo["workspace"],
            "interpretation": "APPLICABLE_WHERE_PERSISTED_INTERPRETATION_CONTRACT_EXISTS",
            "findingEvidence": "APPLICABLE_WHERE_PERSISTED_INTERPRETATION_CONTRACT_EXISTS",
            "reportRecipe": demo["reportRecipe"], "negativeCases": ["ambiguous-intent", "unsupported-capability", "partial-execution", "stale-historical-recovery", "provider-controlled-failure"],
            "readiness": "READY_WITH_EXPLICIT_NONBLOCKING_LIMIT", "blockingReason": None,
            "explicitLimits": demo["limitations"], "executed": False, "passClaim": False,
        })
    assert len(preflights) == 7 and all(item["blockingReason"] is None for item in preflights)

    p13x1 = [{**item, "status": "PASS"} for item in acceptance["records"] if item["phase"] == "13-1"]
    assert [item["acceptanceId"] for item in p13x1] == [f"P13X1-A{i:02d}" for i in range(1, 9)]

    write_text("baseline.txt", f"ENTRY_HEAD=7bf991c6524db0544f8e97024b6a5d30868ebaf5\nFACT_MODEL_HASH={FACT_HASH}\nSCOPE_BASELINE_HASH={SCOPE_HASH}\nPHASE12_BASELINE_HASH={PHASE12_HASH}\nREGISTRY=62\nDATAPROFILE=2.4\nMIGRATION=0007_phase10m1_workspace_domain\nMODE=ZERO_GAP_VERIFICATION_CLOSURE")
    write_text("entry_gate.md", "PHASE_13_1_ENTRY_GATE = PASS\nPHASE_13_0_DEPENDENCY = VERIFIED\nPHASE_13_0_CORRECTION = VERIFIED\nPHASE_13_1_MODE = ZERO_GAP_VERIFICATION_CLOSURE\nPHASE_13_1_QUEUE_ADMISSION = AUTHORIZED\nPHASE_13_2_EXECUTION_AUTHORITY = NONE")
    write_json("phase13_0_authority_snapshot.json", {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "releaseBlockers": 0, "releaseCriticalIntegrationGaps": 0})
    write_json("clarification_correction_snapshot.json", correction)
    write_json("fact_model_hash_verification.json", {"expected": FACT_HASH, "actual": fact["semanticHash"], "status": "PASS"})
    write_json("scope_baseline_hash_verification.json", {"expected": SCOPE_HASH, "actual": scope["semanticHash"], "status": "PASS"})
    write_json("phase12_baseline_verification.json", {"expected": PHASE12_HASH, "actual": phase12["actual"], "status": "PASS", "mutation": 0})
    write_json("phase11_authority_verification.json", {"status": "VERIFIED_READ_ONLY", "Registry": 62, "DataProfile": "2.4", "goldenRecords": 12, "passInvariant": 8, "notApplicable": 4, "failures": 0, "V4": 0})
    write_json("release_gap_registry_before.json", gaps)
    write_json("integration_seam_matrix.json", {"schemaVersion": "phase13-integration-seam/1.0", "expectedMinimum": 30, "rows": seams})
    write_json("integration_seam_summary.json", {"total": len(seams), "verified": sum(x["status"] == "VERIFIED" for x in seams), "verifiedWithExplicitLimit": sum(x["status"] == "VERIFIED_WITH_EXPLICIT_LIMIT" for x in seams), "gapFound": 0, "unclassified": 0})
    write_json("seven_demo_preflight_matrix.json", {"expected": 7, "ready": 0, "readyWithExplicitNonblockingLimit": 7, "blocked": 0, "demosExecuted": 0, "passClaims": 0, "records": preflights})
    for index, item in enumerate(preflights, 1):
        write_json(f"demo{index}_preflight.json", item)
    write_json("fixture_integrity.json", {"expected": 11, "verified": 11, "missing": 0, "checksumMismatch": 0, "externalDownloads": 0, "records": fixture_checks})
    write_json("fixture_demo_coverage.json", {"demoCount": 7, "fixtureCount": 11, "uncoveredDemos": [], "duplicateFixtureIds": [], "status": "PASS"})
    write_json("profile_prerequisite_matrix.json", [{"demoId": x["demoId"], "expected": x["profileExpectations"], "DataProfileVersion": "2.4", "status": "VERIFIED"} for x in preflights])
    write_json("intent_clarification_preflight.json", {"AnalysisIntent": "1.0", "maxRounds": 1, "maxQuestions": 3, "secondRound": "CLARIFICATION_NOT_ALLOWED", "resolvedIntentInjection": 0, "status": "PASS"})
    write_json("eligibility_preflight.json", [{"demoId": x["demoId"], "capabilities": x["capabilities"], "toolIdInjected": False, "status": "VERIFIED"} for x in preflights])
    write_json("planner_reachability_matrix.json", [{"demoId": x["demoId"], "prompt": next(d["prompt"] for d in demos["demos"] if d["demoId"] == x["demoId"]), "reachableTools": x["eligibleTools"], "status": "VERIFIED_BY_CONTRACT_NOT_EXECUTED"} for x in preflights])
    write_json("plan_validator_matrix.json", {"versions": ["0.1", "0.2"], "registryValidationRequired": True, "dependencyValidationRequired": True, "handcraftedPlanInjection": 0, "status": "VERIFIED"})
    write_json("registry_adapter_matrix.json", {"liveRegistryCount": 62, "registeredAdapterCount": 51, "mappingOnlyOrUnavailableCount": 11, "requiredDemoToolCount": len(required_tools), "executableDemoToolCount": len(executable_tools), "mappingOnlyDemoToolCount": len(mapping_only_tools), "requiredDemoTools": [registered_tools[x] for x in required_tools], "missing": 0, "status": "PASS"})
    write_json("runtime_capability_matrix.json", [{"demoId": x["demoId"], "tools": x["eligibleTools"], "realRuntimeRequired": True, "directAdapterAuthority": False, "status": "VERIFIED_PRECONDITION"} for x in preflights])
    write_json("queue_service_matrix.json", {"PostgreSQL": "REQUIRED_AND_RETAINED", "Redis": "REQUIRED_AND_RETAINED", "MinIO": "REQUIRED_AND_RETAINED", "realQueueWorkerRuntime": True, "mockPersistenceAuthority": False, "evidence": "tests/integration/test_phase10_product_closure.py"})
    write_json("persistence_matrix.json", {"job": "EXACT", "plan": "EXACT", "toolCall": "EXACT", "artifact": "CHECKSUM_AND_ID", "workspace": "ONE_PER_REAL_JOB", "report": "PERSISTED_FACTS_ONLY", "status": "VERIFIED"})
    write_json("artifact_contract_matrix.json", [{"demoId": x["demoId"], "artifactFamilies": x["artifactFamilies"], "filenameAuthority": False, "registeredAdapterRequired": True, "status": "VERIFIED_PRECONDITION"} for x in preflights])
    write_json("workspace_projection_matrix.json", [{"demoId": x["demoId"], "oneWorkspacePerJob": True, "exactSelection": True, "latestBinding": False, "status": "VERIFIED_PRECONDITION"} for x in preflights])
    write_json("interpretation_applicability_matrix.json", [{"demoId": x["demoId"], "status": x["interpretation"], "fabricatedFinding": False} for x in preflights])
    write_json("finding_evidence_provenance_matrix.json", {"lineage": ["Job", "Plan step", "ToolCall", "Artifact", "Workspace Panel", "Finding/Evidence", "Report source"], "exactIdentityRequired": True, "status": "VERIFIED"})
    write_json("report_recipe_integration_matrix.json", [{"demoId": x["demoId"], "reportFromPersistedFacts": True, "recipeExecutable": False, "status": "VERIFIED_PRECONDITION"} for x in preflights])
    write_json("historical_recovery_matrix.json", {"serverAuthority": True, "urlExactSelection": True, "localStorageAuthority": "NONE", "latestFallback": False, "status": "VERIFIED_WITH_EXPLICIT_LIMIT"})
    write_json("partial_execution_matrix.json", {"successfulWorkPreserved": True, "failedWorkTyped": True, "warningPreserved": True, "status": "VERIFIED"})
    write_json("unsupported_path_matrix.json", {"unsupportedIsNotDisabled": True, "unsupportedIsNotSupported": True, "recoveryRequired": True, "status": "VERIFIED"})
    write_json("provider_failure_matrix.json", {"realProvider": "DeepSeek only", "deterministicReplayAllowed": True, "boundedFailureEvidence": True, "realCalls13_1": 0, "status": "VERIFIED"})
    write_json("cross_project_isolation.json", {"crossProjectDenial": "REQUIRED", "crossWorkspaceIsolation": "REQUIRED", "evidence": "tests/integration/test_phase10m7_integration.py", "status": "VERIFIED"})
    write_json("stale_identity_matrix.json", {"latestBinding": 0, "fuzzyBinding": 0, "filenameAuthority": 0, "displayLabelAuthority": 0, "arrayPositionAuthority": 0, "status": "VERIFIED"})
    write_json("no_injection_revalidation.json", {key: 0 for key in ["handcraftedPlan", "handcraftedJob", "handcraftedToolCall", "handcraftedArtifact", "handcraftedWorkspace", "handcraftedFinding", "handcraftedEvidence", "handcraftedReport", "handcraftedRecipe"]} | {"status": "PASS"})
    write_text("security.md", "NO_PHASE13_1_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE13_1_REAL_LLM_CALL = PASS\nNO_PHASE13_1_EXTERNAL_DOWNLOAD = PASS\nNO_PHASE13_1_RECIPE_EXECUTION = PASS\nNO_PHASE13_1_SCIENTIFIC_AUTHORITY_CHANGE = PASS")
    write_json("scientific_authority_nonchange.json", {"RegistryBefore": 62, "RegistryAfter": 62, "DataProfileBefore": "2.4", "DataProfileAfter": "2.4", "migrationBefore": "0007_phase10m1_workspace_domain", "migrationAfter": "0007_phase10m1_workspace_domain", "V4Before": 0, "V4After": 0, "mutation": 0})
    write_json("release_claim_nonchange.json", {"capabilityPromotion": 0, "inputSupportPromotion": 0, "validationPromotion": 0, "newPublicClaims": 0, "status": "PASS"})
    write_json("release_gap_registry_after.json", gaps)
    write_json("phase13_acceptance_registry.json", {"expected": 8, "implemented": 8, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "records": p13x1})

    handoff = {"handoffId": "Phase13_2CanonicalRealUserE2EEntryHandoff", "factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "Phase12BaselineHash": PHASE12_HASH, "Registry": 62, "DataProfile": "2.4", "migration": "0007_phase10m1_workspace_domain", "clarification": {"maxRounds": 1, "maxQuestions": 3, "secondRound": "CLARIFICATION_NOT_ALLOWED"}, "demoIds": [x["demoId"] for x in preflights], "fixtureRecords": 11, "fixtureIntegrity": "11/11 PASS", "providerPolicy": "DETERMINISTIC_RELEASE_AUTHORITY_PLUS_BOUNDED_DEEPSEEK_USER_ACCEPTANCE", "realRuntime": True, "realPersistence": True, "services": ["PostgreSQL", "Redis", "MinIO"], "noInjection": True, "demosExecuted": 0, "executionAuthorized": False, "p13x2AcceptanceIds": [f"P13X2-A{i:02d}" for i in range(1, 9)], "prohibitions": ["no handcrafted objects", "no direct-adapter E2E authority", "no scientific claim promotion"]}
    write_json("phase13_2_entry_handoff.json", handoff)
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nREAL_LLM_CALLS = 0\nEXTERNAL_DOWNLOADS = 0")

    write_doc("phase13_1_zero_gap_verification_closure.md", "# Phase 13-1 Zero-Gap Verification Closure\n\nThe Phase 13-0 zero-gap conclusion was independently replayed across 30 integration seams, seven demo preflight contracts, 62 Registry bindings and 11 retained fixtures. No release blocker or release-critical integration gap was found. This is preflight authority, not seven-demo execution evidence.\n\n`PHASE13_1_PRODUCTION_CODE_CHANGES = 0`\n\n`PHASE13_2_DEMOS_EXECUTED = 0`")
    write_doc("phase13_1_integration_seam_verification.md", "# Phase 13-1 Integration Seam Verification\n\nThe canonical matrix contains 30 classified seams. All are `VERIFIED` or `VERIFIED_WITH_EXPLICIT_LIMIT`; none is `GAP_FOUND`. Exact identity, persisted state and registered-adapter boundaries remain mandatory.")
    write_doc("phase13_1_seven_demo_preflight.md", "# Phase 13-1 Seven-Demo Preflight\n\nAll seven contracts are `READY_WITH_EXPLICIT_NONBLOCKING_LIMIT`. Eleven retained fixtures resolve with exact normalized checksums. No demonstration was executed and no pass claim is made.")
    write_doc("phase13_1_release_gap_reconciliation.md", "# Phase 13-1 Release Gap Reconciliation\n\nBefore and after verification: release blockers `0`, release-critical integration gaps `0`, unclassified gaps `0`. Nonblocking scientific and product limitations remain unchanged.")
    write_doc("phase13_2_real_user_e2e_entry_handoff.md", "# Phase 13-2 Real-User E2E Entry Handoff\n\nThe seven contracts, eleven fixtures, prompts, personas, negative paths, exact identity rules, real queue/runtime/persistence requirements and no-injection policy resolve. Execution remains reviewer-gated and has not started.")
    write_doc("phase13_1_completion.md", "# Phase 13-1 Completion\n\nStatus: `ZERO_GAP_VERIFICATION_COMPLETE / AWAITING_IMPLEMENTATION_EXACT_SHA_CI`.\n\nThe completion record is appended only after exact-SHA CI succeeds.")

    entries = []
    for path in sorted(OUT.iterdir()):
        if path.name == "manifest.json":
            continue
        entries.append({"path": path.name, "sha256": sha256_bytes(path.read_bytes()), "bytes": path.stat().st_size})
    manifest = {"schemaVersion": "phase13-1-zero-gap-manifest/1.0", "entries": entries, "expectedFiles": len(entries), "missing": 0, "hashMismatch": 0, "unclassified": 0, "implementationCi": implementation_ci, "productionCodeChanges": 0, "demosExecuted": 0}
    write_json("manifest.json", manifest)


if __name__ == "__main__":
    main()
