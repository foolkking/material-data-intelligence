from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m2_workspace_shell"


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m2_acceptance_browser_and_security_evidence() -> None:
    acceptance = _json("acceptance_mapping.json")
    assert acceptance["expected"] == acceptance["implemented"] == 7
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == 0
    assert [item["id"] for item in acceptance["items"]] == [
        "M2-A01", "M2-A02", "M2-A03", "M2-A04", "M2-A05", "M2-A06", "M2-A07"
    ]
    assert all(item["result"] == "PASS" for item in acceptance["items"])

    browser = _json("browser_matrix.json")
    assert set(browser) == {"chromium", "firefox", "webkit"}
    assert all(item["navigationGroups"] == 9 for item in browser.values())
    assert all(item["consoleErrors"] == [] and item["pageErrors"] == [] for item in browser.values())
    assert all(item["externalRequests"] == [] and item["artifactPayloadCalls"] == [] for item in browser.values())
    assert browser["chromium"]["panelCapCases"]["32"]["apiPanelCount"] == 32
    assert browser["chromium"]["panelCapCases"]["repeatedSwitches"]["activePanelCount"] == 1

    mobile = _json("mobile_smoke.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["overflow"] == {"body": 0, "root": 0}
    assert mobile["minTouchTarget"] >= 44
    assert mobile["panel32SwitcherCount"] == 32
    assert mobile["focusedClose"] is mobile["focusRestored"] is True

    security = _json("security_cases.json")
    assert security["artifactPayloadRequests"] == security["externalRequests"] == 0
    assert security["consoleErrors"] == security["pageErrors"] == 0
    assert security["realLlmCalls"] == 0
    assert "NO_WORKSPACE_SHELL_ARBITRARY_CODE_EXECUTION" in security["markers"]
    assert "NO_SECRET_PATTERN_HITS" in security["markers"]


def test_phase10m2_evidence_manifest_and_redaction() -> None:
    required = {
        "baseline.txt", "entry_gate.txt", "m1_archive_verification.txt",
        "acceptance_mapping.json", "route_inventory.json", "workspace_api_cases.json",
        "planner_transition.json", "completed_workspace.json", "running_workspace.json",
        "partial_workspace.json", "legacy_workspace.json", "stale_missing_workspace.json",
        "unsupported_panel.json", "active_panel_url.json", "back_forward.json", "refresh.json",
        "accessibility.json", "responsive.json", "performance.json", "security.json",
        "deepseek_policy_regression.json", "real_deepseek_evidence.json",
        "network_summary.json", "console_summary.json", "test_summary.txt", "secret_scan.txt",
    }
    assert required.issubset({item.name for item in EVIDENCE.iterdir()})
    manifest = _json("file_manifest.json")
    entries = manifest["entries"]
    assert entries == sorted(entries, key=lambda item: item["path"])
    manifest_paths = {item["path"] for item in entries}
    actual_paths = {
        item.relative_to(EVIDENCE).as_posix()
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.name != "file_manifest.json"
    }
    assert manifest_paths == actual_paths
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        hashed = raw.replace(b"\r\n", b"\n") if entry["hashMode"] == "lf_normalized_text" else raw
        assert len(raw) == entry["bytes"]
        assert sha256(hashed).hexdigest() == entry["sha256"]

    text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in text
    assert "Authorization:" not in text
    assert not re.search(r"[A-Za-z]:\\Users\\", text)
    assert "/home/runner/" not in text
    assert "PRIVATE_ARTIFACT_PAYLOAD" not in text


def test_phase10m2_has_current_browser_screenshots() -> None:
    screenshots = EVIDENCE / "screenshots"
    assert all((screenshots / f"{browser}_completed.png").stat().st_size > 10_000 for browser in ("chromium", "firefox", "webkit"))
    assert (screenshots / "chromium_mobile_context.png").stat().st_size > 10_000
    assert (screenshots / "chromium_mobile_inspector.png").stat().st_size > 10_000
