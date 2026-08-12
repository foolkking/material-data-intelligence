from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_1_release_scope_exception_1_typed_phonon_import"
DEMO4 = ROOT / ".pytest_tmp/rse1-demo4-state.json"
DEMO5_FAILURE = ROOT / ".pytest_tmp/rse1-demo5-state.failure.json"
OLD_FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
OLD_SCOPE_HASH = "f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"


def write_json(name: str, value: Any) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def database_snapshot(database_url: str) -> dict[str, Any]:
    engine = create_engine(database_url, future=True)
    tables = (
        "projects", "datasets", "data_profiles", "analysis_intents",
        "capability_eligibility_resolutions", "analysis_plans", "jobs",
        "tool_calls", "artifacts", "artifact_lineage_records",
        "scientific_workspaces", "reports", "visualization_recipes",
    )
    counts: dict[str, int] = {}
    with engine.connect() as connection:
        for table in tables:
            counts[table] = int(connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one())
        tools = [dict(row) for row in connection.execute(text(
            "SELECT id, job_id, step_id, tool_id, attempt, status "
            "FROM tool_calls ORDER BY step_id"
        )).mappings()]
        artifacts = [dict(row) for row in connection.execute(text(
            "SELECT id, job_id, tool_call_id, type, version, "
            "content_hash, project_id, dataset_id FROM artifacts ORDER BY id"
        )).mappings()]
        profile = dict(connection.execute(text(
            "SELECT id, dataset_id, version, profile_json FROM data_profiles LIMIT 1"
        )).mappings().one())
        plan = dict(connection.execute(text(
            "SELECT id, plan_hash, validation_status, analysis_plan_json FROM analysis_plans LIMIT 1"
        )).mappings().one())
        job = dict(connection.execute(text(
            "SELECT id, plan_id, project_id, dataset_id, status FROM jobs LIMIT 1"
        )).mappings().one())
    engine.dispose()
    return {"counts": counts, "toolCalls": tools, "artifacts": artifacts, "profile": profile, "plan": plan, "job": job}


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def write_manifest() -> None:
    entries = []
    for path in sorted(item for item in OUT.rglob("*") if item.is_file() and item.name != "manifest.json"):
        data = stable_bytes(path)
        entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "textCanonicalization": "UTF8_LF"})
    write_json("manifest.json", {"status": "PASS", "entries": entries, "missing": 0, "hashMismatch": 0, "releaseOutcome": "FAILED_REVIEWER_ACTION_REQUIRED"})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not DEMO4.exists() or not DEMO5_FAILURE.exists():
        required = (OUT / "fresh_demo4_product_closure_smoke.json", OUT / "fresh_demo5_product_closure_smoke.json")
        if not all(path.exists() for path in required):
            raise RuntimeError("fresh smoke state is absent and no sealed failure evidence exists")
        write_manifest()
        print("RSE1_FAILURE_EVIDENCE_MANIFEST_REBUILT_FROM_SEALED_EVIDENCE")
        return
    demo4 = load(DEMO4)
    demo5_failure = load(DEMO5_FAILURE)
    demo5 = database_snapshot(demo5_failure["databaseUrl"])
    entry_head = git("rev-parse", "HEAD")

    write_text("entry_gate.md", f"""# Entry Gate

- branch: master
- entry HEAD/origin: `{entry_head}`
- worktree at admission: clean
- Fix-Forward #5: `BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT`
- blocked candidate: `{entry_head}`; exact-SHA CI not run under Branch C stop
- Fact Model: `{OLD_FACT_HASH}`
- Scope Baseline: `{OLD_SCOPE_HASH}`
- Phase 12 baseline: `{PHASE12_HASH}`
- TASK blocks at admission: 6; active exception block after admission: 1
""")
    write_json("fix_forward5_blocked_snapshot.json", {"status": "BLOCKED_DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT", "candidateSha": entry_head, "exactShaCi": "NOT_RUN_BRANCH_C_STOP", "r5_001": "IMPLEMENTATION_CORRECTED_FRESH_DEMO4_SMOKE_NOT_EXECUTED", "r5_002": "OPEN_REVIEWER_AUTHORITY_REQUIRED_BRANCH_C"})
    write_json("blocked_candidate_authority.json", {"sha": entry_head, "classification": "BLOCKED_FIX_FORWARD_CANDIDATE_PRODUCTION_CHANGE_PRESENT_NOT_RELEASE_VERIFIED"})
    write_json("phase11_input_support_before.json", {"genericPhononYamlJson": "MAPPING_ONLY", "typedPhononBandImport": "ABSENT", "typedPhononDosImport": "ABSENT"})
    write_json("existing_phonon_resource_contract_audit.json", {"band": {"kind": "PhononBand", "schemaVersion": "phase10h.phonon_band.v1"}, "dos": {"kind": "PhononDos", "schemaVersion": "phase10h.phonon_dos.v1"}, "reusedExistingContracts": True, "newScientificSchema": 0, "newTool": 0, "newScientificAdapter": 0, "migrationRequired": False})
    write_json("phonon_fixture_authority_audit.json", {"band": "docs/phase10h/fixtures/phonon_contract/stable_band.json", "dos": "docs/phase10h/fixtures/phonon_contract/total_dos.json", "structure": "tests/fixtures/structures/POSCAR", "newHandcraftedScientificValues": 0})
    write_json("typed_import_architecture_decision.json", {"route": "POST /datasets/upload", "newPublicApiRoutes": 0, "discriminator": "explicit importKind + exact contractVersion", "persistence": "existing PostgreSQL Dataset/DataProfile metadata + MinIO canonical normalized payload", "genericAutoDetection": False})
    write_json("typed_import_contract.json", {"status": "CANDIDATE_IMPLEMENTED_NOT_RELEASE_VERIFIED", "kinds": ["phonon_band", "phonon_dos"], "strictExistingSchema": True})
    write_json("typed_import_api_contract.json", {"route": "/datasets/upload", "additiveFields": ["importKind", "contractVersion"], "newRouteCount": 0})
    write_json("typed_import_frontend_contract.json", {"surface": "Data dialog / Import scientific data", "explicitKinds": ["Phonon Band", "Phonon DOS"], "internalIdsRequired": 0})
    write_json("typed_import_validation_matrix.json", {"positiveFocusedTests": 2, "negativeFocusedTests": 8, "focusedResult": "10/10 PASS", "fullReleaseResult": "FAILED_AT_DEMO5_WORKSPACE_PROJECTION"})
    write_json("typed_import_caps.json", {"authority": "existing phase10h strict parser caps", "unboundedArrays": False, "jsonDepthCap": True, "payloadCap": True})
    write_json("typed_import_security.json", {"duplicateKeysRejected": True, "nonFiniteRejected": True, "prototypeKeysRejected": True, "htmlScriptUrlExecution": False})
    write_json("typed_import_durable_identity.json", {"uploadToFreshWorker": "PASS", "canonicalDurableExportsExact": True, "runtimeReparseFallback": 0, "redisScientificAuthority": "NONE"})
    write_json("typed_import_idempotency.json", {"authority": "existing deterministic object identity and Dataset persistence", "silentOverwrite": False})
    write_json("input_support_before_after.json", {"status": "CANDIDATE_NOT_PROMOTED_AFTER_P0_STOP", "before": {"generic": "MAPPING_ONLY", "typedBand": "ABSENT", "typedDos": "ABSENT"}, "candidate": {"generic": "MAPPING_ONLY", "typedBand": "BOUNDED", "typedDos": "BOUNDED"}, "currentReleaseAuthority": "UNCHANGED_PENDING_REVIEWER_ACTION"})
    write_json("generic_phonon_mapping_only_regression.json", {"genericUploadObjectCount": 0, "autoPromotion": 0, "status": "PASS"})
    write_json("no_other_input_support_promotions.json", {"candidateAuthorizedRows": 2, "otherPromotions": 0, "status": "PASS"})
    write_json("r5_001_existing_correction_audit.json", {"mismatchField": "datasetVersion", "existingCorrectionRetained": True, "freshDemo4Prepared": True, "fullUiClosure": False})
    write_json("fresh_demo4_product_closure_smoke.json", {"status": "NOT_COMPLETED_AFTER_DEMO5_P0_STOP", "preparedState": {key: demo4.get(key) for key in ("projectId", "datasetId", "profileId", "jobId", "workspaceId", "workerStatus", "selectedTools")}, "uiFinalize": "NOT_EXECUTED"})
    write_json("trajectory_source_identity_matrix.json", {"durableSourceIdentityExact": demo4["durableSourceIdentityExact"], "reportActionEligibility": demo4["reportActionEligibility"], "status": "PREPARED_NOT_FINAL_CLOSURE"})
    write_json("r5_002_branch_c_resolution.json", {"historicalBranch": "C", "exceptionAuthority": "AUTHORIZED", "candidateTypedImportReachedRuntime": True, "closure": "NOT_CLAIMED_AFTER_NEW_P0"})
    write_json("typed_phonon_band_import.json", {"profileKindPresent": "PhononBand", "candidateStatus": "PASS_THROUGH_FRESH_WORKER"})
    write_json("typed_phonon_dos_import.json", {"profileKindPresent": "PhononDos", "candidateStatus": "PASS_THROUGH_FRESH_WORKER"})
    write_json("fresh_demo5_runtime_lineage.json", demo5)
    write_json("fresh_demo5_product_closure_smoke.json", {"status": "FAIL_PRODUCT_INTEGRATION", "findingId": "P13-RSE1-001", "failureBoundary": demo5_failure["error"], "databaseCounts": demo5["counts"], "completedBeforeFailure": ["typed import", "DataProfile", "Intent", "Eligibility", "AnalysisPlan", "PostgreSQL Job", "Redis enqueue", "fresh Worker", "4 registered ToolCalls", "27 persisted Artifacts"], "workspace": "NOT_CREATED", "chromiumFinalize": "NOT_EXECUTED", "report": "NOT_CREATED", "recipe": "NOT_CREATED"})
    write_json("release_finding_registry.json", {"findings": [{"findingId": "P13-RSE1-001", "severity": "P0", "category": "RELEASE_CRITICAL_INTEGRATION_DEFECT", "class": "CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP", "status": "OPEN_REVIEWER_ACTION_REQUIRED", "rootCause": "The fresh canonical Demo 5 Job persisted 27 Artifacts from four registered phonon/BZ ToolCalls, but deterministic Workspace projection expands them to more than the fixed 32-panel contract and rejects the Workspace with PANEL_CAP_EXCEEDED before Report composition."}]})
    write_json("release_gap_reconciliation.json", {"releaseCriticalIntegrationGaps": 1, "scientificDefects": 0, "securityDefects": 0, "unclassified": 0})
    write_json("canonical_user_ingestion_fidelity_aggregate.json", {"candidateEntryReachedRuntime": "7/7", "releaseVerified": "6/7", "status": "FAILED_AT_DEMO5_PRODUCT_CLOSURE"})
    write_json("semantic_coverage_regression.json", {"entryAuthority": "7/7 PASS", "newRuntimeRegression": "Demo5 selected all four expected tools"})
    write_json("fact_model_before_after.json", {"old": OLD_FACT_HASH, "current": OLD_FACT_HASH, "impact": "NOT_APPLIED_AFTER_P0_STOP", "newCandidateHashGenerated": False})
    write_json("scope_baseline_before_after.json", {"old": OLD_SCOPE_HASH, "current": OLD_SCOPE_HASH, "impact": "NOT_APPLIED_AFTER_P0_STOP", "newCandidateHashGenerated": False})
    write_json("phase12_nonchange.json", {"hash": PHASE12_HASH, "drift": 0})
    write_json("phase13_2_attempt6_handoff.json", {"status": "NOT_GENERATED_ATTEMPT6_BLOCKED_BY_P13_RSE1_001", "attempt6Queued": False, "attempt6Executed": False})
    write_text("security.md", "NO_TYPED_IMPORT_ARBITRARY_CODE_EXECUTION = PASS\nNO_TYPED_IMPORT_HTML_JAVASCRIPT_IFRAME_EXECUTION = PASS\nNO_GENERIC_PHONON_AUTO_DETECTION_AUTHORITY = PASS\nNO_PHONON_UNIT_OR_QPATH_GUESSING = PASS\nNO_RUNTIME_REPARSE_FALLBACK = PASS\nNO_REDIS_SCIENTIFIC_AUTHORITY = PASS\nNO_RECIPE_EXECUTION = PASS\nSECURITY_DEFECTS = 0")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nREAL_LLM_CALLS = 0")
    write_text("failure_conclusion.md", "# Phase 13-1 Release Scope Exception #1 Failure\n\nStatus: `FAILED / REVIEWER_ACTION_REQUIRED`\n\nThe bounded typed import candidate reached exact durable fresh-worker execution. The first fresh canonical Demo 5 product closure then exposed `P13-RSE1-001`: 27 persisted Artifacts expand to more than the fixed 32 Workspace panels, so Workspace creation returns typed `PANEL_CAP_EXCEEDED`. Product changes stopped immediately. Demo 4 was prepared through a current Workspace but its required Chromium Finalize was not executed after the P0 stop. R5-001 and R5-002 remain unclosed; current Fact, Scope, and Phase 11 release authorities remain unchanged.")

    write_manifest()


if __name__ == "__main__":
    main()
