"""Bounded, read-only storage-budget projection for operator diagnostics."""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


GIB = 1024**3
MAX_FILESYSTEM_ENTRIES = 100_000
FILESYSTEM_CACHE_SECONDS = 30
_filesystem_cache: dict[str, tuple[float, dict[str, dict[str, Any]]]] = {}
_filesystem_cache_lock = threading.Lock()


@dataclass(frozen=True)
class StorageBudgetPolicy:
    workspace_bytes: int = 25 * GIB
    database_bytes: int = 10 * GIB
    minio_bytes: int = 25 * GIB
    logs_bytes: int = 2 * GIB
    profiles_bytes: int = 4 * GIB
    build_caches_bytes: int = 25 * GIB

    @classmethod
    def from_environment(cls) -> "StorageBudgetPolicy":
        defaults = cls()
        return cls(
            workspace_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_WORKSPACE_BYTES", defaults.workspace_bytes
            ),
            database_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_DATABASE_BYTES", defaults.database_bytes
            ),
            minio_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_MINIO_BYTES", defaults.minio_bytes
            ),
            logs_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_LOGS_BYTES", defaults.logs_bytes
            ),
            profiles_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_PROFILES_BYTES", defaults.profiles_bytes
            ),
            build_caches_bytes=_positive_budget(
                "MDI_STORAGE_BUDGET_BUILD_CACHES_BYTES",
                defaults.build_caches_bytes,
            ),
        )


def build_storage_budget_snapshot(
    *,
    repository_root: Path,
    database: dict[str, Any],
    artifact_storage: dict[str, Any],
    policy: StorageBudgetPolicy | None = None,
) -> dict[str, Any]:
    """Return aggregate byte counts without serializing paths or object keys."""

    active_policy = policy or StorageBudgetPolicy.from_environment()
    root = repository_root.resolve()
    filesystem = _filesystem_measurements(root)
    categories = [
        _category(
            "workspace",
            filesystem["workspace"],
            active_policy.workspace_bytes,
            scope="repository source, tests, documentation and evidence",
        ),
        _category(
            "database",
            _service_measurement(database, "storageBytes"),
            active_policy.database_bytes,
            scope="current PostgreSQL database",
        ),
        _category(
            "minio",
            _service_measurement(
                artifact_storage,
                "storageBytes",
                count_key="objectCount",
                complete_key="usageScanComplete",
            ),
            active_policy.minio_bytes,
            scope="configured artifact bucket",
        ),
        _category(
            "logs",
            filesystem["logs"],
            active_policy.logs_bytes,
            scope="repository-managed runtime logs",
        ),
        _category(
            "profiles",
            filesystem["profiles"],
            active_policy.profiles_bytes,
            scope="repository-local browser qualification profiles",
        ),
        _category(
            "buildCaches",
            filesystem["buildCaches"],
            active_policy.build_caches_bytes,
            scope="repository-local build and test caches",
        ),
    ]
    states = {item["state"] for item in categories}
    return {
        "schemaVersion": "phase14r-storage-budget/1.0",
        "status": (
            "attention"
            if "exceeded" in states
            else "partial"
            if "unknown" in states
            else "ok"
        ),
        "readOnly": True,
        "redacted": True,
        "scanEntryLimit": MAX_FILESYSTEM_ENTRIES,
        "categories": categories,
    }


