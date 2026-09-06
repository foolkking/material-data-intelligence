from __future__ import annotations

import importlib.util
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase14r_log_runner.py"
SPEC = importlib.util.spec_from_file_location("phase14r_log_runner", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
LOG_RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LOG_RUNNER
SPEC.loader.exec_module(LOG_RUNNER)


def test_size_and_time_rotation_keep_the_active_log(tmp_path: Path) -> None:
    active = tmp_path / ".phase14r-api.out.log"
    policy = LOG_RUNNER.RotationPolicy(
        max_bytes=16, max_archives=8, max_age_days=14
    )
    day_one = datetime(2026, 9, 5, 10, tzinfo=UTC)
    day_two = datetime(2026, 9, 6, 10, tzinfo=UTC)

    with LOG_RUNNER.RotatingLogStream(active, policy) as stream:
        stream.write("1234567890\n", now=day_one)
        stream.write("abcdefghij\n", now=day_one)
        stream.write("next-day\n", now=day_two)

    archives = sorted(tmp_path.glob(".phase14r-api.out.*.log"))
    assert active.read_text(encoding="utf-8") == "next-day\n"
    assert len(archives) == 2
    assert archives[0].read_text(encoding="utf-8") == "1234567890\n"
    assert archives[1].read_text(encoding="utf-8") == "abcdefghij\n"


def test_retention_dry_run_never_deletes_active_log(
    tmp_path: Path,
) -> None:
    active = tmp_path / ".phase14r-worker.out.log"
    active.write_text("active", encoding="utf-8")
    now = datetime(2026, 9, 5, 12, tzinfo=UTC)
    archives = []
    for index in range(4):
        archive = tmp_path / (
            f".phase14r-worker.out.2026080{index + 1}T000000Z.0001.log"
        )
        archive.write_text(str(index), encoding="utf-8")
        old_time = (now - timedelta(days=30 + index)).timestamp()
        os.utime(archive, (old_time, old_time))
        archives.append(archive)
    policy = LOG_RUNNER.RotationPolicy(
        max_bytes=1024, max_archives=2, max_age_days=14
    )

    planned = LOG_RUNNER.apply_retention(
        active, policy, dry_run=True, now=now
    )

    assert set(planned) == set(archives)
    assert active.read_text(encoding="utf-8") == "active"
    assert all(path.exists() for path in archives)

    removed = LOG_RUNNER.apply_retention(
        active, policy, dry_run=False, now=now
    )
    assert set(removed) == set(archives)
    assert active.read_text(encoding="utf-8") == "active"
    assert not any(path.exists() for path in archives)


def test_retention_count_is_bounded_and_ignores_unmanaged_files(
    tmp_path: Path,
) -> None:
    active = tmp_path / ".phase14r-frontend.out.log"
    active.write_text("active", encoding="utf-8")
    unmanaged = tmp_path / ".phase14r-frontend.out.manual-copy.log"
    unmanaged.write_text("keep", encoding="utf-8")
    now = datetime(2026, 9, 5, 12, tzinfo=UTC)
    archives = []
    for index in range(4):
        archive = tmp_path / (
            f".phase14r-frontend.out.20260905T00000{index}Z.0001.log"
        )
        archive.write_text(str(index), encoding="utf-8")
        timestamp = (now - timedelta(minutes=4 - index)).timestamp()
        os.utime(archive, (timestamp, timestamp))
        archives.append(archive)
    policy = LOG_RUNNER.RotationPolicy(
        max_bytes=1024, max_archives=2, max_age_days=14
    )

    removed = LOG_RUNNER.apply_retention(
        active, policy, dry_run=False, now=now
    )

    assert set(removed) == set(archives[:2])
    assert active.read_text(encoding="utf-8") == "active"
    assert unmanaged.read_text(encoding="utf-8") == "keep"
    assert all(path.exists() for path in archives[2:])


def test_command_runner_captures_both_streams(tmp_path: Path) -> None:
    stdout_log = tmp_path / "service.out.log"
    stderr_log = tmp_path / "service.err.log"
    policy = LOG_RUNNER.RotationPolicy(
        max_bytes=1024, max_archives=2, max_age_days=14
    )

    exit_code = LOG_RUNNER.run_command(
        [
            sys.executable,
            "-c",
            "import sys; print('ready'); print('warning', file=sys.stderr)",
        ],
        stdout_log,
        stderr_log,
        policy,
    )

    assert exit_code == 0
    assert stdout_log.read_text(encoding="utf-8") == "ready\n"
    assert stderr_log.read_text(encoding="utf-8") == "warning\n"


def test_api_worker_and_frontend_use_the_bounded_log_runner() -> None:
    api = (ROOT / "scripts" / "phase14r_start_api.ps1").read_text(
        encoding="utf-8"
    )
    workers = (
        ROOT / "scripts" / "phase14r_start_workers.ps1"
    ).read_text(encoding="utf-8")
    stack = (ROOT / "scripts" / "phase14r_start_stack.ps1").read_text(
        encoding="utf-8"
    )

    for source in (api, workers, stack):
        assert "phase14r_log_runner.py" in source
        assert "--stdout-log" in source
        assert "--stderr-log" in source
    assert ".phase14r-api-$Port.out.log" in api
    assert ".phase14r-api-$Port.err.log" in api
    assert ".phase14r-worker-$safeName$generationSuffix.out.log" in workers
    assert ".phase14r-worker-$safeName$generationSuffix.err.log" in workers
    assert ".phase14r-frontend-$FrontendPort.out.log" in stack
