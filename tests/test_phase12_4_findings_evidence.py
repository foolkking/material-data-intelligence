import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_4_findings_evidence_inspector_provenance"


def load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_phase12_4_evidence_is_complete_and_exact():
    subprocess.run([sys.executable, "scripts/generate_phase12_4_findings_evidence.py"], cwd=ROOT, check=True)
    manifest = load("manifest.json")
    assert manifest["phase"] == "12-4"
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == 0
    assert len(manifest["entries"]) >= 40
    acceptance = load("acceptance_registry.json")
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == acceptance["conflicting"] == acceptance["shorthand"] == 0


def test_trust_path_and_problem_closure_preserve_authority():
    trust = load("trust_path_matrix.json")
    membership = load("finding_evidence_membership.json")
    closure = load("phase12_4_problem_closure.json")
    payload = load("scientific_payload_nonchange.json")
    assert trust["exact"] is True and trust["frontendInference"] == 0
    assert membership["textSimilarity"] is membership["fuzzyMatching"] is False
    assert [item["problemId"] for item in closure["closed"]] == ["UX-004"]
    assert closure["open"] == [] and closure["newP0"] == closure["newP1"] == 0
    assert all(value == 0 for value in payload.values())


def test_recommendations_and_phase12_5_remain_non_executable():
    recommendation = load("recommendation_boundary.json")
    handoff = load("phase12_5_handoff.json")
    assert all(value is False for value in recommendation.values())
    assert handoff["status"] == "REVIEWER_GATE"
    assert handoff["executableTaskCreated"] is False
