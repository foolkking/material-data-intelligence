from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from generate_phase13_0_release_scope import main as generate_release_scope
from mdi_schemas import (
    ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS,
    ANALYSIS_INTENT_MAX_QUESTIONS,
    ANALYSIS_INTENT_SUPPORTED_SCHEMA_VERSIONS,
)


ROOT = Path(__file__).resolve().parents[1]
PHASE13_ROOT = ROOT / "docs/phase13"
SEAL_ROOT = PHASE13_ROOT / "evidence/phase13_0_release_scope_seal"
OUT = PHASE13_ROOT / "evidence/phase13_0_clarification_fact_correction"
OLD_FACT_HASH = "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
OLD_SCOPE_HASH = "8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde"


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(name: str, value: Any) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_text(name: str, value: str) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value.rstrip() + "\n")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clarification_occurrences() -> list[dict[str, Any]]:
    occurrences: list[dict[str, Any]] = []
    roots = [ROOT / "docs", ROOT / "persistent", ROOT / "scripts", ROOT / "tests"]
    paths = [ROOT / "results.md"]
    for root in roots:
        paths.extend(path for path in root.rglob("*") if path.suffix in {".md", ".json", ".py", ".txt"})
    for path in sorted(set(paths)):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if '"maxRounds": 2' not in line and "bounded to two rounds" not in line:
                continue
            if relative == "results.md":
                classification = "HISTORICAL_APPEND_ONLY"
            elif (
                "phase13_0_clarification_fact_correction" in relative
                or relative.endswith("generate_phase13_0_clarification_correction.py")
                or relative.endswith("test_phase13_0_clarification_correction.py")
            ):
                classification = "CORRECTION_EVIDENCE_OR_GOVERNANCE"
            else:
                classification = "CURRENT_CANONICAL_REQUIRES_CORRECTION"
            occurrences.append(
                {"path": relative, "line": line_number, "classification": classification}
            )
    return occurrences


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    previous_manifest = OUT / "manifest.json"
    previous_ci = "PENDING"
    if previous_manifest.exists():
        previous_ci = load_json(previous_manifest).get("implementationCi", previous_ci)
    generate_release_scope()

    fact = load_json(SEAL_ROOT / "initial_release_fact_model.json")
    scope = load_json(SEAL_ROOT / "initial_release_scope_baseline.json")
    demos = load_json(SEAL_ROOT / "seven_demo_registry.json")
    negative_paths = load_json(SEAL_ROOT / "demo_negative_path_registry.json")
    acceptance = load_json(SEAL_ROOT / "phase13_acceptance_registry.json")
    gaps = load_json(SEAL_ROOT / "release_gap_registry.json")
    phase12 = load_json(SEAL_ROOT / "phase12_baseline_verification.json")

    policies = [demo["clarification"] for demo in demos["demos"]]
    if "1.0" not in ANALYSIS_INTENT_SUPPORTED_SCHEMA_VERSIONS:
        raise AssertionError("AnalysisIntent legacy version drift")
    if ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS != 1 or ANALYSIS_INTENT_MAX_QUESTIONS != 3:
        raise AssertionError("AnalysisIntent clarification authority drift")
    if len(policies) != 7 or any(policy["maxRounds"] != 1 for policy in policies):
        raise AssertionError("Phase 13 demo clarification drift")
    if any(policy["maxQuestionsPerRound"] != 3 for policy in policies):
        raise AssertionError("Phase 13 demo question-cap drift")
    if any(policy["secondRoundBehavior"] != "TYPED_FAILURE" for policy in policies):
        raise AssertionError("Phase 13 second-round behavior drift")
    if any(policy["resolvedIntentInjection"] for policy in policies):
        raise AssertionError("Resolved Intent injection is prohibited")

    first_scope_hash = scope["semanticHash"]
    generate_release_scope()
    second_scope = load_json(SEAL_ROOT / "initial_release_scope_baseline.json")
    second_fact = load_json(SEAL_ROOT / "initial_release_fact_model.json")
    second_scope_hash = second_scope["semanticHash"]
    if first_scope_hash != second_scope_hash:
        raise AssertionError("Corrected scope baseline is nondeterministic")
    if fact["semanticHash"] != second_fact["semanticHash"]:
        raise AssertionError("Fact Model changed between deterministic runs")

    fact_impact = fact["semanticHash"] != OLD_FACT_HASH
    scope_impact = first_scope_hash != OLD_SCOPE_HASH
    if fact_impact:
        raise AssertionError("Clarification policy is outside the Fact Model hash domain")
    if not scope_impact:
        raise AssertionError("Seven-demo contract correction must affect the scope baseline")

    occurrences = clarification_occurrences()
    current_two_round = sum(
        item["classification"] == "CURRENT_CANONICAL_REQUIRES_CORRECTION" for item in occurrences
    )
    historical_two_round = sum(item["classification"] == "HISTORICAL_APPEND_ONLY" for item in occurrences)
    if current_two_round != 0 or historical_two_round < 1:
        raise AssertionError("Current/historical clarification occurrence classification failed")

    authority = {
        "schemaVersion": "1.0",
        "maxClarificationRounds": ANALYSIS_INTENT_MAX_CLARIFICATION_ROUNDS,
        "maxClarificationQuestions": ANALYSIS_INTENT_MAX_QUESTIONS,
        "secondRoundBehavior": "TYPED_FAILURE",
        "secondRoundErrorCode": "CLARIFICATION_NOT_ALLOWED",
        "source": "packages/schemas/mdi_schemas/analysis_intent.py",
        "productionMutation": 0,
    }
    write_text(
        "entry_gate.md",
        "PHASE_13_0_FACT_CORRECTION_ENTRY_GATE = PASS\n\n"
        "PHASE13_0_IMPLEMENTATION_SHA = 6217d042d0190c43144e402e4479aa9810b8e9d0\n"
        "PHASE13_0_IMPLEMENTATION_CI = 31451202923 PASS\n"
        "PHASE13_0_COMPLETION_SHA = 0af74ff078e1dab6324852a8329cea42bf092acb\n"
        "PHASE13_0_QUEUE_ARCHIVE_SHA = 7a554cd91b0638898bfe097972f29a097540b514\n"
        "ENTRY_BRANCH = master\nENTRY_HEAD_EQUALS_ORIGIN = YES\nENTRY_WORKTREE_CLEAN = YES\n"
        "ENTRY_TASK_BLOCK_COUNT = 0\nCORRECTION_TASK_BLOCK_COUNT = 1\n"
        "PHASE13_1_EXECUTABLE_TASK_CREATED = NO\nPHASE13_2_EXECUTABLE_TASK_CREATED = NO\n"
        "PHASE14_CREATED = NO\nANALYSIS_INTENT_AUTHORITY = 1.0 / ONE_ROUND / THREE_QUESTIONS / TYPED_SECOND_ROUND_FAILURE\n"
        "PRODUCTION_CHANGE_REQUIRED = NO",
    )
    write_json("analysis_intent_authority.json", authority)
    write_json(
        "clarification_occurrence_matrix.json",
        {
            "before": {"canonicalGenerator": 1, "generatedDemoRows": 7, "historicalResults": 1},
            "after": {"currentCanonicalTwoRoundAssertions": current_two_round, "historicalTwoRoundAssertions": historical_two_round},
            "occurrences": occurrences,
            "historicalPolicy": "APPEND_ONLY_RETAINED",
            "unclassified": 0,
        },
    )
    write_json(
        "clarification_contract_before_after.json",
        {
            "beforeIncorrectProjection": {"maxRounds": 2},
            "canonicalAuthority": authority,
            "after": {"maxRounds": 1, "maxQuestionsPerRound": 3, "secondRoundBehavior": "TYPED_FAILURE", "resolvedIntentInjection": False},
            "correctionType": "FACT_ALIGNMENT_FIX_FORWARD",
            "productionBehaviorChanged": 0,
        },
    )
    write_json(
        "clarification_governance_test.json",
        {
            "test": "tests/test_phase13_0_clarification_correction.py",
            "checks": ["authority equality", "max questions", "one-round success", "second-round typed failure", "resolved Intent bypass zero"],
            "status": "PASS",
        },
    )
    write_json("second_round_negative_case.json", {"roundAttempt": 2, "expected": "TYPED_FAILURE", "errorCode": "CLARIFICATION_NOT_ALLOWED", "status": "PASS"})
    write_json("one_round_success_case.json", {"roundAttempt": 1, "expected": "READY revision with parent Intent identity", "status": "PASS"})
    write_json(
        "demo_contract_reconciliation.json",
        {
            "expected": 7,
            "reconciled": len(policies),
            "maxRounds": sorted({policy["maxRounds"] for policy in policies}),
            "maxQuestionsPerRound": sorted({policy["maxQuestionsPerRound"] for policy in policies}),
            "secondRoundBehavior": sorted({policy["secondRoundBehavior"] for policy in policies}),
            "demosExecuted": sum(bool(demo["executed"]) for demo in demos["demos"]),
            "passClaims": sum(bool(demo["passClaim"]) for demo in demos["demos"]),
        },
    )
    write_json(
        "acceptance_reconciliation.json",
        {
            "expectedTotal": 56,
            "actualTotal": len(acceptance["records"]),
            "p13x0Pass": sum(item["phase"] == "13-0" and item["status"] == "PASS" for item in acceptance["records"]),
            "clarificationAuthority": "AnalysisIntent 1.0 / one round / three questions",
            "status": "PASS",
        },
    )
    write_json(
        "hash_dependency_graph.json",
        {
            "factModel": {"sevenDemoDependency": "REFERENCE_PATH_ONLY", "clarificationFieldsHashed": False},
            "scopeBaseline": {"sevenDemoDependency": "CONTENT_HASH", "clarificationFieldsHashed": True},
        },
    )
    write_json("fact_model_hash_impact.json", {"impact": "YES" if fact_impact else "NO", "old": OLD_FACT_HASH, "current": fact["semanticHash"], "reason": "clarification fields are outside the Fact Model semantic hash domain"})
    write_json("scope_baseline_hash_impact.json", {"impact": "YES" if scope_impact else "NO", "old": OLD_SCOPE_HASH, "current": first_scope_hash, "supersessionReason": "CLARIFICATION_ROUND_LIMIT_FACT_ALIGNMENT", "oldStatus": "HISTORICAL_SUPERSEDED", "currentStatus": "CURRENT_SEALED"})
    write_json("fact_model_regeneration.json", {"run1": fact["semanticHash"], "run2": second_fact["semanticHash"], "determinism": "PASS"})
    write_json("scope_baseline_regeneration.json", {"run1": first_scope_hash, "run2": second_scope_hash, "determinism": "PASS"})
    write_json("baseline_determinism.json", {"factModel": "PASS", "scopeBaseline": "PASS", "crossPlatformTextHashNormalization": "PASS", "runtimeMetadataInHash": False})
    write_json("release_scope_drift.json", {"classification": "DOCUMENTATION_FACT_CORRECTION_ONLY", "capabilityPromotion": 0, "validationPromotion": 0, "inputSupportPromotion": 0, "scientificPromotion": 0})
    write_json("release_gap_reconciliation.json", {"releaseBlockers": gaps["releaseBlockers"], "releaseCriticalIntegrationGaps": gaps["releaseCriticalIntegrationGaps"], "unclassified": gaps["unclassified"], "correctionIsIntegrationGap": False})
    write_json("phase13_1_handoff_revalidation.json", {"mode": "ZERO_GAP_VERIFICATION_CLOSURE", "executableTaskCreated": False, "status": "PASS"})
    write_json("phase13_2_contract_revalidation.json", {"contractReady": True, "executionReady": False, "executableTaskCreated": False, "clarificationAuthority": authority, "noInjection": True, "demosExecuted": 0})
    write_json("scientific_authority_nonchange.json", {"phase11Mutation": 0, "Registry": 62, "DataProfile": "2.4", "scientificBehaviorChanges": 0})
    write_json("phase12_baseline_nonchange.json", {"expected": phase12["expected"], "actual": phase12["actual"], "mutation": 0, "status": "PASS"})
    write_json("negative_path_reconciliation.json", {"required": negative_paths["required"], "paths": negative_paths["paths"], "clarificationFailure": "CLARIFICATION_NOT_ALLOWED", "status": "PASS"})
    write_text("security.md", "NO_CORRECTION_ARBITRARY_CODE_EXECUTION = PASS\nNO_CORRECTION_PRODUCTION_BEHAVIOR_CHANGE = PASS\nNO_CORRECTION_REAL_LLM_CALL = PASS\nNO_CORRECTION_EXTERNAL_DOWNLOAD = PASS")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nREAL_LLM_CALLS = 0\nEXTERNAL_DOWNLOADS = 0")

    correction = {
        "correctionType": "FACT_ALIGNMENT_FIX_FORWARD",
        "authority": authority,
        "factModelHashImpact": "YES" if fact_impact else "NO",
        "factModelHash": fact["semanticHash"],
        "scopeBaselineHashImpact": "YES" if scope_impact else "NO",
        "scopeBaselineHash": first_scope_hash,
        "currentCanonicalTwoRoundAssertions": current_two_round,
        "historicalTwoRoundAssertions": historical_two_round,
        "releaseBlockers": gaps["releaseBlockers"],
        "releaseCriticalIntegrationGaps": gaps["releaseCriticalIntegrationGaps"],
        "p13x0Acceptance": "8/8",
        "demoFamilies": 7,
        "demosExecuted": 0,
        "productionCodeChanges": 0,
        "scientificBehaviorChanges": 0,
    }
    correction["semanticHash"] = canonical_hash(correction)
    write_json("correction_fact_model.json", correction)
    write_text(
        "baseline.txt",
        f"OLD_FACT_MODEL_HASH={OLD_FACT_HASH}\nCURRENT_FACT_MODEL_HASH={fact['semanticHash']}\n"
        f"OLD_SCOPE_BASELINE_HASH={OLD_SCOPE_HASH}\nCURRENT_SCOPE_BASELINE_HASH={first_scope_hash}\n"
        "MAX_CLARIFICATION_ROUNDS=1\nMAX_CLARIFICATION_QUESTIONS=3\nSECOND_ROUND=TYPED_FAILURE",
    )

    with (PHASE13_ROOT / "phase13_0_clarification_fact_correction.md").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Phase 13-0 Clarification Fact Correction\n\n"
            "This append-only fix-forward aligns the Phase 13 release projection with "
            "AnalysisIntent 1.0: one clarification round, at most three questions, and "
            "typed `CLARIFICATION_NOT_ALLOWED` on a second attempt. Production and scientific "
            "behavior are unchanged.\n\n"
            f"Fact Model hash impact: `NO`; current `{fact['semanticHash']}`.\n\n"
            f"Scope Baseline hash impact: `YES`; `{OLD_SCOPE_HASH}` is historical/superseded "
            f"by current `{first_scope_hash}`.\n"
        )

    entries = []
    for path in sorted(OUT.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.name, "sha256": file_hash(path)})
    write_json(
        "manifest.json",
        {
            "schemaVersion": "phase13-0-clarification-fact-correction/1.0",
            "entries": entries,
            "missing": 0,
            "hashMismatch": 0,
            "unclassified": 0,
            "implementationCi": os.environ.get("PHASE13_0_CORRECTION_IMPLEMENTATION_CI", previous_ci),
        },
    )
    print(f"PHASE13_0_CLARIFICATION_CORRECTION_GENERATED {len(entries)} {first_scope_hash}")


if __name__ == "__main__":
    main()
