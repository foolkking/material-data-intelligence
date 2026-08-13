from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_4_targeted_final_product_polish"


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_handoff_census_is_complete_and_bounded() -> None:
    handoff = load("phase13_4_handoff_snapshot.json")
    census = load("polish_census.json")["items"]
    selected = load("selected_polish_items.json")
    nonselected = load("nonselected_items.json")
    assert handoff["discovered"] == len(census) == 2
    assert selected["count"] == nonselected["count"] == 1
    assert selected["items"][0]["polishId"] == "P13-POLISH-002"
    assert nonselected["items"][0]["actionability"] == "ALREADY_RESOLVED"
    assert all(not row["releaseCritical"] for row in census)


def test_help_link_before_after_and_accessibility_are_exact() -> None:
    before = load("polish_p13_polish_002_before.json")
    after = load("polish_p13_polish_002_after.json")
    expected = (
        "https://github.com/foolkking/material-data-intelligence/"
        "blob/master/docs/phase13/release/README.md"
    )
    for viewport in ("desktop", "mobile"):
        assert before[viewport]["tagName"] == "BUTTON"
        assert before[viewport]["href"] is None
        assert before[viewport]["keyboardActivation"] == "NO_ACTION"
        assert after[viewport]["tagName"] == "A"
        assert after[viewport]["href"] == expected
        assert after[viewport]["target"] == "_blank"
        assert after[viewport]["rel"] == "noreferrer"
        assert after[viewport]["keyboardActivation"] == "PASS"
        assert after[viewport]["focusVisible"] is True
        assert after[viewport]["touchTarget"] == "PASS"
        assert after[viewport]["horizontalOverflow"] is False


def test_fact_scope_repro_and_canonical_contracts_are_unchanged() -> None:
    hashes = load("fact_scope_nonchange.json")
    assert hashes["factModelHash"] == hashes["factRun1"] == hashes["factRun2"] == (
        "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
    )
    assert hashes["scopeBaselineHash"] == hashes["scopeRun1"] == hashes["scopeRun2"] == (
        "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
    )
    assert hashes["phase12ProductBaselineHash"] == (
        "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
    )
    scope = load("scope_nonexpansion.json")
    assert scope["status"] == "PASS"
    assert scope["reproManifestHash"] == (
        "931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2"
    )
    assert all(row["unchanged"] for row in scope["comparisons"])
    for field in (
        "canonicalDemoContractChanges",
        "canonicalPromptChanges",
        "canonicalFixtureChanges",
        "canonicalUserEntryChanges",
        "capabilityCoverageChanges",
        "inputSupportPromotions",
        "inputSupportDemotions",
    ):
        assert scope[field] == 0


def test_performance_security_and_next_phase_are_bounded() -> None:
    performance = load("performance_regression.json")
    assert performance["status"] == "PASS"
    assert performance["newExternalAssets"] == performance["newDependencies"] == 0
    assert performance["newInitialArtifactRequests"] == 0
    assert performance["maxActiveHeavyViewers"] == 1
    assert "rel=noreferrer" in (OUT / "security.md").read_text(encoding="utf-8")
    secret_scan = (OUT / "secret_scan.txt").read_text(encoding="utf-8")
    private_scan = (OUT / "private_path_scan.txt").read_text(encoding="utf-8")
    assert "SECRET_PATTERN_HITS = 0" in secret_scan
    assert "PRIVATE_LOCAL_PATH_HITS = 0" in private_scan
    assert "SCAN_SCOPE = PHASE13_4_CHANGED_TEXT_FILES" in secret_scan
    assert "SCAN_SCOPE = PHASE13_4_CHANGED_TEXT_FILES" in private_scan
    handoff = load("phase13_5_handoff.json")
    assert handoff["status"] == "REVIEWER_GATE"
    assert handoff["executableTaskCreated"] is False
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if "Task: Phase 13-5 Final Regression + Release Acceptance" in tasks:
        assert tasks.count("---TASK---") == tasks.count("---END---") == 1
        assert "状态：处理中" in tasks
        assert "Task: Phase 13-6" not in tasks
    else:
        assert "Phase 13-4 Targeted Final Product Polish" in tasks


def test_evidence_manifest_matches_raw_bytes() -> None:
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["hashMismatches"] == 0
    for row in manifest["entries"]:
        payload = (OUT / row["path"]).read_bytes()
        assert len(payload) == row["bytes"]
        assert hashlib.sha256(payload).hexdigest() == row["sha256"]


def test_failed_candidate_provenance_is_retained() -> None:
    failed = load("failed_candidates.json")["candidates"]
    assert failed == [
        {
            "sha": "34f7cb7cea3db351edff0d3b39ff7fe39cd7e192",
            "ciRun": 31713598663,
            "failedJob": "Unit Tests (Python 3.11) / Phase 13-4 targeted product polish",
            "rootCause": "GitHub shallow checkout omitted the sealed entry SHA required by canonical nonchange git-show checks",
            "classification": "TEST_EVIDENCE_PORTABILITY_ONLY",
            "productBehaviorFailure": False,
            "correctedBy": "NEXT_IMPLEMENTATION_CANDIDATE",
        }
    ]
