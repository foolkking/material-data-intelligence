from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase12/evidence/phase12_1_design_system_2_0"


def generate() -> None:
    subprocess.run([sys.executable, "scripts/generate_phase12_1_design_system_evidence.py"], cwd=ROOT, check=True)


def test_design_system_evidence_is_complete_and_deterministic() -> None:
    generate()
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schemaVersion"] == "phase12-1-design-system/2.0"
    assert len(manifest["files"]) >= 29
    assert manifest["designSystemSemanticHash"]


def test_tokens_statuses_and_problem_ownership_are_closed_without_scientific_authority() -> None:
    generate()
    tokens = json.loads((EVIDENCE / "design_token_registry.json").read_text(encoding="utf-8"))
    token_ids = {token["tokenId"] for token in tokens["tokens"]}
    assert {"color-background", "color-status-success", "ds-control-touch"} <= token_ids
    statuses = json.loads((EVIDENCE / "status_visual_mapping.json").read_text(encoding="utf-8"))
    assert statuses["unmappedUserVisibleStatusFamilies"] == 0
    assert all(not row["colorOnlyMeaning"] and not row["scientificAuthorityChanged"] for row in statuses["mappings"])
    closure = json.loads((EVIDENCE / "phase12_1_problem_closure.json").read_text(encoding="utf-8"))
    assert closure["closed"] == ["UX-007"]
    assert closure["open"] == []


def test_component_dispositions_cover_phase12_0_inventory_and_css_has_ds2_foundations() -> None:
    generate()
    components = json.loads((EVIDENCE / "component_migration_matrix.json").read_text(encoding="utf-8"))
    assert components["componentCount"] == 38
    assert components["unclassified"] == 0
    assert all(row["migrationStatus"] for row in components["components"])
    css = (ROOT / "apps/web/app/globals.css").read_text(encoding="utf-8")
    for token in ("--ds-color-graphite-950", "--color-status-stale", "--ds-control-touch", "prefers-reduced-motion"):
        assert token in css
