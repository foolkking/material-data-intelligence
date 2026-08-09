from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n4_trajectory_rdf_msd_diffusion"


def test_n4_canonical_acceptance_registry_is_exact_and_complete() -> None:
    text = (ROOT / "docs/phase10n/phase10n_acceptance_and_test_plan.md").read_text(encoding="utf-8")
    section = text.split("## Canonical Phase 10N-4 Acceptance Registry", 1)[1]
    definitions = re.findall(r"^\| (N4-A\d{2}) \| ([A-Z0-9_]+) \|", section, re.MULTILINE)
    assert [item[0] for item in definitions[:10]] == [f"N4-A{i:02d}" for i in range(1, 11)]
    assert len({item[0] for item in definitions[:10]}) == 10
    assert len(load_manifests().tools) == 60


def test_n4_evidence_inventory_and_manifest_integrity() -> None:
    required = {
        "baseline.txt", "entry_gate.md", "trajectory_authority_audit.md", "n4_r0_contract_closure.md",
        "n4_acceptance_registry.md", "n4_decision_traceability.md", "trajectory_identity_contract.json",
        "trajectory_time_cell_policy.md", "rdf_contract.md", "rdf_parameters.json", "rdf_reference_results.json",
        "unwrapping_contract.md", "unwrapping_reference_results.json", "msd_contract.md", "msd_parameters.json",
        "msd_reference_results.json", "diffusion_contract.md", "diffusion_parameters.json",
        "diffusion_reference_results.json", "diffusion_diagnostics.json", "ballistic_negative_case.json",
        "random_walk_positive_case.json", "variable_cell_case.json", "missing_time_case.json",
        "boundary_crossing_case.json", "profile_eligibility_cases.json", "planner_plan_cases.json",
        "runtime_cases.json", "workspace_selection.json", "interpretation.json", "report_recipe.json",
        "performance.json", "viewer_lifecycle.json", "accessibility.md", "security.md", "docs_link_check.txt",
        "secret_scan.txt", "manifest.json", "artifact_contract_samples/rdf.json",
        "artifact_contract_samples/msd.json", "artifact_contract_samples/diffusion.json",
        "service_backed/status.md", "browser/matrix.json", "screenshots/README.md",
    }
    assert all((EVIDENCE / path).is_file() for path in required)
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == "phase10n4.evidence_manifest.v1"
    assert manifest["realLlmCalls"] == 0 and manifest["newLlmCallSites"] == 0
    assert "DOCS_LINK_CHECK = PASS" in (EVIDENCE / "docs_link_check.txt").read_text(encoding="utf-8")
    assert "NO_SECRET_PATTERN_HITS = PASS" in (EVIDENCE / "secret_scan.txt").read_text(encoding="utf-8")
    assert "PENDING" not in "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in EVIDENCE.rglob("*")
        if path.is_file() and ".runtime" not in path.parts
    )
    for entry in manifest["entries"]:
        path = EVIDENCE / entry["path"]
        assert path.is_file()
        canonical = path.read_bytes().replace(b"\r\n", b"\n")
        assert sha256(canonical).hexdigest() == entry["sha256"]
        assert len(canonical) == entry["bytes"]


def test_n4_scientific_negative_and_positive_controls_are_honest() -> None:
    ballistic = json.loads((EVIDENCE / "ballistic_negative_case.json").read_text(encoding="utf-8"))
    random_walk = json.loads((EVIDENCE / "random_walk_positive_case.json").read_text(encoding="utf-8"))
    runtime = json.loads((EVIDENCE / "runtime_cases.json").read_text(encoding="utf-8"))
    assert ballistic["status"] == "BALLISTIC_LIKE_WINDOW"
    assert ballistic["BALLISTIC_FIXTURE_DIFFUSION_ACCEPTED"] is False
    assert random_walk["diagnostic"] == "DIFFUSIVE_WINDOW_ACCEPTED"
    assert abs(random_walk["actualD"] - 0.1) <= 1e-9
    assert runtime["noNetwork"] is True and runtime["noFallback"] is True


def test_n4_queue_state_preserves_the_n5_reviewer_gate() -> None:
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert tasks.count("---TASK---") == tasks.count("---END---")
    if "Task: Phase 10N-4" in tasks:
        assert tasks.count("---TASK---") == 1
    else:
        assert tasks.count("---TASK---") == 0
        assert "Phase 10N-4:\nPASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT" in tasks
        assert "Phase 10N-5:\nREVIEWER_GATE / AWAITING REVIEWER PROMPT" in tasks
    assert "Task: Phase 10N-5" not in tasks
