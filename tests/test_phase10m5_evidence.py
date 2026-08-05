from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m5_scientific_report_recipe"


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m5_acceptance_browser_and_scientific_integrity_evidence() -> None:
    acceptance = _json("acceptance_mapping.json")
    assert acceptance["expected"] == acceptance["implemented"] == 7
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == 0
    assert [item["id"] for item in acceptance["items"]] == [f"M5-A0{index}" for index in range(1, 8)]

    browser = _json("browser_matrix.json")
    assert set(browser) == {"chromium", "firefox", "webkit"}
    for result in browser.values():
        assert result["metadataFirst"] is True
        assert result["initialArtifactPayloadRequests"] == result["reportPreviewWebglContexts"] == 0
        assert result["previewWrites"] == 0
        assert result["finalizePair"] is True
        assert result["idempotentHistoryCount"] == 1
        assert result["overflow"] == {"body": 0, "root": 0}
        assert result["consoleErrors"] == result["pageErrors"] == result["failedResponses"] == []
        assert result["externalRequests"] == []

    mobile = _json("browser_mobile.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["sourceSheet"] is mobile["focusRestored"] is True
    assert mobile["minTouchTarget"] >= 44
    assert mobile["overflow"] == {"body": 0, "root": 0}

    preview = _json("preview_no_writes.json")
    assert preview["reportWrites"] == preview["recipeWrites"] == 0
    assert preview["jobCreation"] == preview["toolCallCreation"] == preview["queueMessageCreation"] == 0
    assert preview["before"] == preview["after"]
    idempotency = _json("idempotency.json")
    assert idempotency["reportRecordCount"] == idempotency["recipeRecordCount"] == 1
    assert idempotency["sameReportId"] is idempotency["sameRecipeId"] is True


def test_phase10m5_manifest_security_and_deepseek_policy() -> None:
    manifest = _json("manifest.json")
    assert manifest["schemaVersion"] == "phase10m5.evidence_manifest.v1"
    entries = manifest["entries"]
    assert entries == sorted(entries, key=lambda item: item["path"])
    actual = {
        item.relative_to(EVIDENCE).as_posix()
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.name != "manifest.json"
    }
    assert {item["path"] for item in entries} == actual
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        hashed = raw.replace(b"\r\n", b"\n") if entry["hashMode"] == "lf_normalized_text" else raw
        assert len(raw) == entry["bytes"]
        assert sha256(hashed).hexdigest() == entry["sha256"]

    security = _json("security.json")
    required = {
        "ARTIFACT_CONTENT_IS_INERT_DATA",
        "NO_REPORT_ARBITRARY_CODE_EXECUTION",
        "NO_REPORT_SHELL_OR_FILESYSTEM_AUTHORITY",
        "NO_REPORT_PROVIDER_AUTHORITY",
        "NO_RECIPE_EXECUTION_AUTHORITY",
        "NO_RECIPE_PLAN_CREATION_AUTHORITY",
        "NO_RECIPE_JOB_CREATION_AUTHORITY",
        "NO_RECIPE_QUEUE_AUTHORITY",
        "NO_REPORT_ARTIFACT_JAVASCRIPT",
        "NO_REPORT_ARTIFACT_HTML_EXECUTION",
        "NO_REPORT_EXTERNAL_ARTIFACT_URL_EXECUTION",
        "NO_CROSS_PROJECT_REPORT_SOURCE",
        "NO_STALE_REPORT_SOURCE_REBINDING",
        "NO_REPORT_SCIENTIFIC_RECOMPUTATION",
        "NO_REPORT_GENERATED_SCIENTIFIC_CLAIMS",
        "NO_SECRET_PATTERN_HITS",
        "DEEPSEEK_POLICY_REGRESSION",
    }
    assert all(security[marker] == "PASS" for marker in required)
    assert security["REAL_LLM_CALLS"] == 0

    evidence_text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in evidence_text
    assert "Authorization:" not in evidence_text
    assert not re.search(r"[A-Za-z]:\\Users\\", evidence_text)
    assert "/home/runner/" not in evidence_text


def test_phase10m5_required_inventory_and_screenshots() -> None:
    required = {
        "entry_gate.json",
        "authority_audit.json",
        "report_recipe_contracts.json",
        "source_eligibility_matrix.json",
        "report_complete_case.json",
        "report_plan01_case.json",
        "report_partial_case.json",
        "report_no_interpretation_case.json",
        "report_stale_missing_legacy_case.json",
        "recipe_plan01.json",
        "recipe_plan02.json",
        "recipe_determinism.json",
        "preview_no_writes.json",
        "persistence_atomicity.json",
        "idempotency.json",
        "authorization.json",
        "export_json.json",
        "export_markdown.md",
        "export_manifest.json",
        "performance.json",
        "security.json",
        "browser_chromium.json",
        "browser_firefox.json",
        "browser_webkit.json",
        "browser_mobile.json",
        "manifest.json",
    }
    assert required.issubset({item.name for item in EVIDENCE.iterdir()})
    screenshots = EVIDENCE / "screenshots"
    for name in ("chromium_report.png", "firefox_report.png", "webkit_report.png", "mobile_report.png"):
        assert (screenshots / name).stat().st_size > 10_000
