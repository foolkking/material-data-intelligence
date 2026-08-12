from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_1_trajectory_phonon_fix_forward_5"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_r5_001_records_exact_version_mismatch_without_currentness_bypass() -> None:
    root_cause = load("r5_001_root_cause.json")
    diff = load("trajectory_source_identity_diff.json")
    stale = load("trajectory_stale_negative.json")

    assert root_cause["findingId"] == "P13-R5-001"
    assert root_cause["authorityWeakened"] is False
    assert diff["expectedDatasetVersion"] == "2"
    assert diff["workspaceDatasetVersion"] is None
    assert stale["status"] == "PASS"
    assert stale["typedOutcome"] == "STALE"


def test_r5_002_branch_c_preserves_phase11_input_support_authority() -> None:
    decision = load("phonon_branch_decision.json")
    support = load("phonon_input_support_matrix_snapshot.json")
    nonpromotion = load("no_input_support_promotion_audit.json")

    assert decision["selectedBranch"] == "C"
    assert decision["result"] == "BLOCKED_DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT"
    assert support["supportVerdict"] == "MAPPING_ONLY"
    assert support["matrixChanged"] is False
    assert nonpromotion == {
        "inputSupportPromotions": 0,
        "phase11MatrixChanged": False,
        "phononDirectUploadSupportPromotion": 0,
        "status": "PASS",
    }


def test_blocked_state_does_not_claim_demo_smokes_or_attempt6_handoff() -> None:
    fidelity = load("canonical_user_ingestion_fidelity_aggregate.json")
    demo4 = load("fresh_demo4_product_closure_smoke.json")
    demo5 = load("fresh_demo5_product_closure_smoke.json")
    handoff = load("phase13_2_attempt6_handoff.json")

    assert fidelity["passed"] == 6
    assert fidelity["userEntryContractMismatches"] == 1
    assert demo4["status"] == "NOT_EXECUTED_AFTER_BRANCH_C_STOP"
    assert demo5["status"] == "NOT_APPLICABLE_BRANCH_C"
    assert handoff["attempt6Authorized"] is False
    assert handoff["attempt6TaskCreated"] is False
