param(
  [ValidatePattern("^[A-Za-z0-9_-]*$")]
  [string]$WorkerGeneration = "",
  [string[]]$OnlyQueue = @()
)

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
if (-not $env:MDI_RELEASE_SHA) {
  $env:MDI_RELEASE_SHA = (& git.exe -C $repo rev-parse HEAD).Trim()
}
$diskPreflightOutput = & powershell.exe `
  -NoProfile `
  -ExecutionPolicy Bypass `
  -File (Join-Path $repo "scripts\phase14r_disk_preflight.ps1") `
  -CheckPath $repo
$diskPreflightExitCode = $LASTEXITCODE
if ($diskPreflightExitCode -ne 0) {
  throw "MDI_DISK_PREFLIGHT_FAILED(exit=$diskPreflightExitCode): $($diskPreflightOutput -join '')"
}
$runtimeEnvironmentJson = & python.exe `
  (Join-Path $repo "scripts\phase14r_runtime_environment.py") `
  --compact
if ($LASTEXITCODE -ne 0) {
  throw "MDI_RUNTIME_ENVIRONMENT_FAILED(exit=$LASTEXITCODE)"
}
$runtimeEnvironment = $runtimeEnvironmentJson | ConvertFrom-Json
foreach ($property in $runtimeEnvironment.PSObject.Properties) {
  Set-Item -Path "Env:$($property.Name)" -Value ([string]$property.Value)
}
$redisUrl = [string]$runtimeEnvironment.REDIS_URL
$env:PYTHONPATH = @(
  (Join-Path $repo "apps/api"),
  (Join-Path $repo "packages/schemas"),
  (Join-Path $repo "packages/tool-registry"),
  (Join-Path $repo "packages/adapters"),
  (Join-Path $repo "packages/artifact-core"),
  (Join-Path $repo "packages/material-parsers"),
  (Join-Path $repo "services/workers"),
  (Join-Path $repo "services/llm")
) -join [IO.Path]::PathSeparator

$queueManifestJson = & python.exe -m mdi_schemas.worker_queues
if ($LASTEXITCODE -ne 0) {
  throw "MDI_WORKER_QUEUE_MANIFEST_FAILED(exit=$LASTEXITCODE)"
}
$queueManifest = $queueManifestJson | ConvertFrom-Json
$queues = @($queueManifest.queues | ForEach-Object { [string]$_.name })
if ($queues.Count -eq 0 -or $queues.Count -ne (@($queues | Select-Object -Unique)).Count) {
  throw "MDI_WORKER_QUEUE_MANIFEST_INVALID"
}

$requestedQueues = if ($OnlyQueue.Count -gt 0) {
  @($OnlyQueue | ForEach-Object { [string]$_.Trim() } | Where-Object { $_ })
} else {
  @($queues)
}
$unknownQueues = @($requestedQueues | Where-Object { $_ -notin $queues })
if ($unknownQueues.Count -gt 0) {
  throw "MDI_WORKER_QUEUE_NOT_IN_MANIFEST: $($unknownQueues -join ',')"
}

foreach ($queue in @($requestedQueues | Select-Object -Unique)) {
  $safeName = $queue -replace "[^A-Za-z0-9_-]", "-"
  $generationSuffix = if ($WorkerGeneration) { "-$WorkerGeneration" } else { "" }
  Start-Process -FilePath "python.exe" `
    -ArgumentList @(
      "scripts/phase14r_log_runner.py",
      "--stdout-log", ".phase14r-worker-$safeName$generationSuffix.out.log",
      "--stderr-log", ".phase14r-worker-$safeName$generationSuffix.err.log",
      "--",
      "python.exe", "-m", "mdi_workers.worker_entrypoint",
      $queue,
      "--url", $redisUrl,
      "--name", "phase14r-$safeName$generationSuffix"
    ) `
    -WorkingDirectory $repo `
    -WindowStyle Hidden
}

& powershell.exe `
  -NoProfile `
  -ExecutionPolicy Bypass `
  -File (Join-Path $repo "scripts\phase14r_discover_workers.ps1") `
  -TimeoutSeconds 20 | Out-Null
