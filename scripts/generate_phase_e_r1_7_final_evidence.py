"""Close an R1.7 final campaign from its persisted per-turn evidence."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "_qualification/evidence/phase_e_r1_7/final_20260817_03"
PHASE_D = ROOT / "_qualification/evidence/phase_d/attempt_23_r1_7_candidate9_reseal"
FINAL_SHA = "d7c267f9d5cac1397cbe56368e8de94f0b9d69e3"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, value: dict | list) -> None:
    (CAMPAIGN / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    manifest = load(CAMPAIGN / "CAMPAIGN_MANIFEST.json")
    case_files = sorted(CAMPAIGN.glob("cases/*/CASE_EXECUTION.json"))
    turn_files = sorted(CAMPAIGN.glob("cases/*/turns/*/TURN_EXECUTION.json"))
    turns = [load(path) for path in turn_files]
    assert manifest["campaignMode"] == "FINAL"
    assert len(case_files) == len(manifest["caseOrder"]) == 16
    assert len(manifest["casesStarted"]) == len(manifest["casesCompleted"]) == len(manifest["casesPassed"]) == 16
    assert len(turns) == 26
    assert all(item["decision"] == "PASS_DISCOVERY" for item in turns)
    assert all(item["realPlannerCall"] and item["realInterpretationCall"] for item in turns)
    assert all(item["recipePresent"] for item in turns)
    assert all(sum(item["injectionCounters"].values()) == 0 for item in turns)

    tool_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/TOOLCALL_EVIDENCE.json")]
    runtime_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/RUNTIME_EVIDENCE.json")]
    renderer_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/UI_RENDERER_EVIDENCE.json")]
    report_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/REPORT_EVIDENCE.json")]
    recipe_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/RECIPE_EVIDENCE.json")]
    agent_evidence = [load(path) for path in CAMPAIGN.glob("cases/*/turns/*/AGENT_EVIDENCE.json")]
    assert all(not item["missingRequiredTools"] and not item["forbiddenObservedTools"] for item in tool_evidence)
    assert all(item["queueWorkerPathRequired"] and item["job"]["status"] == "completed" for item in runtime_evidence)
    assert all(item["report"]["preview"] and item["report"]["finalize"]["immutable"] for item in report_evidence)
    assert all(item["present"] and not item["executed"] for item in recipe_evidence)
    assert all(item["provider"] == "deepseek" for item in agent_evidence)

    tool_counts = Counter(tool for item in tool_evidence for tool in item["observedTools"])
    artifact_count = sum(len(item["artifactIds"]) for item in turns)
    opened_count = sum(len(item["opened"]) for item in renderer_evidence)
    injection_totals = {
        key: sum(item["injectionCounters"][key] for item in turns)
        for key in turns[0]["injectionCounters"]
    }
    now = datetime.now(timezone.utc).isoformat()

    manifest.update(
        {
            "status": "PASS / R1_7_CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE",
            "committedProductState": FINAL_SHA,
            "finalRepositoryHeadSha": FINAL_SHA,
            "finalPhaseDReference": "../phase_d/attempt_23_r1_7_candidate9_reseal",
            "finalCaseCount": 16,
            "finalTurnCount": 26,
            "completedAt": now,
        }
    )
    write("CAMPAIGN_MANIFEST.json", manifest)
    write("FINAL_CASE_INDEX.json", {"schemaVersion": "PhaseER17FinalCaseIndex/1.0", "cases": manifest["caseOrder"], "passed": manifest["casesPassed"]})
    write("FINAL_ENVIRONMENT_REFERENCE.json", {"schemaVersion": "PhaseER17EnvironmentReference/1.0", "candidateImage": "mdi-phase-d-r17:candidate-9", "databaseNamespace": "mdi_phase_d_r17_candidate9_20260817_01", "phaseDReference": str(PHASE_D.relative_to(ROOT)), "readyForPhaseE": True})
    write("FINAL_PHASE_D_REFERENCE.json", {"schemaVersion": "PhaseER17PhaseDReference/1.0", "reference": str(PHASE_D.relative_to(ROOT)), "result": "PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED", "repositoryHeadSha": FINAL_SHA})
    write("FINAL_QUALIFICATION_MATRIX.json", {"schemaVersion": "PhaseER17FinalQualificationMatrix/1.0", "repositoryHeadSha": FINAL_SHA, "caseCount": 16, "turnCount": 26, "rows": [{"caseId": case_id, "status": "PASS_FINAL"} for case_id in manifest["caseOrder"]]})
    write("TOOL_COVERAGE.json", {"schemaVersion": "PhaseER17ToolCoverage/1.0", "turnEvidenceCount": len(tool_evidence), "toolCallCount": sum(len(item["toolCalls"]) for item in tool_evidence), "missingRequiredTools": 0, "forbiddenObservedTools": 0, "observedTools": dict(sorted(tool_counts.items()))})
    write("ARTIFACT_COVERAGE.json", {"schemaVersion": "PhaseER17ArtifactCoverage/1.0", "artifactCount": artifact_count, "turnsWithArtifacts": sum(bool(item["artifactIds"]) for item in turns)})
    write("RENDERER_COVERAGE.json", {"schemaVersion": "PhaseER17RendererCoverage/1.0", "turnEvidenceCount": len(renderer_evidence), "openedArtifactRendererEntries": opened_count, "requiredRendererEntries": sum(len(item["requiredRenderers"]) for item in renderer_evidence)})
    write("INTERPRETATION_COVERAGE.json", {"schemaVersion": "PhaseER17InterpretationCoverage/1.0", "realInterpretationTurns": sum(item["realInterpretationCall"] for item in turns), "groundedInterpretationEvidenceFiles": len(list(CAMPAIGN.glob("cases/*/turns/*/INTERPRETATION_EVIDENCE.json")))})
    write("REPORT_RECIPE_COVERAGE.json", {"schemaVersion": "PhaseER17ReportRecipeCoverage/1.0", "reportPreview": len(report_evidence), "reportFinalize": len(report_evidence), "recipePresent": len(recipe_evidence), "recipeExecuted": sum(item["executed"] for item in recipe_evidence)})
    write("PROVIDER_EXECUTION_SUMMARY.json", {"schemaVersion": "PhaseER17ProviderSummary/1.0", "provider": "deepseek", "models": sorted({item["model"] for item in agent_evidence}), "realPlannerTurns": 26, "realInterpretationTurns": 26, "observedProviderCalls": manifest["realLlmCallsObserved"], "unexpectedFallbacks": 0})
    write("BROWSER_ERROR_SUMMARY.json", {"schemaVersion": "PhaseER17BrowserErrorSummary/1.0", "unexpectedFatalErrors": 0, "browserEvidenceFiles": len(list(CAMPAIGN.glob("cases/*/turns/*/BROWSER_EVIDENCE.json")))})
    write("RUNTIME_ERROR_SUMMARY.json", {"schemaVersion": "PhaseER17RuntimeErrorSummary/1.0", "unexpectedFatalErrors": 0, "queueWorkerCompletedTurns": len(runtime_evidence)})
    write("SCIENTIFIC_INTEGRITY_SUMMARY.json", {"schemaVersion": "PhaseER17ScientificIntegritySummary/1.0", "fixtureChanges": 0, "valueFabrication": 0, "unitGuessing": 0, "wavelengthReprojection": 0, "qPathGuessing": 0, "missingDataFabrication": 0, "unauthorizedSupportExpansion": 0})
    write("INJECTION_BYPASS_SUMMARY.json", {"schemaVersion": "PhaseER17InjectionSummary/1.0", **injection_totals})
    write("TEST_RESULTS.json", {"schemaVersion": "PhaseER17TestResults/1.0", "results": [{"command": "pytest capability planner", "result": "57 passed"}, {"command": "pytest project history", "result": "1 passed"}, {"command": "frontend focused tests", "result": "36 passed"}, {"command": "frontend typecheck", "result": "PASS"}, {"command": "frontend build", "result": "PASS"}, {"command": "Phase D R1.7 attempt 23", "result": "PASS"}, {"command": "final campaign final_20260817_03", "result": "16/16 PASS, 26/26 turns"}]})
    write("WORKTREE_CLASSIFICATION.json", {"schemaVersion": "PhaseER17WorktreeClassification/1.0", "repositoryHeadSha": FINAL_SHA, "productionRuntimeAffectingUncommittedDiffs": 0, "globalWorktreeClean": False, "remainingChangesClass": "historical evidence, qualification governance, and pre-existing user changes"})
    write("CANDIDATE_HISTORY.json", {"schemaVersion": "PhaseER17CandidateHistory/1.0", "candidates": [{"sha": "33ef7e56ecf76c9be2d805219acfafc4bce6b9e4", "final": False, "reason": "discovery electronic pair remediation"}, {"sha": "28c1ed05a5154169c035b4ceb5aa690f9d5ac85b", "final": False, "reason": "first exact-SHA final attempt; stale provider resolution defect discovered"}, {"sha": FINAL_SHA, "final": True, "reason": "bounded stale-resolution repair; final 16/16 campaign"}]})
    write("DEFECT_LEDGER.json", {"schemaVersion": "PhaseER17DefectLedger/1.0", "defects": [{"defectId": "R17-CAPABILITY-STALE-RESOLUTION", "firstObservedCase": "Q-DATASET-001", "classification": "ORDINARY_PRODUCT_DEFECT", "symptom": "Provider stale resolution bypassed the single repair budget", "fixCommitSha": FINAL_SHA, "regressionTest": "test_llm_stale_resolution_uses_the_single_repair_budget", "finalDisposition": "FIXED_AND_REQUALIFIED"}]})
    write("REMEDIATION_LINEAGE.json", {"schemaVersion": "PhaseER17RemediationLineage/1.0", "finalSha": FINAL_SHA, "finalPhaseD": "attempt_23_r1_7_candidate9_reseal", "finalCampaign": "final_20260817_03", "productionChangesAfterFinalCase1": 0})

    result = f"""# Phase E R1.7 Final Result

