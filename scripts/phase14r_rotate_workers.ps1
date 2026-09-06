[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "High")]
param(
  [ValidateRange(5, 120)]
  [int]$TimeoutSeconds = 20,
  [ValidatePattern("^[A-Za-z0-9_-]*$")]
  [string]$WorkerGeneration = "",
  [string[]]$Queue = @(),
  [switch]$Apply
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

function ConvertTo-ProcessArgument([string]$Value) {
  if ($Value.Contains('"')) {
    throw "WORKER_PROCESS_ARGUMENT_CONTAINS_QUOTE"
  }
  return '"' + $Value + '"'
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

function Get-CurrentProcess([int]$ProcessId) {
  return Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" |
    Select-Object -First 1
}

function Find-WorkerReplacement(
  [string]$QueueName,
  [string]$Generation,
  [int]$OldChildPid
) {
  $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe'")
  $escapedQueue = [regex]::Escape($QueueName)
  $escapedGeneration = [regex]::Escape($Generation)
  $child = $processes | Where-Object {
    [int]$_.ProcessId -ne $OldChildPid -and
    [string]$_.CommandLine -notmatch "phase14r_log_runner\.py" -and
    [string]$_.CommandLine -match (
      "mdi_workers\.worker_entrypoint\s+['`"]?" + $escapedQueue +
      "['`"]?.*--name\s+['`"]?phase14r-" + $escapedQueue +
      "-" + $escapedGeneration + "['`"]?(\s|$)"
    )
  } | Select-Object -First 1
  if ($null -eq $child) {
    return $null
  }
  $runner = $processes | Where-Object {
    [int]$_.ProcessId -eq [int]$child.ParentProcessId -and
    [string]$_.CommandLine -match (
      "phase14r_log_runner\.py.*worker.*" + $escapedQueue +
      ".*" + $escapedGeneration
    )
  } | Select-Object -First 1
  if ($null -eq $runner) {
    return $null
  }
  return [pscustomobject]@{
    runner = $runner
    child = $child
  }
}

function Wait-WorkerReplacement(
  [string]$QueueName,
  [string]$Generation,
  [object]$OldManifest
) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  do {
    $pair = Find-WorkerReplacement $QueueName $Generation ([int]$OldManifest.childPid)
    if ($null -ne $pair) {
      $redisIdentity = "redis:unknown"
      $registrationRedisUrl = ""
      if ([string]$pair.child.CommandLine -match "--url\s+['`"]?([^'`"\s]+)") {
        $registrationRedisUrl = [string]$Matches[1]
        $redisIdentity = Get-RedactedRedisIdentity $registrationRedisUrl
      }
      $escapedQueue = [regex]::Escape($QueueName)
      $queueMatches = [string]$pair.child.CommandLine -match (
        "mdi_workers\.worker_entrypoint\s+['`"]?" + $escapedQueue +
        "['`"]?(\s|$)"
      )
      $parentMatches = [int]$pair.child.ParentProcessId -eq [int]$pair.runner.ProcessId
      $redisMatches = $redisIdentity -eq [string]$OldManifest.redisIdentity
      $runnerAlive = $null -ne (Get-Process -Id ([int]$pair.runner.ProcessId) -ErrorAction SilentlyContinue)
      $childAlive = $null -ne (Get-Process -Id ([int]$pair.child.ProcessId) -ErrorAction SilentlyContinue)
      if (
        $queueMatches -and $parentMatches -and $redisMatches -and
        $runnerAlive -and $childAlive
      ) {
        $expectedName = "phase14r-$QueueName-$Generation"
        $previousRedisUrl = $env:MDI_WORKER_REGISTRATION_REDIS_URL
        $env:MDI_WORKER_REGISTRATION_REDIS_URL = $registrationRedisUrl
        try {
          $registrationJson = & $python `
            (Join-Path $repo "scripts\phase14r_worker_registration.py") `
            --worker-name $expectedName `
            --queue $QueueName `
            --maximum-heartbeat-age-seconds 900
          $registrationExitCode = $LASTEXITCODE
        } finally {
          $env:MDI_WORKER_REGISTRATION_REDIS_URL = $previousRedisUrl
        }
        if ($registrationExitCode -eq 0) {
          $registration = $registrationJson | ConvertFrom-Json
          if ([bool]$registration.healthy) {
            $pair | Add-Member -NotePropertyName registration -NotePropertyValue $registration
            return $pair
          }
        }
      }
    }
    Start-Sleep -Milliseconds 250
  } while ((Get-Date) -lt $deadline)
  throw "WORKER_REPLACEMENT_HEALTH_TIMEOUT(queue=$QueueName)"
}

