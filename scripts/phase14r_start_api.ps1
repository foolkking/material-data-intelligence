[CmdletBinding()]
param(
  [ValidateRange(1024, 65535)]
  [int]$Port = 8005,

  [ValidateRange(5, 300)]
  [int]$TimeoutSeconds = 45,

  [ValidatePattern("^[a-f0-9]{32}$")]
  [string]$InstanceId = ([guid]::NewGuid().ToString("N"))
)

$ErrorActionPreference = "Stop"

$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
. (Join-Path $PSScriptRoot "phase14r_runtime_paths.ps1")
$python = [IO.Path]::GetFullPath(
  (Get-Command "python.exe" -ErrorAction Stop).Source
)
$runnerPath = [IO.Path]::GetFullPath(
  (Join-Path $repo "scripts\phase14r_log_runner.py")
)
$stdoutLog = [IO.Path]::GetFullPath(
  (Join-Path $repo ".phase14r-api-$Port.out.log")
)
$stderrLog = [IO.Path]::GetFullPath(
  (Join-Path $repo ".phase14r-api-$Port.err.log")
)
$runtimeDirectory = Get-MdiApiRuntimeDirectory $repo
$manifestPath = Join-Path $runtimeDirectory "api-$Port.json"

function Get-Sha256Text([string]$Value) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Value)
    return [BitConverter]::ToString(
      $sha.ComputeHash($bytes)
    ).Replace("-", "").ToLowerInvariant()
  } finally {
    $sha.Dispose()
  }
}

function ConvertTo-ProcessArgument([string]$Value) {
  if ($Value.Contains('"')) {
    throw "API_PROCESS_ARGUMENT_CONTAINS_QUOTE"
  }
  return '"' + $Value + '"'
}

function Get-PortOwner([int]$TargetPort) {
  $owners = @(
    Get-NetTCPConnection `
      -State Listen `
      -LocalPort $TargetPort `
      -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty OwningProcess -Unique
  )
  if ($owners.Count -gt 1) {
    throw "API_PORT_MULTIPLE_OWNERS(port=$TargetPort)"
  }
  if ($owners.Count -eq 0) {
    return $null
  }
  return [int]$owners[0]
}

function Wait-ApiHealth([int]$TargetPort) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    try {
      $health = Invoke-RestMethod `
        -Uri "http://127.0.0.1:$TargetPort/health/runtime" `
        -Method Get `
        -TimeoutSec 3
      if (
        $health.database.backend -ne "sqlite" -and
        $health.redis.backend -notin @("local", "unknown") -and
        $health.artifactStorage.backend -ne "local" -and
        $health.worker.backend -ne "local"
      ) {
        return $health
      }
    } catch {
      # Admission may still be running its migration/recovery lifespan.
    }
    Start-Sleep -Milliseconds 250
  } while ((Get-Date) -lt $deadline)
  throw "API_HEALTH_TIMEOUT(port=$TargetPort)"
}

function Stop-StartedTree(
  [Diagnostics.Process]$Runner,
  [int]$TargetPort
) {
  $owner = Get-PortOwner $TargetPort
  if ($null -ne $owner) {
    $child = Get-CimInstance Win32_Process `
      -Filter "ProcessId = $owner" `
      -ErrorAction SilentlyContinue
    if ($null -ne $child -and [int]$child.ParentProcessId -eq $Runner.Id) {
      Stop-Process -Id $owner -Force -ErrorAction SilentlyContinue
    }
  }
  if (-not $Runner.HasExited) {
    Stop-Process -Id $Runner.Id -Force -ErrorAction SilentlyContinue
  }
}

if (Get-PortOwner $Port) {
  throw "API_PORT_ALREADY_IN_USE(port=$Port)"
}