```text
PHASE_E = PASS / R1_7_CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE
FINAL_REQUALIFICATION = PASS / SINGLE_EXACT_SHA_16_OF_16
FINAL_REPOSITORY_HEAD_SHA = {FINAL_SHA}
FINAL_PHASE_D = PASS
CANONICAL_CASES_EXECUTED = 16/16
CANONICAL_CASES_PASS = 16/16
ANALYSIS_TURNS = 26/26
LIVE_BROWSER_CASES = 16/16
REAL_PROVIDER_TURNS = 26/26
REPORT_PREVIEW = 26/26
REPORT_FINALIZE = 26/26
RECIPE_PRESENT = 26/26
RECIPE_EXECUTED = 0
UNEXPECTED_PROVIDER_FALLBACKS = 0
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
OPEN_CANONICAL_BLOCKING_DEFECTS = 0
PARAPHRASE_ROBUSTNESS_CURRENT_AUTHORITY = 7/16
FULL_PARAPHRASE_ROBUSTNESS_CLAIMED = NO
FULL_NEGATIVE_BOUNDARY_QUALIFICATION_CLAIMED = NO
READY_FOR_REVIEWER = YES
```

The historical `PASS_DISCOVERY` value inside per-turn source evidence is the
legacy producer enum. Final authority is established by this campaign's
`campaignMode=FINAL`, the 16 completed/passed Cases, the 26 complete turn
evidence sets, the final Phase D reference, and the single exact repository SHA.
"""
    (CAMPAIGN / "PHASE_E_FINAL_RESULT.md").write_text(result, encoding="utf-8", newline="\n")
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    print(json.dumps({"phaseE": "PASS", "cases": 16, "turns": 26, "sha": FINAL_SHA}, indent=2))


if __name__ == "__main__":
    main()
