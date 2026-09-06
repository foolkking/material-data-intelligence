from __future__ import annotations

import os
import json
import subprocess
import sys
from pathlib import Path

from scripts.repo_safe_cleanup import (
    apply_cleanup,
    classify_workspace,
    plan_cleanup,
)


def _old(path: Path, now: float) -> None:
    path.touch()
    os.utime(path, (now - 90 * 86400, now - 90 * 86400))


def test_cleanup_is_allowlisted_dry_run_and_archives_only_managed_files(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    old_temp = tmp_path / ".tmp-owned.json"
    old_pytest = tmp_path / ".pytest_tmp" / "worker" / "intermediate.txt"
    old_log = tmp_path / ".managed_logs" / "worker.log"
    protected_log = tmp_path / ".phase14r-api-8005.out.log"
    protected_db = tmp_path / "mdi_phase5.db"
    for path in (old_temp, old_pytest, old_log, protected_log, protected_db):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x", encoding="utf-8")
    now = 2_000_000_000.0
    for path in (old_temp, old_pytest, old_log, protected_log, protected_db):
        os.utime(path, (now - 90 * 86400, now - 90 * 86400))

    candidates = plan_cleanup(tmp_path, older_than_days=30, now=now)
    assert [(item.kind, item.path) for item in candidates] == [
        ("expired_log", ".managed_logs/worker.log"),
        ("temporary", ".pytest_tmp/worker/intermediate.txt"),
        ("temporary", ".tmp-owned.json"),
    ]
    assert not (tmp_path / ".cleanup_archive").exists()
    apply_cleanup(tmp_path, candidates)
    assert not old_temp.exists() and not old_pytest.exists() and not old_log.exists()
    assert (tmp_path / ".cleanup_archive/.tmp-owned.json").exists()
    assert (tmp_path / ".cleanup_archive/.pytest_tmp/worker/intermediate.txt").exists()
    assert (tmp_path / ".cleanup_archive/.managed_logs/worker.log").exists()
    assert protected_log.exists() and protected_db.exists()


def test_cleanup_rejects_symlinks_and_recent_files(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    recent = tmp_path / ".tmp-recent.json"
    recent.write_text("x", encoding="utf-8")
    (tmp_path / ".managed_logs").mkdir()
    link = tmp_path / ".managed_logs" / "link.log"
    try:
        link.symlink_to(recent)
    except OSError:
        # Windows CI may not grant unprivileged symlink creation; the regular
        # recent-file safety assertion still exercises the same plan.
        assert plan_cleanup(tmp_path, older_than_days=30, now=recent.stat().st_mtime + 60) == []
        return
    candidates = plan_cleanup(tmp_path, older_than_days=30, now=recent.stat().st_mtime + 60)
    assert candidates == []


def test_dry_run_classifies_temporary_evidence_active_data_and_archive(
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    recent = tmp_path / ".tmp-recent.json"
    evidence = tmp_path / "docs" / "phase" / "evidence"
    service_data = tmp_path / ".phase14r-minio-fresh"
    runtime_manifest = (
        tmp_path / ".runtime_services" / "managed" / "api" / "api-8005.json"
    )
    runtime_log = tmp_path / ".phase14r-api-8005.out.log"
    archived = tmp_path / ".cleanup_archive" / "previous-build"
    recent.write_text("recent", encoding="utf-8")
    evidence.mkdir(parents=True)
    service_data.mkdir()
    runtime_manifest.parent.mkdir(parents=True)
    runtime_manifest.write_text('{"status":"RUNNING"}', encoding="utf-8")
    runtime_log.write_text("active", encoding="utf-8")
    archived.mkdir(parents=True)

    candidates = plan_cleanup(
        tmp_path,
        older_than_days=30,
        now=recent.stat().st_mtime + 60,
    )
    classification = classify_workspace(
        tmp_path,
        candidates=candidates,
        older_than_days=30,
        now=recent.stat().st_mtime + 60,
    )

    assert classification["retainedTemporary"]["paths"] == [
        ".tmp-recent.json"
    ]
    assert classification["protectedReleaseEvidence"]["paths"] == [
        "docs/phase/evidence"
    ]
    assert classification["protectedActiveServiceData"]["paths"] == [
        ".phase14r-minio-fresh",
        ".runtime_services",
    ]
    assert runtime_manifest.exists()
    assert classification["protectedRuntimeLogs"]["paths"] == [
        ".phase14r-api-8005.out.log"
    ]
    assert classification["recoverableCleanupArchive"]["paths"] == [
        "previous-build"
    ]


def test_cli_accepts_explicit_dry_run_and_does_not_modify_workspace(
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    temporary = tmp_path / ".tmp-old.json"
    temporary.write_text("old", encoding="utf-8")
    os.utime(temporary, (1, 1))

    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "repo_safe_cleanup.py"),
            "--root",
            str(tmp_path),
            "--older-than-days",
            "0",
            "--dry-run",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["candidateCount"] == 1
    assert temporary.exists()
    assert not (tmp_path / ".cleanup_archive").exists()
