from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


COUNTER_PATTERN = re.compile(
    r"DISCOVERED = (?P<discovered>\d+)\s+"
    r"COMPLETED = (?P<completed>\d+)\s+"
    r"BLOCKED = (?P<blocked>\d+)\s+"
    r"REMAINING = (?P<remaining>\d+)\s+"
    r"CURRENT = (?P<current>CO-\d{3}|NONE)",
    re.MULTILINE,
)
ROW_PATTERN = re.compile(
    r"^\|\s*(?P<identifier>CO-\d{3})\s*"
    r"\|\s*(?P<status>OPEN|COMPLETED|BLOCKED)\s*\|",
    re.MULTILINE,
)


@dataclass(frozen=True)
class LedgerSummary:
    discovered: int
    completed: int
    blocked: int
    remaining: int
    current: str


class LedgerValidationError(ValueError):
    pass


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_ledger(backlog_path: Path, results_path: Path) -> LedgerSummary:
    backlog = _read(backlog_path)
    results = _read(results_path)
    counter_match = COUNTER_PATTERN.search(backlog)
    if counter_match is None:
        raise LedgerValidationError("optimization counters are missing or malformed")

    declared = LedgerSummary(
        discovered=int(counter_match.group("discovered")),
        completed=int(counter_match.group("completed")),
        blocked=int(counter_match.group("blocked")),
        remaining=int(counter_match.group("remaining")),
        current=counter_match.group("current"),
    )
    rows = ROW_PATTERN.findall(backlog)
    identifiers = [identifier for identifier, _status in rows]
    duplicate_ids = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicate_ids:
        raise LedgerValidationError(
            f"duplicate optimization IDs: {', '.join(duplicate_ids)}"
        )

    status_by_id = dict(rows)
    if not status_by_id:
        raise LedgerValidationError("optimization backlog contains no task rows")

    numeric_ids = sorted(int(identifier.removeprefix("CO-")) for identifier in status_by_id)
    expected_ids = list(range(1, max(numeric_ids) + 1))
    if numeric_ids != expected_ids:
        missing = sorted(set(expected_ids) - set(numeric_ids))
        raise LedgerValidationError(
            "optimization IDs must be contiguous; missing "
            + ", ".join(f"CO-{value:03d}" for value in missing)
        )

    actual_completed = sum(status == "COMPLETED" for status in status_by_id.values())
    actual_blocked = sum(status == "BLOCKED" for status in status_by_id.values())
    actual_remaining = sum(status == "OPEN" for status in status_by_id.values())
    actual = LedgerSummary(
        discovered=len(status_by_id),
        completed=actual_completed,
        blocked=actual_blocked,
        remaining=actual_remaining,
        current=declared.current,
    )
    if declared != actual:
        raise LedgerValidationError(
            "declared counters do not match backlog rows: "
            f"declared={declared}, actual={actual}"
        )

    if declared.current != "NONE":
        current_status = status_by_id.get(declared.current)
        if current_status is None:
            raise LedgerValidationError(
                f"CURRENT references unknown optimization ID {declared.current}"
            )
        if current_status != "OPEN":
            raise LedgerValidationError(
                f"CURRENT must reference an OPEN item, got {declared.current}={current_status}"
            )

    missing_results = sorted(
        identifier
        for identifier, status in status_by_id.items()
        if status == "COMPLETED"
        and re.search(rf"\b{re.escape(identifier)}\b", results) is None
    )
    if missing_results:
        raise LedgerValidationError(
            "completed optimizations missing from results.md: "
            + ", ".join(missing_results)
        )

    return declared


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the continuous-optimization ledger and result archive."
    )
    parser.add_argument(
        "--backlog",
        type=Path,
        default=Path("docs/agent2/continuous_optimization/OPTIMIZATION_BACKLOG.md"),
    )
    parser.add_argument("--results", type=Path, default=Path("results.md"))
    args = parser.parse_args()
    summary = validate_ledger(args.backlog, args.results)
    print(
        "optimization ledger valid: "
        f"discovered={summary.discovered} "
        f"completed={summary.completed} "
        f"blocked={summary.blocked} "
        f"remaining={summary.remaining} "
        f"current={summary.current}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
