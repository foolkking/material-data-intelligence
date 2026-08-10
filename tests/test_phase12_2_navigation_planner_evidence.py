import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_2_navigation_planner"


def test_phase12_2_evidence_generator_is_deterministic_and_complete():
    subprocess.run(
        ["uv", "run", "python", "scripts/generate_phase12_2_navigation_planner_evidence.py"],
        cwd=ROOT,
        check=True,
    )
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == "12-2"
    assert manifest["missing"] == 0
    assert manifest["hashMismatch"] == 0
    assert len(manifest["entries"]) >= 14


def test_phase12_2_navigation_uses_existing_authority_boundaries():
    navigation = json.loads((EVIDENCE / "navigation_matrix.json").read_text(encoding="utf-8"))
    assert navigation["globalIA"] == ["Home", "Data", "Analyses", "Workspaces", "Reports", "Settings"]
    assert navigation["newBackendAuthority"] == 0
    assert navigation["newScientificAuthority"] == 0
    assert {item["id"] for item in navigation["items"]} == {
        "home", "data", "analyses", "workspaces", "reports", "settings"
    }


def test_phase12_2_closes_only_its_owned_ux_problems():
    closure = json.loads((EVIDENCE / "problem_closure.json").read_text(encoding="utf-8"))
    assert {item["problemId"] for item in closure["closed"]} == {"UX-001", "UX-008"}
    assert all(item["status"] == "FIXED_WITH_EVIDENCE" for item in closure["closed"])
    assert all(item["owner"] in {"12-3", "12-4", "12-5", "12-6", "12-7"} for item in closure["deferred"])
