from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_0_current_ux_reality"


def read(name: str) -> dict:
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_phase12_audit_preserves_phase11_and_inventories_surfaces() -> None:
    assert len(load_manifests().tools) == 62
    phase11 = read("phase11_scientific_authority_snapshot.json")
    assert phase11["readOnly"] is True
    assert phase11["golden"] == {"records": 12, "passInvariant": 8, "notApplicable": 4, "failures": 0}
    assert read("surface_registry.json")["unclassified"] == 0
    assert read("component_inventory.json")["unclassified"] == 0
    assert read("user_journey_matrix.json")["unaudited"] == 0
    assert read("ux_problem_matrix.json")["unassigned"] == 0


def test_phase12_decisions_and_acceptance_are_sealed() -> None:
    decisions = read("phase12_decision_registry.json")
    assert decisions["implementationCriticalTbd"] == 0
    assert decisions["resultFirst"] is True
    acceptance = read("acceptance_registry.json")
    assert [acceptance[key] for key in ("expected", "implemented", "missing", "extra", "duplicate", "conflicting", "shorthand")] == [12, 12, 0, 0, 0, 0, 0]


def test_phase12_manifest_hashes_and_no_production_authority() -> None:
    for item in read("manifest.json")["files"]:
        path = OUT / item["path"]
        data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        assert hashlib.sha256(data).hexdigest() == item["sha256"]
    assert read("scientific_viewer_matrix.json")["frontendScientificRecomputation"] == 0
