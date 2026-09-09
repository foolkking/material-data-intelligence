[CmdletBinding()]
param(
  [int]$FrontendPort = 3023,
  [int]$TimeoutSeconds = 45,
  [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

function Assert-DiskPreflight {
  $output = & powershell.exe `
    -NoProfile `
    -ExecutionPolicy Bypass `
    -File (Join-Path $repo "scripts\phase14r_disk_preflight.ps1") `
    -CheckPath $repo
  $exitCode = $LASTEXITCODE
  if ($exitCode -ne 0) {
    throw "MDI_DISK_PREFLIGHT_FAILED(exit=$exitCode): $($output -join '')"
  }
  return ($output -join "" | ConvertFrom-Json)
}

function Test-TcpPort([string]$HostName, [int]$Port) {
  try {
    return [bool](Test-NetConnection -ComputerName $HostName -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)
  } catch {
    return $false
  }
}

function Wait-TcpPort([string]$HostName, [int]$Port, [string]$Label) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    if (Test-TcpPort $HostName $Port) { return }
    Start-Sleep -Milliseconds 500
  } while ((Get-Date) -lt $deadline)
  throw "$Label did not become ready on $HostName`:$Port within $TimeoutSeconds seconds."
}

function Test-ProcessPattern([string]$Pattern) {
  try {
    return $null -ne (Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction Stop |
      Where-Object { $_.CommandLine -like "*$Pattern*" } |
      Select-Object -First 1)
  } catch {
    return $false
  }
}

function Get-ConfiguredWorkerQueues {
  $previousPythonPath = $env:PYTHONPATH
  $schemaPath = Join-Path $repo "packages\schemas"
  $env:PYTHONPATH = if ($previousPythonPath) {
    "$schemaPath$([IO.Path]::PathSeparator)$previousPythonPath"
  } else {
    $schemaPath
  }
  try {
    $json = & python.exe -m mdi_schemas.worker_queues
    if ($LASTEXITCODE -ne 0) {
      throw "MDI_WORKER_QUEUE_MANIFEST_FAILED(exit=$LASTEXITCODE)"
    }
  } finally {
    $env:PYTHONPATH = $previousPythonPath
  }
  $manifest = $json | ConvertFrom-Json
  $queues = @($manifest.queues | ForEach-Object { [string]$_.name })
  if ($queues.Count -eq 0 -or $queues.Count -ne (@($queues | Select-Object -Unique)).Count) {
    throw "MDI_WORKER_QUEUE_MANIFEST_INVALID"
  }
  return $queues
}

function Get-RunningWorkerQueues([string[]]$ExpectedQueues) {
  try {
    $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction Stop)
  } catch {
    return @()
  }
  $running = [System.Collections.Generic.List[string]]::new()
  foreach ($queue in $ExpectedQueues) {
    $escapedQueue = [regex]::Escape([string]$queue)
    $match = $processes | Where-Object {
      [string]$_.CommandLine -match (
        "mdi_workers\.worker_entrypoint\s+['`"]?" + $escapedQueue + "['`"]?(\s|$)"
      )
    } | Select-Object -First 1
    if ($null -ne $match) {
      $running.Add([string]$queue)
    }
  }
  return @($running)
}

function Start-ChildScript([string]$Path) {
  Start-Process -FilePath "powershell.exe" -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $Path
  ) -WorkingDirectory $repo -WindowStyle Hidden | Out-Null
}

$diskPreflight = Assert-DiskPreflight

if (-not $CheckOnly) {
  if (-not (Test-TcpPort "127.0.0.1" 8005)) {
    Start-ChildScript (Join-Path $repo "scripts\phase14r_start_api.ps1")
  }

  $expectedWorkerQueues = @(Get-ConfiguredWorkerQueues)
  $runningWorkerQueues = @(Get-RunningWorkerQueues $expectedWorkerQueues)
  $missingWorkerQueues = @(
    $expectedWorkerQueues | Where-Object { $_ -notin $runningWorkerQueues }
  )
  if ($missingWorkerQueues.Count -gt 0) {
    foreach ($queue in $missingWorkerQueues) {
      Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", (Join-Path $repo "scripts\phase14r_start_workers.ps1"),
        "-OnlyQueue", $queue
      ) -WorkingDirectory $repo -WindowStyle Hidden | Out-Null
    }
    & powershell.exe `
      -NoProfile `
      -ExecutionPolicy Bypass `
      -File (Join-Path $repo "scripts\phase14r_discover_workers.ps1") `
      -TimeoutSeconds $TimeoutSeconds | Out-Null
  }

  if (-not (Test-TcpPort "127.0.0.1" $FrontendPort)) {
    $previousFrontendPort = $env:MDI_FRONTEND_PORT
    $previousApiProxyTarget = $env:MDI_API_PROXY_TARGET
    $env:MDI_FRONTEND_PORT = [string]$FrontendPort
    $env:MDI_API_PROXY_TARGET = "http://127.0.0.1:8005"
    Start-Process -FilePath "python.exe" -ArgumentList @(
      "scripts/phase14r_log_runner.py",
      "--stdout-log", ".phase14r-frontend-$FrontendPort.out.log",
      "--stderr-log", ".phase14r-frontend-$FrontendPort.err.log",
      "--",
      "node.exe", "scripts/phase14r_frontend_start.mjs"
    ) `
      -WorkingDirectory $repo `
      -WindowStyle Hidden | Out-Null
    $env:MDI_FRONTEND_PORT = $previousFrontendPort
    $env:MDI_API_PROXY_TARGET = $previousApiProxyTarget
  }
}

Wait-TcpPort "127.0.0.1" 55434 "PostgreSQL"
Wait-TcpPort "127.0.0.1" 6379 "Redis"
Wait-TcpPort "127.0.0.1" 9000 "MinIO"
Wait-TcpPort "127.0.0.1" 8005 "API"
Wait-TcpPort "127.0.0.1" $FrontendPort "frontend"

$runtime = Invoke-RestMethod -Uri "http://127.0.0.1:8005/health/runtime" -Method Get
if (
  $runtime.database.backend -eq "sqlite" -or
  $runtime.redis.backend -in @("local", "unknown") -or
  $runtime.artifactStorage.backend -eq "local" -or
  $runtime.worker.backend -eq "local"
) {
  throw "Same-stack runtime check failed: $($runtime | ConvertTo-Json -Compress)"
}
$frontendRuntime = try {
  Invoke-RestMethod `
    -Uri "http://127.0.0.1:$FrontendPort/api/health/runtime" `
    -Method Get `
    -TimeoutSec 10
} catch {
  throw "Frontend API proxy check failed on port $FrontendPort`: $($_.Exception.Message)"
}
if (
  $frontendRuntime.database.backend -eq "sqlite" -or
  $frontendRuntime.redis.backend -in @("local", "unknown") -or
  $frontendRuntime.artifactStorage.backend -eq "local" -or
  $frontendRuntime.worker.backend -eq "local"
) {
  throw "Frontend API proxy runtime check failed: $($frontendRuntime | ConvertTo-Json -Compress)"
}

[pscustomobject]@{
  postgres = "127.0.0.1:55434"
  redis = "127.0.0.1:6379"
  minio = "127.0.0.1:9000"
  api = "http://127.0.0.1:8005"
  frontend = "http://127.0.0.1:$FrontendPort"
  disk = $diskPreflight
  runtime = $runtime
  frontendProxyRuntime = $frontendRuntime
} | ConvertTo-Json -Depth 8
