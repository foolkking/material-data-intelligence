"""Inventory and explicitly purge obsolete repository-local Next build caches.

The command is read-only by default. Apply mode is deliberately guarded by
both an exact dry-run fingerprint and a successful probe of every configured
active frontend. Only direct ``apps/web/.next*`` directories can ever become
candidates. The current ``apps/web/.cache`` build root is inventory-only and
permanently excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "mdi.repo-build-cache-cleanup/1.0"
DEFAULT_ACTIVE_FRONTEND_URL = "http://127.0.0.1:3023"
DEFAULT_MINIMUM_AGE_HOURS = 24.0
ACTIVE_PROBE_TIMEOUT_SECONDS = 1.0


@dataclass(frozen=True)
class CacheDirectory:
    path: str
    bytes: int
    file_count: int
    newest_modified_ns: int
    age_hours: float
    build_id: str | None
    contains_symlink: bool


def _repository_root(path: Path) -> Path:
    resolved = path.resolve()
    if not (resolved / ".git").is_dir():
        raise ValueError(f"cleanup root must contain .git: {resolved}")
    return resolved


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_inventory_cache(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    web_root = (root / "apps" / "web").resolve()
    web_cache = (web_root / ".cache").resolve()
    return (
        resolved.parent == web_root
        and resolved.name.startswith(".next")
    ) or (
        resolved.parent == web_cache
        and resolved.name.startswith("next")
    )


def _is_cleanup_candidate(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    web_root = (root / "apps" / "web").resolve()
    return (
        resolved.parent == web_root
        and resolved.name.startswith(".next")
    )


def _cache_roots(root: Path) -> list[Path]:
    web_root = root / "apps" / "web"
    web_cache = web_root / ".cache"
    roots = [
        path
        for path in web_root.glob(".next*")
        if path.is_dir() and not path.is_symlink()
    ]
    if web_cache.is_dir() and not web_cache.is_symlink():
        roots.extend(
            path
            for path in web_cache.glob("next*")
            if path.is_dir() and not path.is_symlink()
        )
    return sorted({path.resolve() for path in roots}, key=str)


def _measure_cache(path: Path, root: Path, *, now_ns: int) -> CacheDirectory:
    if not _is_inventory_cache(path, root):
        raise ValueError(f"cache path is outside the allowlist: {path}")
    total_bytes = 0
    file_count = 0
    contains_symlink = False
    newest_modified_ns = path.stat().st_mtime_ns
    stack = [path]
    while stack:
        current = stack.pop()
        with os.scandir(current) as entries:
            for entry in entries:
                if entry.is_symlink():
                    contains_symlink = True
                    continue
                stat = entry.stat(follow_symlinks=False)
                newest_modified_ns = max(newest_modified_ns, stat.st_mtime_ns)
                if entry.is_file(follow_symlinks=False):
                    total_bytes += stat.st_size
                    file_count += 1
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
    build_id_path = path / "BUILD_ID"
    build_id = (
        build_id_path.read_text(encoding="utf-8").strip()
        if build_id_path.is_file() and not build_id_path.is_symlink()
        else None
    )
    relative = path.relative_to(root).as_posix()
    return CacheDirectory(
        path=relative,
        bytes=total_bytes,
        file_count=file_count,
        newest_modified_ns=newest_modified_ns,
        age_hours=round(max(0, now_ns - newest_modified_ns) / 3_600_000_000_000, 3),
        build_id=build_id or None,
        contains_symlink=contains_symlink,
    )


def inventory_build_caches(
    root: Path,
    *,
    now_ns: int | None = None,
) -> list[CacheDirectory]:
    repository = _repository_root(root)
    current_ns = (
        datetime.now(timezone.utc).timestamp() * 1_000_000_000
        if now_ns is None
        else now_ns
    )
    return [
        _measure_cache(path, repository, now_ns=int(current_ns))
        for path in _cache_roots(repository)
    ]


def _normalized_frontend_url(value: str) -> str:
    normalized = value.strip().rstrip("/")
    if not normalized.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ValueError("active frontend probes must target localhost")
    return normalized


def probe_active_builds(
    caches: Iterable[CacheDirectory],
    frontend_urls: Iterable[str],
    *,
    timeout_seconds: float = ACTIVE_PROBE_TIMEOUT_SECONDS,
) -> tuple[set[str], list[dict[str, Any]]]:
    by_build_id: dict[str, list[str]] = {}
    for cache in caches:
        if cache.build_id:
            by_build_id.setdefault(cache.build_id, []).append(cache.path)
    active_paths: set[str] = set()
    probes: list[dict[str, Any]] = []
    for raw_url in frontend_urls:
        base_url = _normalized_frontend_url(raw_url)
        matched_build_id: str | None = None
        matched_paths: list[str] = []
        reachable = False
        try:
            with urllib.request.urlopen(base_url, timeout=timeout_seconds) as response:
                reachable = 200 <= response.status < 500
        except (OSError, urllib.error.URLError):
            reachable = False
        if reachable:
            for build_id, paths in by_build_id.items():
                manifest_url = (
                    f"{base_url}/_next/static/{build_id}/_buildManifest.js"
                )
                try:
                    with urllib.request.urlopen(
                        manifest_url, timeout=timeout_seconds
                    ) as response:
                        if response.status == 200:
                            matched_build_id = build_id
                            matched_paths = sorted(paths)
                            active_paths.update(paths)
                            break
                except (OSError, urllib.error.HTTPError, urllib.error.URLError):
                    continue
        probes.append(
            {
                "url": base_url,
                "reachable": reachable,
                "matchedBuildId": matched_build_id,
                "matchedPaths": matched_paths,
            }
        )
    return active_paths, probes


def _fingerprint(candidates: Iterable[CacheDirectory]) -> str:
    payload = [
        {
            "path": item.path,
            "bytes": item.bytes,
            "fileCount": item.file_count,
            "newestModifiedNs": item.newest_modified_ns,
            "buildId": item.build_id,
        }
        for item in sorted(candidates, key=lambda item: item.path)
    ]
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _tracked_cache_paths(
    root: Path,
    caches: Iterable[CacheDirectory],
) -> tuple[set[str], bool]:
    completed = subprocess.run(
        ["git", "ls-files", "-z", "--", "apps/web"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return set(), False
    tracked_files = {
        item.decode("utf-8")
        for item in completed.stdout.split(b"\0")
        if item
    }
    tracked_caches = {
        cache.path
        for cache in caches
        if any(
            tracked == cache.path or tracked.startswith(f"{cache.path}/")
            for tracked in tracked_files
        )
    }
    return tracked_caches, True


def build_cleanup_plan(
    root: Path,
    *,
    minimum_age_hours: float = DEFAULT_MINIMUM_AGE_HOURS,
    frontend_urls: Iterable[str] = (DEFAULT_ACTIVE_FRONTEND_URL,),
    now_ns: int | None = None,
    active_build_ids: set[str] | None = None,
    tracked_paths: set[str] | None = None,
) -> dict[str, Any]:
    if minimum_age_hours < 1:
        raise ValueError("minimum_age_hours must be at least one hour")
    repository = _repository_root(root)
    caches = inventory_build_caches(repository, now_ns=now_ns)
    if tracked_paths is None:
        tracked_cache_paths, git_tracking_complete = _tracked_cache_paths(
            repository, caches
        )
    else:
        tracked_cache_paths = set(tracked_paths)
        git_tracking_complete = True
    urls = tuple(frontend_urls)
    if active_build_ids is None:
        active_paths, probes = probe_active_builds(caches, urls)
    else:
        active_paths = {
            cache.path
            for cache in caches
            if cache.build_id in active_build_ids
        }
        probes = [
            {
                "url": "test-authority",
                "reachable": True,
                "matchedBuildId": build_id,
                "matchedPaths": sorted(
                    cache.path
                    for cache in caches
                    if cache.build_id == build_id
                ),
            }
            for build_id in sorted(active_build_ids)
        ]
    active_resolution_complete = bool(probes) and all(
        probe["reachable"]
        and probe["matchedBuildId"]
        and probe["matchedPaths"]
        for probe in probes
    )
    candidates: list[CacheDirectory] = []
    retained: list[dict[str, Any]] = []
    for cache in caches:
        if cache.path in active_paths:
            retained.append({**asdict(cache), "reason": "ACTIVE_FRONTEND_BUILD"})
        elif cache.path in tracked_cache_paths:
            retained.append({**asdict(cache), "reason": "GIT_TRACKED_CONTENT"})
        elif not _is_cleanup_candidate(repository / cache.path, repository):
            retained.append({**asdict(cache), "reason": "CURRENT_CACHE_ROOT"})
        elif cache.contains_symlink:
            retained.append({**asdict(cache), "reason": "CONTAINS_SYMLINK"})
        elif cache.age_hours < minimum_age_hours:
            retained.append({**asdict(cache), "reason": "RECENT_BUILD"})
        else:
            candidates.append(cache)
    candidate_bytes = sum(item.bytes for item in candidates)
    total_bytes = sum(item.bytes for item in caches)
    plan_fingerprint = _fingerprint(candidates)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "dry-run",
        "root": str(repository),
        "minimumAgeHours": minimum_age_hours,
        "activeResolutionComplete": active_resolution_complete,
        "safeToApply": active_resolution_complete and git_tracking_complete,
        "gitTrackingComplete": git_tracking_complete,
        "trackedCachePaths": sorted(tracked_cache_paths),
        "activeFrontendProbes": probes,
        "summary": {
            "directoryCount": len(caches),
            "observedBytes": total_bytes,
            "candidateCount": len(candidates),
            "candidateBytes": candidate_bytes,
            "retainedCount": len(retained),
            "retainedBytes": total_bytes - candidate_bytes,
        },
        "planFingerprint": plan_fingerprint,
        "candidates": [asdict(item) for item in candidates],
        "retained": retained,
        "permanentlyExcluded": [
            "repository source and configuration",
            "node_modules and Python environments",
            "apps/web/.cache current build root",
            "PostgreSQL, Redis and MinIO data",
            "browser profiles",
            "runtime logs",
            "release and qualification evidence",
        ],
    }


def apply_cleanup_plan(
    root: Path,
    *,
    expected_plan_fingerprint: str,
    minimum_age_hours: float = DEFAULT_MINIMUM_AGE_HOURS,
    frontend_urls: Iterable[str] = (DEFAULT_ACTIVE_FRONTEND_URL,),
    now_ns: int | None = None,
    active_build_ids: set[str] | None = None,
    tracked_paths: set[str] | None = None,
) -> dict[str, Any]:
    repository = _repository_root(root)
    plan = build_cleanup_plan(
        repository,
        minimum_age_hours=minimum_age_hours,
        frontend_urls=frontend_urls,
        now_ns=now_ns,
        active_build_ids=active_build_ids,
        tracked_paths=tracked_paths,
    )
    if not plan["safeToApply"]:
        raise ValueError("active frontend build could not be resolved; apply refused")
    if plan["planFingerprint"] != expected_plan_fingerprint:
        raise ValueError("cleanup plan changed; run dry-run again")
    removed: list[str] = []
    targets: list[tuple[Path, str]] = []
    for raw_candidate in plan["candidates"]:
        candidate = repository / raw_candidate["path"]
        if (
            not _inside(candidate, repository)
            or not _is_cleanup_candidate(candidate, repository)
            or not candidate.is_dir()
            or candidate.is_symlink()
        ):
            raise ValueError(
                f"cleanup candidate is no longer an allowlisted directory: {candidate}"
            )
        targets.append((candidate, raw_candidate["path"]))
    for candidate, relative_path in targets:
        shutil.rmtree(candidate)
        removed.append(relative_path)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "mode": "apply",
        "planFingerprint": expected_plan_fingerprint,
        "removedCount": len(removed),
        "removedBytes": plan["summary"]["candidateBytes"],
        "removed": removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--minimum-age-hours",
        type=float,
        default=DEFAULT_MINIMUM_AGE_HOURS,
    )
    parser.add_argument(
        "--active-frontend-url",
        action="append",
        default=None,
        help="repeat for every active repository frontend",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="permanently delete only the exact fingerprinted cache candidates",
    )
    parser.add_argument("--expected-plan-fingerprint")
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")
    urls = tuple(
        args.active_frontend_url or [DEFAULT_ACTIVE_FRONTEND_URL]
    )
    if args.apply:
        if not args.expected_plan_fingerprint:
            parser.error("--apply requires --expected-plan-fingerprint")
        result = apply_cleanup_plan(
            args.root,
            expected_plan_fingerprint=args.expected_plan_fingerprint,
            minimum_age_hours=args.minimum_age_hours,
            frontend_urls=urls,
        )
    else:
        result = build_cleanup_plan(
            args.root,
            minimum_age_hours=args.minimum_age_hours,
            frontend_urls=urls,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
