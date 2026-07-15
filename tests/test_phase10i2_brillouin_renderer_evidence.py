from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i2_brillouin_renderer"


def _json(relative: str) -> object:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def test_phase10i2_browser_api_performance_and_security_evidence_is_closed() -> None:
    manifest = _json("evidence_manifest.json")
    assert manifest["tool"] == "structure.brillouin_zone"
    assert manifest["source"] == "Phase 10I-1 QueueWorkerRuntime artifact captures"
    assert manifest["external_requests"] == 0
    assert set(manifest["markers"]) == {
        "BRILLOUIN_ZONE_RENDERER_BROWSER_EVIDENCE_PASS",
        "BRILLOUIN_ZONE_RENDERER_PERFORMANCE_EVIDENCE_PASS",
        "BRILLOUIN_ZONE_RENDERER_ACCESSIBILITY_EVIDENCE_PASS",
        "BRILLOUIN_ZONE_RENDERER_API_EVIDENCE_PASS",
        "NO_BRILLOUIN_RENDERER_EXTERNAL_NETWORK_REQUESTS",
        "NO_SECRET_PATTERN_HITS",
    }
    matrix = _json("browser/matrix.json")["results"]
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] and item["externalRequests"] == 0 for item in matrix)
    assert all(item["simple"]["metrics"]["canvasCount"] == 1 for item in matrix)
    assert all(item["simple"]["metrics"]["contextCount"] == 1 for item in matrix)
    assert all(item["simple"]["metrics"]["drawCalls"] > 0 for item in matrix)
    runtime = _json("api/runtime_source.json")
    assert runtime == {
        "source": "Phase 10I-1 QueueWorkerRuntime",
        "selectedTool": "structure.brillouin_zone",
        "status": "completed",
        "artifactCount": 6,
        "externalNetworkRequests": 0,
    }
    network = _json("browser/network_audit.json")
    assert network["external_requests"] == network["texture_requests"] == network["module_requests"] == 0
    assert network["marker"] == "NO_BRILLOUIN_RENDERER_EXTERNAL_NETWORK_REQUESTS"
    security = _json("security/security_audit.json")
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert security["renderer_owned_by_application"] is True
    assert not any(security[key] for key in ("artifact_javascript", "artifact_html", "artifact_css", "artifact_shader", "artifact_module", "external_urls", "remote_assets", "iframe", "eval", "dynamic_artifact_import"))


def test_phase10i2_mobile_png_screenshots_and_hash_inventory_are_replayable() -> None:
    mobile = _json("browser/mobile.json")
    assert mobile["portrait"]["overflow"] is False
    assert mobile["landscape"]["overflow"] is False
    png = EVIDENCE / "screenshots" / "17_png_export.png"
    assert png.read_bytes()[:8] == bytes((137, 80, 78, 71, 13, 10, 26, 10))
    screenshots = sorted((EVIDENCE / "screenshots").glob("*.png"))
    assert len(screenshots) == 18
    assert screenshots[-1].name == "18_largest_scientific_topology.png"
    inventory = _json("artifact_hashes.json")
    assert inventory["algorithm"] == "sha256"
    records = {item["name"]: item for item in inventory["files"]}
    files = sorted(path for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    assert set(records) == {path.relative_to(EVIDENCE).as_posix() for path in files}
    for path in files:
        relative = path.relative_to(EVIDENCE).as_posix()
        content = path.read_bytes()
        assert records[relative]["bytes"] == len(content)
        assert records[relative]["sha256"] == hashlib.sha256(content).hexdigest()


def test_phase10i2_evidence_contains_no_private_path_or_secret_pattern() -> None:
    forbidden = ("authorization:", "bearer ", "api_key", "secret_key", "password=", "file://", "c:\\users\\")
    for path in EVIDENCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() == ".png":
            continue
        text = path.read_text(encoding="utf-8").lower()
        assert not any(marker in text for marker in forbidden), path
