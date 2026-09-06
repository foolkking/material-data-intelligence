from __future__ import annotations

from pathlib import Path

import pytest

from scripts.pytest_junit_summary import parse_pytest_junit


def test_parse_pytest_junit_aggregates_multiple_suites(tmp_path: Path) -> None:
    report = tmp_path / "integration.junit.xml"
    report.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="phase-a" tests="4" failures="1" errors="0" skipped="1" />
  <testsuite name="phase-b" tests="3" failures="0" errors="1" skipped="0" />
</testsuites>
""",
        encoding="utf-8",
    )

    summary = parse_pytest_junit(report)

    assert summary.selected == 7
    assert summary.passed == 4
    assert summary.failed == 1
    assert summary.errors == 1
    assert summary.skipped == 1


def test_parse_pytest_junit_rejects_inconsistent_counters(tmp_path: Path) -> None:
    report = tmp_path / "invalid.junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="1" errors="1" skipped="0" />',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="inconsistent"):
        parse_pytest_junit(report)
