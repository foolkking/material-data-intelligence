from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.repo_build_cache_cleanup import (
    apply_cleanup_plan,
    build_cleanup_plan,
)


NOW_NS = 2_000_000_000_000_000_000


def _cache(
    root: Path,
    relative: str,
    *,
    build_id: str,
    age_hours: float,
    size: int = 10,
) -> Path:
    path = root / relative
    path.mkdir(parents=True)
    (path / "BUILD_ID").write_text(build_id, encoding="utf-8")
    payload = path / "cache.bin"
    payload.write_bytes(b"x" * size)
    modified_ns = NOW_NS - int(age_hours * 3_600_000_000_000)
    for item in (path / "BUILD_ID", payload, path):
        os.utime(item, ns=(modified_ns, modified_ns))
    return path


def _root(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    (tmp_path / "apps" / "web" / ".cache").mkdir(parents=True)
    return tmp_path


def test_dry_run_only_candidates_old_allowlisted_non_active_builds(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    old = _cache(
        root, "apps/web/.next-old", build_id="old-build", age_hours=72
    )
    active = _cache(
        root,
        "apps/web/.cache/next-live",
        build_id="active-build",
        age_hours=72,
    )
    inactive_current_root = _cache(
        root,
        "apps/web/.cache/next-inactive",
        build_id="inactive-current-build",
        age_hours=72,
    )
    recent = _cache(
        root, "apps/web/.next-recent", build_id="recent-build", age_hours=2
    )
    source = root / "apps" / "web" / "app" / "page.tsx"
    source.parent.mkdir(parents=True)
    source.write_text("export default function Page() {}", encoding="utf-8")
    evidence = root / "docs" / "phase13" / "evidence" / "manifest.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("{}", encoding="utf-8")
    profile = root / ".phase14r-test-browser-profile" / "state"
    profile.parent.mkdir()
    profile.write_text("profile", encoding="utf-8")
    minio = root / ".phase14r-minio-fresh" / "object"
    minio.parent.mkdir()
    minio.write_text("artifact", encoding="utf-8")

    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"active-build"},
        tracked_paths=set(),
    )

    assert plan["mode"] == "dry-run"
    assert plan["safeToApply"] is True
    assert [item["path"] for item in plan["candidates"]] == [
        "apps/web/.next-old"
    ]
    retained = {item["path"]: item["reason"] for item in plan["retained"]}
    assert retained == {
        "apps/web/.cache/next-inactive": "CURRENT_CACHE_ROOT",
        "apps/web/.cache/next-live": "ACTIVE_FRONTEND_BUILD",
        "apps/web/.next-recent": "RECENT_BUILD",
    }
    assert (
        old.exists()
        and active.exists()
        and inactive_current_root.exists()
        and recent.exists()
    )
    assert source.exists() and evidence.exists() and profile.exists() and minio.exists()


def test_apply_requires_unchanged_fingerprint_and_revalidates_candidates(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    old = _cache(
        root, "apps/web/.next-old", build_id="old-build", age_hours=72
    )
    _cache(
        root,
        "apps/web/.cache/next-live",
        build_id="active-build",
        age_hours=72,
    )
    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"active-build"},
        tracked_paths=set(),
    )
    changed = old / "changed.bin"
    changed.write_text("changed after review", encoding="utf-8")
    os.utime(changed, ns=(NOW_NS - 48 * 3_600_000_000_000,) * 2)

    with pytest.raises(ValueError, match="plan changed"):
        apply_cleanup_plan(
            root,
            expected_plan_fingerprint=plan["planFingerprint"],
            minimum_age_hours=24,
            now_ns=NOW_NS,
            active_build_ids={"active-build"},
            tracked_paths=set(),
        )

    assert old.exists()


def test_apply_removes_only_reviewed_cache_and_preserves_active_authorities(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    old = _cache(
        root, "apps/web/.next-old", build_id="old-build", age_hours=72
    )
    active = _cache(
        root,
        "apps/web/.cache/next-live",
        build_id="active-build",
        age_hours=72,
    )
    source = root / "apps" / "web" / "next.config.mjs"
    source.write_text("export default {}", encoding="utf-8")
    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"active-build"},
        tracked_paths=set(),
    )

    result = apply_cleanup_plan(
        root,
        expected_plan_fingerprint=plan["planFingerprint"],
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"active-build"},
        tracked_paths=set(),
    )

    assert result["removed"] == ["apps/web/.next-old"]
    assert not old.exists()
    assert active.exists()
    assert source.exists()


def test_apps_web_cache_is_never_a_cleanup_candidate(tmp_path: Path) -> None:
    root = _root(tmp_path)
    current_root = _cache(
        root,
        "apps/web/.cache/next-old-but-protected",
        build_id="protected-current-root",
        age_hours=720,
    )

    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"unrelated-active-build"},
        tracked_paths=set(),
    )

    assert plan["candidates"] == []
    assert plan["retained"][0]["reason"] == "CURRENT_CACHE_ROOT"
    assert current_root.exists()


def test_apply_fails_closed_without_resolved_active_frontend(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    old = _cache(
        root, "apps/web/.next-old", build_id="old-build", age_hours=72
    )
    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        frontend_urls=("http://127.0.0.1:9",),
        now_ns=NOW_NS,
        tracked_paths=set(),
    )

    assert plan["safeToApply"] is False
    with pytest.raises(ValueError, match="active frontend build"):
        apply_cleanup_plan(
            root,
            expected_plan_fingerprint=plan["planFingerprint"],
            minimum_age_hours=24,
            frontend_urls=("http://127.0.0.1:9",),
            now_ns=NOW_NS,
            tracked_paths=set(),
        )
    assert old.exists()


def test_non_allowlisted_path_cannot_be_promoted_by_name(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    protected = _cache(
        root, "docs/.next-evidence", build_id="evidence", age_hours=72
    )
    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"unrelated-active-build"},
        tracked_paths=set(),
    )

    assert plan["candidates"] == []
    assert protected.exists()


def test_git_tracked_build_directory_is_never_a_candidate(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    tracked = _cache(
        root, "apps/web/.next-tracked", build_id="tracked-build", age_hours=72
    )

    plan = build_cleanup_plan(
        root,
        minimum_age_hours=24,
        now_ns=NOW_NS,
        active_build_ids={"unrelated-active-build"},
        tracked_paths={"apps/web/.next-tracked"},
    )

    assert plan["candidates"] == []
    assert plan["retained"][0]["reason"] == "GIT_TRACKED_CONTENT"
    assert tracked.exists()
