from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m3_canonical_selection"


def _json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10m3_acceptance_and_browser_evidence() -> None:
    acceptance = _json("acceptance_mapping.json")
    assert acceptance["expected"] == acceptance["implemented"] == 7
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == 0
    assert [item["id"] for item in acceptance["items"]] == [f"M3-A0{index}" for index in range(1, 8)]
    assert all(item["result"] == "PASS" for item in acceptance["items"])

    browser = _json("browser_matrix.json")
    assert set(browser) == {"chromium", "firefox", "webkit"}
    assert all(
        item["urlRestore"]
        and item["artifactSelection"]
        and item["backForward"]
        and item["staleRejected"]
        for item in browser.values()
    )
    mobile = _json("mobile_smoke.json")
    assert mobile["viewport"] == [390, 844]
    assert mobile["overflow"] == {"body": 0, "root": 0}
    assert mobile["minTouchTarget"] >= 44
    assert mobile["focusedClose"] is mobile["focusRestored"] is True
    performance = _json("performance.json")
    assert performance["runnerElapsedMs"] > 0
    assert performance["nodeHeapBytes"]["final"] >= performance["nodeHeapBytes"]["initial"]
    assert all(item["elapsedMs"] > 0 for item in performance["desktop"].values())
    assert performance["mobile"]["elapsedMs"] > 0


def test_phase10m3_manifest_security_and_no_hidden_write() -> None:
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
        "NO_SELECTION_ARBITRARY_CODE_EXECUTION",
        "NO_SELECTION_ARRAY_INDEX_AUTHORITY",
        "NO_SELECTION_DISPLAY_LABEL_AUTHORITY",
        "NO_SELECTION_FUZZY_MATCH",
        "NO_SELECTION_STALE_IDENTITY_REBINDING",
        "NO_SECRET_PATTERN_HITS",
    }
    assert required.issubset(security["markers"])
    assert security["browserConsoleErrors"] == 0
    assert security["externalRequests"] == 0
    assert security["artifactPayloadRequests"] == 0
    assert security["executionRequests"] == 0

    database = _json("database_write_audit.json")
    assert database["migration"] == "UNCHANGED"
    assert database["selectionAutoPersistence"] is False
    assert database["jobToolArtifactCreatedBySelection"] is False

    evidence_text = "\n".join(
        item.read_text(encoding="utf-8", errors="ignore")
        for item in EVIDENCE.rglob("*")
        if item.is_file() and item.suffix.lower() in {".txt", ".json", ".md"}
    )
    assert "DEEPSEEK_KEY=" not in evidence_text
    assert "Authorization:" not in evidence_text
    assert not re.search(r"[A-Za-z]:\\Users\\", evidence_text)
    assert "/home/runner/" not in evidence_text
    assert "PRIVATE_ARTIFACT_PAYLOAD" not in evidence_text


def test_phase10m3_identity_and_provider_policy() -> None:
    contract = _json("selection_contract_snapshot.json")
    assert contract["schemaVersion"] == "1.0"
    assert len(contract["supportedKinds"]) == 13
    assert contract["maxSecondary"] == 16
    assert contract["urlMaxBytes"] == 2048

    matrix = _json("identity_producer_matrix.json")
    assert len(matrix["supported"]) == 13
    assert "rowIndex" in matrix["forbidden"]
    policy = _json("deepseek_policy_regression.json")
    assert policy["providerPolicy"] == "DEEPSEEK_ONLY"
    assert policy["realLlmCalls"] == policy["newLlmCallSites"] == 0
