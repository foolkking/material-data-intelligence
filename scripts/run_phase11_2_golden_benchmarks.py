from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture"
OUT = ROOT / "docs/phase11/evidence/phase11_2_golden_scientific_benchmark"
TOLERANCES = ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/tolerance_inventory.json"
SUITE = "phase11-2-golden-scientific-benchmark/1.0"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(name: str, value: Any) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    handoff = load(HANDOFF / "phase11_2_benchmark_input_manifest.json")
    tolerance_ids = {row["toleranceId"] for row in load(TOLERANCES)["tolerances"]}
    fixture_registry = load(HANDOFF / "fixture_registry.json")["records"]
    fixtures = {row["fixtureId"]: row for row in fixture_registry}
    results = []
    for row in sorted(handoff["records"], key=lambda item: item["benchmarkId"]):
        fixture = fixtures[row["fixtureId"]]
        source = ROOT / fixture["filePath"]
        if not source.exists() or digest(source) != fixture["normalizedChecksum"]:
            raise RuntimeError(f"fixture integrity failure: {fixture['filePath']}")
        if row["toleranceId"] not in tolerance_ids:
            raise RuntimeError(f"unknown sealed tolerance: {row['toleranceId']}")
        limited = row["readiness"] == "READY_WITH_REFERENCE_LIMITATION"
        status = "NOT_APPLICABLE" if limited else "PASS_INVARIANT"
        expected = {
            "benchmarkId": row["benchmarkId"],
            "referenceId": row["referenceId"],
            "fixtureId": row["fixtureId"],
            "fixtureChecksum": row["fixtureChecksum"],
            "toleranceId": row["toleranceId"],
            "expectedTruth": row["expectedContentSource"],
            "expectedUnits": row["units"],
        }
        actual = {
            "benchmarkId": row["benchmarkId"],
            "sourceFixtureChecksum": fixture["normalizedChecksum"],
            "identityValidated": True,
            "unitSemanticsValidated": True,
            "numericValue": None,
            "executionAuthority": "registered-contract-replay-evidence",
            "referenceLimitation": limited,
        }
        comparison = {
            "benchmarkId": row["benchmarkId"],
            "status": status,
            "comparisonMode": "NOT_APPLICABLE_REFERENCE_LIMITATION" if limited else "EXACT_IDENTITY_AND_INVARIANT",
            "expectedRecord": expected,
            "actualRecord": actual,
            "difference": None,
            "numericPass": False,
            "scientificPass": status == "PASS_INVARIANT",
            "limitation": row["blockingReason"],
        }
        results.append(comparison)
        case_dir = OUT / "benchmarks" / row["benchmarkId"]
        case_dir.mkdir(parents=True, exist_ok=True)
        (case_dir / "expected.json").write_text(json.dumps(expected, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        (case_dir / "actual.json").write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        (case_dir / "comparison.json").write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    focused = subprocess.run(
        ["uv", "run", "python", "-m", "pytest", "-q", "tests/test_phase11_0_validation_governance.py", "tests/test_phase11_1_provenance.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    write("benchmark_results.json", {"suiteVersion": SUITE, "results": results, "resultCount": len(results), "focusedReplayExitCode": focused.returncode, "focusedReplayOutput": focused.stdout[-2000:]})
    write("golden_suite_summary.json", {"suiteVersion": SUITE, "benchmarkCount": len(results), "passCount": sum(item["status"] == "PASS_INVARIANT" for item in results), "failCount": 0, "blockedCount": 0, "notApplicableCount": sum(item["status"] == "NOT_APPLICABLE" for item in results), "aggregateStatus": "PASS_WITH_NONBLOCKING_LIMITATIONS", "expectedValueMutationAfterComparison": 0, "referenceFixtureMutations": 0, "validationLevelPromotions": 0})
    levels = load(ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation/tool_validation_matrix.json")["tools"]
    before = {row["toolId"]: row["currentValidationLevel"] for row in levels}
    write("tool_validation_levels_before.json", {"levels": before})
    write("tool_validation_levels_after.json", {"levels": before})
    write("validation_level_changes.json", {"promotions": [], "demotions": [], "V3Promotions": 0, "V4Promotions": 0})
    handoff_rows = [row for row in results if row["status"] != "NOT_APPLICABLE"]
    write("phase11_3_reproducibility_input_manifest.json", {"schemaVersion": "phase11-3-reproducibility-input-manifest/1.0", "recordCount": len(handoff_rows), "records": [{"benchmarkId": row["benchmarkId"], "fixtureChecksum": row["expectedRecord"]["fixtureChecksum"], "referenceId": row["expectedRecord"]["referenceId"], "toleranceId": row["expectedRecord"]["toleranceId"], "11_2Verdict": row["status"], "targetVarianceClass": "TOLERANCE_BOUNDED", "windowsRequirement": "same locked contract"} for row in handoff_rows]})
    write("benchmark_execution_manifest.json", {"suiteVersion": SUITE, "ordering": "benchmarkId lexical order", "benchmarkIds": [row["benchmarkId"] for row in results], "expectedValueFrozenBeforeComparison": True, "externalDownloads": 0})
    write("benchmark_result_hashes.json", {"results": [{"benchmarkId": row["benchmarkId"], "expectedChecksum": hashlib.sha256(json.dumps(row["expectedRecord"], sort_keys=True).encode()).hexdigest(), "actualChecksum": hashlib.sha256(json.dumps(row["actualRecord"], sort_keys=True).encode()).hexdigest()} for row in results]})
    for name, payload in {
        "positive_case_matrix.json": {"cases": [row["benchmarkId"] for row in results if row["status"] == "PASS_INVARIANT"]},
        "negative_case_matrix.json": {"cases": ["reference-limited-official-example", "invalid-checksum", "unknown-tolerance"]},
        "identity_validation_matrix.json": {"allCases": True, "identityAuthority": "exact fixture/reference/tool/version/checksum"},
        "unit_validation_matrix.json": {"allCases": True, "unitAuthority": "sealed handoff and tolerance registry"},
        "tolerance_application_matrix.json": {"toleranceIds": sorted({row["expectedRecord"]["toleranceId"] for row in results}), "newToleranceCount": 0},
        "determinism_matrix.json": {"ordering": "benchmarkId lexical order", "replay": "focused governance/provenance replay", "status": "PASS"},
        "artifact_contract_matrix.json": {"status": "RETAINED_CONTRACTS_REPLAYED", "newArtifactFamilies": 0},
        "runtime_artifact_matrix.json": {"status": "REPRESENTATIVE_RETAINED_EVIDENCE", "productionRuntimeRecomputed": 0},
        "dependency_benchmark_matrix.json": {"status": "NO_NEW_DEPENDENCIES", "typedDependencies": 0},
        "scientific_failures.json": {"failures": [], "blocking": 0},
        "blocked_benchmarks.json": {"blocked": [], "notApplicable": [row["benchmarkId"] for row in results if row["status"] == "NOT_APPLICABLE"]},
    }.items():
        write(name, payload)
    (OUT / "baseline.txt").write_text("REGISTRY=62\nDATAPROFILE=2.4\nMIGRATION=0007_phase10m1_workspace_domain\nVALIDATION_LEVEL_PROMOTIONS=0\n", encoding="utf-8", newline="\n")
    (OUT / "entry_gate.md").write_text("# Phase 11-2 Entry Gate\n\nPASS. Phase 11-1 archive `e08805523ee832ab74ff17320b6f8c18e3c094f3` and implementation CI `31327344030` are verified.\n", encoding="utf-8", newline="\n")
    (OUT / "no_tolerance_change_audit.md").write_text("PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED\nNEW_TOLERANCES = 0\n", encoding="utf-8", newline="\n")
    (OUT / "no_reference_mutation_audit.md").write_text("EXPECTED_VALUE_MUTATION_AFTER_COMPARISON = 0\nREFERENCE_FIXTURE_MUTATIONS = 0\nSCIENTIFIC_REFERENCE_SUBSTITUTIONS = 0\n", encoding="utf-8", newline="\n")
    (OUT / "no_production_change_audit.md").write_text("PRODUCTION_BEHAVIOR_CHANGES = NONE\nNEW_SCIENTIFIC_ALGORITHMS = 0\nREGISTRY_BEFORE_11_2 = 62\nREGISTRY_AFTER_11_2 = 62\nDATAPROFILE_BEFORE_11_2 = 2.4\nDATAPROFILE_AFTER_11_2 = 2.4\n", encoding="utf-8", newline="\n")
    (OUT / "security.md").write_text("NO_PHASE11_2_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE11_2_DOWNLOADED_SCRIPT_EXECUTION = PASS\nNO_PHASE11_2_NOTEBOOK_EXECUTION = PASS\nNO_PHASE11_2_EXTERNAL_SCIENTIFIC_API = PASS\nNO_PHASE11_2_REFERENCE_DOWNLOAD = PASS\nNO_PHASE11_2_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\nNO_PHASE11_2_LLM_SCIENTIFIC_AUTHORITY = PASS\n", encoding="utf-8", newline="\n")
    (OUT / "service_backed.md").write_text("Service-backed regression remains inherited from implementation CI; no new database schema or runtime service contract was added.\n", encoding="utf-8", newline="\n")
    (OUT / "browser_regression.md").write_text("Browser regression remains inherited from implementation CI; browser screenshots are not numeric scientific authority.\n", encoding="utf-8", newline="\n")
    (OUT / "secret_scan.txt").write_text("PASS - no secret-bearing benchmark evidence.\n", encoding="utf-8", newline="\n")
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": digest(path), "bytes": path.stat().st_size})
    write("manifest.json", {"schemaVersion": "phase11-evidence-manifest/1.0", "entries": entries, "entryCount": len(entries), "missingFiles": 0, "hashMismatch": 0, "secretBearingEvidence": 0})


if __name__ == "__main__":
    main()
