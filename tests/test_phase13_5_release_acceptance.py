from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_5_final_regression_release_acceptance"


def load(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_phase13_5_seven_fresh_real_user_records_are_complete() -> None:
    aggregate = load("seven_demo_aggregate.json")
    assert aggregate == {
        **aggregate,
        "status": "PASS",
        "started": 7,
        "completed": 7,
        "passOrExplicitLimit": 7,
        "toolCalls": 18,
        "artifacts": 85,
        "workspaces": 7,
        "reports": 7,
        "recipes": 7,
        "oldAttempt6EvidenceUsedAsPass": 0,
    }
    required = {
        "fresh_user_path", "durable_identity", "plan_runtime", "artifact_manifest",
        "workspace", "artifact_reachability", "report_ui", "report", "recipe", "result",
    }
    for index in range(1, 8):
        assert {path.stem.removeprefix(f"demo{index}_") for path in OUT.glob(f"demo{index}_*.json")} >= required
        result = load(f"demo{index}_result.json")
        reachability = load(f"demo{index}_artifact_reachability.json")
        workspace = load(f"demo{index}_workspace.json")
        identity = load(f"demo{index}_durable_identity.json")
        report = load(f"demo{index}_report_ui.json")
        recipe = load(f"demo{index}_recipe.json")
        assert result["status"] == "PASS" and result["fresh"] is True
        assert reachability["expected"] == reachability["passed"] and reachability["unreachable"] == 0
        assert workspace["panelCount"] <= workspace["maxPanels"] == 32
        assert identity["identityExact"] is True
        assert report["realUiFinalize"] is True
        assert recipe["executionAuthority"] == "NONE"


def test_phase13_5_authorities_support_and_panel_contract_are_frozen() -> None:
    identity = load("release_candidate_identity.json")
    assert identity["entryGitSha"] == "ff3f923330acede6c5442cc1226d3bce10b7c299"
    assert identity["factModelHash"] == "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
    assert identity["scopeBaselineHash"] == "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
    assert identity["phase12ProductBaselineHash"] == "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
    assert identity["registry"] == 62 and identity["dataProfile"] == "2.4"
    assert identity["analysisIntent"] == identity["eligibilityResolution"] == "1.0"
    assert identity["analysisPlan"] == ["0.1", "0.2"]
    assert identity["migration"] == "0007_phase10m1_workspace_domain"
    assert identity["maxPanels"] == 32 and identity["maxLayoutRevisions"] == 128
    assert identity["inputSupport"] == {
        "typedPhononBand": "SUPPORTED_WITH_LIMITS",
        "typedPhononDos": "SUPPORTED_WITH_LIMITS",
        "genericPhononYamlJson": "MAPPING_ONLY",
    }
    panel = load("workspace_cardinality_audit.json")
    assert panel["panelCap32Case"] == "PASS"
    assert panel["panelCap33Case"] == "PANEL_CAP_EXCEEDED"
    assert panel["panelTruncation"] == 0


def test_phase13_5_browser_help_and_gallery_matrix_is_real_and_clean() -> None:
    browser = load("browser_matrix.json")
    assert browser["chromiumSevenDemos"] == "PASS"
    for engine, row in browser["representativeGalleryRuns"].items():
        assert engine in {"chromium", "firefox", "webkit", "mobile_390x844"}
        assert row["status"] == "PASS" and row["cards"] == row["expected"] == 27
        assert row["horizontalOverflow"] == 0
        assert all(not row[key] for key in ("pageErrors", "consoleErrors", "failedRequests", "externalRequests"))
    help_rows = [row["desktop"] for row in browser["helpLinkRuns"]["browsers"].values()]
    help_rows.append(browser["helpLinkRuns"]["mobile"])
    assert len(help_rows) == 4
    for row in help_rows:
        assert row["keyboardActivation"] == "PASS" and row["focusVisible"] is True
        assert row["touchTarget"] == "PASS" and row["horizontalOverflow"] is False
        assert all(not row[key] for key in ("pageErrors", "consoleErrors", "unexpectedFailedRequests", "unapprovedExternalRequests"))


def test_phase13_5_decision_manifest_and_phase13_6_handoff_are_bounded() -> None:
    decision = load("release_acceptance_decision.json")
    assert decision["overall"] == "PASS" and decision["releaseCandidateAccepted"] is True
    assert decision["readyForPhase13_6"] is True
    assert all(item["decision"].startswith("PASS") for item in decision["dimensions"])
    handoff = load("phase13_6_handoff.json")
    assert handoff["status"] == "REVIEWER_GATE" and handoff["executableTaskCreated"] is False
    assert handoff["initialReleaseComplete"] is False
    manifest = load("manifest.json")
    assert manifest["missingFiles"] == manifest["hashMismatches"] == 0
    for entry in manifest["entries"]:
        payload = (OUT / entry["path"]).read_bytes()
        assert len(payload) == entry["bytes"]
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert "Task: Phase 13-5 Final Regression + Release Acceptance" in tasks
    assert "Task: Phase 13-6" not in tasks
