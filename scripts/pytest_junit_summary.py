from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class PytestJunitSummary:
    selected: int
    passed: int
    failed: int
    errors: int
    skipped: int


def parse_pytest_junit(path: Path) -> PytestJunitSummary:
    root = ET.parse(path).getroot()
    suites = _top_level_suites(root)
    selected = sum(_count(suite, "tests") for suite in suites)
    failed = sum(_count(suite, "failures") for suite in suites)
    errors = sum(_count(suite, "errors") for suite in suites)
    skipped = sum(_count(suite, "skipped") for suite in suites)
    passed = selected - failed - errors - skipped
    if min(selected, passed, failed, errors, skipped) < 0:
        raise ValueError("JUnit counters are inconsistent.")
    return PytestJunitSummary(
        selected=selected,
        passed=passed,
        failed=failed,
        errors=errors,
        skipped=skipped,
    )


def _top_level_suites(root: ET.Element) -> list[ET.Element]:
    if _local_name(root.tag) == "testsuite":
        return [root]
    direct = [
        child for child in root
        if _local_name(child.tag) == "testsuite"
    ]
    if direct:
        return direct
    raise ValueError("JUnit report does not contain a top-level testsuite.")


def _count(suite: ET.Element, name: str) -> int:
    raw = suite.attrib.get(name, "0")
    value = int(raw)
    if value < 0:
        raise ValueError(f"JUnit {name} counter cannot be negative.")
    return value


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a pytest JUnit XML report without parsing terminal text.",
    )
    parser.add_argument("report", type=Path)
    parser.add_argument("--minimum-passed", type=int, default=0)
    parser.add_argument("--require-zero-skips", action="store_true")
    parser.add_argument("--require-zero-failures", action="store_true")
    args = parser.parse_args()

    try:
        summary = parse_pytest_junit(args.report)
    except (ET.ParseError, OSError, ValueError) as error:
        print(f"ERROR: unable to read pytest JUnit report: {error}")
        return 2

    print("=== Integration Summary (JUnit XML) ===")
    print(f"  selected: {summary.selected}")
    print(f"  passed:   {summary.passed}")
    print(f"  skipped:  {summary.skipped}")
    print(f"  failed:   {summary.failed}")
    print(f"  errors:   {summary.errors}")
    print("========================================")

    failures: list[str] = []
    if args.require_zero_skips and summary.skipped:
        failures.append(f"{summary.skipped} integration test(s) skipped")
    if args.require_zero_failures and (summary.failed or summary.errors):
        failures.append(
            f"{summary.failed} failed and {summary.errors} errored integration test(s)",
        )
    if summary.passed < args.minimum_passed:
        failures.append(
            f"only {summary.passed}/{args.minimum_passed} minimum integration tests passed",
        )
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
