from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m4_artifact_gallery_viewers"


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m4_acceptance_renderer_and_browser_evidence() -> None:
    acceptance = _json("acceptance_mapping.json")
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == 0
    assert [item["id"] for item in acceptance["items"]] == [f"M4-A0{index}" for index in range(1, 9)]
    assert all("PENDING_MAINLINE" not in item["status"] for item in acceptance["items"])

    registry = _json("renderer_registry.json")
    assert registry["registryEntryCount"] == registry["artifactTypeCount"] == 42
    assert registry["resolutionAuthority"].startswith("exact Artifact type and version")
    assert {"filename", "MIME alone", "dynamic component name"}.issubset(registry["forbiddenAuthorities"])

    browser = _json("browser_matrix.json")
    assert set(browser) == {"chromium", "firefox", "webkit"}
    for result in browser.values():
        assert result["metadataFirst"] is True
        assert result["exactReferenceNavigation"]["exact"] is True
        assert result["partialIsolation"] == {
            "dependencyOutcome": "PARTIAL_RESULTS",
            "panelState": "PARTIAL",
            "warningVisible": True,
            "successfulArtifactsRemainOpenable": True,
        }
        assert result["maxActiveCanvases"] == 1 and result["remainingCanvases"] == 0
        assert result["consoleErrors"] == result["pageErrors"] == result["externalRequests"] == []
        assert all(item["rendererReady"] for item in result["cases"].values())
        assert result["lifecycleAudit"]["growth"] in (
            {"listeners": 0, "resizeObservers": 0, "intersectionObservers": 0, "pendingAnimationFrames": 0, "activeWebglContexts": 0, "usedJsHeapBytes": 0},
            {"listeners": 0, "resizeObservers": 0, "intersectionObservers": 0, "pendingAnimationFrames": 0, "activeWebglContexts": 0, "usedJsHeapBytes": None},
        )
        assert result["lifecycleAudit"]["peak"]["activeWebglContexts"] == 1
        assert result["lifecycleAudit"]["final"]["activeWebglContexts"] == 0
    assert browser["chromium"]["heavySwitchCycles"] == 50
    assert browser["chromium"]["contextLoss"]["recovered"] is True

    lifecycle = _json("webgl_lifecycle.json")
    assert lifecycle["maxActiveHeavyViewers"] == 1
    assert lifecycle["webglContextGrowth"] == lifecycle["listenerGrowth"] == lifecycle["observerGrowth"] == lifecycle["pendingAnimationFrameGrowth"] == 0
    assert lifecycle["status"] == "PASS"

    mobile = _json("mobile_smoke.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["oneActiveViewer"] is mobile["focusedClose"] is mobile["focusRestored"] is True
    assert mobile["overflow"] == {"body": 0, "root": 0}
    assert mobile["minTouchTarget"] >= 44


def test_phase10m4_manifest_security_and_provider_policy() -> None:
    manifest = _json("file_manifest.json")
    entries = manifest["entries"]
    assert entries == sorted(entries, key=lambda item: item["path"])
    actual = {
        item.relative_to(EVIDENCE).as_posix()
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.name != "file_manifest.json"
    }
    assert {item["path"] for item in entries} == actual
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        hashed = raw.replace(b"\r\n", b"\n") if entry["hashMode"] == "lf_normalized_text" else raw
        assert len(raw) == entry["bytes"]
        assert sha256(hashed).hexdigest() == entry["sha256"]

    security = _json("security.json")
    required = {
        "NO_ARTIFACT_GALLERY_ARBITRARY_CODE_EXECUTION",
        "NO_ARTIFACT_HTML_EXECUTION",
        "NO_ARTIFACT_JAVASCRIPT_EXECUTION",
        "NO_ARTIFACT_IFRAME_EXECUTION",
        "NO_ARTIFACT_DYNAMIC_MODULE_EXECUTION",
        "NO_ARTIFACT_EXTERNAL_URL_EXECUTION",
        "NO_ARTIFACT_FILENAME_RENDERER_AUTHORITY",
        "NO_FRONTEND_SCIENTIFIC_RECOMPUTATION",
        "NO_SELECTION_ARRAY_INDEX_AUTHORITY",
        "NO_SELECTION_DISPLAY_LABEL_AUTHORITY",
        "NO_SELECTION_FUZZY_MATCH",
        "NO_SECRET_PATTERN_HITS",
    }
    assert required.issubset(security["markers"])
    policy = _json("deepseek_policy_regression.json")
    assert policy["allowedRealProvider"] == "DEEPSEEK"
    assert policy["allowedKeySource"] == "DEEPSEEK_KEY"
    assert policy["realLlmCalls"] == policy["newLlmCallSites"] == 0

    evidence_text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in evidence_text
    assert "Authorization:" not in evidence_text
    assert not re.search(r"[A-Za-z]:\\Users\\", evidence_text)
    assert "/home/runner/" not in evidence_text


def test_phase10m4_required_inventory_and_screenshots() -> None:
    required = {
        "baseline.txt", "entry_gate.txt", "m3_archive_verification.txt", "acceptance_mapping.json",
        "artifact_contract_inventory.json", "renderer_inventory.json", "renderer_registry.json",
        "selection_emitter_consumer_matrix.json", "webgl_ownership_audit.json", "artifact_gallery_cases.json",
        "artifact_loader_cases.json", "dataset_viewer.json", "ml_viewers.json", "composition_space_viewer.json",
        "structure_viewer.json", "trajectory_viewer.json", "phonon_viewer.json", "brillouin_zone_viewer.json",
        "volumetric_viewer.json", "generic_fallbacks.json", "partial_failure.json", "legacy_unsupported.json",
        "selection_integration.json", "webgl_lifecycle.json", "context_lost.json", "performance.json",
        "accessibility.json", "security.json", "service_backed.json", "deepseek_policy_regression.json",
        "real_deepseek_evidence.json", "browser_matrix.json", "mobile_smoke.json", "network_summary.json",
        "console_summary.json", "test_summary.txt", "secret_scan.txt", "file_manifest.json",
    }
    assert required.issubset({item.name for item in EVIDENCE.iterdir()})
    screenshots = EVIDENCE / "screenshots"
    for browser in ("chromium", "firefox", "webkit"):
        assert (screenshots / f"{browser}_gallery.png").stat().st_size > 10_000
        assert (screenshots / f"{browser}_partial.png").stat().st_size > 10_000
    assert (screenshots / "chromium_mobile_gallery.png").stat().st_size > 10_000
