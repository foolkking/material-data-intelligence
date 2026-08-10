import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_3_scientific_workspace_viewers"


def test_phase12_3_evidence_is_complete_and_honest():
    subprocess.run([sys.executable, "scripts/generate_phase12_3_workspace_viewer_evidence.py"], cwd=ROOT, check=True)
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["phase"] == "12-3"
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == 0
    assert len(manifest["entries"]) >= 35
    closure = json.loads((EVIDENCE / "phase12_3_problem_closure.json").read_text(encoding="utf-8"))
    assert {item["problemId"] for item in closure["closed"]} == {"UX-002", "UX-003"}
    assert closure["newP0"] == closure["newP1"] == 0


def test_phase12_3_authority_boundaries_are_sealed():
    authority = json.loads((EVIDENCE / "workspace_authority_nonchange.json").read_text(encoding="utf-8"))
    payload = json.loads((EVIDENCE / "scientific_payload_nonchange.json").read_text(encoding="utf-8"))
    assert authority["oneWorkspacePerJob"] is True
    assert authority["localStorageAuthority"] == "NONE"
    assert payload["frontendRecomputation"] == payload["algorithm"] == payload["units"] == 0
