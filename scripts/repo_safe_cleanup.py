"""Plan and safely archive repository-owned temporary files and expired logs.

The command is intentionally dry-run by default.  Only the explicit
``.tmp-*``/``.pytest_tmp`` temporary allowlist and ``.managed_logs`` log
directory are eligible; runtime logs, evidence, databases, object stores and
all other repository paths are never candidates.
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TEMP_SUFFIXES = {".json", ".txt", ".tmp", ".bin"}
MANAGED_LOG_DIR = ".managed_logs"
ARCHIVE_DIR = ".cleanup_archive"
MAX_DISCLOSED_PATHS_PER_CLASS = 20


@dataclass(frozen=True)
class CleanupCandidate:
    path: str
    kind: str
    age_days: float
    destination: str


def _root(path: Path) -> Path:
    resolved = path.resolve()
    if not (resolved / ".git").exists():
        raise ValueError(f"cleanup root must contain .git: {resolved}")
    return resolved


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _eligible_file(path: Path, root: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    if not _inside(path, root):
        return False
    if path.suffix.lower() not in TEMP_SUFFIXES:
        return False
    return path.name.startswith(".tmp-") or _inside(path, root / ".pytest_tmp")


def _managed_log(path: Path, root: Path) -> bool:
    logs = root / MANAGED_LOG_DIR
    return (
        path.is_file()
        and not path.is_symlink()
        and path.suffix.lower() == ".log"
        and _inside(path, logs)
        and path.parent == logs
    )


def plan_cleanup(root: Path, *, older_than_days: float, now: float | None = None) -> list[CleanupCandidate]:
    repo = _root(root)
    if older_than_days < 0:
        raise ValueError("older_than_days must be non-negative")
    current = datetime.now(timezone.utc).timestamp() if now is None else now
    cutoff = current - older_than_days * 86400
    candidates: list[CleanupCandidate] = []

    sources: list[tuple[Path, str]] = []
    for item in repo.iterdir():
        if item.name.startswith(".tmp-") and item.is_file():
            sources.append((item, "temporary"))
    temp_dir = repo / ".pytest_tmp"
    if temp_dir.is_dir() and not temp_dir.is_symlink():
        sources.extend((item, "temporary") for item in temp_dir.rglob("*"))
    managed_logs = repo / MANAGED_LOG_DIR
    if managed_logs.is_dir() and not managed_logs.is_symlink():
        sources.extend((item, "expired_log") for item in managed_logs.iterdir())

    archive_root = repo / ARCHIVE_DIR
    for source, kind in sources:
        if source.is_symlink() or not source.is_file():
            continue
        if kind == "temporary" and not _eligible_file(source, repo):
            continue
        if kind == "expired_log" and not _managed_log(source, repo):
            continue
        modified = source.stat().st_mtime
        if modified > cutoff:
            continue
        age_days = max(0.0, (current - modified) / 86400)
        relative = source.relative_to(repo)
        destination = archive_root / relative
        candidates.append(CleanupCandidate(
            path=str(relative).replace("\\", "/"),
            kind=kind,
            age_days=round(age_days, 3),
            destination=str(destination.relative_to(repo)).replace("\\", "/"),
        ))
    return sorted(candidates, key=lambda item: (item.kind, item.path))


def apply_cleanup(root: Path, candidates: list[CleanupCandidate]) -> None:
    repo = _root(root)
    archive_root = repo / ARCHIVE_DIR
    for candidate in candidates:
        source = repo / candidate.path
        destination = repo / candidate.destination
        if not _inside(source, repo) or not _inside(destination, archive_root):
            raise ValueError("cleanup candidate escaped the repository archive boundary")
        if not source.is_file() or source.is_symlink():
            raise ValueError(f"cleanup source is no longer a safe regular file: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError(destination)
        shutil.move(str(source), str(destination))


def classify_workspace(
    root: Path,
    *,
    candidates: list[CleanupCandidate],
    older_than_days: float,
    now: float | None = None,
) -> dict[str, Any]:
    """Explain protected and retained residue without widening cleanup scope."""

    repo = _root(root)
    current = datetime.now(timezone.utc).timestamp() if now is None else now
    cutoff = current - older_than_days * 86400
    candidate_paths = {item.path for item in candidates}

    retained_temporary: list[str] = []
    for item in repo.iterdir():
        if (
            item.name.startswith(".tmp-")
            and item.is_file()
            and not item.is_symlink()
            and item.name not in candidate_paths
            and item.suffix.lower() in TEMP_SUFFIXES
            and item.stat().st_mtime > cutoff
        ):
            retained_temporary.append(item.name)

    protected_service_data = sorted(
        item.name
        for item in repo.iterdir()
        if item.is_dir()
        and (
            item.name.startswith(".phase13-postgres-data")
            or item.name.startswith(".phase13-minio")
            or item.name.startswith(".phase14r-minio")
            or item.name.startswith(".phase14r-recovery")
            or item.name.startswith(".phase14r-redis")
            or item.name == ".runtime_services"
        )
    )
    protected_runtime_logs = sorted(
        item.name
        for item in repo.iterdir()
        if item.is_file()
        and item.suffix.lower() == ".log"
        and (
            item.name.startswith(".phase14r-")
            or item.name.startswith(".phase13-")
        )
    )
    evidence_roots = sorted(
        path.relative_to(repo).as_posix()
        for path in (repo / "docs").glob("**/evidence")
        if path.is_dir()
    )
    recovery_archive = repo / ARCHIVE_DIR
    recovery_entries = (
        sorted(item.name for item in recovery_archive.iterdir())
        if recovery_archive.is_dir()
        else []
    )

    return {
        "retainedTemporary": _bounded_class(retained_temporary),
        "protectedReleaseEvidence": _bounded_class(evidence_roots),
        "protectedActiveServiceData": _bounded_class(protected_service_data),
        "protectedRuntimeLogs": _bounded_class(protected_runtime_logs),
        "recoverableCleanupArchive": _bounded_class(recovery_entries),
    }


def _bounded_class(paths: list[str]) -> dict[str, Any]:
    return {
        "count": len(paths),
        "paths": paths[:MAX_DISCLOSED_PATHS_PER_CLASS],
        "truncated": len(paths) > MAX_DISCLOSED_PATHS_PER_CLASS,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--older-than-days", type=float, default=30)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--apply",
        action="store_true",
        help="move planned files into .cleanup_archive",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="explicitly select the default read-only planning mode",
    )
    args = parser.parse_args()
    candidates = plan_cleanup(args.root, older_than_days=args.older_than_days)
    classification = classify_workspace(
        args.root,
        candidates=candidates,
        older_than_days=args.older_than_days,
    )
    if args.apply:
        apply_cleanup(args.root, candidates)
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "candidateCount": len(candidates),
        "candidates": [asdict(item) for item in candidates],
        "classification": classification,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
