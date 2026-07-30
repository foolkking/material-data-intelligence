from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


EVIDENCE = Path("docs/phase10l/evidence/phase10l3_bounded_multi_tool")


def _load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase10l3_runtime_api_failure_and_security_evidence() -> None:
    success = _load("two_step_success.json")
    partial = _load("producer_failure_partial.json")
    mismatch = _load("binding_mismatch.json")
    matrix = _load("compatibility_matrix.json")
    assert success["execution"]["outcome"] == "ALL_SUCCEEDED"
    assert set(success["topologicalOrder"]) == {item["stepId"] for item in success["plan"]["steps"]}
    assert len(success["bindingResolutions"]) == 2
    assert len(success["lineage"]) >= 3
    assert {item["producerToolId"] for item in success["lineage"]} >= {
        "phonon.band",
        "phonon.dos",
        "phonon.band_dos",
    }
    assert partial["execution"]["outcome"] == "PARTIAL_RESULTS"
    failed_binding = next(item for item in partial["execution"]["bindings"] if item["state"] == "FAILED_PRODUCER")
    binding = next(item for item in partial["plan"]["dependencyBindings"] if item["bindingId"] == failed_binding["bindingId"])
    states = {item["stepId"]: item["state"] for item in partial["execution"]["steps"]}
    assert states[binding["producerStepId"]] == "FAILED"
    assert states[binding["consumerStepId"]] == "BLOCKED_DEPENDENCY"
    independent_producer = next(
        item["producerStepId"]
        for item in partial["plan"]["dependencyBindings"]
        if item["consumerStepId"] == binding["consumerStepId"] and item["bindingId"] != binding["bindingId"]
    )
    assert states[independent_producer] == "SUCCEEDED"
    assert any(item["validationOutcome"] == "CHECKSUM_MISMATCH" for item in mismatch["bindingResolutions"])
    assert len([item for item in matrix["pairs"] if item["compatible"]]) == 2
    security = (EVIDENCE / "security_audit.md").read_text(encoding="utf-8")
    for marker in (
        "REAL_LLM_CALLS = 0",
        "NO_PHASE10L3_UNAPPROVED_EXTERNAL_NETWORK_REQUESTS",
        "NO_DEPENDENCY_ARBITRARY_CODE_EXECUTION",
        "NO_PROVIDER_ARTIFACT_PAYLOAD_EXPOSURE",
        "NO_PLAN_JOB_OR_ENQUEUE_FOR_NON_READY_OUTCOMES",
        "NO_SECRET_PATTERN_HITS",
    ):
        assert marker in security


def test_phase10l3_near_cap_and_legacy_evidence() -> None:
    near_cap = _load("cap_rejections.json")["nearCap"]
    legacy = _load("legacy_01_compatibility.json")
    assert near_cap["steps"] == 4
    assert near_cap["bindings"] == 6
    assert near_cap["depth"] == 4
    assert near_cap["bounded"] is True
    assert near_cap["serializedBytes"] <= near_cap["serializedByteCap"]
    assert legacy["schemaVersion"] == "0.1"
    assert legacy["dependencyBindingsPresent"] is False
    assert legacy["listOrderReinterpreted"] is False


def test_phase10l3_evidence_manifest_is_complete_and_reproducible() -> None:
    manifest = _load("evidence_manifest.json")
    assert manifest["algorithm"] == "sha256-lf-normalized-text-v1"
    expected = {
        path.relative_to(EVIDENCE).as_posix()
        for path in EVIDENCE.rglob("*")
        if path.is_file() and path.name != "evidence_manifest.json"
    }
    assert {item["path"] for item in manifest["files"]} == expected
    for item in manifest["files"]:
        payload = (EVIDENCE / item["path"]).read_bytes()
        canonical = payload if item["path"].lower().endswith(".png") else payload.replace(b"\r\n", b"\n")
        assert len(canonical) == item["bytes"]
        assert sha256(canonical).hexdigest() == item["sha256"]
