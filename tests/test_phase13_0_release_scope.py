from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_0_release_scope_seal"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def stable_fixture_hash(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() in {".cif", ".csv", ".json", ".md", ".txt", ".vasp", ".yaml", ".yml", ".xyz"}:
        content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(content).hexdigest()


def test_phase13_0_evidence_is_deterministic_and_complete() -> None:
    before = (OUT / "initial_release_scope_baseline_hash.txt").read_text(encoding="utf-8").strip()
    subprocess.run([sys.executable, "scripts/generate_phase13_0_release_scope.py"], cwd=ROOT, check=True)
    after = (OUT / "initial_release_scope_baseline_hash.txt").read_text(encoding="utf-8").strip()
    assert before == after == load("initial_release_scope_baseline.json")["semanticHash"]
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    assert len(manifest["entries"]) >= 35
    for entry in manifest["entries"]:
        path = OUT / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_live_registry_capability_and_input_reconciliation_is_exact() -> None:
    registry = load_manifests()
    reconciliation = load("registry_reconciliation.json")
    assert len(registry.tools) == 62
    assert reconciliation["liveRegistryCount"] == reconciliation["documentedRegistryCount"] == reconciliation["releaseMatrixToolCount"] == 62
    assert reconciliation["uniqueVersionedToolCount"] == 62
    capabilities = load("capability_matrix.json")
    assigned = [tool for row in capabilities["capabilities"] for tool in row["currentToolIds"]]
    assert len(assigned) == len(set(assigned)) == 62
    assert capabilities["duplicateToolAssignments"] == capabilities["unassignedTools"] == 0
    inputs = load("input_support_matrix.json")
    assert inputs["rowCount"] == 14 and inputs["supportPromotions"] == 0
    assert {row["supportVerdict"] for row in inputs["inputs"]} <= {"DIRECT_SUPPORTED", "SUPPORTED_WITH_LIMITS", "MAPPING_ONLY", "UNSUPPORTED"}


def test_scientific_authority_and_release_claims_remain_honest() -> None:
    science = load("scientific_validation_matrix.json")
    assert science["goldenRecords"] == 12
    assert science["passInvariant"] == 8 and science["notApplicable"] == 4 and science["failures"] == 0
    assert science["linuxInvariantReplay"] == science["windowsInvariantReplay"] == "PASS"
    assert science["numericCrossPlatformValidation"] == "NOT_APPLICABLE"
    assert science["v4"] == 0
    assert len(load("forbidden_release_claims.json")["claims"]) >= 10
    assert load("phase12_baseline_verification.json")["determinism"] == "PASS"
    assert load("phase12_baseline_verification.json")["mutations"] == 0


def test_seven_demo_real_user_and_no_injection_contracts_are_sealed_not_executed() -> None:
    registry = load("seven_demo_registry.json")
    assert registry["expected"] == registry["registered"] == 7
    assert registry["extra"] == registry["missing"] == 0
    assert len({demo["demoId"] for demo in registry["demos"]}) == 7
    assert all(demo["mode"] == "REAL_USER_ENTRY_E2E" for demo in registry["demos"])
    assert all(demo["executed"] is False and demo["passClaim"] is False for demo in registry["demos"])
    assert all(len(demo["acceptanceDimensions"]) == 17 for demo in registry["demos"])
    fixtures = load("demo_fixture_registry.json")
    assert fixtures["missing"] == fixtures["checksumMismatch"] == fixtures["externalDownloads"] == 0
    for fixture in fixtures["records"]:
        path = ROOT / fixture["path"]
        assert path.is_file()
        assert stable_fixture_hash(path) == fixture["checksum"]
    injection = load("demo_no_injection_policy.json")
    for key in ("analysisPlan", "job", "toolCall", "artifact", "workspace", "finding", "evidence", "report", "recipe"):
        assert injection[key] == 0
    runtime = load("demo_runtime_policy.json")
    assert all(runtime[key] is True for key in ("realPersistenceRequired", "realQueueWorkerRuntimeRequired", "registeredAdapterExecutionRequired", "workspaceFromRealJobRequired", "reportFromRealPersistedFactsRequired"))


def test_gap_acceptance_fact_model_and_future_boundaries_are_exact() -> None:
    gaps = load("release_gap_registry.json")
    assert gaps["releaseBlockers"] == gaps["releaseCriticalIntegrationGaps"] == gaps["unclassified"] == 0
    assert gaps["nonblockingLimitations"] == 2 and gaps["evidenceGaps"] == 1
    acceptance = load("phase13_acceptance_registry.json")
    assert acceptance["expected"] == len(acceptance["records"]) == 56
    assert len({item["acceptanceId"] for item in acceptance["records"]}) == 56
    assert [item["acceptanceId"] for item in acceptance["records"] if item["phase"] == "13-0"] == [f"P13X0-A{i:02d}" for i in range(1, 9)]
    assert all(item["status"] == "PASS" for item in acceptance["records"] if item["phase"] == "13-0")
    assert load("future_scope_registry.json")["status"] == "DOCUMENTED_NOT_QUEUED"
    assert "arbitrary Python/Shell/notebook execution" in load("not_planned_registry.json")["items"]
    fact = load("initial_release_fact_model.json")
    assert fact["RegistryCount"] == 62 and fact["DataProfileVersion"] == "2.4"
    assert fact["initialReleaseComplete"] is False


def test_phase13_0_docs_ci_and_queue_contract_resolve() -> None:
    required = [
        "phase13_0_final_fact_alignment_release_scope_seal.md",
        "phase13_initial_release_scope.md",
        "phase13_release_capability_matrix.md",
        "phase13_release_claims_and_limitations.md",
        "phase13_future_and_not_planned_scope.md",
        "phase13_release_critical_gap_registry.md",
        "phase13_seven_canonical_e2e_demo_contract.md",
        "phase13_real_user_simulation_contract.md",
        "phase13_acceptance_registry.md",
        "phase13_evidence_and_lifecycle_contract.md",
        "phase13_1_integration_gap_handoff.md",
        "phase13_initial_release_fact_model.md",
        "phase13_0_completion.md",
    ]
    assert all((ROOT / "docs/phase13" / name).is_file() for name in required)
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "generate_phase13_0_release_scope.py" in workflow
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if tasks.strip():
        blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        assert len(blocks) == 1
        assert "Phase 13-0 Reviewer Prompt" in blocks[0] or "Phase 13-0 Reviewer Correction Prompt" in blocks[0]
        assert re.search(r"状态：(处理中|已完成)", blocks[0])
        assert "Phase 13-1 Reviewer Prompt" not in tasks
