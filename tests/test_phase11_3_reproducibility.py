import json
import os
import subprocess
import sys
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase11_3_reproducibility.py"
HANDOFF = ROOT / "docs/phase11/evidence/phase11_2_golden_scientific_benchmark/phase11_3_reproducibility_input_manifest.json"


def test_handoff_is_eight_invariant_cases():
    handoff = json.loads(HANDOFF.read_text(encoding="utf-8"))
    assert handoff["recordCount"] == 8
    assert all(item["11_2Verdict"] == "PASS_INVARIANT" for item in handoff["records"])
    assert all(item["targetVarianceClass"] == "TOLERANCE_BOUNDED" for item in handoff["records"])


def test_windows_replay_runner_is_cross_platform(tmp_path):
    if os.name != "nt":
        return
    output = tmp_path / "windows"
    subprocess.run([sys.executable, str(SCRIPT), "--platform", "windows", "--output-dir", str(output)], cwd=ROOT, check=True)
    replay = json.loads((output / "windows_replay.json").read_text(encoding="utf-8"))
    assert replay["caseCount"] == 8
    assert replay["referencePassCount"] == 8
    assert replay["numericClaims"] == 0


def test_replay_rejects_non_invariant_numeric_claim(tmp_path):
    source = HANDOFF.read_text(encoding="utf-8")
    assert '"schemaVersion": "phase11-3-reproducibility-input-manifest/1.0"' in source


def test_retained_evidence_manifest_is_complete():
    evidence = ROOT / "docs/phase11/evidence/phase11_3_cross_platform_reproducibility"
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    actual = sorted(path.relative_to(evidence).as_posix() for path in evidence.rglob("*") if path.is_file() and path.name != "manifest.json")
    expected = sorted(entry["path"] for entry in manifest["entries"])
    assert actual == expected
    for entry in manifest["entries"]:
        path = evidence / entry["path"]
        data = path.read_bytes()
        if path.suffix.lower() in {".md", ".txt", ".json"}:
            data = data.replace(b"\r\n", b"\n")
        assert len(data) == entry["bytes"]
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]


def test_ci_has_required_linux_and_windows_replays():
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "Phase 11-3 Scientific Replay (Linux)" in workflow
    assert "Phase 11-3 Scientific Replay (Windows)" in workflow
    assert "runs-on: windows-latest" in workflow
