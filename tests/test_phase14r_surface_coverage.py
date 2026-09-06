from __future__ import annotations

import re
from pathlib import Path

from mdi_api.research_agent.registry_validation import build_default_agent2_registries


_MATRIX_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "agent2"
    / "phase14r"
    / "SCIENTIFIC_SURFACE_COVERAGE_MATRIX.md"
)
_ROW_PATTERN = re.compile(r"^\| `([^`]+)` \| (.+) \|$")


def _matrix_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for raw_line in _MATRIX_PATH.read_text(encoding="utf-8").splitlines():
        match = _ROW_PATTERN.match(raw_line)
        if not match:
            continue
        capability_id, remainder = match.groups()
        rows[capability_id] = [capability_id, *[cell.strip() for cell in remainder.split("|")]]
    return rows


def test_phase14r_surface_matrix_matches_active_registry_contracts() -> None:
    """Keep the human coverage matrix honest when registry declarations drift."""

    registries = build_default_agent2_registries()
    manifests = {
        manifest.capability_id: manifest
        for manifest in registries.capabilities.list_all()
        if manifest.status.value == "ACTIVE"
    }
    matrix = _matrix_rows()

    assert matrix, f"coverage matrix is empty: {_MATRIX_PATH}"
    assert set(matrix) == set(manifests)

    pack_by_capability = {
        item.manifest.capability_id: pack.pack_id
        for pack in registries.extension_registry.list_packs()
        for item in pack.capabilities
    }
    assert set(pack_by_capability) == set(manifests)

    for capability_id, manifest in manifests.items():
        row = matrix[capability_id]
        # Columns are: id, pack, input, tool, projector, presentation,
        # viewer/figure/table, evidence/report, status.
        assert row[1] == pack_by_capability[capability_id]
        assert row[3].strip("`") == manifest.tool_bindings[0].tool_id
        assert row[4].strip("`") == manifest.result_projector
        assert row[5].strip()
        assert row[6].strip()
        assert row[7].strip()
        assert row[8].strip()
        assert row[8] in {"PASS", "PARTIAL", "FAIL", "NOT_QUALIFIED", "N/A"}

        # Every active capability must point at a registered projector. This
        # protects the executable registry boundary as well as the document.
        assert registries.result_projectors.contains(manifest.result_projector)
