from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching"
DOCS = [ROOT / f"docs/phase10n/{name}" for name in (
    "phase10n_acceptance_and_test_plan.md", "phase10n_implementation_backlog.md",
    "phase10n_execution_lock.md", "phase10n_execution_manifest.md",
)]
EXPECTED = {
    "N3-A01": "BASELINE_THEORETICAL_XRD_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE",
    "N3-A02": "EXPERIMENTAL_XRD_RESOURCE_PROFILE_UNITS_AND_SEMANTIC_VALIDATION",
    "N3-A03": "EXPERIMENTAL_PEAK_DETECTION_AND_DETERMINISTIC_NORMALIZATION",
    "N3-A04": "THEORETICAL_PEAK_BINDING_AND_BOUNDED_ONE_TO_ONE_PEAK_MATCHING",
    "N3-A05": "EXACT_PEAK_IDENTITY_RESIDUALS_COVERAGE_AND_DETERMINISM",
    "N3-A06": "ELIGIBILITY_PLANNER_PLANVALIDATOR_DEPENDENCY_RUNTIME_AND_PERSISTENCE",
    "N3-A07": "WORKSPACE_XRD_OVERLAY_SELECTION_TABLES_AND_INSPECTOR",
    "N3-A08": "GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_SCIENTIFIC_CLAIM_BOUNDARY",
    "N3-A09": "REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE",
    "N3-A10": "THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N4_REVIEWER_GATE",
}


def test_exact_n3_registry_is_identical_in_four_canonical_docs() -> None:
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        marker = "## Canonical Phase 10N-3 Acceptance Registry"
        assert text.count(marker) == 1
        section = text.split(marker, 1)[1].split("\n## ", 1)[0]
        entries = re.findall(r"`(N3-A\d{2}) ([A-Z0-9_]+)`", section)
        assert dict(entries) == EXPECTED
        assert len(entries) == len(set(item[0] for item in entries)) == 10
        assert not re.search(r"N3-A\d{2}\s+(?:through|to)\s+N3-A\d{2}", section, re.IGNORECASE)


def test_n3_evidence_manifest_is_complete_hashed_and_inert() -> None:
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    actual = {item.relative_to(EVIDENCE).as_posix() for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"}
    assert {item["path"] for item in entries} == actual
    assert len(entries) == len(actual) == len({item["path"] for item in entries})
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert entry["bytes"] == len(raw)
        assert entry["sha256"] == sha256(normalized).hexdigest()
    assert manifest["missingEntries"] == manifest["duplicateEntries"] == manifest["secretEntries"] == 0
    text = "\n".join((EVIDENCE / entry["path"]).read_text(encoding="utf-8", errors="ignore") for entry in entries)
    assert "Authorization:" not in text and "DEEPSEEK_KEY=" not in text
    assert not re.search(r"[A-Za-z]:\\Users\\", text)


def test_n3_ci_registers_browser_and_zero_skip_service_closure() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--n3-experimental-xrd-only" in workflow
    assert "test_phase10n3_experimental_xrd_service_backed.py" in workflow
    assert "test_phase10n3_postgres_redis_minio_theoretical_xrd_comparison_closure" in workflow
    assert 'if [ "${PASSED:-0}" -lt 45 ]; then' in workflow


def test_n3_task_and_n4_gate_are_exact() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert tasks.count("---TASK---") == tasks.count("---END---") == 1
    assert "Phase 10N-3 Experimental XRD Comparison + Peak Matching" in tasks
    assert "Phase 10N-4:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    assert "Phase 10N-4 Trajectory" not in tasks
