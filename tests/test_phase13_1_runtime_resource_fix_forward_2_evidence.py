from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.generate_phase13_1_product_entry_fix_forward import canonical_hash
from scripts.generate_phase13_1_runtime_resource_fix_forward_2 import main


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_1_runtime_resource_fix_forward_2"
REQUIRED = {
    "entry_gate.md", "phase13_2_attempt2_failure_snapshot.json", "release_findings_before.json",
    "scientific_resource_lifecycle_matrix.json", "execution_eligible_resource_resolution_matrix.json",
    "rr001_root_cause.json", "rr001_before_after.json", "rr002_root_cause.json", "rr002_before_after.json",
    "xrd_wavelength_authority_audit.json", "rr003_branch_decision.json", "rr003_before_after.json",
    "xrd_mismatch_negative_control.json", "canonical_entry_slice_regression.json",
    "canonical_execution_preflight_contract.json", "c2_aggregate.json", "c2_service_backed_contract.json", "negative_resource_resolution.json",
    "dependency_compatibility_matrix.json", "no_fallback_audit.json", "release_findings_after.json",
    "release_gap_reconciliation.json", "fact_model_hash_impact.json", "scope_baseline_hash_impact.json",
    "baseline_determinism.json", "phase11_science_nonchange.json", "phase12_baseline_nonchange.json",
    "phase13_2_attempt3_handoff.json", "security.md", "secret_scan.txt", "manifest.json",
    *(f"demo{index}_c2_preflight.json" for index in range(1, 8)),
}


def _load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_fix_forward_2_evidence_is_deterministic_and_complete() -> None:
    main()
    assert REQUIRED <= {path.name for path in EVIDENCE.iterdir() if path.is_file()}
    aggregate = _load("c2_aggregate.json")
    assert (aggregate["ready"], aggregate["blocked"]) == (7, 0)
    assert not any(aggregate["sideEffects"].values())
    assert _load("canonical_entry_slice_regression.json")["ready"] == 7
    assert _load("release_findings_after.json")["releaseCriticalIntegrationDefects"] == 0


def test_scope_and_fact_hash_impacts_are_explicit() -> None:
    fact = _load("fact_model_hash_impact.json")
    assert fact["impact"] == "NO"
    assert fact["old"] == fact["current"] == "e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06"
    scope = _load("initial_release_scope_baseline.json")
    without_hash = {key: value for key, value in scope.items() if key != "semanticHash"}
    assert canonical_hash(without_hash) == scope["semanticHash"]
    assert _load("scope_baseline_hash_impact.json")["impact"] == "YES"


def test_manifest_hashes_all_non_manifest_evidence() -> None:
    manifest = _load("manifest.json")
    expected = {path.name for path in EVIDENCE.iterdir() if path.is_file() and path.name != "manifest.json"}
    records = {record["path"]: record for record in manifest["records"]}
    assert set(records) == expected
    for name, record in records.items():
        payload = (EVIDENCE / name).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        assert len(payload) == record["size"]


def test_attempt_history_and_production_routing_are_not_rewritten() -> None:
    assert (ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e").is_dir()
    assert (ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e_rerun").is_dir()
    source = "\n".join(path.read_text(encoding="utf-8") for path in (
        ROOT / "apps/api/mdi_api/phase2_runtime.py",
        ROOT / "apps/api/mdi_api/routers/planner.py",
        ROOT / "services/workers/mdi_workers/source_resources.py",
    )).lower()
    for forbidden in ("demo5", "demo7", "phase13_demo", "latest_resource", "nearest_resource"):
        assert forbidden not in source
