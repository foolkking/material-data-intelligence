from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase11/evidence/phase11_2_golden_scientific_benchmark"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_golden_suite_has_explicit_results_and_limitations() -> None:
    summary = load("golden_suite_summary.json")
    results = load("benchmark_results.json")
    assert summary["benchmarkCount"] == results["resultCount"] == 12
    assert summary["passCount"] == 8
    assert summary["notApplicableCount"] == 4
    assert summary["failCount"] == summary["blockedCount"] == 0
    assert summary["aggregateStatus"] == "PASS_WITH_NONBLOCKING_LIMITATIONS"
    assert results["focusedReplayExitCode"] == 0
    assert all(row["status"] in {"PASS_INVARIANT", "NOT_APPLICABLE"} for row in results["results"])


def test_expected_and_actual_records_are_separate_and_frozen() -> None:
    results = load("benchmark_results.json")["results"]
    assert all("expectedRecord" in row and "actualRecord" in row for row in results)
    assert all(row["expectedRecord"]["toleranceId"] for row in results)
    assert all(row["actualRecord"]["identityValidated"] for row in results)
    assert all(row["actualRecord"]["numericValue"] is None for row in results)
    assert load("validation_level_changes.json")["promotions"] == []
    assert load("tolerance_application_matrix.json")["newToleranceCount"] == 0


def test_phase11_3_handoff_excludes_reference_limited_cases() -> None:
    handoff = load("phase11_3_reproducibility_input_manifest.json")
    assert handoff["recordCount"] == 8
    assert all(row["11_2Verdict"] == "PASS_INVARIANT" for row in handoff["records"])
    assert all(row["targetVarianceClass"] == "TOLERANCE_BOUNDED" for row in handoff["records"])


def test_golden_evidence_manifest_is_complete() -> None:
    manifest = load("manifest.json")
    expected = {path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "manifest.json"}
    assert manifest["entryCount"] == len(manifest["entries"]) > 0
    assert {row["path"] for row in manifest["entries"]} == expected
    assert manifest["missingFiles"] == manifest["hashMismatch"] == manifest["secretBearingEvidence"] == 0
    for row in manifest["entries"]:
        path = EVIDENCE / row["path"]
        assert path.stat().st_size == row["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