function Stop-VerifiedWorkerPair([object]$Pair) {
  $child = Get-CurrentProcess ([int]$Pair.child.ProcessId)
  $runner = Get-CurrentProcess ([int]$Pair.runner.ProcessId)
  if ($null -eq $child -or $null -eq $runner) {
    return
  }
  if ([int]$child.ParentProcessId -ne [int]$runner.ProcessId) {
    throw "WORKER_STOP_PARENT_MISMATCH"
  }
  if ((Get-Sha256Text ([string]$child.CommandLine)) -ne [string]$Pair.childCommandDigest) {
    throw "WORKER_STOP_CHILD_COMMAND_DRIFT"
  }
  if ((Get-Sha256Text ([string]$runner.CommandLine)) -ne [string]$Pair.runnerCommandDigest) {
    throw "WORKER_STOP_RUNNER_COMMAND_DRIFT"
  }
  Stop-Process -Id ([int]$child.ProcessId) -Force
  $deadline = (Get-Date).AddSeconds(5)
  do {
    if ($null -eq (Get-CurrentProcess ([int]$child.ProcessId))) {
      break
    }
    Start-Sleep -Milliseconds 100
  } while ((Get-Date) -lt $deadline)
  if ($null -ne (Get-CurrentProcess ([int]$child.ProcessId))) {
    throw "WORKER_STOP_CHILD_TIMEOUT"
  }
  if ($null -ne (Get-CurrentProcess ([int]$runner.ProcessId))) {
    Stop-Process -Id ([int]$runner.ProcessId) -Force
  }
}

function Remove-WorkerRegistration([string]$WorkerName, [string]$QueueName, [string]$RedisUrl) {
  $previousRedisUrl = $env:MDI_WORKER_REGISTRATION_REDIS_URL
  $env:MDI_WORKER_REGISTRATION_REDIS_URL = $RedisUrl
  try {
    $registrationJson = & $python `
      (Join-Path $repo "scripts\phase14r_worker_registration.py") `
      --worker-name $WorkerName `
      --queue $QueueName `
      --unregister
    $exitCode = $LASTEXITCODE
  } finally {
    $env:MDI_WORKER_REGISTRATION_REDIS_URL = $previousRedisUrl
  }
  if ($exitCode -ne 0) {
    throw "WORKER_REGISTRATION_UNREGISTER_FAILED(queue=$QueueName)"
  }
  return $registrationJson | ConvertFrom-Json
}