def _positive_budget(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _workspace_roots(root: Path) -> list[Path]:
    roots = [
        root / name
        for name in (
            "packages",
            "services",
            "scripts",
            "tests",
            "docs",
            "persistent",
            "config",
            "tool_registry",
            "tools",
            "design",
        )
    ]
    roots.extend(
        root / "apps" / "web" / name
        for name in ("app", "test", "types")
    )
    roots.append(root / "apps" / "api")
    roots.extend(
        root / "apps" / "web" / name
        for name in (
            "package.json",
            "package-lock.json",
            "next.config.mjs",
            "tsconfig.json",
            "tsconfig.typecheck.json",
            "vitest.config.ts",
        )
    )
    roots.extend(path for path in root.iterdir() if path.is_file())
    return roots


def _log_roots(root: Path) -> list[Path]:
    roots = [
        root / ".phase14r-runtime-logs",
        root / ".managed_logs",
        root / "apps" / "web" / ".phase14r-runtime-logs",
    ]
    roots.extend(root.glob("*.log"))
    roots.extend((root / "apps" / "web").glob("*.log"))
    return roots


def _profile_roots(root: Path) -> list[Path]:
    return list(root.glob(".phase14r-*-browser-profile"))


def _build_cache_roots(root: Path) -> list[Path]:
    roots = [
        root / ".cache",
        root / ".vite",
        root / ".pytest_cache",
        root / ".ruff_cache",
        root / ".next",
        root / "apps" / "web" / ".cache",
        root / "apps" / "web" / ".vite",
        root / "apps" / "web" / ".pytest_cache",
        root / "apps" / "web" / ".ruff_cache",
    ]
    roots.extend((root / "apps" / "web").glob(".next*"))
    return roots


def _filesystem_measurements(root: Path) -> dict[str, dict[str, Any]]:
    cache_key = str(root)
    now = time.monotonic()
    with _filesystem_cache_lock:
        cached = _filesystem_cache.get(cache_key)
        if cached and cached[0] > now:
            return cached[1]
    result = {
        "workspace": _measure_paths(_workspace_roots(root)),
        "logs": _measure_paths(_log_roots(root)),
        "profiles": _measure_paths(_profile_roots(root)),
        "buildCaches": _measure_paths(_build_cache_roots(root)),
    }
    with _filesystem_cache_lock:
        _filesystem_cache[cache_key] = (
            now + FILESYSTEM_CACHE_SECONDS,
            result,
        )
    return result


def _measure_paths(paths: Iterable[Path]) -> dict[str, Any]:
    stack: list[Path] = []
    seen: set[Path] = set()
    for candidate in paths:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.exists() or resolved.is_symlink():
            continue
        seen.add(resolved)
        stack.append(resolved)

    observed_bytes = 0
    item_count = 0
    inaccessible_count = 0
    truncated = False
    while stack:
        current = stack.pop()
        if item_count >= MAX_FILESYSTEM_ENTRIES:
            truncated = True
            break
        try:
            if current.is_file():
                observed_bytes += current.stat().st_size
                item_count += 1
                continue
            with os.scandir(current) as entries:
                for entry in entries:
                    if item_count + len(stack) >= MAX_FILESYSTEM_ENTRIES:
                        truncated = True
                        break
                    try:
                        if entry.is_symlink():
                            continue
                        child = Path(entry.path)
                        if entry.is_file(follow_symlinks=False):
                            observed_bytes += entry.stat(
                                follow_symlinks=False
                            ).st_size
                            item_count += 1
                        elif entry.is_dir(follow_symlinks=False):
                            stack.append(child)
                    except OSError:
                        inaccessible_count += 1
                if truncated:
                    break
        except OSError:
            inaccessible_count += 1
    return {
        "observedBytes": observed_bytes,
        "itemCount": item_count,
        "scanComplete": not truncated and inaccessible_count == 0,
        "inaccessibleCount": inaccessible_count,
    }


def _service_measurement(
    source: dict[str, Any],
    bytes_key: str,
    *,
    count_key: str | None = None,
    complete_key: str | None = None,
) -> dict[str, Any]:
    raw_bytes = source.get(bytes_key)
    if not isinstance(raw_bytes, int) or raw_bytes < 0:
        return {
            "observedBytes": None,
            "itemCount": None,
            "scanComplete": False,
            "inaccessibleCount": 0,
        }
    count = source.get(count_key) if count_key else None
    return {
        "observedBytes": raw_bytes,
        "itemCount": count if isinstance(count, int) and count >= 0 else None,
        "scanComplete": (
            bool(source.get(complete_key)) if complete_key else True
        ),
        "inaccessibleCount": 0,
    }


def _category(
    category: str,
    measurement: dict[str, Any],
    budget_bytes: int,
    *,
    scope: str,
) -> dict[str, Any]:
    observed = measurement["observedBytes"]
    complete = bool(measurement["scanComplete"])
    state = (
        "unknown"
        if observed is None
        else "exceeded"
        if observed > budget_bytes
        else "within"
        if complete
        else "unknown"
    )
    return {
        "category": category,
        "scope": scope,
        "observedBytes": observed,
        "budgetBytes": budget_bytes,
        "utilizationPercent": (
            round((observed / budget_bytes) * 100, 2)
            if isinstance(observed, int) and complete
            else None
        ),
        "state": state,
        "itemCount": measurement["itemCount"],
        "scanComplete": complete,
        "inaccessibleCount": measurement["inaccessibleCount"],
    }


__all__ = [
    "MAX_FILESYSTEM_ENTRIES",
    "StorageBudgetPolicy",
    "build_storage_budget_snapshot",
]
