from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from mdi_llm import ARTIFACT_PROJECTOR_CONTRACTS, PROJECTOR_VERSION
from mdi_tool_registry import build_registry_snapshot, load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10l/evidence/phase10l4_grounded_interpretation"


def _task_snapshot() -> dict:
    blocks = []
    for raw_block in (ROOT / "TASKS.md").read_text(encoding="utf-8").split("---TASK---")[1:]:
        body, separator, _ = raw_block.partition("---END---")
        if not separator:
            continue
        match = re.search(r"Phase 10L-[0-9]+", body)
        status = re.search(r"^\u72b6\u6001\uff1a(.+)$", body, re.MULTILINE)
        blocks.append({"title": match.group(0) if match else "UNKNOWN", "status": status.group(1).strip() if status else "UNKNOWN"})
    processing = [block for block in blocks if block["status"] == "\u5904\u7406\u4e2d"]
    pending = [block for block in blocks if block["status"] == "\u5f85\u5904\u7406"]
    return {
        "taskBlockCountAfterAdmission": len(blocks),
        "activeExecutableTaskCount": len(processing),
        "activeTask": processing[0]["title"] if len(processing) == 1 else None,
        "reviewerQueuedPendingTaskCount": len(pending),
        "reviewerQueuedPendingTasks": [block["title"] for block in pending],
        "taskBlocks": blocks,
    }


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
    registry = load_manifests()
    snapshot, metadata_by_id = build_registry_snapshot(registry)
    available = {
        tool.toolId: metadata_by_id[tool.toolId]
        for tool in registry.tools
        if metadata_by_id[tool.toolId].availability.value == "AVAILABLE"
    }
    assert inventory["registrySnapshotId"] == snapshot.snapshotId
    assert inventory["registrySnapshotHash"] == snapshot.snapshotHash
    assert inventory["toolCount"] == len(available)
    assert {item["toolId"] for item in inventory["tools"]} == set(available)
    for item in inventory["tools"]:
        assert item["aggregateState"] == item["state"]
        assert {artifact["artifactType"] for artifact in item["artifacts"]} == set(item["declaredArtifactTypes"])
        for artifact in item["artifacts"]:
            assert artifact["state"] in {
                "INTERPRETATION_READY",
                "DISPLAY_ONLY",
                "UNSUPPORTED_CONTRACT",
                "UNSAFE_UNTRUSTED_TEXT",
                "NO_STRUCTURED_FACTS",
            }
            assert artifact["safeProjectorReady"] is (artifact["state"] == "INTERPRETATION_READY")
            if artifact["state"] == "INTERPRETATION_READY":
                assert all(artifact[key] is True for key in ("structuredFactsAuthority", "unitAuthority", "warningAuthority", "identityAuthority"))
                contract = ARTIFACT_PROJECTOR_CONTRACTS[(item["toolId"], artifact["artifactType"])]
                assert artifact["contractStatus"] == "PROJECTOR_CONTRACT_ALLOWLIST"
                assert artifact["contractFamily"] == contract.contract_family
                assert artifact["acceptedContractVersions"] == list(contract.accepted_versions)
                assert artifact["mediaTypes"] == list(contract.media_types)
                assert artifact["projectorVersion"] == PROJECTOR_VERSION
            else:
                assert all(artifact[key] is False for key in ("structuredFactsAuthority", "unitAuthority", "warningAuthority", "identityAuthority"))
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
    required_components = {
        "deterministic summary", "LLM summary", "findings", "warnings", "recommendations",
        "artifact explanation", "report text", "recipe text", "artifact-specific summary builders",
        "frontend findings UI", "persistence", "API", "provider prompt", "provider output schema",
        "grounding validator", "full natural-language evidence closure", "unified workspace",
    }
    component_inventory = {item["component"]: item for item in authority["preImplementationInventory"]}
    assert set(component_inventory) == required_components
    assert all(item["status"] in {"READY", "REUSABLE_FOUNDATION", "PARTIAL", "UNSAFE_FOR_L4", "MISSING", "DEFER_10L5", "DEFER_10M"} for item in component_inventory.values())
    assert all("sourceFiles" in item and item["currentBehavior"] and item["l4Decision"] for item in component_inventory.values())
    current = authority["currentL4Authority"]
    assert all(item["status"] == "READY" for item in current.values())
    assert current["recommendations"]["executionAuthority"] == "NON_EXECUTABLE"

    gate = _load("entry_gate.json")
    expected_queue = _task_snapshot()
    assert {key: gate[key] for key in expected_queue} == expected_queue

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
        canonical = payload if relative.lower().endswith(".png") else payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
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
        assert browser["backendMode"] == "FIXTURE_REPLAY_FROM_PERSISTED_API_CASES"
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
    assert all(
        browser["backendMode"] == "FIXTURE_REPLAY_FROM_PERSISTED_API_CASES"
        for browser in semantic_contract["browsers"].values()
    )
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