function Assert-WorkerManifest([object]$Manifest) {
  if ([string]$Manifest.status -ne "RUNNING") {
    throw "WORKER_MANIFEST_NOT_RUNNING(queue=$($Manifest.queue))"
  }
  $runner = Get-CurrentProcess ([int]$Manifest.runnerPid)
  $child = Get-CurrentProcess ([int]$Manifest.childPid)
  if ($null -eq $runner -or $null -eq $child) {
    throw "WORKER_PROCESS_MISSING(queue=$($Manifest.queue))"
  }
  if ([int]$child.ParentProcessId -ne [int]$runner.ProcessId) {
    throw "WORKER_PARENT_MISMATCH(queue=$($Manifest.queue))"
  }
  if ([long]$runner.CreationDate.ToFileTimeUtc() -ne [long]$Manifest.runnerCreationFileTimeUtc) {
    throw "WORKER_RUNNER_CREATION_DRIFT(queue=$($Manifest.queue))"
  }
  if ([long]$child.CreationDate.ToFileTimeUtc() -ne [long]$Manifest.childCreationFileTimeUtc) {
    throw "WORKER_CHILD_CREATION_DRIFT(queue=$($Manifest.queue))"
  }
  if ((Get-Sha256Text ([string]$runner.CommandLine)) -ne [string]$Manifest.runnerCommandDigest) {
    throw "WORKER_RUNNER_COMMAND_DRIFT(queue=$($Manifest.queue))"
  }
  if ((Get-Sha256Text ([string]$child.CommandLine)) -ne [string]$Manifest.childCommandDigest) {
    throw "WORKER_CHILD_COMMAND_DRIFT(queue=$($Manifest.queue))"
  }
  $escapedQueue = [regex]::Escape([string]$Manifest.queue)
  if ([string]$child.CommandLine -notmatch (
      "mdi_workers\.worker_entrypoint\s+['`"]?" + $escapedQueue + "['`"]?(\s|$)"
    )) {
    throw "WORKER_QUEUE_COMMAND_MISMATCH(queue=$($Manifest.queue))"
  }
  $redisIdentity = "redis:unknown"
  if ([string]$child.CommandLine -match "--url\s+['`"]?([^'`"\s]+)") {
    $redisIdentity = Get-RedactedRedisIdentity ([string]$Matches[1])
  }
  if ($redisIdentity -ne [string]$Manifest.redisIdentity) {
    throw "WORKER_REDIS_IDENTITY_MISMATCH(queue=$($Manifest.queue))"
  }
  return [pscustomobject]@{
    manifest = $Manifest
    runner = $runner
    child = $child
    runnerCommandDigest = [string]$Manifest.runnerCommandDigest
    childCommandDigest = [string]$Manifest.childCommandDigest
  }
}

if (-not (Test-Path -LiteralPath $runtimeDirectory)) {
  throw "WORKER_RUNTIME_DIRECTORY_MISSING"
}
$expectedReleaseSha = ((& git.exe -C $repo rev-parse HEAD).Trim())
$repositoryToken = Get-Sha256Text ($repo.ToLowerInvariant())
$manifestFiles = @(Get-ChildItem -LiteralPath $runtimeDirectory -Filter "worker-*.json")
$manifests = @($manifestFiles | ForEach-Object {
  Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
})
$allQueues = @($manifests | ForEach-Object { [string]$_.queue } | Select-Object -Unique)
$selectedQueues = if ($Queue.Count -gt 0) {
  @($Queue | ForEach-Object { [string]$_.Trim() } | Where-Object { $_ })
} else {
  @($allQueues)
}
if ($selectedQueues.Count -eq 0) {
  throw "WORKER_MANIFESTS_EMPTY"
}
if ($Apply -and $selectedQueues.Count -ne 1) {
  throw "WORKER_APPLY_REQUIRES_ONE_QUEUE"
}

$validated = [System.Collections.Generic.List[object]]::new()
foreach ($queue in @($selectedQueues | Select-Object -Unique)) {
  $manifest = $manifests | Where-Object { [string]$_.queue -eq $queue } |
    Select-Object -First 1
  if ($null -eq $manifest) {
    throw "WORKER_MANIFEST_NOT_FOUND(queue=$queue)"
  }
  if ([string]$manifest.repositoryToken -ne $repositoryToken) {
    throw "WORKER_REPOSITORY_TOKEN_MISMATCH(queue=$queue)"
  }
  if ([string]$manifest.releaseSha -ne $expectedReleaseSha) {
    throw "WORKER_RELEASE_SHA_MISMATCH(queue=$queue)"
  }
  $validated.Add((Assert-WorkerManifest $manifest))
}

$actions = @("validate-exact-worker-ownership")
  if ($Apply) {
  $target = $validated[0]
  $queueName = [string]$target.manifest.queue
  $generation = if ($WorkerGeneration) {
    $WorkerGeneration
  } else {
    "rotate-$((Get-Date).ToUniversalTime().ToString('yyyyMMddHHmmss'))"
  }
  $actions = @(
    "start-replacement-queue-$queueName-generation-$generation",
    "stop-exact-child-then-runner",
    "rediscover-worker-manifest"
  )
  if (-not $PSCmdlet.ShouldProcess(
      "$queueName child=$($target.manifest.childPid) runner=$($target.manifest.runnerPid)",
      "replace exact worker queue"
    )) {
    $Apply = $false
  } else {
    $startScript = Join-Path $repo "scripts\phase14r_start_workers.ps1"
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
      "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
      (ConvertTo-ProcessArgument $startScript),
      "-WorkerGeneration", (ConvertTo-ProcessArgument $generation),
      "-OnlyQueue", (ConvertTo-ProcessArgument $queueName)
    ) -WorkingDirectory $repo -WindowStyle Hidden | Out-Null
    $replacement = $null
    $oldPairStopped = $false
    $oldWorkerName = ""
    $oldRedisUrl = ""
    if ([string]$target.child.CommandLine -match "--name\s+['`"]?([^'`"\s]+)") {
      $oldWorkerName = [string]$Matches[1]
    }
    if ([string]$target.child.CommandLine -match "--url\s+['`"]?([^'`"\s]+)") {
      $oldRedisUrl = [string]$Matches[1]
    }
    try {
      $replacement = Wait-WorkerReplacement $queueName $generation $target.manifest
      $replacementRecord = [pscustomobject]@{
        child = $replacement.child
        runner = $replacement.runner
        childCommandDigest = Get-Sha256Text ([string]$replacement.child.CommandLine)
        runnerCommandDigest = Get-Sha256Text ([string]$replacement.runner.CommandLine)
      }
      Stop-VerifiedWorkerPair $target
      $oldPairStopped = $true
      Remove-WorkerRegistration $oldWorkerName $queueName $oldRedisUrl | Out-Null
      & powershell.exe -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $repo "scripts\phase14r_discover_workers.ps1") `
        -TimeoutSeconds $TimeoutSeconds | Out-Null
    } catch {
      if ($null -ne $replacement -and -not $oldPairStopped) {
        try {
          Stop-VerifiedWorkerPair $replacementRecord
          Remove-WorkerRegistration `
            "phase14r-$queueName-$generation" `
            $queueName `
            $oldRedisUrl | Out-Null
        } catch {
          Write-Warning "WORKER_REPLACEMENT_ROLLBACK_FAILED"
        }
      }
      throw
    }
  }
}

[pscustomobject]@{
  schemaVersion = "phase14r-worker-rotation/1.0"
  mode = if ($Apply) { "apply" } else { "dry-run" }
  runtimeDirectory = $runtimeDirectory
  selectedQueues = $selectedQueues
  validated = @($validated | ForEach-Object {
    [pscustomobject]@{
      queue = [string]$_.manifest.queue
      childPid = [int]$_.manifest.childPid
      runnerPid = [int]$_.manifest.runnerPid
      redisIdentity = [string]$_.manifest.redisIdentity
    }
  })
  plannedActions = $actions
} | ConvertTo-Json -Depth 6
