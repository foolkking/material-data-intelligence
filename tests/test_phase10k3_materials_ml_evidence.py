from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EVIDENCE_RELATIVE = Path("docs/phase10k/evidence/phase10k3_materials_ml_evaluation")


def _json(root: Path, relative: str):
    return json.loads((root / EVIDENCE_RELATIVE / relative).read_text(encoding="utf-8"))


def test_runtime_api_artifacts_close_all_three_profile_bound_products(repo_root: Path) -> None:
    cases = {
        "regression": ("ml.regression_evaluation", "phase10k3.materials_ml_regression.v1"),
        "uncertainty": ("ml.uncertainty_evaluation", "phase10k3.materials_ml_uncertainty.v1"),
        "classification": ("ml.classification_evaluation", "phase10k3.materials_ml_classification.v1"),
    }
    for case_id, (tool_id, schema) in cases.items():
        capture = _json(repo_root, f"api/{case_id}_runtime_capture.json")
        product = _json(repo_root, f"artifacts/{case_id}/materials_ml_{case_id}.json")
        assert capture["job"]["status"] == "completed"
        assert capture["job"]["validationStatus"] == "validated"
        assert [item["toolId"] for item in capture["toolCalls"]] == [tool_id]
        assert capture["apiContentRetrieval"]["allContentRoutesValidated"] is True
        assert product["schemaVersion"] == schema
        assert product["dataset"]["profileContractVersion"] == "2.0"
        assert product["dataset"]["semanticHash"]
        assert product["security"] == {
            "artifactJavaScript": False,
            "executableContent": False,
            "externalAssets": False,
            "externalUrls": False,
        }


def test_required_scientific_cases_and_performance_caps_are_recorded(repo_root: Path) -> None:
    fixtures = _json(repo_root, "fixtures/required_cases.json")
    regression = fixtures["regression"]
    assert len(regression["evaluations"]) == 2
    assert regression["residualConvention"] == "prediction_minus_target"
    assert regression["modelComparisons"][0]["policy"] == "common_valid_samples"
    assert regression["evaluations"][0]["chemistryConditioned"]["byElement"]
    assert regression["evaluations"][0]["highErrorSamples"][0]["sampleRef"]
    assert fixtures["uncertainty"]["evaluations"][0]["reliability"]["method"] == "equal_count_mean_uncertainty_vs_mean_absolute_error"
    assert fixtures["uncertainty"]["evaluations"][0]["errorDecay"]["method"] == "retain_lowest_uncertainty_first"
    assert fixtures["classification"]["evaluations"][0]["curves"]["status"] == "READY"
    assert fixtures["classification"]["evaluations"][0]["curves"]["positiveClass"] == "B"

    performance = _json(repo_root, "performance/performance_metrics.json")
    assert performance["acceptance"] == "PASS"
    cases = {item["caseId"]: item for item in performance["cases"]}
    assert cases["small_regression"]["inputRows"] == 4
    assert cases["medium_regression"]["inputRows"] == 5000
    assert cases["near_cap_regression"]["inputRows"] == performance["caps"]["maxRows"] == 100000
    assert cases["near_cap_uncertainty"]["inputRows"] == 100000
    assert all(item["displayPoints"] <= 2000 for item in cases.values())
    assert all(item["artifactBytes"] < performance["caps"]["maxArtifactBytes"] for item in cases.values())


def test_browser_mobile_network_and_evidence_integrity(repo_root: Path) -> None:
    matrix = _json(repo_root, "browser/browser_matrix.json")
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] for item in matrix)
    assert all(item["externalRequests"] == 0 for item in matrix)
    assert all(not item["consoleErrors"] and not item["pageErrors"] for item in matrix)
    assert all(set(item["cases"]) == {"regression", "uncertainty", "classification"} for item in matrix)
    assert matrix[0]["mobile"]["horizontalOverflow"] is False
    assert matrix[0]["mobile"]["accessibility"]["regionLabel"] == "Materials ML Evaluation"
    for name in ("regression.png", "uncertainty.png", "classification.png", "mobile_regression.png"):
        payload = (repo_root / EVIDENCE_RELATIVE / "browser" / "screenshots" / name).read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(payload) > 5000

    assert _json(repo_root, "network_audit.json")["marker"] == "NO_MATERIALS_ML_EXTERNAL_NETWORK_REQUESTS"
    assert _json(repo_root, "security_audit.json")["marker"] == "NO_SECRET_PATTERN_HITS"
    evidence = repo_root / EVIDENCE_RELATIVE
    manifest = _json(repo_root, "evidence_manifest.json")
    for item in manifest["files"]:
        payload = (evidence / item["name"]).read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]

    private_path = re.compile(r"[A-Za-z]:[\\/](?:Users|home|1project)[\\/]", re.IGNORECASE)
    executable = re.compile(r"(?:<script|javascript:|dangerouslySetInnerHTML|\beval\s*\()", re.IGNORECASE)
    for path in evidence.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            assert not private_path.search(text), path
            assert not executable.search(text), path
