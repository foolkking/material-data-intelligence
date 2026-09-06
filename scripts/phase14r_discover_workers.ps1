[CmdletBinding()]
param(
  [ValidateRange(1, 120)]
  [int]$TimeoutSeconds = 20
)

$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
. (Join-Path $PSScriptRoot "phase14r_runtime_paths.ps1")
$runtimeDirectory = Get-MdiWorkerRuntimeDirectory $repo
$python = [IO.Path]::GetFullPath((Get-Command "python.exe" -ErrorAction Stop).Source)

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

function Get-RedactedRedisIdentity([string]$Value) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    return "redis:unknown"
  }
  try {
    $uri = [Uri]$Value
    if (-not $uri.IsAbsoluteUri) {
      return "redis:opaque"
    }
    $authority = "$($uri.Scheme)://$($uri.Host)"
    if (-not $uri.IsDefaultPort) {
      $authority = "$authority`:$($uri.Port)"
    }
    $database = $uri.AbsolutePath.Trim("/")
    if ($database -match "^[0-9]{1,4}$") {
      return "$authority/$database"
    }
    return $authority
  } catch {
    return "redis:opaque"
  }
}

function Get-QueueManifest {
  $previousPythonPath = $env:PYTHONPATH
  $schemaPath = Join-Path $repo "packages\schemas"
  $env:PYTHONPATH = if ($previousPythonPath) {
    "$schemaPath$([IO.Path]::PathSeparator)$previousPythonPath"
  } else {
    $schemaPath
  }
  try {
    $json = & $python -m mdi_schemas.worker_queues
    if ($LASTEXITCODE -ne 0) {
      throw "MDI_WORKER_QUEUE_MANIFEST_FAILED(exit=$LASTEXITCODE)"
    }
    return $json | ConvertFrom-Json
  } finally {
    $env:PYTHONPATH = $previousPythonPath
  }
}

function Get-WorkerRecords([object]$Manifest) {
  $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'")
  $children = @($processes | Where-Object {
    [string]$_.CommandLine -match "mdi_workers\.worker_entrypoint"
  })
  $runners = @($processes | Where-Object {
    [string]$_.CommandLine -match "phase14r_log_runner\.py"
  })
  $records = [System.Collections.Generic.List[object]]::new()
  foreach ($definition in @($Manifest.queues)) {
    $queue = [string]$definition.name
    $escapedQueue = [regex]::Escape($queue)
    $queueChildren = @($children | Where-Object {
      [string]$_.CommandLine -match (
        "mdi_workers\.worker_entrypoint\s+['`"]?" +
        $escapedQueue + "['`"]?(\s|$)"
      )
    })
    foreach ($child in $queueChildren) {
      $runner = $runners | Where-Object {
        [int]$_.ProcessId -eq [int]$child.ParentProcessId -and
        [string]$_.CommandLine -match (
          "phase14r_log_runner\.py.*worker.*" + $escapedQueue
        )
      } | Select-Object -First 1
      if ($null -eq $runner) {
        continue
      }
      $redisUrl = ""
      if ([string]$child.CommandLine -match "--url\s+['`"]?([^'`"\s]+)") {
        $redisUrl = [string]$Matches[1]
      }
      $records.Add([ordered]@{
        schemaVersion = "phase14r-worker-instance/1.0"
        repositoryToken = Get-Sha256Text ($repo.ToLowerInvariant())
        releaseSha = ((& git.exe -C $repo rev-parse HEAD).Trim())
        role = [string]$definition.role
        queue = $queue
        handler = [string]$definition.handler
        redisIdentity = Get-RedactedRedisIdentity $redisUrl
        runnerPid = [int]$runner.ProcessId
        runnerCreatedAt = $runner.CreationDate.ToUniversalTime().ToString("o")
        runnerCreationFileTimeUtc = [long]$runner.CreationDate.ToFileTimeUtc()
        runnerExecutable = [IO.Path]::GetFullPath([string]$runner.ExecutablePath)
        runnerCommandDigest = Get-Sha256Text ([string]$runner.CommandLine)
        childPid = [int]$child.ProcessId
        childCreatedAt = $child.CreationDate.ToUniversalTime().ToString("o")
        childCreationFileTimeUtc = [long]$child.CreationDate.ToFileTimeUtc()
        childExecutable = [IO.Path]::GetFullPath([string]$child.ExecutablePath)
        childCommandDigest = Get-Sha256Text ([string]$child.CommandLine)
        discoveredAt = (Get-Date).ToUniversalTime().ToString("o")
        lastSeenAt = (Get-Date).ToUniversalTime().ToString("o")
        status = "RUNNING"
        staleSince = $null
      })
      break
    }
  }
  return @($records)
}

