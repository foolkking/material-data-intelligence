from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EVIDENCE_RELATIVE = Path("docs/phase10k/evidence/phase10k2_dataset_materials_explorer")


def _json(root: Path, relative: str):
    return json.loads((root / EVIDENCE_RELATIVE / relative).read_text(encoding="utf-8"))


def test_runtime_api_and_required_product_cases_are_real(repo_root: Path) -> None:
    capture = _json(repo_root, "api/runtime_capture.json")
    product = _json(repo_root, "artifacts/dataset_materials_explorer.json")
    assert capture["job"]["status"] == "completed"
    assert capture["job"]["validationStatus"] == "validated"
    assert [item["toolId"] for item in capture["toolCalls"]] == ["dataset.materials_explorer"]
    assert capture["apiContentRetrieval"] == {
        "artifactNames": ["dataset_materials_explorer.json", "dataset_quality.json", "recipe.json", "summary.md"],
        "allContentRoutesValidated": True,
    }
    assert product["schemaVersion"] == "phase10k2.dataset_materials_explorer.v1"
    assert product["semantics"]["source"] == "material_data_profile_2"
    assert product["composition"]["coverage"] == {"total": 4, "nonNull": 4, "valid": 3, "invalid": 1}
    assert product["structures"]["structureCount"] == 3
    assert product["structures"]["exactStructureDuplicateGroups"][0]["objectIds"] == ["obj_si_a", "obj_si_b"]
    assert {item["column"] for item in product["properties"]["properties"]} == {"band_gap", "formation_energy"}
    assert product["quality"]["invalidFormulaCount"] == 1
    assert product["quality"]["duplicateSampleIdentityValues"][0]["value"] == "sample-nacl"
    assert product["comparison"]["status"] == "READY"
    assert product["comparison"]["binding"] == {"groupColumn": "split", "groupA": "train", "groupB": "test"}
    assert product["comparison"]["semantics"].endswith("no row-order inference")
    assert product["security"] == {
        "artifactJavaScript": False,
        "externalUrls": False,
        "externalAssets": False,
        "executableContent": False,
    }


def test_performance_and_browser_evidence_is_bounded(repo_root: Path) -> None:
    performance = _json(repo_root, "performance/performance_metrics.json")
    assert performance["acceptance"] == "PASS"
    cases = {item["caseId"]: item for item in performance["cases"]}
    assert cases["small"]["inputRows"] == 4
    assert cases["medium"]["inputRows"] == 5000
    assert cases["near_cap"]["inputRows"] == performance["caps"]["maxRows"] == 100000
    assert cases["near_cap"]["sampleRowsMaterialized"] <= performance["caps"]["maxTableRows"]
    assert cases["near_cap"]["artifactBytes"] < performance["caps"]["maxArtifactBytes"]

    matrix = _json(repo_root, "browser/browser_matrix.json")
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] for item in matrix)
    assert all(item["externalRequests"] == 0 for item in matrix)
    # Phase 10K-2 evidence is immutable historical evidence. Current UI may add
    # later product tabs while preserving all seven original product tabs.
    assert all(item["desktop"]["accessibility"]["tabCount"] >= 7 for item in matrix)
    assert matrix[0]["mobile"]["horizontalOverflow"] is False
    assert matrix[0]["mobile"]["accessibility"]["regionLabel"] == "Dataset Materials Explorer"
    for name in (
        "01_dataset_overview.png",
        "02_composition_explorer.png",
        "03_structure_statistics.png",
        "04_property_explorer.png",
        "05_data_quality.png",
        "06_dataset_comparison.png",
        "07_mobile_dataset_explorer.png",
    ):
        payload = (repo_root / EVIDENCE_RELATIVE / "browser" / "screenshots" / name).read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(payload) > 5000


def test_security_markers_and_evidence_manifest(repo_root: Path) -> None:
    evidence = repo_root / EVIDENCE_RELATIVE
    assert _json(repo_root, "network_audit.json") == {
        "externalRequests": 0,
        "marker": "NO_DATASET_EXPLORER_EXTERNAL_NETWORK_REQUESTS",
    }
    security = _json(repo_root, "security_audit.json")
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert security["secretPatternHits"] == []
    assert security["realLlmCalls"] == 0
    manifest = _json(repo_root, "evidence_manifest.json")
    for item in manifest["files"]:
        payload = (evidence / item["name"]).read_bytes()
        assert len(payload) == item["bytes"]
        assert hashlib.sha256(payload).hexdigest() == item["sha256"]

    private_path = re.compile(r"[A-Za-z]:[\\/](?:Users|home|1project)[\\/]", re.IGNORECASE)
    executable = re.compile(r"(?:<script|javascript:|dangerouslySetInnerHTML|\beval\s*\()", re.IGNORECASE)
    for path in evidence.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert not private_path.search(text), path
        assert not executable.search(text), path
