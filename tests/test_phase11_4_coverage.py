from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage"
ALLOWED = {
    "DIRECT_VERIFIED",
    "OFFICIAL_DERIVED_VERIFIED",
    "REFERENCE_VERIFIED",
    "MAPPING_ONLY",
    "EXTRACTION_REQUIRED",
    "FUTURE_SCOPE",
    "UNSUPPORTED",
}
TEXT_SUFFIXES = {".json", ".md", ".txt", ".yaml", ".yml"}


def read(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def semantic_sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def test_live_registry_and_matrices_are_exactly_classified() -> None:
    registry = load_manifests()
    matrix = read("tool_coverage_matrix.json")
    ids = [row["toolId"] for row in matrix["tools"]]
    assert len(registry.tools) == 62
    assert len(ids) == 62
    assert ids == sorted(ids)
    assert set(ids) == {tool.toolId for tool in registry.tools}
    assert len(ids) == len(set(ids))
    assert all(row["toolVersion"] == "0.1.0" for row in matrix["tools"])
    assert all(row["coverageVerdict"] in ALLOWED for row in matrix["tools"])


def test_input_and_example_rows_have_honest_verdicts() -> None:
    inputs = read("input_coverage_matrix.json")["inputs"]
    examples = read("official_example_coverage_matrix.json")["records"]
    assert len(inputs) == 14
    assert len(examples) == 55
    assert all(row["coverageVerdict"] in ALLOWED for row in inputs + examples)
    assert all(row["scientificNumericAuthority"] == "NONE" for row in examples)
    assert all("support verdict" in row["coverageReason"] for row in inputs)


def test_phase11_3_handoff_is_not_promoted_to_numeric_v4() -> None:
    summary = read("coverage_summary.json")
    assert summary["numericCrossPlatformClaims"] == 0
    assert summary["v4Promotions"] == 0
    assert summary["validationLevelChanges"] == 0
    assert summary["supportVerdictChanges"] == 0
    assert len(summary["toolCoverageMatrixHash"]) == 64
    assert len(summary["inputCoverageMatrixHash"]) == 64
    assert len(summary["officialExampleCoverageMatrixHash"]) == 64


def test_evidence_manifest_hashes_and_acceptance_registry() -> None:
    manifest = read("manifest.json")
    for item in manifest["files"]:
        path = EVIDENCE / item["path"]
        assert path.is_file()
        assert semantic_sha256(path) == item["sha256"]
    acceptance = read("acceptance_registry.json")
    assert acceptance["expected"] == acceptance["implemented"] == 10
    assert acceptance["missing"] == acceptance["extra"] == 0
    assert acceptance["duplicate"] == acceptance["conflicting"] == acceptance["shorthand"] == 0
