from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10l/evidence/phase10l4_grounded_interpretation"


def _load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10l4_evidence_manifest_and_required_inventory() -> None:
    required = {
        "entry_gate.json",
        "interpretability_matrix.json",
        "scientific_boundary_matrix.json",
        "phonon_chain_case.json",
        "partial_execution_case.json",
        "provider_projection.json",
        "provider_isolation_audit.json",
        "security_audit.md",
        "performance_audit.md",
        "browser_matrix.json",
        "mobile_smoke.json",
        "deterministic_replay.json",
        "browser_semantic_contract.json",
        "console_audit.json",
        "network_audit.json",
        "dom_snapshot.json",
        "screenshots/desktop_deterministic.png",
        "screenshots/desktop_strict_provider.png",
        "screenshots/desktop_partial.png",
        "screenshots/mobile_deterministic.png",
        "screenshots/mobile_partial.png",
    }
    assert all((EVIDENCE / name).is_file() for name in required)

    inventory = _load("interpretability_matrix.json")
    assert inventory["availabilityFilter"] == "AVAILABLE"
    assert inventory["toolCount"] == 38
    assert len(inventory["tools"]) == 38
    assert len({item["toolId"] for item in inventory["tools"]}) == 38
    ready = {item["toolId"] for item in inventory["tools"] if item["state"] == "INTERPRETATION_READY"}
    assert {
        "table.numeric_summary",
        "ml.basic_metrics",
        "structure.summary",
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
        "structure.volumetric_data",
    }.issubset(ready)

    authority = _load("interpretation_inventory.json")
    assert authority["rawSummaryTrusted"] is False
    assert authority["rawArtifactSentToProvider"] is False
    assert authority["providerCanModifyIntentPlanOrJob"] is False
    assert authority["artifactPromptInjectionBoundary"] == "RAW_TEXT_EXCLUDED_FROM_PROVIDER_SAFE_PROJECTION"
    assert authority["fileMap"]["terminalSourceGateAndApi"] == "apps/api/mdi_api/routers/planner.py"

    manifest = _load("evidence_manifest.json")
    assert manifest["algorithm"] == "sha256-lf-normalized-text-v1"
    listed = {item["path"]: item for item in manifest["files"]}
    actual = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "evidence_manifest.json"
    }
    assert set(listed) == actual
    for relative, record in listed.items():
        payload = (EVIDENCE / relative).read_bytes()
        canonical = payload if relative.lower().endswith(".png") else payload.replace(b"\r\n", b"\n")
        assert record["bytes"] == len(canonical)
        assert record["sha256"] == sha256(canonical).hexdigest()


def test_phase10l4_runtime_provider_and_partial_evidence_is_exact() -> None:
    chain = _load("phonon_chain_case.json")
    partial = _load("partial_execution_case.json")
    assert chain["runtime"]["status"] == "completed"
    assert chain["execution"]["outcome"] == "ALL_SUCCEEDED"
    assert chain["api"]["outcome"] == "INTERPRETATION_READY_WITH_LIMITS"
    assert chain["api"]["limitations"]
    assert chain["strictProviderApi"]["outcome"] == "INTERPRETATION_READY_WITH_LIMITS"
    assert chain["strictProviderApi"]["mode"] == "STRICT_PROVIDER"
    assert chain["executionAuthorityChanged"] is False
    assert {item["sourceToolId"] for item in chain["evidence"]["evidenceItems"]} == {
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
    }
    visible = set(chain["providerVisibleEvidenceIds"])
    projected = {item["evidenceItemId"] for item in chain["strictProviderEvidence"]["evidenceItems"]}
    assert visible == projected

    assert partial["execution"]["outcome"] == "PARTIAL_RESULTS"
    assert partial["api"]["outcome"] == "INTERPRETATION_READY_WITH_LIMITS"
    assert partial["api"]["partialResultState"] is True
    assert partial["api"]["limitations"]
    assert partial["executionAuthorityChanged"] is False
    assert all(not value for value in partial["api"]["noExecution"].values())


