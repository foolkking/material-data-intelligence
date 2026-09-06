"""Run a local service with bounded, rotating stdout/stderr logs.

The active ``*.log`` file is never part of retention cleanup.  Only archives
created by this runner are eligible for age/count deletion, which makes the
policy safe to inspect in dry-run mode while services remain online.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import BinaryIO, TextIO


DEFAULT_MAX_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_ARCHIVES = 8
DEFAULT_MAX_AGE_DAYS = 14


@dataclass(frozen=True)
class RotationPolicy:
    max_bytes: int = DEFAULT_MAX_BYTES
    max_archives: int = DEFAULT_MAX_ARCHIVES
    max_age_days: int = DEFAULT_MAX_AGE_DAYS

    def __post_init__(self) -> None:
        if self.max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        if self.max_archives < 1:
            raise ValueError("max_archives must be positive")
        if self.max_age_days < 1:
            raise ValueError("max_age_days must be positive")


def _archive_pattern(active_path: Path) -> str:
    return f"{active_path.stem}.*{active_path.suffix}"


def _is_managed_archive(active_path: Path, candidate: Path) -> bool:
    escaped_stem = re.escape(active_path.stem)
    escaped_suffix = re.escape(active_path.suffix)
    return bool(
        re.fullmatch(
            rf"{escaped_stem}\.\d{{8}}T\d{{6}}Z\.\d{{4}}{escaped_suffix}",
            candidate.name,
        )
    )


def _archive_path(active_path: Path, now: datetime) -> Path:
    timestamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    for sequence in range(1, 10_000):
        candidate = active_path.with_name(
            f"{active_path.stem}.{timestamp}.{sequence:04d}{active_path.suffix}"
        )
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not allocate a log archive name for {active_path}")


def retention_candidates(
    active_path: Path,
    policy: RotationPolicy,
    *,
    now: datetime | None = None,
) -> list[Path]:
    """Return archives that exceed age or count limits, never the active log."""

    now = now or datetime.now(UTC)
    active_resolved = active_path.resolve()
    archives = sorted(
        (
            path
            for path in active_path.parent.glob(_archive_pattern(active_path))
            if (
                path.resolve() != active_resolved
                and path.is_file()
                and _is_managed_archive(active_path, path)
            )
        ),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    cutoff = now - timedelta(days=policy.max_age_days)
    expired = {
        path
        for path in archives
        if datetime.fromtimestamp(path.stat().st_mtime, UTC) < cutoff
    }
    overflow = set(archives[policy.max_archives :])
    return sorted(expired | overflow, key=lambda path: path.name)


def apply_retention(
    active_path: Path,
    policy: RotationPolicy,
    *,
    dry_run: bool,
    now: datetime | None = None,
) -> list[Path]:
    candidates = retention_candidates(active_path, policy, now=now)
    if not dry_run:
        for candidate in candidates:
            candidate.unlink(missing_ok=True)
    return candidates


class RotatingLogStream:
    def __init__(self, active_path: Path, policy: RotationPolicy) -> None:
        self.active_path = active_path.resolve()
        self.policy = policy
        self._lock = threading.Lock()
        self._handle: TextIO | None = None
        self._period: str | None = None

    def __enter__(self) -> "RotatingLogStream":
        self.active_path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(UTC)
        if self._existing_log_needs_rotation(now):
            archive = _archive_path(self.active_path, now)
            os.replace(self.active_path, archive)
            apply_retention(self.active_path, self.policy, dry_run=False, now=now)
        self._open(now)
        return self

    def __exit__(self, *_: object) -> None:
        with self._lock:
            if self._handle is not None:
                self._handle.close()
                self._handle = None

    def _open(self, now: datetime) -> None:
        self._handle = self.active_path.open(
            "a", encoding="utf-8", buffering=1, newline=""
        )
        self._period = now.astimezone(UTC).strftime("%Y-%m-%d")

    def _existing_log_needs_rotation(self, now: datetime) -> bool:
        if not self.active_path.exists() or self.active_path.stat().st_size == 0:
            return False
        modified = datetime.fromtimestamp(self.active_path.stat().st_mtime, UTC)
        return (
            modified.date() != now.astimezone(UTC).date()
            or self.active_path.stat().st_size >= self.policy.max_bytes
        )

    def _should_rotate(self, incoming_bytes: int, now: datetime) -> bool:
        if not self.active_path.exists() or self.active_path.stat().st_size == 0:
            return False
        period_changed = self._period != now.astimezone(UTC).strftime("%Y-%m-%d")
        size_exceeded = (
            self.active_path.stat().st_size + incoming_bytes > self.policy.max_bytes
        )
        return period_changed or size_exceeded

    def _rotate(self, now: datetime) -> None:
        if self._handle is not None:
            self._handle.flush()
            self._handle.close()
            self._handle = None
        archive = _archive_path(self.active_path, now)
        os.replace(self.active_path, archive)
        apply_retention(self.active_path, self.policy, dry_run=False, now=now)
        self._open(now)

    def write(self, text: str, *, now: datetime | None = None) -> None:
        now = now or datetime.now(UTC)
        encoded_length = len(text.encode("utf-8", errors="replace"))
        with self._lock:
            if self._handle is None:
                raise RuntimeError("log stream is not open")
            if self._should_rotate(encoded_length, now):
                self._rotate(now)
            self._handle.write(text)


def _pump(source: BinaryIO, destination: RotatingLogStream) -> None:
    while chunk := source.readline():
        destination.write(chunk.decode("utf-8", errors="replace"))


def run_command(
    command: list[str],
    stdout_path: Path,
    stderr_path: Path,
    policy: RotationPolicy,
) -> int:
    if not command:
        raise ValueError("A child command is required")
    with (
        RotatingLogStream(stdout_path, policy) as stdout_log,
        RotatingLogStream(stderr_path, policy) as stderr_log,
    ):
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
        assert process.stdout is not None
        assert process.stderr is not None
        readers = [
            threading.Thread(
                target=_pump, args=(process.stdout, stdout_log), daemon=True
            ),
            threading.Thread(
                target=_pump, args=(process.stderr, stderr_log), daemon=True
            ),
        ]
        for reader in readers:
            reader.start()
        try:
            return process.wait()
        except KeyboardInterrupt:
            process.terminate()
            return process.wait()
        finally:
            for reader in readers:
                reader.join(timeout=5)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout-log", required=True, type=Path)
    parser.add_argument("--stderr-log", required=True, type=Path)
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=int(os.getenv("MDI_LOG_MAX_BYTES", DEFAULT_MAX_BYTES)),
    )
    parser.add_argument(
        "--max-archives",
        type=int,
        default=int(os.getenv("MDI_LOG_MAX_ARCHIVES", DEFAULT_MAX_ARCHIVES)),
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=int(os.getenv("MDI_LOG_MAX_AGE_DAYS", DEFAULT_MAX_AGE_DAYS)),
    )
    parser.add_argument("--maintenance-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    policy = RotationPolicy(
        max_bytes=args.max_bytes,
        max_archives=args.max_archives,
        max_age_days=args.max_age_days,
    )
    if args.maintenance_only:
        for active_path in (args.stdout_log, args.stderr_log):
            candidates = apply_retention(
                active_path, policy, dry_run=args.dry_run
            )
            for candidate in candidates:
                action = "would-delete" if args.dry_run else "deleted"
                print(f"{action}: {candidate}")
        return 0
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if args.dry_run:
        raise ValueError("--dry-run is only valid with --maintenance-only")
    return run_command(command, args.stdout_log, args.stderr_log, policy)


if __name__ == "__main__":
    raise SystemExit(main())
