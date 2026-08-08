from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10n/evidence/phase10n2_local_environment_coordination_polyhedra"


def test_n2_evidence_manifest_is_complete_and_hashed() -> None:
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    actual = {item.relative_to(EVIDENCE).as_posix() for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"}
    assert {item["path"] for item in entries} == actual
    assert len(entries) == len(actual) == len({item["path"] for item in entries})
    for entry in entries:
        raw = (EVIDENCE / entry["path"]).read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert entry["bytes"] == len(raw)
        assert entry["sha256"] == sha256(normalized).hexdigest()
    assert manifest["missingEntries"] == manifest["duplicateEntries"] == manifest["secretEntries"] == 0
    text = "\n".join((EVIDENCE / entry["path"]).read_text(encoding="utf-8", errors="ignore") for entry in entries)
    assert "DEEPSEEK_KEY=" not in text
    assert "Authorization:" not in text
    assert not re.search(r"[A-Za-z]:\\Users\\", text)
    assert "/home/runner/" not in text


def test_n2_evidence_records_one_tool_and_no_recomputation() -> None:
    registry = json.loads((EVIDENCE / "registry_entries.json").read_text(encoding="utf-8"))
    assert registry == {
        "baselineCount": 55,
        "addedCount": 1,
        "finalCount": 56,
        "comparisonToolCount": 0,
        "tools": [{"toolId": "structure.local_environment_polyhedra", "version": "0.1.0"}],
    }
    authority = (EVIDENCE / "n1_authority_audit.md").read_text(encoding="utf-8")
    assert "N2_RECOMPUTED_N1_NEIGHBORS = 0" in authority
    assert "N2_INDEPENDENT_NEIGHBOR_SEARCH = 0" in authority
    assert "N2_COORDINATION_ALGORITHM_FALLBACK = 0" in authority


def test_n2_ci_requires_browser_and_zero_skip_service_closure() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--n2-local-environment-only" in workflow
    assert "test_phase10n2_local_environment_service_backed.py" in workflow
    assert "test_phase10n2_postgres_redis_minio_exact_n1_dependency_closure" in workflow
    assert 'if [ "${PASSED:-0}" -lt 45 ]; then' in workflow
