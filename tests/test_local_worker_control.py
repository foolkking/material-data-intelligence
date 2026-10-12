from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import socket
import shutil
import subprocess
import sys
import time
from uuid import uuid4

import pytest
from redis import Redis
from rq import Queue, Worker

from mdi_workers.local_control import inspect_worker, set_drain


def _complete_after_release(entered: str, release: str, completed: str):
    Path(entered).write_text("entered")
    deadline = time.monotonic() + 20
    while not Path(release).exists():
        if time.monotonic() > deadline:
            raise RuntimeError("Test release timeout")
        time.sleep(0.02)
    Path(completed).write_text("complete")
    return "finished"


def _wait(predicate, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(0.05)
    raise AssertionError("Test worker did not reach the expected state")


@pytest.fixture
def redis_connection():
    url = os.getenv("MDI_TEST_REDIS_URL")
    if not url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required")
    connection = Redis.from_url(url)
    yield connection, url
    connection.close()


@pytest.mark.integration
@pytest.mark.parametrize("busy,withdraw", [(False, False), (True, False), (True, True)])
def test_local_worker_drain_preserves_work_and_unregisters(redis_connection, tmp_path, busy, withdraw):
    connection, url = redis_connection
    name = f"mdi-test-local-control-{uuid4().hex}"
    queue = Queue(name, connection=connection)
    job = None
    entered, release, completed = [tmp_path / part for part in ("entered", "release", "completed")]
    if busy:
        job = queue.enqueue(_complete_after_release, str(entered), str(release), str(completed), job_timeout=30)
    before = datetime.now(timezone.utc) - timedelta(seconds=1)
    environment = {**os.environ, "MDI_RUNTIME_PROFILE": "local", "MDI_ENV": "test",
        "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    process = subprocess.Popen([sys.executable, "-m", "mdi_workers.worker_entrypoint", name,
        "--url", url, "--name", name, "--local-control", "--logging-level", "CRITICAL"],
        cwd=Path(__file__).resolve().parents[1], env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        registration = _wait(lambda: connection.hgetall(f"rq:worker:{name}"))
        pid = int(registration[b"pid"])
        health = _wait(lambda: (data if (data := inspect_worker(connection, name, [pid], [name], before))["ready"] else None))
        assert not health["draining"]
        if busy:
            _wait(entered.exists)
            health = inspect_worker(connection, name, [pid], [name], before)
            assert health["state"] == "busy"
        assert set_drain(connection, name, health, True)
        if busy:
            assert process.poll() is None and not completed.exists()
            assert job.get_status(refresh=True).value == "started"
            if withdraw:
                assert set_drain(connection, name, health, False)
            release.write_text("release")
            if withdraw:
                _wait(lambda: job.get_status(refresh=True).value == "finished")
                assert process.poll() is None
                current = inspect_worker(connection, name, [pid], [name], before)
                assert current["ready"] and not current["draining"]
                assert set_drain(connection, name, current, True)
        stdout, stderr = process.communicate(timeout=15)
        assert process.returncode == 0, stderr[-2000:]
        assert inspect_worker(connection, name, [pid], [name], before) == {"ready": False, "reason": "not_registered"}
        assert connection.hget(f"rq:worker:{name}", "death")
        if busy:
            job.refresh()
            assert job.is_finished and job.return_value() == "finished" and completed.read_text() == "complete"
    finally:
        release.write_text("release")
        if process.poll() is None:
            record = connection.hgetall(f"rq:worker:{name}")
            if record.get(b"pid") and record.get(b"birth"):
                set_drain(connection, name, {"pid": int(record[b"pid"]), "birth": record[b"birth"].decode()}, True)
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate(timeout=5)
        if job is not None:
            queue.remove(job.id)
            job.delete()
        queue.delete()
        worker = Worker.find_by_key(f"rq:worker:{name}", connection=connection)
        if worker:
            worker.register_death()


@pytest.mark.integration
def test_worker_probe_and_drain_refuse_foreign_or_replaced_identity(redis_connection):
    connection, _ = redis_connection
    name = f"mdi-test-local-control-{uuid4().hex}"
    key = f"rq:worker:{name}"
    birth = datetime.now(timezone.utc)
    row = {"pid": "999999", "birth": birth.isoformat(), "last_heartbeat": birth.isoformat(),
           "hostname": socket.gethostname(), "queues": "owned-one,owned-two", "state": "idle"}
    connection.hset(key, mapping=row)
    connection.expire(key, 60)
    try:
        args = (connection, name, [999999], ["owned-one", "owned-two"], birth - timedelta(seconds=1))
        health = inspect_worker(*args)
        assert health["ready"]
        assert not inspect_worker(connection, name, [111], args[3], args[4])["ready"]
        assert not inspect_worker(connection, name, args[2], ["foreign"], args[4])["ready"]
        assert not inspect_worker(connection, name, args[2], args[3], birth + timedelta(seconds=1))["ready"]
        # PID reuse must not permit a drain to touch a newer registration.
        connection.hset(key, "birth", (birth + timedelta(seconds=2)).isoformat())
        assert not set_drain(connection, name, health, True)
        assert connection.hget(key, "mdi_drain") is None
        connection.hset(key, "hostname", "a-different-host")
        assert not inspect_worker(*args)["ready"]
    finally:
        connection.delete(key)


@pytest.mark.skipif(os.name != "nt", reason="Windows project controller")
@pytest.mark.parametrize("scenario", ["reused_pid", "foreign_executable", "busy", "app_scope", "windows_launchers", "unowned_listener", "custom_ports"])
def test_powershell_controller_ownership_and_restart_scope(tmp_path, scenario):
    shell = shutil.which("pwsh")
    if not shell:
        pytest.skip("PowerShell 7 required")
    script = tmp_path / "controller-test.ps1"
    script.write_text(r'''
$ErrorActionPreference = 'Stop'
$tokens = $null; $parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($args[0], [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'Controller parse failure' }
$functions = $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)
Invoke-Expression (($functions | ForEach-Object { $_.Extent.Text }) -join "`n")
$Repo = 'C:\owned-repo'; $LocalRoot = 'C:\owned-data'
$stamp = [datetimeoffset]::UtcNow
$entry = [pscustomobject]@{ pid = 123456; startedAt = $stamp.ToString('o'); file = 'C:\owned-python.exe'; cwd = $Repo; localControl = $true }
$api = [pscustomobject]@{ pid = 123457; startedAt = $stamp.ToString('o'); file = 'C:\owned-python.exe'; cwd = $Repo }
$script:fakeState = [pscustomobject]@{localRoot = $LocalRoot; services = [pscustomobject]@{worker = $entry; api = $api}}
$script:fakeProcess = [pscustomobject]@{ProcessId = $entry.pid; ExecutablePath = $entry.file; CreationDate = $stamp; CommandLine = '-m mdi_workers.worker_entrypoint'}
function Read-State { return $script:fakeState }
function Import-LocalEnvironment { }
function Get-CimInstance { return $script:fakeProcess }
function Get-Process { throw 'Unexpected process access' }
$scenario = $args[1]
if ($scenario -eq 'unowned_listener') {
  function Get-NetTCPConnection { return [pscustomobject]@{OwningProcess=777} }
  try { Assert-OwnedListener 'api' 18005 $null; throw 'Foreign listener accepted' }
  catch { if ($_.Exception.Message -notlike '*without a project ownership record*') { throw } }
} elseif ($scenario -eq 'custom_ports') {
  $env:POSTGRES_PORT='25434'; $env:MDI_POSTGRES_PORT='25434'
  $env:MDI_WEB_PORT='13023'; $env:MDI_API_PROXY_TARGET='http://127.0.0.1:18005'
  if ((Get-PostgresPort) -ne 25434 -or (Get-ServicePort 'frontend') -ne 13023 -or (Get-ServicePort 'api') -ne 18005) {
    throw 'Configured ports ignored'
  }
  $env:POSTGRES_PORT='99999'
  try { Get-PostgresPort; throw 'Invalid port accepted' }
  catch { if ($_.Exception.Message -notlike 'Invalid port for postgres*') { throw } }
} elseif ($scenario -eq 'windows_launchers') {
  function Resolve-NpmBinary { return 'C:\node\npm.cmd' }
  $entry.file = 'C:/owned/minio.exe'; $script:fakeProcess.ExecutablePath = 'C:\owned\minio.exe'
  if (-not (Test-RecordedExecutable $entry $script:fakeProcess 'minio')) { throw 'Equivalent executable path rejected' }
  $entry.file = 'C:\node\npm.cmd'; $script:fakeProcess.ExecutablePath = Join-Path $env:SystemRoot 'System32\cmd.exe'
  $script:fakeProcess.CommandLine = $script:fakeProcess.ExecutablePath + ' /c ""C:\node\npm.cmd" --prefix apps/web run dev -- -p 3023 -H 127.0.0.1"'
  if (-not (Test-RecordedExecutable $entry $script:fakeProcess 'frontend')) { throw 'Owned npm launcher rejected' }
  $script:fakeProcess.CommandLine += ' & echo unrelated'
  if (Test-RecordedExecutable $entry $script:fakeProcess 'frontend') { throw 'Unrelated shell command accepted' }
} elseif ($scenario -eq 'reused_pid' -or $scenario -eq 'foreign_executable') {
  if ($scenario -eq 'reused_pid') { $script:fakeProcess.CreationDate = $stamp.AddSeconds(10) }
  else { $script:fakeProcess.ExecutablePath = 'C:\foreign.exe' }
  try { Stop-OwnedTree $entry.pid $Repo; throw 'Unsafe ownership accepted' }
  catch { if ($_.Exception.Message -notlike 'Process identity changed*') { throw } }
} else {
  $script:starts = 0; $script:stops = @(); $script:actions = @()
  function Start-Stack { $script:starts++ }
  function Stop-OwnedTree($id, $cwd) { $script:stops += $id }
  function Read-WorkerHealth($entry, $action = 'probe') {
    $script:actions += $action
    return [pscustomobject]@{ready = $true; state = $(if ($scenario -eq 'busy') {'busy'} else {'idle'})}
  }
  function Wait-Port { }
  function Get-Process { return $null }
  $script:fakeProcess = [pscustomobject]@{ProcessId = $api.pid; ExecutablePath = $api.file; CreationDate = $stamp; CommandLine = '-m uvicorn mdi_api.main:app'}
  if ($scenario -eq 'busy') {
    try { Restart-AppServices; throw 'Busy worker was accepted' }
    catch { if ($_.Exception.Message -notlike 'Worker is not verified idle*') { throw } }
    if ($script:starts -ne 0 -or $script:stops.Count -ne 0 -or $script:actions -contains 'drain') { throw 'Busy work changed' }
  } else {
    Restart-AppServices
    if ($script:starts -ne 1 -or $script:stops.Count -ne 1 -or $script:stops[0] -ne $api.pid -or ($script:actions -join ',') -ne 'probe,drain') { throw 'Unexpected restart scope' }
  }
}
'passed'
''', encoding="utf-8")
    child = subprocess.run([shell, "-NoProfile", "-File", str(script),
        str(Path(__file__).resolve().parents[1] / "scripts" / "dev.ps1"), scenario],
        capture_output=True, text=True, encoding="utf-8", timeout=20)
    assert child.returncode == 0, child.stderr[-3000:]
    assert child.stdout.strip() == "passed"
