from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.mandatory_service_qualification import (
    DEFAULT_MANIFEST,
    REQUIRED_SERVICES,
    load_manifest,
    pytest_arguments,
    validate_report,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_junit(path: Path, names: list[str], *, skipped: int = 0) -> None:
    suite = ET.Element(
        "testsuite",
        {
            "tests": str(len(names)),
            "failures": "0",
            "errors": "0",
            "skipped": str(skipped),
        },
    )
    for index, name in enumerate(names):
        testcase = ET.SubElement(
            suite,
            "testcase",
            {"classname": "mandatory.service", "name": name},
        )
        if index < skipped:
            ET.SubElement(testcase, "skipped")
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def test_manifest_is_the_single_bounded_service_selection_authority() -> None:
    manifest = load_manifest(DEFAULT_MANIFEST)
    config = manifest["pytest"]

    assert tuple(manifest["services"]) == REQUIRED_SERVICES
    assert manifest["enableEnvironment"] == {"MDI_RUN_INTEGRATION": "1"}
    assert config["marker"] == "integration"
    assert config["minimumPassed"] == 50
    assert config["requireZeroSkips"] is True
    assert config["requireZeroFailures"] is True
    assert len(config["paths"]) == len(set(config["paths"]))
    assert len(config["requiredTests"]) == len(set(config["requiredTests"]))
    assert all((ROOT / path).is_file() for path in config["paths"])

    arguments = pytest_arguments(manifest, junit=Path("service.junit.xml"))
    assert arguments[: len(config["paths"])] == config["paths"]
    assert arguments[-2:] == ["--color=yes", "--junitxml=service.junit.xml"]


def test_manifest_validation_uses_junit_identity_not_terminal_grep(
    tmp_path: Path,
) -> None:
    manifest = load_manifest(DEFAULT_MANIFEST)
    names = list(manifest["pytest"]["requiredTests"])
    names.extend(
        f"test_mandatory_service_filler_{index}"
        for index in range(manifest["pytest"]["minimumPassed"] - len(names))
    )
    report = tmp_path / "integration.junit.xml"
    _write_junit(report, names)

    valid, failures = validate_report(manifest, report)

    assert valid is True
    assert failures == []


def test_manifest_validation_fails_when_required_test_is_absent_or_skipped(
    tmp_path: Path,
) -> None:
    manifest = load_manifest(DEFAULT_MANIFEST)
    names = list(manifest["pytest"]["requiredTests"])[1:]
    names.extend(
        f"test_mandatory_service_filler_{index}"
        for index in range(manifest["pytest"]["minimumPassed"] - len(names) + 1)
    )
    report = tmp_path / "integration.junit.xml"
    _write_junit(report, names, skipped=1)

    valid, failures = validate_report(manifest, report)

    assert valid is False
    assert any("skipped" in failure for failure in failures)
    assert any("required tests absent" in failure for failure in failures)


def test_ci_and_local_documentation_consume_the_manifest_runner() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    ci_docs = (ROOT / "docs/CI.md").read_text(encoding="utf-8")
    runbook = (ROOT / "docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md").read_text(
        encoding="utf-8"
    )

    authority = "scripts/mandatory_service_qualification.py"
    assert f"{authority} run" in workflow
    assert f"{authority} validate" in workflow
    assert "test_agent2_phase3_postgresql_planning_is_idempotent" not in workflow
    assert authority in ci_docs
    assert authority in runbook
