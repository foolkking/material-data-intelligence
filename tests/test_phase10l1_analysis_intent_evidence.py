from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from mdi_schemas import AnalysisIntent, compute_analysis_intent_hash, deterministic_intent_id


EVIDENCE = Path("docs/phase10l/evidence/phase10l1_analysis_intent")


def load(relative: str) -> dict:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def test_phase10l1_api_captures_preserve_gate_and_revision_semantics() -> None:
    ready = load("api/ready_planner_job.json")["response"]
    unsupported = load("api/unsupported_no_job.json")["response"]
    clarification = load("api/needs_clarification.json")["response"]
    revised = load("api/clarification_revision.json")["response"]

    assert ready["ok"] is True
    assert ready["intent_outcome"] == "READY"
    assert ready["job_id"] and ready["plan_id"]
    assert unsupported["intent_outcome"] == "UNSUPPORTED"
    assert unsupported["job_id"] is unsupported["plan_id"] is unsupported["plan"] is None
    assert unsupported["enqueued"] is False
    assert clarification["outcome"] == "NEEDS_CLARIFICATION"
    assert len(clarification["intent"]["clarification"]["questions"]) <= 3
    assert revised["outcome"] == "READY"
    assert revised["intent"]["provenance"]["parentIntentId"] == clarification["intent_id"]
    assert revised["intent_id"] != clarification["intent_id"]

    for payload in (ready["intent"], unsupported["intent"], clarification["intent"], revised["intent"]):
        intent = AnalysisIntent.model_validate(payload)
        assert intent.intentHash == compute_analysis_intent_hash(intent)
        assert intent.intentId == deterministic_intent_id(intent.intentHash)


def test_phase10l1_persistence_and_performance_evidence_is_bounded() -> None:
    revisions = load("persistence/immutable_revisions.json")
    persistence = load("persistence/sqlite_and_postgres_gate.json")
    performance = load("performance/near_cap.json")
    assert revisions["intentCount"] == 2
    assert revisions["planCount"] == revisions["jobCount"] == 0
    assert persistence["idempotentReplay"] is True
    assert persistence["immutableHistory"] is True
    assert persistence["postgresqlLocal"] == "UNAVAILABLE_WITHOUT_DATABASE_URL"
    assert performance["goalCharacters"] == 16_384
    assert performance["resourceRefs"] == 32
    assert performance["serializedBytes"] <= performance["serializedByteCap"]
    assert performance["bounded"] is True


def test_phase10l1_browser_matrix_and_mobile_are_real_and_inert() -> None:
    matrix = load("browser/browser_matrix.json")
    assert set(matrix) == {"chromium", "firefox", "webkit"}
    for browser in matrix.values():
        assert browser["version"]
        assert browser["externalRequests"] == 0
        assert browser["consoleErrors"] == []
        assert browser["pageErrors"] == []
        assert browser["cases"]["ready"]["initialOutcome"] == "READY"
        assert browser["cases"]["clarification"]["initialOutcome"] == "NEEDS_CLARIFICATION"
        assert browser["cases"]["clarification"]["revisedOutcome"] == "READY"
        assert browser["cases"]["unsupported"]["initialOutcome"] == "UNSUPPORTED"
        assert browser["cases"]["unsupported"]["runDisabled"] is True
        for case in browser["cases"].values():
            assert case["horizontalOverflow"] is False
            assert not any(case["inert"].values())
    mobile = matrix["chromium"]["mobile"]
    assert mobile["mobile"] is True
    assert mobile["initialOutcome"] == "NEEDS_CLARIFICATION"
    assert mobile["revisedOutcome"] == "READY"
    assert mobile["horizontalOverflow"] is False

    screenshots = sorted((EVIDENCE / "screenshots").glob("*.png"))
    assert len(screenshots) == 6
    assert all(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for path in screenshots)


def test_phase10l1_security_markers_and_manifest_integrity() -> None:
    security = load("security/security_audit.json")
    assert security["realLlmCalls"] == 0
    assert security["externalNetworkRequests"] == 0
    assert security["arbitraryCodeExecution"] is False
    assert security["artifactJavaScript"] is False
    assert security["markers"] == [
        "REAL_LLM_CALLS = 0",
        "NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS",
        "NO_ANALYSIS_INTENT_ARBITRARY_CODE_EXECUTION",
        "NO_ANALYSIS_INTENT_ARTIFACT_JAVASCRIPT",
        "NO_SECRET_PATTERN_HITS",
    ]
    network = load("browser/network_audit.json")
    assert network == {"externalRequests": 0, "marker": "NO_PHASE10L1_EXTERNAL_NETWORK_REQUESTS"}

    manifest = load("evidence_manifest.json")
    expected_files = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "evidence_manifest.json"
    }
    assert {entry["path"] for entry in manifest["files"]} == expected_files
    for entry in manifest["files"]:
        payload = (EVIDENCE / entry["path"]).read_bytes()
        assert len(payload) == entry["bytes"]
        assert sha256(payload).hexdigest() == entry["sha256"]
