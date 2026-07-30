from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


EVIDENCE = Path("docs/phase10l/evidence/phase10l2_capability_aware_planner")


def load(relative: str) -> dict:
    return json.loads((EVIDENCE / relative).read_text(encoding="utf-8"))


def test_registry_inventory_resolution_and_provider_isolation_evidence() -> None:
    inventory = load("registry/actual_capability_inventory.json")
    snapshot = load("registry/snapshot.json")
    trace = load("eligibility/ready_trace.json")
    isolation = load("provider/candidate_isolation.json")
    assert inventory["toolCount"] == len(inventory["tools"]) == len(snapshot["tools"]) == 53
    assert inventory["availableCount"] > 0
    assert snapshot["schemaVersion"] == "1.0"
    assert trace["invariants"] == {
        "analysisPlanSchemaVersion": "0.1",
        "providerVisibleEqualsEligible": True,
        "rejectedProviderIntersection": [],
        "selectedSubsetEligible": True,
    }
    assert isolation["providerVisibleEqualsEligible"] is True
    assert isolation["providerVisibleToolIds"] == isolation["eligibleToolIds"]
    assert set(isolation["selectedToolIds"]).issubset(isolation["eligibleToolIds"])
    assert isolation["rejectedCandidateLeak"] == []


def test_exact_binding_and_known_misselection_regressions_are_closed() -> None:
    exact = load("regressions/formation_energy_vs_band_gap.json")
    uncertainty = load("regressions/uncertainty_trust.json")
    phonon = load("regressions/phonon_no_fallback.json")
    broad = load("regressions/broad_analysis.json")
    formation = exact["formationEnergy"]["decision"]["selections"][0]
    band_gap = exact["bandGap"]["decision"]["selections"][0]
    assert formation["toolId"] == band_gap["toolId"] == "ml.regression_evaluation"
    assert formation["boundParameters"][0]["value"] == ["regression_0"]
    assert band_gap["boundParameters"][0]["value"] == ["regression_1"]
    assert uncertainty["decision"]["selections"][0]["toolId"] == "ml.uncertainty_evaluation"
    assert phonon["decision"]["selections"][0]["toolId"] == "phonon.band"
    assert broad["decision"]["selections"][0]["toolId"] == "dataset.materials_explorer"


def test_llm_repair_api_no_job_persistence_and_performance_evidence() -> None:
    repair = load("llm/strict_parse_and_one_repair.json")
    ready = load("api/plan_ready.json")["response"]
    blocked = load("api/non_ready_no_job.json")
    persistence = load("persistence/immutable_associations.json")
    performance = load("performance/near_cap.json")
    assert repair["calls"] == 2
    assert repair["outcome"] == "PLAN_READY"
    assert repair["decision"]["provenance"]["repairCount"] == 1
    assert repair["initialProviderVisibleIds"] == repair["repairProviderVisibleIds"]
    assert repair["rejectedCandidateLeak"] is False
    assert ready["capability_outcome"] == "PLAN_READY"
    assert ready["plan"]["schemaVersion"] == "0.1"
    assert ready["job_id"] and ready["plan_id"]
    assert blocked["response"]["capability_outcome"] == "CAPABILITY_MISMATCH"
    assert blocked["response"]["job_id"] is blocked["response"]["plan_id"] is None
    assert blocked["persisted"] == {
        "decisions": 1,
        "executions": 0,
        "jobs": 0,
        "plans": 0,
        "queueMessages": 0,
        "resolutions": 1,
        "toolExecutions": 0,
    }
    assert persistence["sqlite"]["resolutionIdempotent"] is True
    assert persistence["sqlite"]["decisionIdempotent"] is True
    assert persistence["migrationUnit"] == "upgrade/downgrade/re-upgrade PASS"
    assert performance["registryCandidates"] == 53
    assert performance["bounded"] is True
    assert performance["resolutionBytes"] <= performance["serializedByteCap"]
    assert performance["decisionBytes"] <= performance["serializedByteCap"]


def test_browser_matrix_mobile_layout_and_security_markers() -> None:
    matrix = load("browser/browser_matrix.json")
    assert set(matrix) == {"chromium", "firefox", "webkit"}
    for browser in matrix.values():
        assert browser["version"]
        assert browser["externalRequests"] == 0
        assert browser["consoleErrors"] == []
        assert browser["pageErrors"] == []
        assert browser["cases"]["ready"]["outcome"] == "PLAN_READY"
        assert browser["cases"]["blocked"]["outcome"] == "CAPABILITY_MISMATCH"
        assert browser["cases"]["blocked"]["runDisabled"] is True
        for case in browser["cases"].values():
            assert case["horizontalOverflow"] is False
            assert not any(case["inert"].values())
    mobile = matrix["chromium"]["mobile"]
    assert mobile["ready"]["outcome"] == "PLAN_READY"
    assert mobile["blocked"]["outcome"] == "CAPABILITY_MISMATCH"
    assert all(item["horizontalOverflow"] is False for item in mobile.values())
    screenshots = sorted((EVIDENCE / "screenshots").glob("*.png"))
    assert [item.name for item in screenshots] == [
        "desktop_blocked.png",
        "desktop_ready.png",
        "mobile_blocked.png",
        "mobile_ready.png",
    ]
    assert all(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") for path in screenshots)

    security = load("security/security_audit.json")
    assert security["realLlmCalls"] == 0
    assert security["externalNetworkRequests"] == 0
    assert security["fullRegistryLeakToLlm"] is False
    assert security["rejectedCandidateLeakToLlm"] is False
    assert security["nonReadyExecutableState"] is False
    assert security["markers"] == [
        "REAL_LLM_CALLS = 0",
        "NO_PHASE10L2_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
        "NO_CAPABILITY_PLANNER_ARBITRARY_CODE_EXECUTION",
        "NO_CAPABILITY_PLANNER_SHELL_OR_FILESYSTEM_AUTHORITY",
        "NO_CAPABILITY_PLANNER_ARTIFACT_JAVASCRIPT",
        "NO_FULL_REGISTRY_LEAK_TO_LLM",
        "NO_REJECTED_CANDIDATE_LEAK_TO_LLM",
        "NO_SECRET_PATTERN_HITS",
        "NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES",
    ]


def test_evidence_manifest_covers_every_retained_file_with_normalized_hashes() -> None:
    manifest = load("evidence_manifest.json")
    assert manifest["algorithm"] == "sha256-lf-normalized-text-v1"
    expected_files = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "evidence_manifest.json"
    }
    assert {entry["path"] for entry in manifest["files"]} == expected_files
    for entry in manifest["files"]:
        payload = (EVIDENCE / entry["path"]).read_bytes()
        canonical = payload if entry["path"].lower().endswith(".png") else payload.replace(b"\r\n", b"\n")
        assert len(canonical) == entry["bytes"]
        assert sha256(canonical).hexdigest() == entry["sha256"]