$manifest = Get-QueueManifest
$expectedQueues = @($manifest.queues | ForEach-Object { [string]$_.name })
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$records = @()
do {
  $records = @(Get-WorkerRecords $manifest)
  $foundQueues = @($records | ForEach-Object { [string]$_.queue } | Select-Object -Unique)
  if ($foundQueues.Count -eq $expectedQueues.Count) {
    break
  }
  Start-Sleep -Milliseconds 500
} while ((Get-Date) -lt $deadline)

New-Item -ItemType Directory -Path $runtimeDirectory -Force | Out-Null
foreach ($record in $records) {
  $safeName = ([string]$record.queue) -replace "[^A-Za-z0-9_-]", "-"
  $path = Join-Path $runtimeDirectory "worker-$safeName.json"
  $temporaryPath = "$path.$([guid]::NewGuid().ToString('N')).tmp"
  [IO.File]::WriteAllText(
    $temporaryPath,
    ($record | ConvertTo-Json -Depth 6),
    [Text.UTF8Encoding]::new($false)
  )
  Move-Item -LiteralPath $temporaryPath -Destination $path -Force
}

$missingQueues = @($expectedQueues | Where-Object { $_ -notin $foundQueues })
$now = (Get-Date).ToUniversalTime().ToString("o")
foreach ($queue in $missingQueues) {
  $safeName = ([string]$queue) -replace "[^A-Za-z0-9_-]", "-"
  $path = Join-Path $runtimeDirectory "worker-$safeName.json"
  if (-not (Test-Path -LiteralPath $path)) {
    continue
  }
  $existing = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
  $staleSince = [string]$existing.staleSince
  if ([string]::IsNullOrWhiteSpace($staleSince)) {
    $staleSince = $now
  }
  $lastSeenAt = [string]$existing.lastSeenAt
  if ([string]::IsNullOrWhiteSpace($lastSeenAt)) {
    $lastSeenAt = [string]$existing.discoveredAt
  }
  $updated = [ordered]@{}
  foreach ($property in $existing.PSObject.Properties) {
    if ($property.Name -in @("redisUrl", "status", "lastSeenAt", "staleSince")) {
      continue
    }
    $updated[$property.Name] = $property.Value
  }
  $updated["redisIdentity"] = if ($existing.redisIdentity) {
    Get-RedactedRedisIdentity ([string]$existing.redisIdentity)
  } else {
    Get-RedactedRedisIdentity ([string]$existing.redisUrl)
  }
  $updated["status"] = "MISSING"
  $updated["lastSeenAt"] = if ($lastSeenAt) { $lastSeenAt } else { $null }
  $updated["staleSince"] = $staleSince
  $temporaryPath = "$path.$([guid]::NewGuid().ToString('N')).tmp"
  [IO.File]::WriteAllText(
    $temporaryPath,
    ($updated | ConvertTo-Json -Depth 6),
    [Text.UTF8Encoding]::new($false)
  )
  Move-Item -LiteralPath $temporaryPath -Destination $path -Force
}
[pscustomobject]@{
  schemaVersion = "phase14r-worker-discovery/1.0"
  runtimeDirectory = $runtimeDirectory
  expectedQueues = $expectedQueues
  discoveredQueues = $foundQueues
  missingQueues = $missingQueues
  complete = $missingQueues.Count -eq 0
  manifestsWritten = $records.Count
} | ConvertTo-Json -Depth 6
