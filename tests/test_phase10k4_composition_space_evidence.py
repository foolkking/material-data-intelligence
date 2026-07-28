from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EVIDENCE_RELATIVE = Path("docs/phase10k/evidence/phase10k4_composition_space")


def _json(root: Path, relative: str):
    return json.loads((root / EVIDENCE_RELATIVE / relative).read_text(encoding="utf-8"))


def _payload(root: Path, case_id: str) -> dict:
    return _json(root, f"artifacts/{case_id}/composition_space.json")


def test_runtime_planner_and_canonical_composition_cases_are_real(repo_root: Path) -> None:
    for case_id in ("normal", "property_color", "group_comparison", "resource_comparison", "k3_ml_color"):
        capture = _json(repo_root, f"api/{case_id}_runtime_capture.json")
        assert capture["request"]["provider"] == "MockLLMProvider"
        assert capture["job"]["status"] == "completed"
        assert capture["job"]["validationStatus"] == "validated"
        assert [item["toolId"] for item in capture["toolCalls"]] == ["dataset.composition_space"]
        assert capture["apiContentRetrieval"]["artifactNames"] == [
            "composition_space.json",
            "composition_space_plot.json",
            "recipe.json",
            "summary.md",
        ]
        assert capture["apiContentRetrieval"]["allContentRoutesValidated"] is True

    payload = _payload(repo_root, "normal")
    assert payload["schemaVersion"] == "phase10k4.composition_space.v1"
    assert payload["artifactType"] == "dataset.composition_space"
    assert payload["dataset"]["profileContractVersion"] == "2.0"
    assert payload["coverage"]["validCompositionSamples"] == 6
    assert payload["coverage"]["invalidCompositionSamples"] == 1
    assert payload["coverage"]["silentDrops"] is False
    assert payload["featureRepresentation"] == {
        **payload["featureRepresentation"],
        "type": "normalized_atomic_fraction",
        "basisOrder": "atomic_number_ascending",
        "normalization": "element_amount_divided_by_total_amount",
        "missingElementValue": 0.0,
        "fractionalOccupancySupported": True,
        "parser": "pymatgen.core.Composition via application composition semantics",
    }
    projection = payload["projection"]
    assert projection["method"] == "PCA"
    assert projection["dimensions"] == 2
    assert projection["centering"] is True
    assert projection["scaling"] == "none"
    assert projection["solver"] == "sklearn_full_svd"
    assert projection["signConvention"] == "largest_absolute_loading_is_positive"
    assert projection["rank"] >= 2
    assert len(projection["components"]) == len(projection["explainedVarianceRatio"]) == 2
    for component in projection["components"]:
        pivot = max(range(len(component)), key=lambda index: abs(component[index]))
        assert component[pivot] >= 0

    assert len(payload["points"]) == 6
    assert len(payload["displayPointKeys"]) == 6
    assert {point["sampleRef"] for point in payload["points"]} == {"si-1", "sige-1", "nacl-1", "lif-1", "mgo-1", "gaas-1"}
    assert all(point["sampleKey"] == f"{point['objectId']}:{point['sampleRef']}" for point in payload["points"])
    assert all(abs(sum(point["elementFractions"].values()) - 1.0) <= 1e-6 for point in payload["points"])
    assert payload["clustering"]["status"] == "READY"
    assert payload["clustering"]["featureSpace"] == "normalized_atomic_fraction"
    assert payload["clustering"]["parameters"]["labelOrdering"] == "centroid_lexicographic"
    assert payload["semantics"] == {
        "source": "material_data_profile_2",
        "roleInferenceRepeated": False,
        "sampleIdentityPreserved": True,
        "projectionIsNotCanonicalMaterialIdentity": True,
        "clusterMeaning": "composition_cluster_only",
        "outlierMeaning": "distance_to_feature_centroid_candidate_only",
        "structuralSimilarityClaimed": False,
        "chemicalFamilyClaimed": False,
    }
    assert payload["security"] == {
        "artifactJavaScript": False,
        "externalUrls": False,
        "externalAssets": False,
        "executableContent": False,
    }