def test_phase10l4_browser_matrix_is_complete_inert_and_mode_exact() -> None:
    matrix = _load("browser_matrix.json")
    expected_cases = {
        "deterministic",
        "strict_provider",
        "partial",
        "no_supported_evidence",
        "validation_failure",
        "source_integrity_failure",
    }
    assert set(matrix) == {"chromium", "firefox", "webkit"}
    for browser_name, browser in matrix.items():
        assert set(browser["cases"]) == expected_cases
        assert browser["externalRequests"] == 0
        assert browser["consoleErrors"] == []
        assert browser["pageErrors"] == []
        for case in browser["cases"].values():
            assert case["horizontalOverflow"] is False
            assert all(value == 0 for value in case["inert"].values())
            assert all(not value for value in case["noExecution"].values())
        assert browser["cases"]["strict_provider"]["requestMode"] == "STRICT_PROVIDER"
        assert browser["cases"]["deterministic"]["requestMode"] == "DETERMINISTIC"
        if browser_name == "chromium":
            assert set(browser["mobile"]) == {"deterministic", "partial", "no_supported_evidence"}
            assert all(case["horizontalOverflow"] is False for case in browser["mobile"].values())
        else:
            assert browser["mobile"] == {}

    assert _load("console_audit.json") == {"consoleErrors": [], "pageErrors": []}
    assert _load("network_audit.json") == {
        "externalRequests": 0,
        "marker": "NO_PHASE10L4_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
    }
    replay = _load("deterministic_replay.json")
    assert set(replay) == {"chromium", "firefox", "webkit"}
    assert all(value["stable"] is True for value in replay.values())
    assert all(value["firstSemanticSha256"] == value["secondSemanticSha256"] for value in replay.values())
    assert all(value["firstDomSha256"] == value["secondDomSha256"] for value in replay.values())

    semantic_contract = _load("browser_semantic_contract.json")
    assert semantic_contract["schemaVersion"] == "1.0"
    assert len(semantic_contract["fixtureContractHash"]) == 64
    assert set(semantic_contract["browsers"]) == {"chromium", "firefox", "webkit"}
    assert all(browser["deterministicReplayStable"] is True for browser in semantic_contract["browsers"].values())
    assert all(browser["externalRequests"] == 0 for browser in semantic_contract["browsers"].values())
    assert all(browser["consoleErrorCount"] == 0 for browser in semantic_contract["browsers"].values())
    assert all(browser["pageErrorCount"] == 0 for browser in semantic_contract["browsers"].values())


def test_phase10l4_security_markers_and_secret_scan() -> None:
    security = (EVIDENCE / "security_audit.md").read_text(encoding="utf-8")
    required_markers = {
        "REAL_LLM_CALLS = 0",
        "NO_INTERPRETATION_TOOL_EXECUTION_AUTHORITY",
        "NO_INTERPRETATION_PLAN_MUTATION",
        "NO_INTERPRETATION_JOB_OR_ENQUEUE",
        "NO_RAW_ARTIFACT_PAYLOAD_TO_PROVIDER",
        "NO_UNGROUNDED_NUMERIC_CLAIMS",
        "NO_UNGROUNDED_UNIT_CLAIMS",
        "NO_UNGROUNDED_ENTITY_CLAIMS",
        "NO_UNSUPPORTED_SCIENTIFIC_CONCLUSIONS",
        "NO_SECRET_PATTERN_HITS",
    }
    assert all(marker in security for marker in required_markers)

    secret_pattern = re.compile(
        rb"(?:sk-[A-Za-z0-9_-]{16,}|api[_-]?key\s*[:=]\s*[A-Za-z0-9._-]{12,}|bearer\s+[A-Za-z0-9._-]{16,})",
        re.IGNORECASE,
    )
    hits = []
    for path in EVIDENCE.rglob("*"):
        if path.is_file() and path.suffix.lower() != ".png" and secret_pattern.search(path.read_bytes()):
            hits.append(path.relative_to(EVIDENCE).as_posix())
    assert hits == []