$releaseSha = (& git.exe -C $repo rev-parse HEAD).Trim()
if (-not $releaseSha) {
  throw "API_RELEASE_SHA_UNAVAILABLE"
}
$env:MDI_RELEASE_SHA = $releaseSha
if ([string]::IsNullOrWhiteSpace($env:MDI_PROVIDER_ENCRYPTION_KEY)) {
  $userProviderKey = [Environment]::GetEnvironmentVariable(
    "MDI_PROVIDER_ENCRYPTION_KEY",
    "User"
  )
  if (-not [string]::IsNullOrWhiteSpace($userProviderKey)) {
    $env:MDI_PROVIDER_ENCRYPTION_KEY = $userProviderKey
  }
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
$runtimeEnvironmentJson = & $python `
  (Join-Path $repo "scripts\phase14r_runtime_environment.py") `
  --compact
if ($LASTEXITCODE -ne 0) {
  throw "MDI_RUNTIME_ENVIRONMENT_FAILED(exit=$LASTEXITCODE)"
}
$runtimeEnvironment = $runtimeEnvironmentJson | ConvertFrom-Json
foreach ($property in $runtimeEnvironment.PSObject.Properties) {
  Set-Item -Path "Env:$($property.Name)" -Value ([string]$property.Value)
}
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

$runner = Start-Process `
  -FilePath $python `
  -ArgumentList @(
    (ConvertTo-ProcessArgument $runnerPath),
    "--stdout-log", (ConvertTo-ProcessArgument $stdoutLog),
    "--stderr-log", (ConvertTo-ProcessArgument $stderrLog),
    "--",
    (ConvertTo-ProcessArgument $python),
    "-m", "uvicorn", "mdi_api.main:app",
    "--host", "0.0.0.0", "--port", "$Port"
  ) `
  -WorkingDirectory $repo `
  -WindowStyle Hidden `
  -PassThru

try {
  $health = Wait-ApiHealth $Port
  $childId = Get-PortOwner $Port
  if ($null -eq $childId) {
    throw "API_LISTENER_MISSING_AFTER_HEALTH(port=$Port)"
  }
  $child = Get-CimInstance Win32_Process `
    -Filter "ProcessId = $childId" `
    -ErrorAction Stop
  $runnerRecord = Get-CimInstance Win32_Process `
    -Filter "ProcessId = $($runner.Id)" `
    -ErrorAction Stop
  if ([int]$child.ParentProcessId -ne $runner.Id) {
    throw "API_PROCESS_PARENT_MISMATCH(port=$Port)"
  }
  $expectedChildFragment = "-m uvicorn mdi_api.main:app"
  if (
    ([string]$child.CommandLine).IndexOf(
      $expectedChildFragment,
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0 -or
    [string]$child.CommandLine -notmatch "(?i)(?:^|\s)--port(?:\s+|=)$Port(?:\s|$)"
  ) {
    throw "API_CHILD_COMMAND_MISMATCH(port=$Port)"
  }
  if (
    ([string]$runnerRecord.CommandLine).IndexOf(
      $runnerPath,
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0 -or
    ([string]$runnerRecord.CommandLine).IndexOf(
      $stdoutLog,
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0 -or
    ([string]$runnerRecord.CommandLine).IndexOf(
      $stderrLog,
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0
  ) {
    throw "API_RUNNER_COMMAND_MISMATCH(port=$Port)"
  }

  New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
  $manifest = [ordered]@{
    schemaVersion = "phase14r-api-instance/1.1"
    repositoryToken = Get-Sha256Text $repo.ToLowerInvariant()
    releaseSha = $releaseSha
    instanceId = $InstanceId
    port = $Port
    status = "RUNNING"
    runnerPid = [int]$runner.Id
    runnerCreatedAt = $runnerRecord.CreationDate.ToUniversalTime().ToString("o")
    runnerCreationFileTimeUtc = [long]$runnerRecord.CreationDate.ToFileTimeUtc()
    runnerExecutable = [IO.Path]::GetFullPath(
      [string]$runnerRecord.ExecutablePath
    )
    runnerCommandDigest = Get-Sha256Text ([string]$runnerRecord.CommandLine)
    childPid = [int]$childId
    childCreatedAt = $child.CreationDate.ToUniversalTime().ToString("o")
    childCreationFileTimeUtc = [long]$child.CreationDate.ToFileTimeUtc()
    childExecutable = [IO.Path]::GetFullPath([string]$child.ExecutablePath)
    childCommandDigest = Get-Sha256Text ([string]$child.CommandLine)
    startedAt = (Get-Date).ToUniversalTime().ToString("o")
    runtimeFingerprint = [string]$health.runtimeConfiguration.fingerprint
  }
  $temporaryManifest = "$manifestPath.$InstanceId.tmp"
  [IO.File]::WriteAllText(
    $temporaryManifest,
    ($manifest | ConvertTo-Json -Depth 5),
    [Text.UTF8Encoding]::new($false)
  )
  Move-Item `
    -LiteralPath $temporaryManifest `
    -Destination $manifestPath `
    -Force
  [pscustomobject]$manifest | ConvertTo-Json -Depth 5
} catch {
  Stop-StartedTree $runner $Port
  throw
}