def test_property_ml_and_comparison_evidence_preserves_explicit_bindings(repo_root: Path) -> None:
    property_payload = _payload(repo_root, "property_color")
    property_options = {item["id"]: item for item in property_payload["coloring"]["available"]}
    assert property_options["property:band_gap"] == {
        "id": "property:band_gap",
        "kind": "continuous",
        "label": "band_gap",
        "unit": "eV",
        "source": "material_data_profile_2_material_property",
    }

    for case_id, expected_mode in (("group_comparison", "group"), ("resource_comparison", "resources")):
        comparison = _payload(repo_root, case_id)["comparison"]
        assert comparison["status"] == "READY"
        assert comparison["mode"] == expected_mode
        assert comparison["projectionPolicy"] == "exploratory_combined_projection"
        assert comparison["sharedElementBasis"] is True
        assert comparison["sharedPcaFit"] is True
        assert comparison["trainingSafetyClaimed"] is False
        assert len(comparison["groups"]) == 2

    ml_payload = _payload(repo_root, "k3_ml_color")
    ml_options = [item for item in ml_payload["coloring"]["available"] if item["id"].startswith("ml:")]
    assert ml_options
    assert all(item["source"] == "phase10k3_sample_bound_artifact" for item in ml_options)
    assert any(point["mlValues"] for point in ml_payload["points"])
    assert _json(repo_root, "fixtures/k3_regression_source.json")["schemaVersion"].startswith("phase10k3.materials_ml_regression.")


def test_typed_negative_cap_and_security_evidence(repo_root: Path) -> None:
    rank = _json(repo_root, "api/rank_failure_runtime_capture.json")
    cap = _json(repo_root, "api/analysis_cap_failure_runtime_capture.json")
    assert rank["job"]["status"] == "failed"
    assert rank["typedAdapterError"]["code"] == "TOOL_INPUT_INVALID"
    assert rank["typedAdapterError"]["details"]["errorType"] == "insufficient_projection_rank"
    assert cap["job"]["status"] == "failed"
    assert cap["typedAdapterError"]["code"] == "TOOL_RESOURCE_LIMIT"
    assert cap["typedAdapterError"]["details"]["validSamples"] == 20001
    assert cap["typedAdapterError"]["details"]["maxAnalyzedSamples"] == 20000

    security = _json(repo_root, "security/plan_validation_rejection.json")
    assert security["validationOk"] is False
    assert security["runtimeStarted"] is False
    assert security["artifactCreated"] is False
    assert any(item["code"] == "PARAMS_SCHEMA_INVALID" for item in security["errors"])


def test_performance_browser_and_manifest_integrity(repo_root: Path) -> None:
    performance = _json(repo_root, "performance/performance_metrics.json")
    assert performance["acceptance"] == "PASS"
    cases = {item["caseId"]: item for item in performance["cases"]}
    assert cases["small"]["inputRows"] == 6
    assert cases["medium"]["inputRows"] == 5000
    assert cases["near_cap"]["inputRows"] == performance["caps"]["maxAnalyzedSamples"] == 20000
    assert cases["near_cap"]["displayPoints"] <= 1000
    assert cases["near_cap"]["artifactBytes"] < performance["caps"]["maxArtifactBytes"]

    matrix = _json(repo_root, "browser/browser_matrix.json")
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] for item in matrix)
    assert all(item["externalRequests"] == 0 for item in matrix)
    assert matrix[0]["mobile"]["horizontalOverflow"] is False
    assert matrix[0]["mobile"]["accessibility"]["regionLabel"] == "Composition Space Explorer"
    for browser in matrix:
        for case_id in ("normal", "property_color", "group_comparison", "resource_comparison", "k3_ml_color"):
            assert browser["cases"][case_id]["accessibility"]["keyboardPointCount"] >= 3
            assert browser["cases"][case_id]["accessibility"]["tableFallback"] is True
    for name in (*[f"{case_id}.png" for case_id in ("normal", "property_color", "group_comparison", "resource_comparison", "k3_ml_color")], "mobile_sample_inspection.png"):
        payload = (repo_root / EVIDENCE_RELATIVE / "browser" / "screenshots" / name).read_bytes()
        assert payload.startswith(b"\x89PNG\r\n\x1a\n")
        assert len(payload) > 5000

    assert _json(repo_root, "network_audit.json") == {
        "externalRequests": 0,
        "marker": "NO_COMPOSITION_SPACE_EXTERNAL_NETWORK_REQUESTS",
    }
    security = _json(repo_root, "security/security_audit.json")
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert security["secretPatternHits"] == []
    assert security["privatePathHits"] == []
    assert security["executableEvidenceHits"] == []

    evidence = repo_root / EVIDENCE_RELATIVE
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
