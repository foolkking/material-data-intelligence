[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [ValidateRange(1024, 65535)]
  [int]$CanonicalPort = 8005,

  [ValidateRange(1024, 65535)]
  [int]$ShadowPort = 8006,

  [ValidateRange(1024, 65535)]
  [int]$FrontendPort = 3023,

  [ValidateRange(5, 300)]
  [int]$TimeoutSeconds = 45,

  [ValidateRange(0, 2147483647)]
  [int]$ExpectedCanonicalPid = 0,

  [switch]$Apply
)

$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
. (Join-Path $PSScriptRoot "phase14r_runtime_paths.ps1")
$python = [IO.Path]::GetFullPath(
  (Get-Command "python.exe" -ErrorAction Stop).Source
)
$startScript = [IO.Path]::GetFullPath(
  (Join-Path $repo "scripts\phase14r_start_api.ps1")
)
$runtimeDirectory = Get-MdiApiRuntimeDirectory $repo
$legacyRuntimeDirectory = Join-Path $repo ".cache\runtime"

function Get-Sha256Text([string]$Value) {
  $sha = [Security.Cryptography.SHA256]::Create()
  try {
    return [BitConverter]::ToString(
      $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))
    ).Replace("-", "").ToLowerInvariant()
  } finally {
    $sha.Dispose()
  }
}

