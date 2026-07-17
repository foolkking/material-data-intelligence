from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "phase10i" / "evidence" / "phase10i3_band_bz_linked_view"


def _json(relative: str) -> object:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def _canonical_evidence_bytes(path: Path) -> bytes:
    if path.suffix.lower() == ".png":
        return path.read_bytes()
    return path.read_text(encoding="utf-8").encode("utf-8")


def test_runtime_browser_mapping_and_network_evidence_is_closed() -> None:
    manifest = _json("evidence_manifest.json")
    assert manifest["source"] == "QueueWorkerRuntime phonon.band + structure.brillouin_zone artifacts"
    assert manifest["schema"] == "phase10i3.reciprocal_band_bz_link.v1"
    assert manifest["externalRequests"] == 0
    assert set(manifest["markers"]) == {
        "BAND_BZ_LINKED_VIEW_BROWSER_EVIDENCE_PASS",
        "BAND_BZ_BIDIRECTIONAL_SELECTION_EVIDENCE_PASS",
        "BAND_BZ_LINK_PERFORMANCE_EVIDENCE_PASS",
        "BAND_BZ_LINK_ACCESSIBILITY_EVIDENCE_PASS",
        "NO_BAND_BZ_LINK_EXTERNAL_NETWORK_REQUESTS",
        "NO_SECRET_PATTERN_HITS",
    }
    calls = _json("api/tool_calls.json")
    assert [(item["toolId"], item["status"]) for item in calls] == [("phonon.band", "completed"), ("structure.brillouin_zone", "completed")]
    compatibility = _json("compatibility/backend_validation.json")
    assert compatibility["compatible"] is True
    animation = _json("compatibility/animation_handoff.json")
    assert animation["status"] == "exact_canonical_mode"
    matrix = _json("browser/matrix.json")["results"]
    assert [item["browser"] for item in matrix] == ["chromium", "firefox", "webkit"]
    assert all(item["available"] and item["externalRequests"] == 0 for item in matrix)
    assert all(item["linked"]["selection"]["kind"] == "reciprocal_sample" for item in matrix)
    assert _json("mobile/audit.json") == {"band": {"canvasCount": 0}, "bz": {"canvasCount": 1, "overflow": False}, "inspector": {"canvasCount": 0, "overflow": False}}


def test_screenshots_and_hash_inventory_are_complete() -> None:
    screenshots = sorted((EVIDENCE / "screenshots").glob("*.png"))
    assert len(screenshots) == 18
    assert screenshots[0].read_bytes()[:8] == bytes((137, 80, 78, 71, 13, 10, 26, 10))
    inventory = _json("artifact_hashes.json")
    records = {item["name"]: item for item in inventory["files"]}
    files = sorted(path for path in EVIDENCE.rglob("*") if path.is_file() and path.name != "artifact_hashes.json")
    assert set(records) == {path.relative_to(EVIDENCE).as_posix() for path in files}
    for path in files:
        relative = path.relative_to(EVIDENCE).as_posix()
        content = _canonical_evidence_bytes(path)
        assert records[relative]["bytes"] == len(content)
        assert records[relative]["sha256"] == hashlib.sha256(content).hexdigest()


def test_evidence_is_sanitized_and_inert() -> None:
    forbidden = ("authorization:", "bearer ", "api_key", "secret_key", "password=", "file://", "c:\\users\\", "javascript:", "<script")
    for path in EVIDENCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() == ".png":
            continue
        text = path.read_text(encoding="utf-8").lower()
        assert not any(marker in text for marker in forbidden), path
    security = _json("security/audit.json")
    assert security["marker"] == "NO_SECRET_PATTERN_HITS"
    assert not any(security[key] for key in ("artifactJavaScript", "artifactHtml", "artifactCss", "artifactShader", "externalUrls", "dynamicArtifactImport", "labelMapping"))
