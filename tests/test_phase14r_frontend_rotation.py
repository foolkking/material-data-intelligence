from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase14r_rotate_frontend.ps1"


def test_frontend_rotation_is_health_gated_scoped_and_dry_run_by_default():
    source = SCRIPT.read_text(encoding="utf-8")

    assert "[CmdletBinding(SupportsShouldProcess = $true)]" in source
    assert "[switch]$Apply" in source
    assert "if (-not (Test-FrontendHealth $CurrentPort))" in source
    assert "$_ -ne $CurrentPort" in source
    assert '"apps",' in source and '"web",' in source
    assert '"node_modules",' in source and '"next"' in source
    assert "[Microsoft.Management.Infrastructure.CimInstance]$Process" in source
    assert "Test-RepositoryNextListener" in source
    assert "NOT_REPOSITORY_NEXT_START" in source
    assert "Stop-Process -Id $candidate.pid" in source
    assert 'mode = if ($Apply) { "apply" } else { "dry-run" }' in source


def test_frontend_rotation_does_not_target_backend_or_storage_processes():
    source = SCRIPT.read_text(encoding="utf-8").lower()
    stop_lines = [
        line.strip()
        for line in source.splitlines()
        if "stop-process" in line
    ]

    assert stop_lines == ["stop-process -id $candidate.pid -force -erroraction stop"]
    for forbidden in ("uvicorn", "postgres.exe", "redis-server", "minio.exe", "mdi_workers"):
        assert forbidden not in source
