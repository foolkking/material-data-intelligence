from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase14r_rotate_workers.ps1"
DISCOVERY = ROOT / "scripts" / "phase14r_discover_workers.ps1"


def test_worker_rotation_is_dry_run_by_default_and_manifest_authorized() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "[switch]$Apply" in source
    assert "[int]$TimeoutSeconds = 20" in source
    assert 'mode = if ($Apply) { "apply" } else { "dry-run" }' in source
    assert "WORKER_APPLY_REQUIRES_ONE_QUEUE" in source
    assert "WORKER_REPOSITORY_TOKEN_MISMATCH" in source
    assert "WORKER_RELEASE_SHA_MISMATCH" in source
    assert "WORKER_PARENT_MISMATCH" in source
    assert "WORKER_RUNNER_CREATION_DRIFT" in source
    assert "WORKER_CHILD_CREATION_DRIFT" in source
    assert "WORKER_RUNNER_COMMAND_DRIFT" in source
    assert "WORKER_CHILD_COMMAND_DRIFT" in source
    assert "WORKER_REDIS_IDENTITY_MISMATCH" in source
    assert "ConvertTo-ProcessArgument" in source
    assert "WORKER_PROCESS_ARGUMENT_CONTAINS_QUOTE" in source
    assert "(ConvertTo-ProcessArgument $startScript)" in source
    assert "Find-WorkerReplacement" in source
    assert '-notmatch "phase14r_log_runner\\.py"' in source
    assert "Wait-WorkerReplacement" in source
    assert "WORKER_REPLACEMENT_HEALTH_TIMEOUT" in source
    assert "Stop-VerifiedWorkerPair $target" in source
    assert "WORKER_REPLACEMENT_ROLLBACK_FAILED" in source
    assert "runnerAlive" in source and "childAlive" in source
    assert "phase14r_worker_registration.py" in source
    assert "WORKER_REGISTRATION_REDIS_URL" in source
    assert "--maximum-heartbeat-age-seconds 900" in source
    assert "registrationExitCode -eq 0" in source
    assert "Remove-WorkerRegistration" in source
    assert "--unregister" in source
    assert "WORKER_REGISTRATION_UNREGISTER_FAILED" in source
    assert "$oldPairStopped = $false" in source
    assert "$oldPairStopped = $true" in source
    assert "-and -not $oldPairStopped" in source
    assert "Stop-Process -Id ([int]$child.ProcessId)" in source
    assert "Stop-Process -Id ([int]$runner.ProcessId)" in source
    assert "phase14r_discover_workers.ps1" in source
    assert "WindowStyle Hidden" in source


def test_worker_rotation_consumes_discovery_contract_without_raw_redis_url() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    discovery = DISCOVERY.read_text(encoding="utf-8")

    assert "Get-MdiWorkerRuntimeDirectory" in source
    assert "Get-RedactedRedisIdentity" in source
    assert "redisIdentity" in source
    assert "redisUrl = $redisUrl" not in discovery
