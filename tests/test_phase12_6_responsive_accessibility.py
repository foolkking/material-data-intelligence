from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_6_responsive_mobile_accessibility"


def load(name: str) -> dict:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase12_6_evidence_is_deterministic_and_complete() -> None:
    subprocess.run([sys.executable, "scripts/generate_phase12_6_responsive_accessibility_evidence.py"], cwd=ROOT, check=True)
    manifest = load("manifest.json")
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == 0
    assert manifest["entries"]
    for entry in manifest["entries"]:
        path = EVIDENCE / entry["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_acceptance_and_problem_ownership_are_exact() -> None:
    acceptance = load("acceptance_registry.json")
    assert list(acceptance["entries"]) == [f"P12X6-A0{i}" for i in range(1, 9)]
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert all(acceptance[key] == 0 for key in ("missing", "extra", "duplicate", "conflicting", "shorthand"))
    closure = load("phase12_6_problem_closure.json")
    assert [item["problemId"] for item in closure["closed"]] == ["UX-006", "UX-009"]
    assert closure["open"] == [] and closure["newP0"] == closure["newP1"] == 0
    assert load("deferred_phase12_7_matrix.json")["12-7"] == ["UX-010"]


def test_accessibility_closure_is_honest_and_authority_safe() -> None:
    assert load("surface_accessibility_inventory.json")["unclassified"] == 0
    assert load("mobile_workflow_matrix.json")["unaudited"] == 0
    assert load("keyboard_navigation_matrix.json")["unaudited"] == 0
    assert load("touch_target_matrix.json")["mobileFailures"] == 0
    assert load("contrast_matrix.json")["formalCertification"] is False
    assert load("screen_reader_matrix.json")["realAssistiveTechnologyCertification"] is False
    assert load("scientific_payload_nonchange.json")["frontendRecomputation"] == 0
    contract = load("contract_nonchange.json")
    assert contract["registry"] == 62 and contract["dataProfile"] == "2.4"
    assert contract["migration"] == "0007_phase10m1_workspace_domain"


def test_production_accessibility_primitives_and_terminology_are_present() -> None:
    planner = (ROOT / "apps/web/app/components/PlannerWorkbench.tsx").read_text(encoding="utf-8")
    workspace = (ROOT / "apps/web/app/components/workspace/ScientificWorkspaceShell.tsx").read_text(encoding="utf-8")
    css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")
    en = (ROOT / "apps/web/app/lib/messages/en-US.ts").read_text(encoding="utf-8")
    zh = (ROOT / "apps/web/app/lib/messages/zh-CN.ts").read_text(encoding="utf-8")
    assert 'href="#planner-primary-content"' in planner and 'role="separator"' in planner
    assert 'href="#workspace-primary-content"' in workspace and "aria-expanded={inspectorOpen}" in workspace
    for marker in (".skip-link", "@media (forced-colors: active)", "@media (prefers-reduced-motion: reduce)", "--ds-control-touch: 44px"):
        assert marker in css
    for key in ("termDataset", "termArtifact", "termEvidence", "termLimitation", "termUnsupported", "termPartial"):
        assert key in en and key in zh


def test_queue_has_only_the_active_phase12_6_task() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    if not tasks.strip():
        return
    blocks = re.findall(r"---TASK---.*?---END---", tasks, flags=re.DOTALL)
    assert len(blocks) == 1
    if "Phase 13-0 Reviewer Prompt" in blocks[0] or "Phase 13-0 Reviewer Correction Prompt" in blocks[0]:
        assert re.search(r"状态：(处理中|已完成)", blocks[0])
        return
    if "Phase 12-7 Reviewer Prompt" in blocks[0]:
        assert re.search(r"状态：(处理中|已完成)", blocks[0])
        return
    assert "Phase 12-6 Reviewer Prompt" in blocks[0]
    assert re.search(r"状态：(处理中|已完成)", blocks[0])
    assert "Phase 12-7 Reviewer Prompt" not in tasks
