from __future__ import annotations

from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = "<!-- phase10m7-acceptance-registry:start -->"
END = "<!-- phase10m7-acceptance-registry:end -->"
DOCUMENTS = (
    "docs/phase10m/phase10m_acceptance_and_test_plan.md",
    "docs/phase10m/phase10m_implementation_backlog.md",
    "docs/phase10m/phase10m_execution_lock.md",
    "docs/phase10m/phase10m_execution_manifest.md",
)
CANONICAL = {
    "M7-A01": ("Service-backed", "PostgreSQL + Redis + MinIO full Workspace lifecycle, 0 skipped/failed"),
    "M7-A02": ("Scientific integrity", "Adapter -> Runtime -> Artifact -> renderer/evidence authority remains exact"),
    "M7-A03": ("Historical compatibility", "0.1/0.2, modern/legacy/partial/missing-source cases retained"),
    "M7-A04": ("Full tests", "Backend/frontend/typecheck/build/lock/migration/closure all pass"),
    "M7-A05": ("Browser", "Chromium/Firefox/WebKit/mobile/accessibility/WebGL current evidence passes"),
    "M7-A06": ("Security", "All Workspace security markers and secret scan pass"),
    "M7-A07": ("Evidence", "Sanitized API/DOM/network/console/screenshots/performance manifest verifies"),
    "M7-A08": ("Lifecycle", "Implementation, completion, and verified queue archive exact-SHA CI pass"),
}


def _registry(path: Path) -> list[tuple[str, str, str]]:
    text = path.read_text(encoding="utf-8")
    assert text.count(START) == text.count(END) == 1
    section = text.split(START, 1)[1].split(END, 1)[0]
    assert "M7-A01 through M7-A08" not in section
    rows: list[tuple[str, str, str]] = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0].startswith("M7-A"):
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def test_phase10m7_canonical_acceptance_registries_are_reconciled() -> None:
    for relative in DOCUMENTS:
        rows = _registry(ROOT / relative)
        counts = Counter(item[0] for item in rows)
        assert set(counts) == set(CANONICAL)
        assert all(count == 1 for count in counts.values())
        assert {item[0]: item[1:] for item in rows} == CANONICAL


def test_phase10m7_registry_validator_ignores_external_references() -> None:
    manifest = (ROOT / "docs/phase10m/phase10m_execution_manifest.md").read_text(encoding="utf-8")
    lock = (ROOT / "docs/phase10m/phase10m_execution_lock.md").read_text(encoding="utf-8")
    assert manifest.count("M7-A01") > 1
    assert lock.count("M7-A03") > 1
    assert len(_registry(ROOT / DOCUMENTS[2])) == 8
    assert len(_registry(ROOT / DOCUMENTS[3])) == 8
