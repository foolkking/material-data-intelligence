from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.qualification_run_retention import (
    apply_retention,
    create_run,
    finish_run,
    load_policy,
    retention_plan,
)


NOW = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)


def _root(tmp_path: Path) -> Path:
    (tmp_path / ".git").mkdir()
    return tmp_path


def test_run_identity_owns_exact_postgresql_and_minio_directories(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    run_id = "qual-20260905T120000Z-1234abcd"

    run = create_run(root, policy=policy, run_id=run_id, now=NOW)

    assert run["runId"] == run_id
    assert run["status"] == "ACTIVE"
    assert run["serviceDirectories"] == {
        "postgresql": f".qualification_runs/{run_id}/postgresql",
        "minio": f".qualification_runs/{run_id}/minio",
    }
    assert (root / run["serviceDirectories"]["postgresql"]).is_dir()
    assert (root / run["serviceDirectories"]["minio"]).is_dir()
    assert (
        root / ".qualification_runs" / run_id / "run-manifest.json"
    ).is_file()
    assert (root / ".qualification_runs" / run_id / ".active.json").is_file()


def test_retention_is_dry_run_and_protects_active_recent_and_release_runs(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    active_id = "qual-20260801T120000Z-00000001"
    recent_id = "qual-20260901T120000Z-00000002"
    release_id = "qual-20260801T120000Z-00000003"
    expired_id = "qual-20260801T120000Z-00000004"
    create_run(root, policy=policy, run_id=active_id, now=NOW - timedelta(days=60))
    create_run(root, policy=policy, run_id=recent_id, now=NOW - timedelta(days=5))
    finish_run(
        root,
        policy=policy,
        run_id=recent_id,
        status="COMPLETED",
        now=NOW - timedelta(days=4),
    )
    create_run(
        root,
        policy=policy,
        run_id=release_id,
        release_evidence=True,
        now=NOW - timedelta(days=60),
    )
    finish_run(
        root,
        policy=policy,
        run_id=release_id,
        status="COMPLETED",
        now=NOW - timedelta(days=50),
    )
    create_run(root, policy=policy, run_id=expired_id, now=NOW - timedelta(days=60))
    finish_run(
        root,
        policy=policy,
        run_id=expired_id,
        status="FAILED",
        now=NOW - timedelta(days=50),
    )
    legacy = root / ".phase13-postgres-data2"
    legacy.mkdir()

    plan = retention_plan(root, policy=policy, now=NOW)

    assert plan["mode"] == "dry-run"
    assert plan["candidateCount"] == 1
    assert plan["candidates"][0]["runId"] == expired_id
    assert plan["protected"] == {
        "active": [active_id],
        "releaseEvidence": [release_id],
        "withinTtl": [recent_id],
        "invalid": [],
    }
    assert plan["legacyDirectoriesManaged"] is False
    assert (root / ".qualification_runs" / expired_id).is_dir()
    assert legacy.is_dir()
    assert not (root / ".cleanup_archive").exists()


def test_apply_moves_only_revalidated_terminal_run_to_recoverable_archive(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    expired_id = "qual-20260801T120000Z-00000005"
    create_run(root, policy=policy, run_id=expired_id, now=NOW - timedelta(days=60))
    finish_run(
        root,
        policy=policy,
        run_id=expired_id,
        status="COMPLETED",
        now=NOW - timedelta(days=30),
    )
    plan = retention_plan(root, policy=policy, now=NOW)

    result = apply_retention(root, policy=policy, plan=plan)

    assert result["mode"] == "apply"
    assert result["movedCount"] == 1
    assert not (root / ".qualification_runs" / expired_id).exists()
    archived = root / ".cleanup_archive" / "qualification-runs" / expired_id
    assert archived.is_dir()
    assert (archived / "run-manifest.json").is_file()
    assert (archived / "postgresql").is_dir()
    assert (archived / "minio").is_dir()


def test_apply_revalidates_and_rejects_run_that_became_active(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    run_id = "qual-20260801T120000Z-00000006"
    create_run(root, policy=policy, run_id=run_id, now=NOW - timedelta(days=60))
    finish_run(
        root,
        policy=policy,
        run_id=run_id,
        status="FAILED",
        now=NOW - timedelta(days=30),
    )
    plan = retention_plan(root, policy=policy, now=NOW)
    marker = root / ".qualification_runs" / run_id / ".active.json"
    marker.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="no longer retention eligible"):
        apply_retention(root, policy=policy, plan=plan)

    assert (root / ".qualification_runs" / run_id).is_dir()


def test_finish_fails_before_mutating_manifest_when_active_marker_is_missing(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    run_id = "qual-20260905T120000Z-00000007"
    create_run(root, policy=policy, run_id=run_id, now=NOW)
    run_directory = root / ".qualification_runs" / run_id
    (run_directory / ".active.json").unlink()

    with pytest.raises(ValueError, match="marker is missing"):
        finish_run(
            root,
            policy=policy,
            run_id=run_id,
            status="FAILED",
            now=NOW + timedelta(minutes=1),
        )

    manifest = json.loads(
        (run_directory / "run-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "ACTIVE"
    assert manifest["completedAt"] is None


def test_malformed_or_identity_mismatched_runs_fail_closed(
    tmp_path: Path,
) -> None:
    root = _root(tmp_path)
    policy = load_policy()
    malformed = root / ".qualification_runs" / "not-a-run-id"
    malformed.mkdir(parents=True)
    (malformed / "run-manifest.json").write_text(
        json.dumps(
            {
                "schemaVersion": "mdi.qualification-run/1.0",
                "runId": "qual-20260801T120000Z-deadbeef",
            }
        ),
        encoding="utf-8",
    )

    plan = retention_plan(root, policy=policy, now=NOW)

    assert plan["candidateCount"] == 0
    assert plan["protected"]["invalid"] == ["not-a-run-id"]


def test_cli_defaults_to_read_only_retention_plan(tmp_path: Path) -> None:
    root = _root(tmp_path)
    script = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "qualification_run_retention.py"
    )

    completed = subprocess.run(
        [sys.executable, str(script), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["candidateCount"] == 0
    assert not (root / ".qualification_runs").exists()
    assert not (root / ".cleanup_archive").exists()
