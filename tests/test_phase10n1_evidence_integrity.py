from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n1_crystalnn_voronoinn_coordination"


def test_n1_evidence_manifest_is_complete_and_sanitized() -> None:
    required = {
        "baseline.txt", "entry_gate.md", "n0_authority_extraction.md", "n1_acceptance_registry.md",
        "n1_acceptance_reconciliation.md", "n1_decision_traceability.md", "locked_dependency_version.txt",
        "algorithm_api_audit.md", "parameter_contract_matrix.md", "scientific_wording_audit.md",
        "identity_audit.md", "unit_audit.md", "tolerance_audit.md", "registry_entries.json",
        "profile_readiness_cases.json", "eligibility_cases.json", "planner_cases.json", "plan_cases.json",
        "runtime_cases.json", "crystalnn_reference_results.json", "voronoinn_reference_results.json",
        "periodic_image_results.json", "algorithm_disagreement_results.json", "partial_failure_results.json",
        "unsupported_cases.json", "artifact_contract_samples/crystalnn_coordination.json",
        "artifact_contract_samples/voronoinn_coordination.json", "api_evidence/routes.md",
        "service_backed/summary.md", "workspace_selection_evidence.json", "interpretation_evidence.json",
        "report_recipe_evidence.json", "performance.json", "viewer_lifecycle.json", "accessibility.md",
        "security.md", "docs_link_check.txt", "secret_scan.txt", "screenshots/README.md",
        "browser/browser_matrix.json", "browser/mobile_smoke.json", "browser/network_summary.json", "browser/console_summary.json",
    }
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    assert required <= {item["path"] for item in entries}
    actual = {item.relative_to(EVIDENCE).as_posix() for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"}
    assert {item["path"] for item in entries} == actual
    assert len(entries) == len({item["path"] for item in entries})
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert entry["bytes"] == len(raw)
        assert entry["sha256"] == sha256(normalized).hexdigest()
    assert manifest["missingEntries"] == manifest["duplicateEntries"] == manifest["secretEntries"] == 0
    text = "\n".join((EVIDENCE / entry["path"]).read_text(encoding="utf-8", errors="ignore") for entry in entries if entry["path"].lower().endswith((".md", ".txt", ".json")))
    assert "DEEPSEEK_KEY=" not in text
    assert "Authorization:" not in text
    assert not re.search(r"[A-Za-z]:\\Users\\", text)
    assert "/home/runner/" not in text


def test_n1_evidence_records_exact_tool_contracts_and_browser_matrix() -> None:
    registry = json.loads((EVIDENCE / "registry_entries.json").read_text(encoding="utf-8"))
    assert registry == {
        "baselineCount": 53,
        "addedCount": 2,
        "finalCount": 55,
        "comparisonToolCount": 0,
        "tools": [
            {"toolId": "structure.coordination_crystalnn", "version": "0.1.0"},
            {"toolId": "structure.coordination_voronoinn", "version": "0.1.0"},
        ],
    }
    for name in ("crystalnn_reference_results.json", "voronoinn_reference_results.json"):
        payload = json.loads((EVIDENCE / name).read_text(encoding="utf-8"))
        assert payload["coverage"]["status"] == "COMPLETE"
        assert payload["siteResults"]
        assert all(len(neighbor["periodicImage"]) == 3 for site in payload["siteResults"] for neighbor in site["neighbors"])
    matrix = json.loads((EVIDENCE / "browser/browser_matrix.json").read_text(encoding="utf-8"))
    assert set(matrix) == {"chromium", "firefox", "webkit"}
    assert all(item["n1Coordination"] for item in matrix.values())
    mobile = json.loads((EVIDENCE / "browser/mobile_smoke.json").read_text(encoding="utf-8"))
    assert mobile["viewport"] == [390, 844]
    assert mobile["overflow"] == {"body": 0, "root": 0}
    assert mobile["minTouchTarget"] >= 44


def test_n1_canonical_documents_are_present_and_indexed() -> None:
    required = {
        "phase10n1_coordination_contract.md",
        "phase10n1_algorithm_parameter_contract.md",
        "phase10n1_identity_and_provenance.md",
        "phase10n1_artifact_contract.md",
        "phase10n1_registry_profile_planner_integration.md",
        "phase10n1_workspace_selection_interpretation.md",
        "phase10n1_reference_and_tolerance_evidence.md",
        "phase10n1_performance_security_accessibility.md",
        "phase10n1_acceptance_evidence_map.md",
        "phase10n1_completion.md",
        "phase10n2_next_scope.md",
    }
    phase_root = ROOT / "docs/phase10n"
    assert required <= {item.name for item in phase_root.glob("*.md")}
    index = (ROOT / "docs/index.md").read_text(encoding="utf-8")
    for name in required:
        assert name in index
    next_scope = (phase_root / "phase10n2_next_scope.md").read_text(encoding="utf-8")
    assert "REVIEWER_GATE" in next_scope
    assert "NOT QUEUED" in next_scope
    assert "NOT EXECUTABLE" in next_scope
