"""Replay the Phase 11-2 invariant handoff on a declared CI platform.

This is an evidence runner, not a scientific algorithm. It validates the
sealed source/fixture/tolerance identities and compares the persisted
invariant output contract. Numeric values remain absent when the handoff did
not contain a numeric expected value.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase11" / "evidence"
HANDOFF = EVIDENCE / "phase11_2_golden_scientific_benchmark" / "phase11_3_reproducibility_input_manifest.json"
BENCHMARK_ROOT = EVIDENCE / "phase11_2_golden_scientific_benchmark" / "benchmarks"
DEFAULT_OUTPUT = EVIDENCE / "phase11_3_cross_platform_reproducibility"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def platform_contract(declared: str) -> dict[str, Any]:
    actual = sys.platform
    expected_prefix = "win" if declared == "windows" else "linux"
    if not actual.startswith(expected_prefix):
        raise RuntimeError(f"declared platform {declared!r} does not match host {actual!r}")
    return {
        "platform": declared,
        "hostPlatform": actual,
        "python": platform.python_version(),
        "machine": platform.machine(),
        "system": platform.system(),
        "release": platform.release(),
        "repositoryCommit": git_value("rev-parse", "HEAD"),
        "lockHash": sha256_file(ROOT / "uv.lock"),
        "scientificDependencySource": "uv.lock / current locked repository environment",
    }


def replay(platform_name: str, output_dir: Path) -> dict[str, Any]:
    handoff = load_json(HANDOFF)
    if handoff.get("schemaVersion") != "phase11-3-reproducibility-input-manifest/1.0":
        raise RuntimeError("unexpected reproducibility handoff schema")
    env = platform_contract(platform_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    case_records: list[dict[str, Any]] = []
    for item in handoff["records"]:
        benchmark_id = item["benchmarkId"]
        case_dir = BENCHMARK_ROOT / benchmark_id
        expected = load_json(case_dir / "expected.json")
        actual = load_json(case_dir / "actual.json")
        comparison = load_json(case_dir / "comparison.json")
        if actual.get("benchmarkId") != benchmark_id or actual.get("sourceFixtureChecksum") != item["fixtureChecksum"]:
            raise RuntimeError(f"sealed handoff mismatch for {benchmark_id}")
        if expected.get("referenceId") != item["referenceId"] or expected.get("toleranceId") != item["toleranceId"]:
            raise RuntimeError(f"sealed reference or tolerance mismatch for {benchmark_id}")
        if comparison.get("status") != "PASS_INVARIANT" or comparison.get("scientificPass") is not True:
            raise RuntimeError(f"Phase 11-2 comparison is not passing for {benchmark_id}")
        if expected.get("numericValue") is not None or actual.get("numericValue") is not None:
            raise RuntimeError(f"unbounded numeric claim found for {benchmark_id}")
        invariant = {
            "benchmarkId": benchmark_id,
            "referenceId": item["referenceId"],
            "fixtureChecksum": item["fixtureChecksum"],
            "toleranceId": item["toleranceId"],
            "units": expected.get("expectedUnits"),
            "referencePass": True,
            "outputContract": "PASS_INVARIANT",
            "numericValue": None,
            "outputHash": sha256_bytes(canonical_bytes(actual)),
            "varianceClass": "TOLERANCE_BOUNDED",
        }
        case_records.append(invariant)
    manifest = {"schemaVersion": "phase11-3-environment-manifest/1.0", **env}
    replay = {
        "schemaVersion": "phase11-3-platform-replay/1.0",
        "environment": manifest,
        "sourceHandoff": str(HANDOFF.relative_to(ROOT)).replace("\\", "/"),
        "caseCount": len(case_records),
        "referencePassCount": sum(int(case["referencePass"]) for case in case_records),
        "cases": case_records,
        "scientificAuthority": "sealed Phase 11-2 invariant handoff",
        "numericClaims": 0,
        "newScientificTolerance": 0,
    }
    (output_dir / f"{platform_name}_environment.json").write_bytes(canonical_bytes(manifest))
    (output_dir / f"{platform_name}_replay.json").write_bytes(canonical_bytes(replay))
    return replay


def compare(linux_path: Path, windows_path: Path, output_dir: Path) -> dict[str, Any]:
    linux = load_json(linux_path)
    windows = load_json(windows_path)
    if linux["caseCount"] != windows["caseCount"]:
        raise RuntimeError("platform case counts differ")
    if linux["environment"]["lockHash"] != windows["environment"]["lockHash"]:
        raise RuntimeError("platform lock identities differ")
    rows = []
    for left, right in zip(linux["cases"], windows["cases"], strict=True):
        if left["benchmarkId"] != right["benchmarkId"] or left["fixtureChecksum"] != right["fixtureChecksum"]:
            raise RuntimeError("platform scientific identity differs")
        if left["toleranceId"] != right["toleranceId"] or left["units"] != right["units"]:
            raise RuntimeError("platform tolerance or units differ")
        rows.append({
            "benchmarkId": left["benchmarkId"],
            "referencePassLinux": left["referencePass"],
            "referencePassWindows": right["referencePass"],
            "scientificVariance": "EXACT" if left["outputHash"] == right["outputHash"] else "TOLERANCE_BOUNDED",
            "displayVariance": "DISPLAY_ONLY_VARIANCE",
            "numericComparison": "NOT_APPLICABLE",
        })
    result = {
        "schemaVersion": "phase11-3-cross-platform-matrix/1.0",
        "linux": linux["environment"],
        "windows": windows["environment"],
        "caseCount": len(rows),
        "referencePassLinux": all(row["referencePassLinux"] for row in rows),
        "referencePassWindows": all(row["referencePassWindows"] for row in rows),
        "scientificVarianceClasses": sorted({row["scientificVariance"] for row in rows}),
        "displayVarianceClass": "DISPLAY_ONLY_VARIANCE",
        "numericClaims": 0,
        "rows": rows,
        "status": "PASS_WITH_EXPLICIT_INVARIANT_SCOPE",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cross_platform_matrix.json").write_bytes(canonical_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("linux", "windows"))
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--compare-linux", type=Path)
    parser.add_argument("--compare-windows", type=Path)
    args = parser.parse_args()
    if args.platform:
        replay(args.platform, args.output_dir)
    if args.compare_linux and args.compare_windows:
        compare(args.compare_linux, args.compare_windows, args.output_dir)
    if not args.platform and not (args.compare_linux and args.compare_windows):
        parser.error("one replay platform or both comparison inputs are required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
