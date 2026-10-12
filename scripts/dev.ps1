param(
  [Parameter(Position = 0)]
  [ValidateSet("init", "doctor", "migrate", "start", "stop", "restart", "status")]
  [string]$Command = "status",
  [ValidateSet("all", "app", "frontend")]
  [string]$Scope = "all"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DefaultLocalRoot = Join-Path (Split-Path $Repo -Parent) "$(Split-Path $Repo -Leaf).local"
if ($env:MDI_LOCAL_ROOT -and -not [IO.Path]::IsPathRooted($env:MDI_LOCAL_ROOT)) {
  throw 'MDI_LOCAL_ROOT must be an absolute path outside the repository.'
}
$LocalRoot = [IO.Path]::GetFullPath($(if ($env:MDI_LOCAL_ROOT) { $env:MDI_LOCAL_ROOT } else { $DefaultLocalRoot }))
if ($LocalRoot -eq $Repo -or $LocalRoot.StartsWith("$Repo\", [StringComparison]::OrdinalIgnoreCase)) {
  throw 'MDI_LOCAL_ROOT must be outside the repository.'
}
$EnvFile = Join-Path $LocalRoot "local.env"
$StateFile = Join-Path $LocalRoot "run\state\services.json"

function Import-LocalEnvironment {
  if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Missing $EnvFile. Install dependencies, then run scripts/dev.ps1 init."
  }
  Get-Content -LiteralPath $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
      if ($Matches[1] -eq 'MDI_LOCAL_ROOT' -and [IO.Path]::GetFullPath($Matches[2].Trim()) -ne $LocalRoot) {
        throw 'MDI_LOCAL_ROOT in local.env conflicts with the selected external root.'
      }
      [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
    }
  }
  $env:MDI_LOCAL_ROOT = $LocalRoot
  $env:MDI_DATA_ROOT = if ($env:MDI_DATA_ROOT) { $env:MDI_DATA_ROOT } else { Join-Path $LocalRoot "data" }
  $env:MDI_RUNTIME_ROOT = if ($env:MDI_RUNTIME_ROOT) { $env:MDI_RUNTIME_ROOT } else { Join-Path $LocalRoot "run" }
  $env:MDI_LOG_ROOT = if ($env:MDI_LOG_ROOT) { $env:MDI_LOG_ROOT } else { Join-Path $LocalRoot "logs" }
  $env:MDI_TEMP_ROOT = if ($env:MDI_TEMP_ROOT) { $env:MDI_TEMP_ROOT } else { Join-Path $LocalRoot "tmp" }
  $env:MDI_CACHE_ROOT = if ($env:MDI_CACHE_ROOT) { $env:MDI_CACHE_ROOT } else { Join-Path $LocalRoot "cache" }
  $env:MDI_NEXT_DIST_DIR = if ($env:MDI_NEXT_DIST_DIR) { $env:MDI_NEXT_DIST_DIR } else { Join-Path $env:MDI_CACHE_ROOT "next" }
  $env:MDI_ARTIFACT_ROOT = if ($env:MDI_ARTIFACT_ROOT) { $env:MDI_ARTIFACT_ROOT } else { Join-Path $env:MDI_DATA_ROOT "artifacts" }
  $env:TEMP = $env:MDI_TEMP_ROOT
  $env:TMP = $env:MDI_TEMP_ROOT
  $env:TMPDIR = $env:MDI_TEMP_ROOT
  $script:StateFile = Join-Path $env:MDI_RUNTIME_ROOT "state\services.json"
  $env:MDI_API_PROXY_TARGET = if ($env:MDI_API_PROXY_TARGET) { $env:MDI_API_PROXY_TARGET } else { "http://127.0.0.1:8005" }
  $env:MINIO_ROOT_USER = $env:MINIO_ACCESS_KEY
  $env:MINIO_ROOT_PASSWORD = $env:MINIO_SECRET_KEY
  if ($env:MDI_NODE_EXE) {
    $nodeDirectory = Split-Path -Parent $env:MDI_NODE_EXE
    if (-not (Test-Path -LiteralPath $env:MDI_NODE_EXE -PathType Leaf)) { throw 'MDI_NODE_EXE does not point to a file.' }
    $env:PATH = "$nodeDirectory;$env:PATH"
  }
  $env:PYTHONPATH = @(
    (Join-Path $Repo "apps\api"),
    (Join-Path $Repo "packages\schemas"),
    (Join-Path $Repo "packages\tool-registry"),
    (Join-Path $Repo "packages\adapters"),
    (Join-Path $Repo "packages\artifact-core"),
    (Join-Path $Repo "packages\material-parsers"),
    (Join-Path $Repo "services\workers"),
    (Join-Path $Repo "services\llm")
  ) -join ';'
  foreach ($path in @($env:MDI_DATA_ROOT, $env:MDI_RUNTIME_ROOT, $env:MDI_LOG_ROOT, $env:MDI_CACHE_ROOT, $env:MDI_NEXT_DIST_DIR, $env:MDI_TEMP_ROOT, $env:MDI_ARTIFACT_ROOT, (Split-Path $StateFile -Parent))) {
    $absolute = [IO.Path]::GetFullPath($path)
    if (-not [IO.Path]::IsPathRooted($path) -or $absolute -eq $Repo -or $absolute.StartsWith("$Repo\", [StringComparison]::OrdinalIgnoreCase)) {
      throw 'Runtime, data, artifact, log, cache and temporary paths must be absolute and outside the repository.'
    }
    if ([IO.Path]::GetFullPath($path) -ne [IO.Path]::GetFullPath($env:MDI_NEXT_DIST_DIR)) {
      New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
  }
}

function Ensure-FrontendDistDirectory {
  $linkPath = Join-Path $Repo "apps\web\.cache\next"
  $targetPath = [IO.Path]::GetFullPath($env:MDI_NEXT_DIST_DIR)
  if ($targetPath -eq $Repo -or $targetPath.StartsWith("$Repo\", [StringComparison]::OrdinalIgnoreCase)) {
    throw 'MDI_NEXT_DIST_DIR must be outside the repository.'
  }
  New-Item -ItemType Directory -Path (Split-Path $linkPath -Parent) -Force | Out-Null
  if (Test-Path -LiteralPath $linkPath) {
    $existing = Get-Item -LiteralPath $linkPath -Force
    if ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) {
      $recordedTarget = [IO.Path]::GetFullPath([string]$existing.Target)
      if ($recordedTarget -ne $targetPath) {
        throw 'The Next.js output junction points to a different directory; leaving it untouched.'
      }
      return
    }
    if (Test-Path -LiteralPath $targetPath) {
      if (@(Get-ChildItem -LiteralPath $targetPath -Force).Count -gt 0) {
        throw 'MDI_NEXT_DIST_DIR already contains files and the repository Next.js output also exists; neither directory was changed.'
      }
      Remove-Item -LiteralPath $targetPath
    }
    New-Item -ItemType Directory -Path (Split-Path $targetPath -Parent) -Force | Out-Null
    Move-Item -LiteralPath $linkPath -Destination $targetPath
  }
  New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
  New-Item -ItemType Junction -Path $linkPath -Target $targetPath | Out-Null
}

function Get-Python {
  $python = if ($env:MDI_PYTHON -and $env:MDI_PYTHON -ne 'python') { $env:MDI_PYTHON } else { Join-Path $Repo '.venv\Scripts\python.exe' }
  if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Python environment missing. Run uv sync --locked --extra test first.' }
  return $python
}

function Invoke-Setup([string]$Action, [string[]]$Extra = @()) {
  & (Get-Python) (Join-Path $Repo 'scripts\local_setup.py') $Action @Extra
  if ($LASTEXITCODE -ne 0) { throw "Local setup '$Action' failed. See diagnostic above." }
}

function Get-ServicePort([string]$Name) {
  $value = switch ($Name) {
    'postgres' { if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } elseif ($env:MDI_POSTGRES_PORT) { $env:MDI_POSTGRES_PORT } else { '55434' } }
    'redis' { if ($env:REDIS_URL) { ([uri]$env:REDIS_URL).Port } else { '6380' } }
    'minio' { if ($env:MINIO_ENDPOINT) { ([uri]$env:MINIO_ENDPOINT).Port } else { '9000' } }
    'console' { if ($env:MDI_MINIO_CONSOLE_PORT) { $env:MDI_MINIO_CONSOLE_PORT } else { '9001' } }
    'api' { if ($env:MDI_API_PROXY_TARGET) { ([uri]$env:MDI_API_PROXY_TARGET).Port } else { '8005' } }
    'frontend' { if ($env:MDI_WEB_PORT) { $env:MDI_WEB_PORT } else { '3023' } }
  }
  $port = 0
  if (-not [int]::TryParse([string]$value, [ref]$port) -or $port -lt 1 -or $port -gt 65535) {
    throw "Invalid port for $Name; use an explicit port in local.env."
  }
  return $port
}

function Resolve-ServiceBinary([string]$Name) {
  $candidates = switch ($Name) {
    'postgres' { if ($env:MDI_POSTGRES_BIN) { Join-Path $env:MDI_POSTGRES_BIN 'pg_ctl.exe' } else { 'pg_ctl.exe' } }
    'redis' {
      if ($env:MDI_REDIS_EXE) { $env:MDI_REDIS_EXE }
      elseif ($env:MDI_REDIS_BIN) { Join-Path $env:MDI_REDIS_BIN 'memurai.exe'; Join-Path $env:MDI_REDIS_BIN 'redis-server.exe' }
      else { 'memurai.exe'; 'redis-server.exe' }
    }
    'minio' { if ($env:MDI_MINIO_BIN) { $env:MDI_MINIO_BIN } else { 'minio.exe' } }
  }
  foreach ($candidate in $candidates) {
    $found = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
  }
  throw "Missing $Name executable. Install it and set the binary override in local.env or PATH."
}

function Resolve-NodeBinary {
  $candidate = if ($env:MDI_NODE_EXE) { $env:MDI_NODE_EXE } else { 'node.exe' }
  $found = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue
  if (-not $found) { throw 'Install Node.js 22 or set MDI_NODE_EXE in local.env.' }
  return $found.Source
}

function Resolve-NpmBinary {
  $candidate = if ($env:MDI_NPM_EXE) { $env:MDI_NPM_EXE } else { 'npm.cmd' }
  $found = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue
  if (-not $found) { throw 'Install npm with Node.js or set MDI_NPM_EXE in local.env.' }
  return $found.Source
}

function Assert-OwnedListener([string]$Name, [int]$Port, $Entry) {
  $listeners = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
  if (-not $listeners) { return }
  if (-not $Entry -or -not $Entry.pid) { throw "Port $Port ($Name) is occupied without a project ownership record; choose a free port. No foreign process will be stopped." }
  $root = Get-CimInstance Win32_Process -Filter "ProcessId=$($Entry.pid)"
  if (-not $root -or -not (Test-RecordedExecutable $Entry $root $Name) -or
      [math]::Abs((([datetimeoffset]$Entry.startedAt) - ([datetimeoffset]$root.CreationDate)).TotalMilliseconds) -ge 1) {
    throw "Port $Port ($Name) has a stale or foreign process record."
  }
  $all = @(Get-CimInstance Win32_Process)
  $owned = @([int]$Entry.pid); $pending = @([int]$Entry.pid)
  while ($pending.Count) {
    $current = $pending[0]; $pending = @($pending | Select-Object -Skip 1)
    $children = @($all | Where-Object { $_.ParentProcessId -eq $current -and ([datetimeoffset]$_.CreationDate) -ge ([datetimeoffset]$Entry.startedAt) } | Select-Object -ExpandProperty ProcessId)
    $owned += $children; $pending += $children
  }
  if ($listeners | Where-Object { $_.OwningProcess -notin $owned }) { throw "Port $Port is owned by a different process." }
}

function Assert-OwnedPostgres {
  $port = Get-PostgresPort
  if (-not (Test-Port $port)) { return }
  $data = Join-Path $env:MDI_DATA_ROOT 'postgres'
  $pidFile = Join-Path $data 'postmaster.pid'
  if (-not (Test-Path -LiteralPath $pidFile)) { throw "PostgreSQL port $port is occupied by an unowned instance." }
  $record = @(Get-Content -LiteralPath $pidFile)
  $process = Get-CimInstance Win32_Process -Filter "ProcessId=$([int]$record[0])"
  $exe = Join-Path (Split-Path (Resolve-ServiceBinary 'postgres')) 'postgres.exe'
  $dataPattern = [regex]::Escape($data) -replace '\\\\', '[/\\]'
  if (-not $process -or $process.ExecutablePath -ne $exe -or
      [IO.Path]::GetFullPath($record[1]) -ne [IO.Path]::GetFullPath($data) -or [int]$record[3] -ne $port -or
      $process.CommandLine -notmatch $dataPattern -or
      [math]::Abs((([datetimeoffset]$process.CreationDate).ToUnixTimeSeconds() - [long]$record[2])) -gt 5 -or
      (Get-NetTCPConnection -State Listen -LocalPort $port | Where-Object OwningProcess -ne $process.ProcessId)) {
    throw "PostgreSQL ownership does not match data directory, process and port $port."
  }
}

function Test-LocalSetup {
  Import-LocalEnvironment
  Invoke-Setup 'check'
  foreach ($name in @('postgres', 'redis', 'minio')) { Resolve-ServiceBinary $name | Out-Null }
  Resolve-NodeBinary | Out-Null
  Resolve-NpmBinary | Out-Null
  if (-not (Test-Path (Join-Path $Repo 'apps\web\node_modules\next\package.json'))) { throw 'Run npm --prefix apps/web ci first.' }
  foreach ($key in @('REDIS_URL', 'MINIO_ENDPOINT', 'MDI_API_PROXY_TARGET')) {
    $uri = [uri][Environment]::GetEnvironmentVariable($key)
    if ($uri.Host -notin @('127.0.0.1', 'localhost') -or $uri.UserInfo -or $uri.Query -or $uri.Fragment -or
        ($key -ne 'REDIS_URL' -and ($uri.Scheme -ne 'http' -or $uri.AbsolutePath -ne '/')) -or
        ($key -eq 'REDIS_URL' -and ($uri.Scheme -ne 'redis' -or $uri.AbsolutePath -notmatch '^/\d+$'))) {
      throw "$key must describe a plain loopback service managed by dev.ps1."
    }
  }
  $ports = @('postgres', 'redis', 'minio', 'console', 'api', 'frontend') | ForEach-Object { Get-ServicePort $_ }
  if (@($ports | Select-Object -Unique).Count -ne 6) { throw 'Service ports must be distinct.' }
  $webPort = Get-ServicePort 'frontend'
  $origins = @($env:MDI_CORS_ORIGINS -split ',' | ForEach-Object { $_.Trim().TrimEnd('/') } | Where-Object { $_ })
  if ($origins -notcontains "http://127.0.0.1:$webPort" -or $origins -notcontains "http://localhost:$webPort") {
    throw "MDI_CORS_ORIGINS must include both localhost and 127.0.0.1 for MDI_WEB_PORT $webPort."
  }
  $state = Read-State
  Assert-OwnedPostgres
  foreach ($name in @('redis', 'minio', 'api', 'frontend')) { Assert-OwnedListener $name (Get-ServicePort $name) $state.services.$name }
  Assert-OwnedListener 'minio' (Get-ServicePort 'console') $state.services.minio
  'Dependencies, paths and port ownership verified.'
}

function Test-Port([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

function Get-PostgresPort {
  return Get-ServicePort 'postgres'
}

function Wait-Port([int]$Port, [bool]$Present = $true, [int]$Seconds = 30) {
  $deadline = (Get-Date).AddSeconds($Seconds)
  do {
    if ((Test-Port $Port) -eq $Present) { return }
    Start-Sleep -Milliseconds 250
  } while ((Get-Date) -lt $deadline)
  throw "Timed out waiting for port $Port present=$Present"
}

function Start-OwnedProcess([string]$Name, [string]$File, [string[]]$Arguments, [string]$WorkingDirectory) {
  $out = Join-Path $env:MDI_LOG_ROOT "$Name.out.log"
  $err = Join-Path $env:MDI_LOG_ROOT "$Name.err.log"
  foreach ($path in @($out, $err)) {
    if ((Test-Path -LiteralPath $path) -and (Get-Item -LiteralPath $path).Length -gt 10MB) {
      $previous = "$path.previous"
      if (Test-Path -LiteralPath $previous) { Remove-Item -LiteralPath $previous -Force }
      Move-Item -LiteralPath $path -Destination $previous
    }
  }
  $quoted = foreach ($argument in $Arguments) {
    if ($argument -match '[\s"]' -or $argument -eq '') {
      '"' + ($argument -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1') + '"'
    } else { $argument }
  }
  $process = Start-Process -FilePath $File -ArgumentList ($quoted -join ' ') -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
  return [ordered]@{ pid = $process.Id; startedAt = $process.StartTime.ToUniversalTime().ToString("o"); file = $File; cwd = $WorkingDirectory }
}

function Read-State {
  if (Test-Path -LiteralPath $StateFile) {
    $state = Get-Content -Raw -LiteralPath $StateFile | ConvertFrom-Json
    if ([IO.Path]::GetFullPath($state.localRoot) -ne $LocalRoot) { throw 'Runtime state belongs to a different local root.' }
    return $state
  }
  return $null
}

function Write-State($State) {
  $State | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $StateFile -Encoding utf8
}

function Test-OwnedWorker($Entry, [string]$Python, [string[]]$Arguments) {
  $processes = @(Get-CimInstance Win32_Process -ErrorAction Stop)
  $current = $processes | Where-Object { $Entry -and $_.ProcessId -eq $Entry.pid }
  $workerPrefix = '\s-m\s+"?mdi_workers\.worker_entrypoint"?(?:\s|$)'
  if (-not $current) {
    if ($processes | Where-Object { $_.CommandLine -match $workerPrefix -and $_.CommandLine -match [regex]::Escape($env:REDIS_URL) -and $_.CommandLine -match 'mdi-agent-turns\s' }) {
      throw "A worker is already running without a matching ownership record in $StateFile. Refusing to start a duplicate."
    }
    return $false
  }
  $expectedCommand = '^\s*"?' + [regex]::Escape($Python) + '"?'
  foreach ($argument in $Arguments) { $expectedCommand += '\s+"?' + [regex]::Escape($argument) + '"?' }
  $expectedCommand += '\s*$'
  $recordedStart = $null
  try { $recordedStart = [datetimeoffset]$Entry.startedAt } catch { }
  # Older records used the time after launch, so ambiguous legacy identities fail closed.
  $sameStart = $recordedStart -and $current.CreationDate -and
    [math]::Abs(($recordedStart - [datetimeoffset]$current.CreationDate).TotalMilliseconds) -lt 1
  if (-not $sameStart -or $Entry.cwd -ne $Repo -or $Entry.file -ne $Python -or
      $current.ExecutablePath -ne $Python -or $current.CommandLine -notmatch $expectedCommand) {
    throw "Recorded worker PID $($Entry.pid) cannot be verified by start time, executable, repository and worker arguments. Refusing to reuse it or start a duplicate."
  }
  return $true
}

function Get-WorkerQueues {
  return @("mdi-agent-turns", "mdi-agent-plans", "mdi-jobs", "mdi-agent-results", "mdi-agent-interpretations", "mdi-agent-reports")
}

function Get-WorkerArguments($Entry) {
  $name = if ($Entry -and $Entry.name) { [string]$Entry.name } else { "mdi-dev-multiqueue" }
  $arguments = @("-m", "mdi_workers.worker_entrypoint") + (Get-WorkerQueues) + @("--url", $env:REDIS_URL, "--name", $name)
  if ($Entry -and $Entry.localControl) { $arguments += "--local-control" }
  return $arguments
}

function Read-WorkerHealth($Entry, [string]$Action = "probe") {
  if (-not $Entry) { return [pscustomobject]@{ ready = $false; reason = "not_started" } }
  if (-not (Test-OwnedWorker $Entry $Entry.file (Get-WorkerArguments $Entry))) {
    return [pscustomobject]@{ ready = $false; reason = "process_exited" }
  }
  $processes = @(Get-CimInstance Win32_Process)
  $pids = @([int]$Entry.pid)
  # Windows venv launchers delegate to one real Python child. Accept only
  # that direct child with the identical worker arguments.
  foreach ($child in @($processes | Where-Object ParentProcessId -eq $Entry.pid)) {
    if ($child.CommandLine -like '*-m mdi_workers.worker_entrypoint*' -and
        ([datetimeoffset]$child.CreationDate) -ge ([datetimeoffset]$Entry.startedAt)) {
      $pids += [int]$child.ProcessId
    }
  }
  $name = if ($Entry.name) { [string]$Entry.name } else { "mdi-dev-multiqueue" }
  $since = ([datetimeoffset]$Entry.startedAt).AddSeconds(-1).ToUniversalTime().ToString("o")
  $result = & $Entry.file -m mdi_workers.local_control $Action --name $name --pids $pids --queues (Get-WorkerQueues) --started-after $since
  if ($LASTEXITCODE -ne 0 -and -not $result) { return [pscustomobject]@{ ready = $false; reason = "control_unavailable" } }
  return $result | ConvertFrom-Json
}

function Wait-WorkerReady($Entry, [int]$Seconds = 30) {
  $deadline = (Get-Date).AddSeconds($Seconds)
  do {
    $health = Read-WorkerHealth $Entry
    if ($health.ready -and -not $health.draining) { return $health }
    if ($health.reason -eq "process_exited") { throw "Worker exited before registering its queues. See worker.err.log." }
    Start-Sleep -Milliseconds 500
  } while ((Get-Date) -lt $deadline)
  throw "Worker did not become ready: $($health.reason). See worker.err.log."
}

function Test-RecordedExecutable($Entry, $Process, [string]$ServiceName) {
  try {
    $file = [IO.Path]::GetFullPath($Entry.file)
    $executable = [IO.Path]::GetFullPath($Process.ExecutablePath)
  } catch { return $false }
  if ($file -eq $executable) { return $true }
  # Start-Process runs the npm.cmd frontend launcher through Windows cmd.exe.
  # Accept only its exact recorded script and the project's frontend command.
  if ($ServiceName -ne "frontend" -or $file -ne [IO.Path]::GetFullPath((Resolve-NpmBinary)) -or
      $Entry.cwd -ne $Repo -or $executable -ne (Join-Path $env:SystemRoot "System32\cmd.exe")) { return $false }
  $pattern = '^\s*"?' + [regex]::Escape($executable) + '"?\s+/c\s+"?"' + [regex]::Escape($file) +
    '"\s+--prefix\s+apps[/\\]web\s+run\s+dev\s+--\s+-p\s+' + (Get-ServicePort 'frontend') + '\s+-H\s+127\.0\.0\.1"?\s*$'
  return $Process.CommandLine -match $pattern
}

function Stop-OwnedTree([int]$RootPid, [string]$RecordedWorkingDirectory) {
  $root = Get-CimInstance Win32_Process -Filter "ProcessId=$RootPid" -ErrorAction SilentlyContinue
  if (-not $root) { return }
  $state = Read-State
  $records = @($state.services.PSObject.Properties | Where-Object { $_.Value.pid -eq $RootPid })
  if ($records.Count -ne 1) { throw "Cannot verify ownership record for PID $RootPid" }
  $entry = $records[0].Value
  if ($entry.cwd -ne $RecordedWorkingDirectory -or -not (Test-RecordedExecutable $entry $root $records[0].Name) -or
      [math]::Abs((([datetimeoffset]$entry.startedAt) - ([datetimeoffset]$root.CreationDate)).TotalMilliseconds) -ge 1) {
    throw "Process identity changed for PID $RootPid; refusing to stop it."
  }
  $identity = "$($root.ExecutablePath) $($root.CommandLine)"
  $recordedOwner = $RecordedWorkingDirectory -and (
    $RecordedWorkingDirectory -eq $Repo -or
    $RecordedWorkingDirectory -eq $LocalRoot -or
    $RecordedWorkingDirectory.StartsWith("$Repo\", [System.StringComparison]::OrdinalIgnoreCase) -or
    $RecordedWorkingDirectory.StartsWith("$LocalRoot\", [System.StringComparison]::OrdinalIgnoreCase)
  )
  if (-not $recordedOwner -and $identity -notlike "*$Repo*" -and $identity -notlike "*$LocalRoot*") {
    throw "Refusing to stop PID $RootPid because ownership is not proven"
  }
  $all = Get-CimInstance Win32_Process
  $pending = @($RootPid); $owned = @()
  while ($pending.Count) {
    $current = $pending[0]; $pending = @($pending | Select-Object -Skip 1)
    $owned += $current
    $pending += @($all | Where-Object ParentProcessId -eq $current | Select-Object -ExpandProperty ProcessId)
  }
  [array]::Reverse($owned)
  foreach ($pidValue in $owned) {
    $snapshot = $all | Where-Object ProcessId -eq $pidValue
    $live = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
    if ($live -and [math]::Abs((([datetimeoffset]$live.StartTime) - ([datetimeoffset]$snapshot.CreationDate)).TotalMilliseconds) -lt 1) {
      $live.Kill()
      $live.WaitForExit(10000) | Out-Null
    }
  }
}

function Start-Stack([switch]$StorageOnly) {
  Test-LocalSetup
  $pgPort = Get-PostgresPort
  $state = [ordered]@{ localRoot = $LocalRoot; services = [ordered]@{} }
  $previous = Read-State
  if ($previous) {
    if ([IO.Path]::GetFullPath($previous.localRoot) -ne [IO.Path]::GetFullPath($LocalRoot)) {
      throw "Runtime state belongs to a different local root: $StateFile"
    }
    foreach ($service in $previous.services.PSObject.Properties) { $state.services[$service.Name] = $service.Value }
  }
  $pgBin = Split-Path (Resolve-ServiceBinary 'postgres')
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (-not (Test-Port $pgPort)) {
    Invoke-Setup 'cluster' @('--pg-bin', $pgBin)
    $pgLog = Join-Path $env:MDI_LOG_ROOT "postgres.log"
    $PSNativeCommandUseErrorActionPreference = $false
    & (Join-Path $pgBin "pg_ctl.exe") start -D $pgData -l $pgLog -o "-p $pgPort -h 127.0.0.1" -w
    $pgExitCode = $LASTEXITCODE
    if ($pgExitCode -ne 0) {
      $diagnostic = "Check Windows IPv4 TCP exclusions with: netsh interface ipv4 show excludedportrange protocol=tcp"
      try {
        $ranges = & netsh interface ipv4 show excludedportrange protocol=tcp 2>$null
        foreach ($line in $ranges) {
          if ($line -match '^\s*(\d+)\s+(\d+)\s*\*?\s*$' -and $pgPort -ge [int]$Matches[1] -and $pgPort -le [int]$Matches[2]) {
            $diagnostic = "PostgreSQL port $pgPort is in Windows' excluded IPv4 TCP range $($Matches[1])-$($Matches[2])."
            break
          }
        }
      } catch { } # Diagnostic failure must not hide the pg_ctl error.
      throw "pg_ctl start failed (exit $pgExitCode) on port $pgPort. See $pgLog. $diagnostic No later services were started."
    }
  }
  $state.services.postgres = [ordered]@{ data = $pgData; port = $pgPort }
  Write-State $state

  $redisPort = Get-ServicePort 'redis'
  $minioPort = Get-ServicePort 'minio'
  $consolePort = Get-ServicePort 'console'
  $apiPort = Get-ServicePort 'api'
  $webPort = Get-ServicePort 'frontend'
  if (-not (Test-Port $redisPort)) {
    $redisRoot = Join-Path $env:MDI_DATA_ROOT "redis"
    New-Item -ItemType Directory -Path $redisRoot -Force | Out-Null
    $redisConfig = Join-Path $env:MDI_RUNTIME_ROOT "redis.conf"
    @("bind 127.0.0.1", "port $redisPort", "save `"`"", "appendonly no", "dir `"$($redisRoot -replace '\\','/')`"", "logfile `"`"") | Set-Content -LiteralPath $redisConfig -Encoding utf8NoBOM
    $redisExe = Resolve-ServiceBinary 'redis'
    $state.services.redis = Start-OwnedProcess "redis" $redisExe @($redisConfig) $LocalRoot
    Write-State $state
    Wait-Port $redisPort
  }

  if (-not (Test-Port $minioPort)) {
    $minioData = Join-Path $env:MDI_DATA_ROOT "minio"
    New-Item -ItemType Directory -Path $minioData -Force | Out-Null
    $state.services.minio = Start-OwnedProcess "minio" (Resolve-ServiceBinary 'minio') @("server", $minioData, "--address", "127.0.0.1:$minioPort", "--console-address", "127.0.0.1:$consolePort") $LocalRoot
    Write-State $state
    Wait-Port $minioPort
  }

  if ($StorageOnly) { return }
  Invoke-Setup 'ready'
  $python = Get-Python
  if (-not (Test-Port $apiPort)) {
    $state.services.api = Start-OwnedProcess "api" $python @("-m", "uvicorn", "mdi_api.main:app", "--host", "127.0.0.1", "--port", "$apiPort") $Repo
    Write-State $state
    Wait-Port $apiPort -Seconds 90
  }
  for ($attempt = 0; $attempt -lt 2; $attempt++) {
    $workerArguments = Get-WorkerArguments $state.services.worker
    if (-not (Test-OwnedWorker $state.services.worker $python $workerArguments)) {
      $workerName = "mdi-dev-multiqueue-" + [guid]::NewGuid().ToString("N")
      $workerArguments = Get-WorkerArguments ([pscustomobject]@{ name = $workerName; localControl = $true })
      $state.services.worker = Start-OwnedProcess "worker" $python $workerArguments $Repo
      $state.services.worker.name = $workerName
      $state.services.worker.localControl = $true
      Write-State $state
    }
    try { Wait-WorkerReady $state.services.worker | Out-Null; break }
    catch {
      # A drained worker may finish between the process and queue probes.
      if ($attempt -eq 1 -or (Test-OwnedWorker $state.services.worker $python (Get-WorkerArguments $state.services.worker))) { throw }
    }
  }
  if (-not (Test-Port $webPort)) {
    $npm = Resolve-NpmBinary
    Ensure-FrontendDistDirectory
    $state.services.frontend = Start-OwnedProcess "frontend" $npm @("--prefix", "apps/web", "run", "dev", "--", "-p", "$webPort", "-H", "127.0.0.1") $Repo
    Write-State $state
    Wait-Port $webPort -Seconds 30
  }
  Write-State $state
  Show-Status
}

function Stop-Stack {
  Import-LocalEnvironment
  $pgPort = Get-PostgresPort
  $state = Read-State
  if ($state) {
    foreach ($name in @("frontend", "worker", "api", "minio", "redis")) {
      $entry = $state.services.$name
      if ($entry -and $entry.pid) { Stop-OwnedTree ([int]$entry.pid) ([string]$entry.cwd) }
    }
  }
  $pgBin = Split-Path (Resolve-ServiceBinary 'postgres')
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (Test-Port $pgPort) {
    Assert-OwnedPostgres
    & (Join-Path $pgBin "pg_ctl.exe") stop -D $pgData -m fast -w
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL did not stop; state is retained.' }
  }
  if (Test-Path -LiteralPath $StateFile) { Remove-Item -LiteralPath $StateFile -Force }
  Show-Status
}

function Show-Status {
  $pgPort = Get-PostgresPort
  $rows = @(
    [pscustomobject]@{ Service = "PostgreSQL"; Port = $pgPort; Listening = Test-Port $pgPort },
    [pscustomobject]@{ Service = "Redis"; Port = (Get-ServicePort 'redis'); Listening = Test-Port (Get-ServicePort 'redis') },
    [pscustomobject]@{ Service = "MinIO"; Port = (Get-ServicePort 'minio'); Listening = Test-Port (Get-ServicePort 'minio') },
    [pscustomobject]@{ Service = "FastAPI"; Port = (Get-ServicePort 'api'); Listening = Test-Port (Get-ServicePort 'api') },
    [pscustomobject]@{ Service = "Next.js"; Port = (Get-ServicePort 'frontend'); Listening = Test-Port (Get-ServicePort 'frontend') }
  )
  $rows | Format-Table -AutoSize
  $state = Read-State
  if ($state -and $state.services.worker) {
    try {
      $health = Read-WorkerHealth $state.services.worker
      "Worker: " + $(if ($health.ready) { "$($health.state) (PID $($health.pid), six logical queues; draining=$($health.draining))" } else { "not ready ($($health.reason))" })
    } catch { "Worker: ownership or readiness could not be verified" }
  }
}

function Restart-AppServices {
  Import-LocalEnvironment
  $state = Read-State
  if (-not $state -or $state.localRoot -ne $LocalRoot) { throw "No matching project runtime state" }
  $worker = $state.services.worker
  if (-not $worker.localControl) { throw "This legacy Worker does not support graceful app restart. Keep it running until a verified idle replacement is available." }
  $health = Read-WorkerHealth $worker
  if (-not $health.ready -or $health.state -ne "idle") { throw "Worker is not verified idle. Current work and services remain running." }
  $api = $state.services.api
  $apiProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$($api.pid)"
  if (-not $apiProcess -or $api.cwd -ne $Repo -or $api.file -ne $apiProcess.ExecutablePath -or
      $apiProcess.CommandLine -notlike '*-m uvicorn mdi_api.main:app*' -or
      [math]::Abs((([datetimeoffset]$api.startedAt) - ([datetimeoffset]$apiProcess.CreationDate)).TotalMilliseconds) -ge 1) {
    throw "API process ownership could not be verified"
  }
  try {
    $drain = Read-WorkerHealth $worker "drain"
    if (-not $drain.ready) { throw "Worker identity changed before drain" }
    $deadline = (Get-Date).AddSeconds(30)
    while (Get-Process -Id $worker.pid -ErrorAction SilentlyContinue) {
      if ((Get-Date) -gt $deadline) {
        $resumed = Read-WorkerHealth $worker "resume"
        if (-not $resumed.ready) { throw "Worker drain withdrawal could not be confirmed; checking application availability." }
        throw "Worker is finishing a task; app restart deferred and drain withdrawn."
      }
      Start-Sleep -Milliseconds 250
    }
    Stop-OwnedTree ([int]$api.pid) $api.cwd
    Wait-Port (Get-ServicePort 'api') $false
  } finally {
    Start-Stack
  }
}

function Restart-FrontendService {
  Import-LocalEnvironment
  $state = Read-State
  if (-not $state -or $state.localRoot -ne $LocalRoot -or -not $state.services.frontend.pid) {
    throw "No matching project frontend runtime state"
  }
  try {
    $frontend = $state.services.frontend
    Stop-OwnedTree ([int]$frontend.pid) ([string]$frontend.cwd)
    Wait-Port (Get-ServicePort 'frontend') $false
  } finally {
    Start-Stack
  }
}

if ($Scope -ne "all" -and $Command -ne "restart") { throw "-Scope $Scope is supported only with restart" }
switch ($Command) {
  "init" { Invoke-Setup 'init' @('--local-root', $LocalRoot) }
  "doctor" { Test-LocalSetup }
  "migrate" {
    Import-LocalEnvironment
    $state = Read-State
    if ((Test-Port (Get-ServicePort 'api')) -or
        (Test-OwnedWorker $state.services.worker (Get-Python) (Get-WorkerArguments $state.services.worker))) {
      throw 'Stop the project API and Worker before migrating. Use dev.ps1 stop, migrate, then start.'
    }
    Start-Stack -StorageOnly
    Invoke-Setup 'database'
    Invoke-Setup 'bucket'
  }
  "start" { Start-Stack }
  "stop" { Stop-Stack }
  "restart" {
    if ($Scope -eq "app") { Restart-AppServices }
    elseif ($Scope -eq "frontend") { Restart-FrontendService }
    else { Stop-Stack; Start-Stack }
  }
  "status" { Import-LocalEnvironment; Show-Status }
}
