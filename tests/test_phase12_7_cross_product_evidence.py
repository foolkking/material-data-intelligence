from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_7_cross_product_ux_validation"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_phase12_7_evidence_is_deterministic_and_complete() -> None:
    subprocess.run([sys.executable, "scripts/generate_phase12_7_cross_product_evidence.py"], cwd=ROOT, check=True)
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == 0
    assert len(manifest["entries"]) >= 55
    for entry in manifest["entries"]:
        path = OUT / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
    baseline = load("phase12_product_experience_baseline.json")
    assert (OUT / "phase12_product_experience_baseline_hash.txt").read_text().strip() == baseline["semanticHash"]


def test_acceptance_decisions_journeys_and_problems_close_exactly() -> None:
    acceptance = load("phase12_acceptance_reconciliation.json")
    assert acceptance["expected"] == acceptance["passed"] == 68
    assert acceptance["failed"] == acceptance["blocked"] == acceptance["missing"] == 0
    assert list(acceptance["phase12_7"]) == [f"P12X7-A0{i}" for i in range(1, 9)]
    decisions = load("phase12_decision_reconciliation.json")
    assert decisions["expected"] == decisions["resolved"] == 20 and decisions["violated"] == 0
    journeys = load("canonical_journey_results.json")
    assert journeys["expected"] == journeys["replayed"] == journeys["passed"] == 11
    assert journeys["failed"] == journeys["blocked"] == journeys["unaudited"] == 0
    closure = load("phase12_ux_problem_closure.json")
    assert [item["problemId"] for item in closure["problems"]] == [f"UX-{i:03d}" for i in range(1, 11)]
    assert closure["ownedOpen"] == closure["unassigned"] == closure["newP0"] == closure["newP1"] == 0


def test_phase12_7_preserves_authority_and_accessibility_honesty() -> None:
    science = load("scientific_payload_nonchange.json")
    assert all(value == 0 for value in science.values())
    authority = load("phase11_authority_nonchange.json")
    assert authority["registry"] == 62 and authority["dataProfile"] == "2.4"
    assert authority["migration"] == "0007_phase10m1_workspace_domain" and authority["mutations"] == 0
    assert load("report_recipe_contract_nonchange.json")["recipeExecutionAuthority"] == "NONE"
    limitations = load("accepted_ux_limitations.json")
    assert limitations["formalAccessibilityCertification"] is False
    assert limitations["humanUsabilityStudy"] is False


def test_phase12_7_docs_and_ci_wiring_resolve() -> None:
    required_docs = [
        "phase12_7_cross_product_ux_validation.md",
        "phase12_7_canonical_journey_validation.md",
        "phase12_7_cross_product_consistency.md",
        "phase12_7_final_ux_problem_closure.md",
        "phase12_7_design_evidence_closure.md",
        "phase12_final_product_experience_baseline.md",
        "phase12_final_known_limitations.md",
        "phase13_final_product_closure_handoff.md",
        "phase12_completion.md",
    ]
    assert all((ROOT / "docs/phase12" / name).is_file() for name in required_docs)
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "phase12-7-cross-product-browser-evidence.mjs" in workflow
    assert "generate_phase12_7_cross_product_evidence.py" in workflow


def test_queue_has_only_active_phase12_7_or_is_archived() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if (
        "Phase 13-1 Reviewer Prompt" in tasks
        or "Phase 13-2 Reviewer Prompt" in tasks
        or "Phase 13-4 Targeted Final Product Polish" in tasks
        or "Phase 13-5 Final Regression + Release Acceptance" in tasks
    ):
        blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
        active = [block for block in blocks if "状态：处理中" in block]
        assert len(blocks) == tasks.count("---TASK---") == tasks.count("---END---")
        assert len(active) <= 1 and (not active or active[0] == blocks[0])
        assert "Task: Phase 13-6" not in tasks
        return
    if not tasks.strip():
        return
    blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
    assert len(blocks) == 1
    if "Phase 13-0 Reviewer Prompt" in blocks[0] or "Phase 13-0 Reviewer Correction Prompt" in blocks[0]:
        assert re.search(r"状态：(处理中|已完成)", blocks[0])
        return
    assert "Phase 12-7 Reviewer Prompt" in blocks[0]
    assert re.search(r"状态：(处理中|已完成)", blocks[0])
    assert "---TASK---\n状态：" not in blocks[0].split("Phase 12-7 Reviewer Prompt", 1)[1]
