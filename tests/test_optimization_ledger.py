from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_optimization_ledger import (
    LedgerValidationError,
    validate_ledger,
)


def _write_ledger(
    tmp_path: Path,
    *,
    counters: str,
    rows: list[str],
    results: str,
) -> tuple[Path, Path]:
    backlog_path = tmp_path / "backlog.md"
    results_path = tmp_path / "results.md"
    backlog_path.write_text(
        f"Status:\n\n```text\n{counters}\n```\n\n" + "\n".join(rows),
        encoding="utf-8",
    )
    results_path.write_text(results, encoding="utf-8")
    return backlog_path, results_path


def test_repository_optimization_ledger_is_self_consistent() -> None:
    root = Path(__file__).resolve().parents[1]

    summary = validate_ledger(
        root / "docs/agent2/continuous_optimization/OPTIMIZATION_BACKLOG.md",
        root / "results.md",
    )

    assert summary.discovered >= 100
    assert summary.completed > 0


def test_duplicate_optimization_id_is_rejected(tmp_path: Path) -> None:
    backlog, results = _write_ledger(
        tmp_path,
        counters=(
            "DISCOVERED = 2\nCOMPLETED = 1\nBLOCKED = 0\n"
            "REMAINING = 1\nCURRENT = CO-002"
        ),
        rows=[
            "| CO-001 | COMPLETED | Test | item | H | P0 | H | S | L | pass |",
            "| CO-001 | OPEN | Test | duplicate | H | P0 | H | S | L | fail |",
            "| CO-002 | OPEN | Test | item | H | P0 | H | S | L | pass |",
        ],
        results="CO-001",
    )

    with pytest.raises(LedgerValidationError, match="duplicate optimization IDs"):
        validate_ledger(backlog, results)


def test_counter_drift_is_rejected(tmp_path: Path) -> None:
    backlog, results = _write_ledger(
        tmp_path,
        counters=(
            "DISCOVERED = 2\nCOMPLETED = 0\nBLOCKED = 0\n"
            "REMAINING = 2\nCURRENT = CO-002"
        ),
        rows=[
            "| CO-001 | COMPLETED | Test | item | H | P0 | H | S | L | pass |",
            "| CO-002 | OPEN | Test | item | H | P0 | H | S | L | pass |",
        ],
        results="CO-001",
    )

    with pytest.raises(LedgerValidationError, match="declared counters"):
        validate_ledger(backlog, results)


def test_completed_item_requires_result_archive_record(tmp_path: Path) -> None:
    backlog, results = _write_ledger(
        tmp_path,
        counters=(
            "DISCOVERED = 2\nCOMPLETED = 1\nBLOCKED = 0\n"
            "REMAINING = 1\nCURRENT = CO-002"
        ),
        rows=[
            "| CO-001 | COMPLETED | Test | item | H | P0 | H | S | L | pass |",
            "| CO-002 | OPEN | Test | item | H | P0 | H | S | L | pass |",
        ],
        results="no optimization identity here",
    )

    with pytest.raises(LedgerValidationError, match="missing from results.md"):
        validate_ledger(backlog, results)


def test_current_item_must_be_open(tmp_path: Path) -> None:
    backlog, results = _write_ledger(
        tmp_path,
        counters=(
            "DISCOVERED = 2\nCOMPLETED = 1\nBLOCKED = 0\n"
            "REMAINING = 1\nCURRENT = CO-001"
        ),
        rows=[
            "| CO-001 | COMPLETED | Test | item | H | P0 | H | S | L | pass |",
            "| CO-002 | OPEN | Test | item | H | P0 | H | S | L | pass |",
        ],
        results="CO-001",
    )

    with pytest.raises(LedgerValidationError, match="must reference an OPEN item"):
        validate_ledger(backlog, results)
