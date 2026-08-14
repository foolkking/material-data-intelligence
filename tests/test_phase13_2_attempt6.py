from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_2_attempt6_seven_real_user_e2e"


def read_json(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_attempt6_seven_fresh_demo_aggregate_is_complete() -> None:
    aggregate = read_json("seven_demo_aggregate.json")
    assert aggregate["demosStarted"] == 7
    assert aggregate["fullDemosExecuted"] == 7
    assert aggregate["passOrExplicitLimit"] == 7
    assert set(aggregate["statuses"].values()) == {"PASS"}
    assert aggregate["oldEvidenceReusedAsPass"] == 0
    assert aggregate["productionCodeChanges"] == 0


def test_attempt6_per_demo_real_product_records_are_complete() -> None:
    required = {
        "fixture.json", "user_prompt.txt", "user_actions.json", "intent.json",
        "eligibility.json", "analysis_plan.json", "plan_validation.json",
        "durable_source_manifest.json", "job.json", "redis_enqueue.json",
        "worker_runtime.json", "tool_calls.json", "artifact_manifest.json",
        "workspace.json", "workspace_panel_census.json", "artifact_reachability.json",
        "workspace_action_eligibility.json", "report_ui.json", "report.json",
        "recipe.json", "demo_result.json", "workspace_report.png",
    }
    for index in range(1, 8):
        demo = OUT / f"demo_{index}"
        assert required.issubset({path.name for path in demo.iterdir()})
        result = json.loads((demo / "demo_result.json").read_text(encoding="utf-8"))
        reachability = json.loads((demo / "artifact_reachability.json").read_text(encoding="utf-8"))
        census = json.loads((demo / "workspace_panel_census.json").read_text(encoding="utf-8"))
        recipe = json.loads((demo / "recipe.json").read_text(encoding="utf-8"))
        report_ui = json.loads((demo / "report_ui.json").read_text(encoding="utf-8"))
        assert result["status"] == "PASS" and result["fresh"] is True
        assert reachability["expected"] == reachability["passed"] and reachability["unreachable"] == 0
        assert census["workspacePanelCount"] <= census["maxPanels"] == 32
        assert census["panelTruncation"] == 0
        assert recipe["executionAuthority"] == "NONE" and recipe["executionCountsUnchanged"] is True
        assert report_ui["realUiFinalize"] is True
        assert report_ui["historicalReopen"]["historyCount"] >= 1


def test_attempt6_demo1_and_demo5_sealed_capabilities_and_entry() -> None:
    demo1 = json.loads((OUT / "demo_1/demo_result.json").read_text(encoding="utf-8"))
    assert demo1["selectedTools"] == ["dataset.composition_space", "dataset.materials_explorer"]
    demo5 = json.loads((OUT / "demo_5/demo_result.json").read_text(encoding="utf-8"))
    assert set(demo5["selectedTools"]) == {
        "phonon.band", "phonon.band_dos", "phonon.dos", "structure.brillouin_zone",
    }
    fixture = json.loads((OUT / "demo_5/fixture.json").read_text(encoding="utf-8"))
    assert {"typed_phonon_band_import", "typed_phonon_dos_import"}.issubset(set(fixture["entryModes"]))
    assert read_json("phase11_reference_reconciliation.json")["genericPhonon"] == "MAPPING_ONLY"


def test_attempt6_panel_and_artifact_invariants_remain_closed() -> None:
    cardinality = read_json("workspace_panel_cardinality_audit.json")
    assert cardinality["maxPanels"] == 32
    assert cardinality["panelCap32Case"] == "PASS"
    assert cardinality["panelCap33Case"] == "PANEL_CAP_EXCEEDED"
    assert cardinality["truncation"] == 0
    reachability = read_json("artifact_reachability_audit.json")
    assert reachability["expected"] == reachability["passed"]
    assert reachability["unreachable"] == 0


def test_attempt6_authorities_and_p13x2_are_exact() -> None:
    authorities = read_json("current_authorities.json")
    assert authorities["factModelHash"] == "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
    assert authorities["scopeBaselineHash"] == "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
    assert authorities["phase12ProductBaselineHash"] == "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
    assert authorities["registry"] == 62 and authorities["migration"] == "0007_phase10m1_workspace_domain"
    p13x2 = read_json("p13x2_acceptance.json")
    assert p13x2["acceptance"] == "8/8" and p13x2["passed"] == p13x2["expected"] == 8
    baseline = read_json("baseline_determinism.json")
    assert baseline["status"] == "PASS"
    assert baseline["linuxFact"] == baseline["windowsFact"] == authorities["factModelHash"]
    assert baseline["linuxScope"] == baseline["windowsScope"] == authorities["scopeBaselineHash"]


def test_attempt6_provider_is_bounded_and_not_science_authority() -> None:
    provider = read_json("provider_acceptance.json")
    assert provider["liveProvider"] == "deepseek"
    assert provider["callCount"] == 1 and provider["retries"] == 0
    assert provider["typedOutcome"] == "PASS"
    assert provider["scientificAuthority"] == "NONE"


def test_attempt6_manifest_raw_bytes_are_self_consistent() -> None:
    manifest = read_json("manifest.json")
    for entry in manifest["entries"]:
        payload = (OUT / entry["path"]).read_bytes()
        assert len(payload) == entry["bytes"]
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
    self_check = read_json("archive_manifest_self_check.json")
    assert self_check["status"] == "PASS" and self_check["rawByteManifestMismatch"] == 0


def test_attempt6_phase13_3_is_handoff_only_and_not_queued() -> None:
    handoff = read_json("phase13_3_handoff.json")
    assert handoff["status"] == "REVIEWER_GATE"
    assert handoff["executableTaskCreated"] is False
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert "Task: Phase 13-3 Documentation + Reproducibility Package" not in tasks
    if (
        "Task: Phase 13-4 Targeted Final Product Polish" in tasks
        or "Task: Phase 13-5 Final Regression + Release Acceptance" in tasks
        or "Phase 13-6 - Final Archive + Presentation Package" in tasks
    ):
        assert tasks.count("---TASK---") == 1
        assert "状态：处理中" in tasks
        assert "Task: Phase 13-6" not in tasks
    else:
        assert "---TASK---" not in tasks
