from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase11_1_acceptance_registry_is_exact() -> None:
    registry = load("acceptance_registry.json")
    assert registry["expected"] == registry["implemented"] == 10
    assert all(registry[key] == 0 for key in ("missing", "extra", "duplicate", "conflicting", "shorthand"))
    assert [entry.split()[0] for entry in registry["entries"]] == [f"P11V1-A{i:02d}" for i in range(1, 11)]


def test_handoff_is_complete_without_numeric_validation() -> None:
    payload = load("phase11_2_benchmark_input_manifest.json")
    assert payload["recordCount"] == len(payload["records"]) > 0
    assert payload["implementationCriticalTBD"] == 0
    assert all(row["readiness"] in {"READY_FOR_11_2", "READY_WITH_REFERENCE_LIMITATION"} for row in payload["records"])
    assert all(row["numericValidation"] == "NOT_AUTHORIZED_IN_PHASE_11_1" for row in payload["records"])


def test_fixture_registry_reuses_immutable_bytes() -> None:
    payload = load("fixture_registry.json")
    assert payload["recordCount"] == len(payload["records"])
    assert payload["retainedFixtureCount"] == 170
    assert payload["benchmarkHandoffFixtureCount"] == 12
    assert payload["existingFixtureRewriteCount"] == 0
    assert all(row["immutable"] for row in payload["records"])
    assert all(row["sourceChecksum"] == row["normalizedChecksum"] for row in payload["records"])


def test_provenance_and_license_records_are_explicit() -> None:
    refs = load("reference_provenance_registry.json")["records"]
    assert len(refs) == 12
    required = {
        "referenceId", "referenceVersion", "referenceType", "sourceLocation",
        "sourceChecksum", "licenseIdentifier", "redistributionDisposition",
        "rawRetentionDisposition", "referenceIndependence", "transformationIds",
        "fixtureIds", "phase11_2BenchmarkIds", "reviewStatus",
    }
    assert all(required <= row.keys() for row in refs)
    assert all(row["numericValidation"] == "NOT_PERFORMED_IN_PHASE_11_1" for row in refs)


def test_phase11_1_manifest_matches_files_and_security_boundary() -> None:
    manifest = load("manifest.json")
    expected = {path.relative_to(EVIDENCE).as_posix() for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "manifest.json"}
    assert manifest["entryCount"] == len(manifest["entries"]) > 0
    assert {row["path"] for row in manifest["entries"]} == expected
    assert manifest["missingFiles"] == manifest["hashMismatch"] == manifest["secretBearingEvidence"] == 0
    for row in manifest["entries"]:
        path = EVIDENCE / row["path"]
        assert path.stat().st_size == row["bytes"]
        assert digest(path) == row["sha256"]
    security = (EVIDENCE / "security.md").read_text(encoding="utf-8")
    for marker in (
        "PHASE11_1_DOWNLOADED_SCRIPT_EXECUTIONS = 0",
        "PHASE11_1_NOTEBOOK_EXECUTIONS = 0",
        "PHASE11_1_EXTERNAL_SCIENTIFIC_API_CALLS = 0",
        "PHASE11_1_EXTERNAL_REFERENCE_DOWNLOADS = 0",
    ):
        assert marker in security


def test_phase11_1_freezes_scientific_authorities() -> None:
    text = (EVIDENCE / "no_production_change_audit.md").read_text(encoding="utf-8")
    assert "PRODUCTION_BEHAVIOR_CHANGES = NONE" in text
    assert "REGISTRY_AFTER_11_1 = 62" in text
    assert "DATAPROFILE_AFTER_11_1 = 2.4" in text
    assert load("transformation_registry.json")["records"][0]["numericMutation"] is False