function Get-PortOwner([int]$Port) {
  $owners = @(
    Get-NetTCPConnection `
      -State Listen `
      -LocalPort $Port `
      -ErrorAction SilentlyContinue |
      Select-Object -ExpandProperty OwningProcess -Unique
  )
  if ($owners.Count -gt 1) {
    throw "API_PORT_MULTIPLE_OWNERS(port=$Port)"
  }
  if ($owners.Count -eq 0) {
    return $null
  }
  return [int]$owners[0]
}

function Get-ApiHealth(
  [int]$Port,
  [string]$Path = "/health/runtime"
) {
  $health = Invoke-RestMethod `
    -Uri "http://127.0.0.1:$Port$Path" `
    -Method Get `
    -TimeoutSec 10
  if (
    $health.database.backend -eq "sqlite" -or
    $health.redis.backend -in @("local", "unknown") -or
    $health.artifactStorage.backend -eq "local" -or
    $health.worker.backend -eq "local"
  ) {
    throw "API_RUNTIME_TOPOLOGY_INVALID(port=$Port,path=$Path)"
  }
  return $health
}

function Get-Manifest([int]$Port) {
  foreach ($directory in @($runtimeDirectory, $legacyRuntimeDirectory)) {
    $path = Join-Path $directory "api-$Port.json"
    if (Test-Path -LiteralPath $path -PathType Leaf) {
      return [pscustomobject]@{
        manifest = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
        path = [IO.Path]::GetFullPath($path)
      }
    }
  }
  return $null
}

function Assert-ApiTree(
  [int]$Port,
  [int]$ExplicitLegacyPid = 0
) {
  $childId = Get-PortOwner $Port
  if ($null -eq $childId) {
    throw "API_LISTENER_MISSING(port=$Port)"
  }
  $child = Get-CimInstance Win32_Process `
    -Filter "ProcessId = $childId" `
    -ErrorAction Stop
  $parent = Get-CimInstance Win32_Process `
    -Filter "ProcessId = $($child.ParentProcessId)" `
    -ErrorAction Stop
  $childCommand = [string]$child.CommandLine
  $parentCommand = [string]$parent.CommandLine
  if (
    [IO.Path]::GetFullPath([string]$child.ExecutablePath) -ne $python -or
    [IO.Path]::GetFullPath([string]$parent.ExecutablePath) -ne $python -or
    $childCommand.IndexOf(
      "-m uvicorn mdi_api.main:app",
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0 -or
    $childCommand -notmatch "(?i)(?:^|\s)--port(?:\s+|=)$Port(?:\s|$)" -or
    $parentCommand.IndexOf(
      "phase14r_log_runner.py",
      [StringComparison]::OrdinalIgnoreCase
    ) -lt 0
  ) {
    throw "API_PROCESS_OWNERSHIP_MISMATCH(port=$Port)"
  }

  $manifestRecord = Get-Manifest $Port
  if ($null -eq $manifestRecord) {
    if (
      $ExplicitLegacyPid -eq 0 -or
      $ExplicitLegacyPid -ne $childId
    ) {
      throw "API_LEGACY_INSTANCE_REQUIRES_EXPLICIT_PID(port=$Port,pid=$childId)"
    }
    return [pscustomobject]@{
      port = $Port
      childPid = $childId
      parentPid = [int]$child.ParentProcessId
      childCreatedAt = $child.CreationDate.ToUniversalTime().ToString("o")
      childCreationFileTimeUtc = [long]$child.CreationDate.ToFileTimeUtc()
      parentCreatedAt = $parent.CreationDate.ToUniversalTime().ToString("o")
      parentCreationFileTimeUtc = [long]$parent.CreationDate.ToFileTimeUtc()
      childCommandDigest = Get-Sha256Text $childCommand
      parentCommandDigest = Get-Sha256Text $parentCommand
      legacyExplicitlyAdopted = $true
      releaseSha = $null
      runtimeFingerprint = $null
      manifestPath = $null
    }
  }
  $manifest = $manifestRecord.manifest

  $repositoryToken = Get-Sha256Text ($repo.ToLowerInvariant())
  # Named, parenthesized checks avoid PowerShell's comma/equality precedence
  # ambiguity and make a failed ownership proof actionable without exposing
  # command lines or runtime secrets.
  $checks = [ordered]@{
    schemaVersion = (
      $manifest.schemaVersion -eq "phase14r-api-instance/1.1"
    )
    repositoryToken = ($manifest.repositoryToken -eq $repositoryToken)
    port = ([int]$manifest.port -eq $Port)
    childPid = ([int]$manifest.childPid -eq $childId)
    runnerPid = (
      [int]$manifest.runnerPid -eq [int]$child.ParentProcessId
    )
    childCreation = (
      [long]$manifest.childCreationFileTimeUtc -eq
        [long]$child.CreationDate.ToFileTimeUtc()
    )
    runnerCreation = (
      [long]$manifest.runnerCreationFileTimeUtc -eq
        [long]$parent.CreationDate.ToFileTimeUtc()
    )
    childExecutable = (
      [string]$manifest.childExecutable -eq
        [IO.Path]::GetFullPath([string]$child.ExecutablePath)
    )
    runnerExecutable = (
      [string]$manifest.runnerExecutable -eq
        [IO.Path]::GetFullPath([string]$parent.ExecutablePath)
    )
    childCommand = (
      [string]$manifest.childCommandDigest -eq
        (Get-Sha256Text $childCommand)
    )
    runnerCommand = (
      [string]$manifest.runnerCommandDigest -eq
        (Get-Sha256Text $parentCommand)
    )
  }
  $failedChecks = @(
    $checks.GetEnumerator() |
      Where-Object { -not [bool]$_.Value } |
      Select-Object -ExpandProperty Key
  )
  if ($failedChecks.Count -gt 0) {
    throw "API_INSTANCE_MANIFEST_MISMATCH(port=$Port,pid=$childId,checks=$($failedChecks -join ','))"
  }
  return [pscustomobject]@{
    port = $Port
    childPid = $childId
    parentPid = [int]$child.ParentProcessId
    childCreatedAt = [string]$manifest.childCreatedAt
    childCreationFileTimeUtc = [long]$manifest.childCreationFileTimeUtc
    parentCreatedAt = [string]$manifest.runnerCreatedAt
    parentCreationFileTimeUtc = [long]$manifest.runnerCreationFileTimeUtc
    childCommandDigest = [string]$manifest.childCommandDigest
    parentCommandDigest = [string]$manifest.runnerCommandDigest
    legacyExplicitlyAdopted = $false
    releaseSha = [string]$manifest.releaseSha
    runtimeFingerprint = [string]$manifest.runtimeFingerprint
    manifestPath = [string]$manifestRecord.path
  }
}

function Assert-TreeUnchanged([pscustomobject]$Tree) {
  $legacyPid = 0
  if ($Tree.legacyExplicitlyAdopted) {
    $legacyPid = [int]$Tree.childPid
  }
  $current = Assert-ApiTree $Tree.port $legacyPid
  if (
    $current.childPid -ne $Tree.childPid -or
    $current.parentPid -ne $Tree.parentPid -or
    $current.childCreationFileTimeUtc -ne $Tree.childCreationFileTimeUtc -or
    $current.parentCreationFileTimeUtc -ne $Tree.parentCreationFileTimeUtc -or
    $current.childCommandDigest -ne $Tree.childCommandDigest -or
    $current.parentCommandDigest -ne $Tree.parentCommandDigest
  ) {
    throw "API_PROCESS_IDENTITY_DRIFT(port=$($Tree.port))"
  }
}

function Assert-RunnerUnchanged([pscustomobject]$Tree) {
  $parent = Get-CimInstance Win32_Process `
    -Filter "ProcessId = $($Tree.parentPid)" `
    -ErrorAction Stop
  if (
    [long]$parent.CreationDate.ToFileTimeUtc() -ne
      [long]$Tree.parentCreationFileTimeUtc -or
    (Get-Sha256Text ([string]$parent.CommandLine)) -ne
      $Tree.parentCommandDigest
  ) {
    throw "API_RUNNER_IDENTITY_DRIFT(pid=$($Tree.parentPid))"
  }
}

function Wait-ProcessExit([int]$ProcessId, [int]$Milliseconds) {
  $deadline = (Get-Date).AddMilliseconds($Milliseconds)
  while (
    (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue) -and
    (Get-Date) -lt $deadline
  ) {
    Start-Sleep -Milliseconds 100
  }
  return -not [bool](
    Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  )
}

function Stop-ApiTree([pscustomobject]$Tree, [string]$Reason) {
  Assert-TreeUnchanged $Tree
  if (
    $PSCmdlet.ShouldProcess(
      "API child PID $($Tree.childPid) / runner PID $($Tree.parentPid)",
      $Reason
    )
  ) {
    Stop-Process -Id $Tree.childPid -Force -ErrorAction Stop
    if (-not (Wait-ProcessExit $Tree.childPid 5000)) {
      throw "API_CHILD_DID_NOT_EXIT(pid=$($Tree.childPid))"
    }
    if (-not (Wait-ProcessExit $Tree.parentPid 3000)) {
      Assert-RunnerUnchanged $Tree
      Stop-Process -Id $Tree.parentPid -Force -ErrorAction Stop
    }
    $manifestPath = [string]$Tree.manifestPath
    if (
      -not [string]::IsNullOrWhiteSpace($manifestPath) -and
      (Test-Path -LiteralPath $manifestPath -PathType Leaf)
    ) {
      $manifest = Get-Content -LiteralPath $manifestPath -Raw |
        ConvertFrom-Json
      if (
        [int]$manifest.childPid -eq [int]$Tree.childPid -and
        [int]$manifest.runnerPid -eq [int]$Tree.parentPid -and
        [long]$manifest.childCreationFileTimeUtc -eq
          [long]$Tree.childCreationFileTimeUtc -and
        [long]$manifest.runnerCreationFileTimeUtc -eq
          [long]$Tree.parentCreationFileTimeUtc
      ) {
        Remove-Item -LiteralPath $manifestPath -Force
      }
    }
  }
}

function Start-Api([int]$Port) {
  & powershell.exe `
    -NoProfile `
    -ExecutionPolicy Bypass `
    -File $startScript `
    -Port $Port `
    -TimeoutSeconds $TimeoutSeconds | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "API_START_FAILED(port=$Port,exit=$LASTEXITCODE)"
  }
  return Assert-ApiTree $Port 0
}

function Stop-NewShadowOnFailure {
  try {
    $tree = Assert-ApiTree $ShadowPort 0
    Stop-ApiTree $tree "Clean failed shadow API"
  } catch {
    # Unknown processes are never stopped by cleanup.
  }
}

if ($CanonicalPort -eq $ShadowPort) {
  throw "API_ROTATION_PORTS_MUST_DIFFER"
}

$currentHealth = Get-ApiHealth $CanonicalPort
$currentTree = Assert-ApiTree $CanonicalPort $ExpectedCanonicalPid
$shadowOwner = Get-PortOwner $ShadowPort
if ($null -ne $shadowOwner) {
  throw "API_SHADOW_PORT_IN_USE(port=$ShadowPort,pid=$shadowOwner)"
}
$releaseSha = (& git.exe -C $repo rev-parse HEAD).Trim()

if (-not $Apply) {
  [pscustomobject]@{
    schemaVersion = "phase14r-api-rotation/1.0"
    mode = "dry-run"
    canonical = $currentTree
    canonicalHealthy = $true
    shadowPort = $ShadowPort
    shadowPortFree = $true
    expectedReleaseSha = $releaseSha
    plannedActions = @(
      "start-and-validate-shadow",
      "stop-exact-canonical-child-then-runner",
      "start-and-validate-canonical",
      "validate-frontend-proxy",
      "stop-exact-shadow-child-then-runner"
    )
  } | ConvertTo-Json -Depth 8
  exit 0
}

$shadowTree = $null
$newCanonicalTree = $null
$canonicalStopped = $false
try {
  $shadowTree = Start-Api $ShadowPort
  $shadowHealth = Get-ApiHealth $ShadowPort
  if (
    $shadowTree.releaseSha -ne $releaseSha -or
    $shadowHealth.runtimeConfiguration.fingerprint -ne
      $currentHealth.runtimeConfiguration.fingerprint
  ) {
    throw "API_SHADOW_IDENTITY_OR_TOPOLOGY_MISMATCH"
  }

  Assert-TreeUnchanged $currentTree
  Stop-ApiTree $currentTree "Replace canonical API after shadow validation"
  $canonicalStopped = $true
  if (Get-PortOwner $CanonicalPort) {
    throw "API_CANONICAL_PORT_DID_NOT_CLOSE(port=$CanonicalPort)"
  }

  $newCanonicalTree = Start-Api $CanonicalPort
  $newCanonicalHealth = Get-ApiHealth $CanonicalPort
  if (
    $newCanonicalTree.releaseSha -ne $releaseSha -or
    $newCanonicalHealth.runtimeConfiguration.fingerprint -ne
      $shadowHealth.runtimeConfiguration.fingerprint
  ) {
    throw "API_CANONICAL_IDENTITY_OR_TOPOLOGY_MISMATCH"
  }

  $frontendHealth = Get-ApiHealth $FrontendPort "/api/health/runtime"
  if (
    $frontendHealth.runtimeConfiguration.fingerprint -ne
      $newCanonicalHealth.runtimeConfiguration.fingerprint
  ) {
    Stop-ApiTree $shadowTree "Remove shadow after canonical proxy mismatch"
    $shadowTree = $null
    throw "API_FRONTEND_PROXY_FINGERPRINT_MISMATCH"
  }

  Stop-ApiTree $shadowTree "Remove validated shadow after canonical cutover"
  $shadowTree = $null
  if (Get-PortOwner $ShadowPort) {
    throw "API_SHADOW_PORT_DID_NOT_CLOSE(port=$ShadowPort)"
  }

  [pscustomobject]@{
    schemaVersion = "phase14r-api-rotation/1.0"
    mode = "apply"
    oldCanonical = $currentTree
    newCanonical = $newCanonicalTree
    shadowPort = $ShadowPort
    shadowClosed = $true
    frontendPort = $FrontendPort
    frontendProxyValidated = $true
    runtimeFingerprint = [string](
      $newCanonicalHealth.runtimeConfiguration.fingerprint
    )
  } | ConvertTo-Json -Depth 8
} catch {
  if (-not $canonicalStopped) {
    Stop-NewShadowOnFailure
  } elseif ($null -ne $newCanonicalTree) {
    try {
      [void](Get-ApiHealth $CanonicalPort)
      if ($null -ne $shadowTree) {
        Stop-ApiTree $shadowTree "Remove shadow after canonical recovery"
        $shadowTree = $null
      }
    } catch {
      # A healthy owned shadow is deliberately retained for operator recovery
      # when the canonical endpoint cannot be restored safely.
    }
  }
  throw
}
