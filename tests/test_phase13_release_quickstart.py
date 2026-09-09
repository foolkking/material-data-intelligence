from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


ROOT = Path(__file__).resolve().parents[1]
QUICKSTART = ROOT / "docs" / "phase13" / "release" / "quick-start.md"
START_STACK = ROOT / "scripts" / "phase14r_start_stack.ps1"
START_FRONTEND = ROOT / "scripts" / "phase14r_frontend_start.mjs"
ROTATE_FRONTEND = ROOT / "scripts" / "phase14r_rotate_frontend.ps1"


def test_repository_entry_points_link_to_the_canonical_quickstart():
    expected_targets = {
        ROOT / "README.md": "docs/phase13/release/quick-start.md",
        ROOT / "docs" / "index.md": "phase13/release/quick-start.md",
        ROOT / "docs" / "phase13" / "release" / "README.md": "quick-start.md",
    }

    for entry_point, target in expected_targets.items():
        assert target in entry_point.read_text(encoding="utf-8")


def test_windows_quickstart_uses_one_locked_same_stack_launch_path():
    source = QUICKSTART.read_text(encoding="utf-8")
    prose = " ".join(source.split())

    ordered_steps = (
        "uv sync --frozen --extra test",
        "npm --prefix apps/web ci",
        '$env:MDI_NEXT_DIST_DIR = ".cache/next-production"',
        '$env:MDI_API_PROXY_TARGET = "http://127.0.0.1:8005"',
        "$env:MDI_RELEASE_SHA = (git rev-parse HEAD).Trim()",
        "npm --prefix apps/web run build",
        "uv run python -m alembic -c apps/api/alembic.ini upgrade head",
        "-File scripts/phase14r_start_stack.ps1 -FrontendPort 3023",
    )
    positions = tuple(source.index(step) for step in ordered_steps)
    assert positions == tuple(sorted(positions))

    assert source.count(
        "-File scripts/phase14r_start_stack.ps1 -FrontendPort 3023"
    ) == 2
    assert "uv run uvicorn" not in source
    assert "npm --prefix apps/web run dev" not in source
    assert "starts only missing processes" in prose
    assert "never replaces an existing listener" in prose
    assert "checked-in `uv.lock`" in prose
    assert "`apps/web/package-lock.json`" in prose


def test_windows_quickstart_matches_checked_in_ports_and_production_build():
    source = QUICKSTART.read_text(encoding="utf-8")
    stack = START_STACK.read_text(encoding="utf-8")
    frontend = START_FRONTEND.read_text(encoding="utf-8")

    for endpoint in (
        "127.0.0.1:55434/mdi",
        "127.0.0.1:6379/13",
        "http://127.0.0.1:9000",
        "http://127.0.0.1:8005",
        "http://127.0.0.1:3023",
    ):
        assert endpoint in source

    for port in ("55434", "6379", "9000", "8005"):
        assert port in stack
    assert "[int]$FrontendPort = 3023" in stack
    assert 'process.env.MDI_NEXT_DIST_DIR || ".cache/next-production"' in frontend
    assert "`http://127.0.0.1:8005/health/runtime`" in source
    assert "http://127.0.0.1:$FrontendPort/api/health/runtime" in stack
    assert "frontendProxyRuntime" in stack


def test_windows_quickstart_uses_current_alembic_head_without_stale_pin():
    source = QUICKSTART.read_text(encoding="utf-8")
    config = Config(str(ROOT / "apps" / "api" / "alembic.ini"))
    config.set_main_option(
        "script_location", str(ROOT / "apps" / "api" / "alembic")
    )
    heads = ScriptDirectory.from_config(config).get_heads()

    assert len(heads) == 1
    assert "upgrade head" in source
    assert "alembic.ini current" in source
    assert "alembic.ini heads" in source
    assert "0007_phase10m1_workspace_domain" not in source


def test_windows_quickstart_preserves_services_and_scopes_old_frontend_cleanup():
    source = QUICKSTART.read_text(encoding="utf-8")
    rotation = ROTATE_FRONTEND.read_text(encoding="utf-8")

    dry_run = "-File scripts/phase14r_rotate_frontend.ps1 -CurrentPort 3023"
    apply = (
        "-File scripts/phase14r_rotate_frontend.ps1 "
        "-CurrentPort 3023 -Apply -Confirm"
    )
    assert source.index(dry_run) < source.index(apply)
    assert "leave PostgreSQL, Redis, MinIO, API, workers" in source
    assert "Never use `docker compose down -v`" in source
    assert "[CmdletBinding(SupportsShouldProcess = $true)]" in rotation
    assert "NOT_REPOSITORY_NEXT_START" in rotation
    assert "Test-FrontendHealth $CurrentPort" in rotation

    for forbidden in ("taskkill /", "Stop-Process -Name", "docker compose down -v\n"):
        assert forbidden not in source
