from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_1_workspace_projection_fix_forward_6"


def read_json(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_ff6_entry_and_history_evidence_are_present() -> None:
    required = {
        "entry_gate.md",
        "attempt5_history_ref.json",
        "fix_forward5_blocked_ref.json",
        "release_scope_exception1_failure_ref.json",
        "blocked_candidate_authority.json",
        "current_authorities.json",
        "phase13_2_attempt6_handoff.json",
    }
    assert required <= {path.name for path in EVIDENCE.iterdir()}
    assert read_json("phase13_2_attempt6_handoff.json")["attempt6Queued"] is False
    assert read_json("phase13_2_attempt6_handoff.json")["attempt6Executed"] == 0


def test_ff6_projection_closes_cardinality_without_dropping_artifacts() -> None:
    aggregate = read_json("workspace_panel_projection_aggregate.json")
    reachability = read_json("demo5_artifact_reachability_aggregate.json")
    assert aggregate["TOTAL_PERSISTED_ARTIFACTS"] == 27
    assert aggregate["TOTAL_PRE_FIX_PANEL_CANDIDATES"] == 33
    assert aggregate["POST_FIX_PANEL_COUNT"] == 7
    assert aggregate["invariant"] == "ARTIFACT_COUNT != WORKSPACE_PANEL_COUNT"
    assert reachability == {
        "DROPPED_ARTIFACTS": 0,
        "UNREACHABLE_ARTIFACTS": 0,
        "WORKSPACE_COPIED_ARTIFACT_PAYLOADS": 0,
        "expected": 27,
        "pass": 27,
    }
    assert read_json("panel_cap_32_positive.json")["result"] == "PASS"
    assert read_json("panel_cap_33_negative.json")["result"] == "PANEL_CAP_EXCEEDED"


def test_ff6_support_matrix_is_narrow_and_semantically_frozen() -> None:
    matrix = read_json("input_support_matrix.current.json")
    families = {row["inputFamily"]: row for row in matrix["inputs"]}
    assert matrix["rowCount"] == 16
    assert families["Phonon YAML/JSON"]["supportVerdict"] == "MAPPING_ONLY"
    assert families["Typed PhononBand import"]["supportVerdict"] == "SUPPORTED_WITH_LIMITS"
    assert families["Typed PhononDos import"]["supportVerdict"] == "SUPPORTED_WITH_LIMITS"
    assert read_json("input_support_before_after.json")["authorizedRowsChanged"] == 2
    assert read_json("input_support_before_after.json")["otherRowsChanged"] == 0
    assert read_json("generic_phonon_mapping_only_regression.json")["autoPromotion"] == 0


def test_ff6_closures_and_hashes_are_deterministic() -> None:
    assert read_json("r5_001_final_closure.json")["status"] == "CLOSED"
    assert read_json("r5_002_final_closure.json")["status"] == "CLOSED"
    assert read_json("rse1_closure.json")["status"] == "CLOSED"
    fact = read_json("fact_model_before_after.json")
    scope = read_json("scope_baseline_before_after.json")
    baseline = json.loads((EVIDENCE / "baseline_determinism.json").read_text(encoding="utf-8"))
    assert fact["impact"] == "YES" and fact["current"] == fact["run1"] == fact["run2"]
    assert scope["impact"] == "YES" and scope["current"] == scope["run1"] == scope["run2"]
    assert baseline["status"] == "PASS"
    assert baseline["factRun1"] == fact["current"] == baseline["linuxFact"] == baseline["windowsFact"]
    assert baseline["scopeRun1"] == scope["current"] == baseline["linuxScope"] == baseline["windowsScope"]


def test_ff6_no_injection_and_no_platform_expansion() -> None:
    authorities = read_json("current_authorities.json")
    assert authorities == {
        "analysisIntent": "1.0",
        "analysisPlan": ["0.1", "0.2"],
        "dataProfile": "2.4",
        "eligibility": "1.0",
        "factModelHash": authorities["factModelHash"],
        "maxPanels": 32,
        "migration": "0007_phase10m1_workspace_domain",
        "phase12BaselineHash": "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4",
        "registry": 62,
        "scopeBaselineHash": authorities["scopeBaselineHash"],
    }
    security = (EVIDENCE / "security.md").read_text(encoding="utf-8")
    assert "NO_PANEL_CAP_BYPASS = PASS" in security
    assert "NO_GENERIC_PHONON_AUTO_PROMOTION = PASS" in security
    assert "NO_RECIPE_EXECUTION = PASS" in security
    assert "REAL_LLM_CALLS = 0" in security
