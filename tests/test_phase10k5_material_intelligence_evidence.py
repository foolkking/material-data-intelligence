from __future__ import annotations

import hashlib
import json
from pathlib import Path


EVIDENCE_RELATIVE = Path("docs/phase10k/evidence/phase10k5_material_intelligence_integration")


def _json(root: Path, relative: str):
    return json.loads((root / EVIDENCE_RELATIVE / relative).read_text(encoding="utf-8"))


def test_phase10k5_runtime_api_identity_version_and_partial_closure(repo_root: Path) -> None:
    runtime = _json(repo_root, "runtime/runtime_integration.json")
    api = _json(repo_root, "api/api_integration.json")
    profile = _json(repo_root, "integration/profile_authority.json")
    identity = _json(repo_root, "integration/cross_artifact_sample_identity.json")
    binding = _json(repo_root, "integration/exact_version_binding.json")
    partial = _json(repo_root, "integration/partial_failure_isolation.json")
    replay = _json(repo_root, "integration/reproducibility.json")
    report_recipe = _json(repo_root, "integration/report_recipe_compatibility.json")

    assert runtime["marker"] == "MATERIAL_INTELLIGENCE_RUNTIME_INTEGRATION_PASS"
    assert api["marker"] == "MATERIAL_INTELLIGENCE_API_INTEGRATION_PASS"
    assert api["allContentRoutesValidated"] is True
    assert profile == {
        "marker": "MATERIAL_INTELLIGENCE_PROFILE_AUTHORITY_EVIDENCE_PASS",
        "products": ["10K-2", "10K-3", "10K-4"],
        "profileContractVersion": "2.0",
        "roleInferenceRepeated": False,
    }
    assert identity["marker"] == "MATERIAL_INTELLIGENCE_SAMPLE_IDENTITY_EVIDENCE_PASS"
    assert identity["sampleKey"] == identity["datasetExplorer"]["sampleKey"]
    assert identity["sampleKey"] == identity["materialsMl"]["sampleKey"]
    assert identity["sampleKey"] == identity["compositionSpace"]["sampleKey"]
    assert identity["sampleKey"] == f'{identity["datasetExplorer"]["objectId"]}:{identity["datasetExplorer"]["sampleRef"]}'
    assert binding["marker"] == "MATERIAL_INTELLIGENCE_VERSION_BINDING_EVIDENCE_PASS"
    assert binding["binding"]["profileContractVersion"] == "2.0"
    assert len(binding["binding"]["semanticHash"]) == 64
    assert len(binding["binding"]["datasetContentHash"]) == 64
    assert binding["binding"]["resourceBindings"]
    assert partial["marker"] == "MATERIAL_INTELLIGENCE_PARTIAL_FAILURE_ISOLATION_PASS"
    assert partial["datasetJobStatus"] == "completed"
    assert partial["executedTool"] == "dataset.materials_explorer"
    assert partial["mlToolExecuted"] is False
    assert partial["profileDataStatus"] == "AMBIGUOUS"
    ambiguous_products = {
        path.name
        for path in (repo_root / EVIDENCE_RELATIVE / "products/case_h_ambiguous_ml").iterdir()
    }
    assert ambiguous_products == {
        "dataset_materials_explorer.json",
        "dataset_quality.json",
        "recipe.json",
        "summary.md",
    }
    assert replay["marker"] == "MATERIAL_INTELLIGENCE_REPRODUCIBILITY_PASS"
    assert all(first == second for first, second in replay["hashes"].values())
    assert report_recipe["marker"] == "MATERIAL_INTELLIGENCE_REPORT_RECIPE_COMPATIBILITY_PASS"
    assert report_recipe["reportCompatibility"]["newReportImplementation"] is False
    assert report_recipe["reportCompatibility"]["artifactReferences"]
    assert {item["toolId"] for item in report_recipe["recipeCompatibility"]} == {
        "dataset.materials_explorer",
        "ml.regression_evaluation",
        "dataset.composition_space",
    }
    assert all(item["binding"] == binding["binding"] for item in report_recipe["recipeCompatibility"])


def test_phase10k5_required_cases_and_performance_are_explicit(repo_root: Path) -> None:
    cases = _json(repo_root, "integration/required_case_matrix.json")
    assert set(cases) == {
        "A_materials_table",
        "B_structure_enriched",
        "C_regression",
        "D_uncertainty",
        "E_classification",
        "F_comparison",
        "G_partial",
        "H_ambiguous",
    }
    assert cases["C_regression"]["ml"] == "completed"
    assert cases["D_uncertainty"]["ml"] == "completed"
    assert cases["E_classification"]["ml"] == "completed"
    assert cases["G_partial"]["ml"] == "UNAVAILABLE"
    assert cases["H_ambiguous"]["ml"] == "SAFELY_BLOCKED"
    assert all(case["api"] == "PASS" for case in cases.values())

    performance = _json(repo_root, "performance/product_envelope.json")
    assert performance["marker"] == "MATERIAL_INTELLIGENCE_PERFORMANCE_EVIDENCE_PASS"
    assert performance["acceptance"] == "PASS"
    assert performance["small"]["dataset"]["inputRows"] == 40
    assert performance["medium"]["dataset"]["inputRows"] == 5_000
    assert performance["nearCap"]["dataset"]["inputRows"] == 100_000
    assert performance["nearCap"]["regression"]["inputRows"] == 100_000
    assert performance["nearCap"]["composition"]["inputRows"] == 20_000


def test_phase10k5_browser_accessibility_network_and_security_closure(repo_root: Path) -> None:
    browser = _json(repo_root, "browser/browser_integration.json")
    matrix = _json(repo_root, "browser/browser_matrix.json")
    accessibility = _json(repo_root, "browser/accessibility_audit.json")
    network = _json(repo_root, "browser/console_network_audit.json")
    security = _json(repo_root, "security/security_audit.json")

    assert browser["marker"] == "MATERIAL_INTELLIGENCE_BROWSER_INTEGRATION_PASS"
    assert browser["browsers"] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] for item in matrix)
    assert all(item["externalRequests"] == 0 for item in matrix)
    assert accessibility["marker"] == "MATERIAL_INTELLIGENCE_ACCESSIBILITY_EVIDENCE_PASS"
    assert {item["case"] for item in accessibility["mobile"]} == {"dataset", "regression", "composition"}
    assert network["marker"] == "NO_MATERIAL_INTELLIGENCE_EXTERNAL_NETWORK_REQUESTS"
    assert all(item["externalRequests"] == 0 and not item["consoleErrors"] and not item["pageErrors"] for item in network["browsers"])
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert security["secretPatternHits"] == []
    assert security["privatePathHits"] == []
    assert security["artifactJavaScript"] is False
    assert security["externalUrls"] is False
    screenshots = {path.name for path in (repo_root / EVIDENCE_RELATIVE / "browser/screenshots").glob("*.png")}
    assert {"dataset.png", "regression.png", "composition.png", "partial.png", "ambiguous.png", "mobile_dataset.png", "mobile_regression.png", "mobile_composition.png"} <= screenshots


def test_phase10k5_evidence_manifest_covers_every_retained_file(repo_root: Path) -> None:
    root = repo_root / EVIDENCE_RELATIVE
    manifest = _json(repo_root, "evidence_manifest.json")
    records = {item["name"]: item for item in manifest["files"]}
    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "evidence_manifest.json"
    }
    assert set(records) == actual
    for relative, record in records.items():
        payload = (root / relative).read_bytes()
        assert record["bytes"] == len(payload)
        assert record["sha256"] == hashlib.sha256(payload).hexdigest()
