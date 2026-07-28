from __future__ import annotations

import json
import re
from pathlib import Path


EVIDENCE_RELATIVE = Path("docs/phase10k/evidence/phase10k1_material_data_profile_2")


def _read_json(root: Path, relative: str):
    return json.loads((root / EVIDENCE_RELATIVE / relative).read_text(encoding="utf-8"))


def test_phase10k1_api_and_semantic_evidence_is_complete(repo_root: Path):
    regression = _read_json(repo_root, "api/regression_uncertainty.json")
    ambiguous = _read_json(repo_root, "api/ambiguous_regression.json")
    classification = _read_json(repo_root, "api/classification.json")
    structure = _read_json(repo_root, "api/periodic_structure.json")

    for capture in (regression, ambiguous, classification, structure):
        assert capture["responses"] == {"uploadStatus": 200, "fetchStatus": 200, "regenerateStatus": 200}
        assert capture["persistenceCheck"] == {"uploadFetchHashMatch": True, "regenerateHashMatch": True}
        assert capture["profile"]["profileContractVersion"] == "2.0"
        assert len(capture["profile"]["semanticHash"]) == 64

    regression_status = {item["capability"]: item for item in regression["profile"]["analysisReadiness"]}
    assert regression_status["regression_evaluation"]["dataStatus"] == "READY"
    assert regression_status["regression_evaluation"]["platformStatus"] == "NOT_IMPLEMENTED"
    ambiguous_status = {item["capability"]: item for item in ambiguous["profile"]["analysisReadiness"]}
    assert ambiguous_status["regression_evaluation"]["dataStatus"] == "AMBIGUOUS"
    assert any(group["status"] == "COMPLETE" for group in classification["profile"]["semanticGroups"])
    assert any(set(resource["capabilities"]) >= {"composition", "structure"} for resource in structure["profile"]["resourceSemantics"])


def test_phase10k1_performance_and_browser_evidence_is_bounded(repo_root: Path):
    performance = _read_json(repo_root, "performance/performance_metrics.json")
    assert performance["acceptance"] == "PASS"
    assert performance["policy"] == {"maxColumns": 512, "maxRows": 4096}
    near_cap = next(item for item in performance["cases"] if item["caseId"] == "near_cap")
    assert near_cap["rowsInspected"] == 4096
    assert near_cap["columnsInspected"] == 512
    assert near_cap["coveragePolicy"] == "deterministic_bounded_sample"
    assert set(near_cap["warnings"]) == {"PROFILE_COLUMN_CAP_APPLIED", "PROFILE_ROW_SAMPLE_APPLIED"}
    assert near_cap["outputBytes"] < 250_000

    matrix = _read_json(repo_root, "browser/browser_matrix.json")
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] for item in matrix)
    assert all(item["desktop"]["hasSemanticSurface"] for item in matrix)
    assert all(item["externalRequests"] == 0 for item in matrix)
    assert matrix[0]["mobile"]["hasSemanticSurface"] is True
    assert matrix[0]["mobile"]["horizontalOverflow"] is False

    for name in ("01_profile_semantics_desktop.png", "02_profile_semantics_mobile.png"):
        payload = (repo_root / EVIDENCE_RELATIVE / "browser/screenshots" / name).read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(payload) > 10_000


def test_phase10k1_security_markers_and_captures_are_sanitized(repo_root: Path):
    evidence = repo_root / EVIDENCE_RELATIVE
    network = _read_json(repo_root, "network_audit.json")
    browser_network = _read_json(repo_root, "browser/console_network_audit.json")
    security = _read_json(repo_root, "security_audit.json")

    assert network == {"externalRequests": 0, "marker": "NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS"}
    assert browser_network["marker"] == "NO_MATERIAL_PROFILE_EXTERNAL_NETWORK_REQUESTS"
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert security["secretPatternHits"] == []
    assert security["realLlmCalls"] == 0

    private_path = re.compile(r"[A-Za-z]:[\\/](?:Users|home|1project)[\\/]", re.IGNORECASE)
    executable = re.compile(r"(?:<script|javascript:|dangerouslySetInnerHTML|\beval\s*\()", re.IGNORECASE)
    for path in evidence.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert not private_path.search(text), path
        assert not executable.search(text), path
