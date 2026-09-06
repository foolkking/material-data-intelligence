from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "scripts" / "phase14r_start_api.ps1"
ROTATE = ROOT / "scripts" / "phase14r_rotate_api.ps1"
PATHS = ROOT / "scripts" / "phase14r_runtime_paths.ps1"
DISCOVER_WORKERS = ROOT / "scripts" / "phase14r_discover_workers.ps1"


def test_api_start_is_health_gated_and_writes_atomic_owned_instance_manifest() -> None:
    source = START.read_text(encoding="utf-8")
    paths = PATHS.read_text(encoding="utf-8")

    assert "API_PORT_ALREADY_IN_USE" in source
    assert "-PassThru" in source
    assert "-WindowStyle Hidden" in source
    assert "Wait-ApiHealth $Port" in source
    assert "phase14r-api-instance/1.1" in source
    assert "repositoryToken" in source
    assert "releaseSha" in source
    assert "runnerPid" in source and "childPid" in source
    assert "runnerCreatedAt" in source and "childCreatedAt" in source
    assert "runnerCreationFileTimeUtc" in source
    assert "childCreationFileTimeUtc" in source
    assert "runnerCommandDigest" in source and "childCommandDigest" in source
    assert "$temporaryManifest" in source
    assert "Move-Item" in source
    assert "-LiteralPath $temporaryManifest" in source
    assert "$runnerPath" in source
    assert "$stdoutLog" in source and "$stderrLog" in source
    assert "ConvertTo-ProcessArgument" in source
    assert "API_PROCESS_ARGUMENT_CONTAINS_QUOTE" in source
    assert "phase14r_runtime_paths.ps1" in source
    assert "Get-MdiApiRuntimeDirectory $repo" in source
    assert '".runtime_services\\managed"' in paths
    assert '"api"' in paths


def test_worker_discovery_records_exact_queue_process_identity() -> None:
    source = DISCOVER_WORKERS.read_text(encoding="utf-8")
    paths = PATHS.read_text(encoding="utf-8")

    for token in (
        "phase14r-worker-instance/1.0",
        "runnerPid",
        "runnerCreationFileTimeUtc",
        "runnerCommandDigest",
        "childPid",
        "childCreationFileTimeUtc",
        "childCommandDigest",
        "redisIdentity",
        "Get-RedactedRedisIdentity",
        'status = "RUNNING"',
        'updated["status"] = "MISSING"',
        'updated["lastSeenAt"]',
        'updated["staleSince"]',
        'if (-not (Test-Path -LiteralPath $path))',
        "Move-Item -LiteralPath $temporaryPath",
    ):
        assert token in source
    assert "Get-MdiWorkerRuntimeDirectory" in source
    assert "Get-MdiWorkerRuntimeDirectory" in paths
    assert "mdi_workers\\.worker_entrypoint" in source


def test_api_rotation_is_dry_run_by_default_and_requires_exact_ownership() -> None:
    source = ROTATE.read_text(encoding="utf-8")

    assert "[CmdletBinding(SupportsShouldProcess = $true" in source
    assert "[switch]$Apply" in source
    assert 'mode = "dry-run"' in source
    assert "Assert-ApiTree" in source
    assert "Assert-TreeUnchanged" in source
    assert "API_INSTANCE_MANIFEST_MISMATCH" in source
    assert "API_PROCESS_IDENTITY_DRIFT" in source
    assert "API_LEGACY_INSTANCE_REQUIRES_EXPLICIT_PID" in source
    assert "$ExpectedCanonicalPid" in source
    assert "repositoryToken" in source
    assert "CreationDate" in source
    assert "CommandDigest" in source
    assert "$checks = [ordered]@{" in source
    assert "$failedChecks" in source
    assert "Select-Object -ExpandProperty Key" in source
    assert "phase14r_runtime_paths.ps1" in source
    assert "Get-MdiApiRuntimeDirectory $repo" in source
    assert '$legacyRuntimeDirectory = Join-Path $repo ".cache\\runtime"' in source
    assert "manifestPath = [string]$manifestRecord.path" in source


def test_api_rotation_validates_shadow_before_stopping_canonical() -> None:
    source = ROTATE.read_text(encoding="utf-8")

    shadow_start = source.index("$shadowTree = Start-Api $ShadowPort")
    shadow_health = source.index("$shadowHealth = Get-ApiHealth $ShadowPort")
    old_stop = source.index(
        'Stop-ApiTree $currentTree "Replace canonical API after shadow validation"'
    )
    canonical_start = source.index("$newCanonicalTree = Start-Api $CanonicalPort")
    frontend_health = source.index(
        '$frontendHealth = Get-ApiHealth $FrontendPort "/api/health/runtime"'
    )
    shadow_stop = source.index(
        'Stop-ApiTree $shadowTree "Remove validated shadow after canonical cutover"'
    )

    assert shadow_start < shadow_health < old_stop < canonical_start
    assert canonical_start < frontend_health < shadow_stop
    assert "runtimeConfiguration.fingerprint" in source
    assert "API_SHADOW_PORT_IN_USE" in source
    assert "API_ROTATION_PORTS_MUST_DIFFER" in source


def test_api_rotation_stops_only_revalidated_explicit_pids_child_first() -> None:
    source = ROTATE.read_text(encoding="utf-8")
    lowered = source.lower()
    stop_lines = [
        line.strip()
        for line in source.splitlines()
        if "Stop-Process" in line
    ]

    assert stop_lines == [
        "Stop-Process -Id $Tree.childPid -Force -ErrorAction Stop",
        "Stop-Process -Id $Tree.parentPid -Force -ErrorAction Stop",
    ]
    assert source.index("Stop-Process -Id $Tree.childPid") < source.index(
        "Stop-Process -Id $Tree.parentPid"
    )
    assert "Assert-TreeUnchanged $Tree" in source
    assert "Assert-RunnerUnchanged $Tree" in source
    assert "$manifestPath = [string]$Tree.manifestPath" in source
    assert "Remove-Item -LiteralPath $manifestPath -Force" in source
    assert "Stop-Process -Name" not in source
    assert "taskkill" not in lowered
    for forbidden in ("postgres.exe", "memurai.exe", "minio.exe", "mdi_workers"):
        assert forbidden not in lowered


def test_api_rotation_failure_policy_does_not_kill_unknown_processes() -> None:
    source = ROTATE.read_text(encoding="utf-8")

    assert "Unknown processes are never stopped by cleanup." in source
    assert "if (-not $canonicalStopped)" in source
    assert "Stop-NewShadowOnFailure" in source
    assert "A healthy owned shadow is deliberately retained" in source
    assert "API_FRONTEND_PROXY_FINGERPRINT_MISMATCH" in source
    assert "API_SHADOW_PORT_DID_NOT_CLOSE" in source
