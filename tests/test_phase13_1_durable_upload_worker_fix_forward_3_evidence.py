from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_phase13_1_durable_upload_worker_fix_forward_3 import OUT


REQUIRED = {
    "entry_gate.md", "attempt3_failure_snapshot.json", "p13_r3_001_reproduction.json",
    "upload_to_worker_durability_matrix.json", "durable_source_authority_audit.json",
    "runtime_input_resolution_authority_map.json", "schema_decision.json", "storage_authority_decision.json",
    "before_durable_state.json", "after_durable_state.json", "normalized_resource_manifest.json",
    "source_identity_chain.json", "process_boundary_proof.json", "d0_contract.json", "d0_positive.json",
    "d0_missing_resource_negative.json", "d0_hash_mismatch_negative.json", "d0_cross_project_negative.json",
    "d0_stale_negative.json", "d0_queue_payload_audit.json", "level_c_regression.json",
    "level_c2_regression.json", "no_manual_preload_audit.json", "no_runtime_reparse_audit.json",
    "release_finding_closure.json", "release_gap_reconciliation.json", "fact_model_hash_impact.json",
    "scope_baseline_hash_impact.json", "baseline_determinism.json", "science_nonchange.json",
    "phase12_nonchange.json", "phase13_2_attempt4_handoff.json", "security.md", "secret_scan.txt", "manifest.json",
    "verification_summary.json",
}


def _load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def _assert_readable_inventory() -> None:
    manifest = _load("manifest.json")
    expected = {record["path"] for record in manifest["records"]}
    actual = {path.name for path in OUT.iterdir() if path.is_file() and path.name != "manifest.json"}
    assert expected == actual
    assert manifest["missing"] == manifest["unclassified"] == 0
    for name in sorted(actual):
        content = (OUT / name).read_text(encoding="utf-8")
        assert content.strip()
        if name.endswith(".json"):
            json.loads(content)


def test_fix_forward_3_evidence_is_complete_and_deterministic() -> None:
    assert REQUIRED <= {path.name for path in OUT.iterdir() if path.is_file()}
    _assert_readable_inventory()
    assert _load("level_c_regression.json")["ready"] == 7
    assert _load("level_c2_regression.json")["ready"] == 7
    assert _load("d0_positive.json")["status"] == "PASS"
    assert _load("schema_decision.json")["canExistingDurableSchemaRepresentRequiredSourceReferences"] == "YES"


def test_manifest_is_complete_and_readable() -> None:
    _assert_readable_inventory()
    assert _load("level_c_regression.json")["ready"] == 7


def test_production_has_no_fixture_or_runtime_fallback_authority() -> None:
    root = Path(__file__).resolve().parents[1]
    source = "\n".join((root / path).read_text(encoding="utf-8").lower() for path in (
        "apps/api/mdi_api/durable_uploads.py",
        "apps/api/mdi_api/phase2_runtime.py",
        "apps/api/mdi_api/routers/planner.py",
        "services/workers/mdi_workers/object_store.py",
    ))
    for forbidden in ("attempt3", "attempt4", "demo_1", "formulas.csv", "latest_resource", "reparse"):
        assert forbidden not in source
