param(
  [Parameter(Position = 0)]
  [ValidateSet("start", "stop", "restart", "status")]
  [string]$Command = "status",
  [ValidateSet("all", "app", "frontend")]
  [string]$Scope = "all"
)

$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DefaultLocalRoot = Join-Path (Split-Path $Repo -Parent) "$(Split-Path $Repo -Leaf).local"
$LocalRoot = if ($env:MDI_LOCAL_ROOT) { $env:MDI_LOCAL_ROOT } else { $DefaultLocalRoot }
$EnvFile = Join-Path $LocalRoot "local.env"
$StateFile = Join-Path $LocalRoot "run\state\services.json"

function Import-LocalEnvironment {
  if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Missing $EnvFile. Copy .env.example there and set local credentials/binary paths."
  }
  Get-Content -LiteralPath $EnvFile | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') {
      [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
    }
  }
  $env:MDI_LOCAL_ROOT = $LocalRoot
  $env:MDI_DATA_ROOT = if ($env:MDI_DATA_ROOT) { $env:MDI_DATA_ROOT } else { Join-Path $LocalRoot "data" }
  $env:MDI_RUNTIME_ROOT = if ($env:MDI_RUNTIME_ROOT) { $env:MDI_RUNTIME_ROOT } else { Join-Path $LocalRoot "run" }
  $env:MDI_LOG_ROOT = if ($env:MDI_LOG_ROOT) { $env:MDI_LOG_ROOT } else { Join-Path $LocalRoot "logs" }
  $env:MDI_TEMP_ROOT = if ($env:MDI_TEMP_ROOT) { $env:MDI_TEMP_ROOT } else { Join-Path $LocalRoot "tmp" }
  $env:TEMP = $env:MDI_TEMP_ROOT
  $env:TMP = $env:MDI_TEMP_ROOT
  $env:TMPDIR = $env:MDI_TEMP_ROOT
  $env:MDI_AGENT2_ORCHESTRATION_ENABLED = "true"
  $env:MDI_AGENT2_INTERPRETATION_ENABLED = "true"
  $env:MDI_AGENT2_REPORT_ENABLED = "true"
  $env:MDI_API_PROXY_TARGET = if ($env:MDI_API_PROXY_TARGET) { $env:MDI_API_PROXY_TARGET } else { "http://127.0.0.1:8005" }
  $env:MINIO_ROOT_USER = $env:MINIO_ACCESS_KEY
  $env:MINIO_ROOT_PASSWORD = $env:MINIO_SECRET_KEY
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
  foreach ($path in @($env:MDI_DATA_ROOT, $env:MDI_RUNTIME_ROOT, $env:MDI_LOG_ROOT, (Join-Path $LocalRoot "cache"), $env:MDI_TEMP_ROOT, (Split-Path $StateFile -Parent))) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
  }
}

function Test-Port([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

function Get-PostgresPort {
  $port = 55434
  if ($env:MDI_POSTGRES_PORT -and (-not [int]::TryParse($env:MDI_POSTGRES_PORT, [ref]$port) -or $port -lt 1 -or $port -gt 65535)) {
    throw "MDI_POSTGRES_PORT must be an integer between 1 and 65535."
  }
  return $port
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
  $process = Start-Process -FilePath $File -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
  return [ordered]@{ pid = $process.Id; startedAt = $process.StartTime.ToUniversalTime().ToString("o"); file = $File; cwd = $WorkingDirectory }
}

function Read-State {
  if (Test-Path -LiteralPath $StateFile) { return Get-Content -Raw -LiteralPath $StateFile | ConvertFrom-Json }
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
  if ($ServiceName -ne "frontend" -or (Split-Path $file -Leaf) -ne "npm.cmd" -or
      $Entry.cwd -ne $Repo -or $executable -ne (Join-Path $env:SystemRoot "System32\cmd.exe")) { return $false }
  $pattern = '^\s*"?' + [regex]::Escape($executable) + '"?\s+/c\s+"?"' + [regex]::Escape($file) +
    '"\s+--prefix\s+apps[/\\]web\s+run\s+dev\s+--\s+-p\s+3023\s+-H\s+127\.0\.0\.1"?\s*$'
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

function Start-Stack {
  Import-LocalEnvironment
  $pgPort = Get-PostgresPort
  $state = [ordered]@{ localRoot = $LocalRoot; services = [ordered]@{} }
  $previous = Read-State
  if ($previous) {
    if ([IO.Path]::GetFullPath($previous.localRoot) -ne [IO.Path]::GetFullPath($LocalRoot)) {
      throw "Runtime state belongs to a different local root: $StateFile"
    }
    foreach ($service in $previous.services.PSObject.Properties) { $state.services[$service.Name] = $service.Value }
  }
  $pgBin = if ($env:MDI_POSTGRES_BIN) { $env:MDI_POSTGRES_BIN } else { "E:\PostgreSQL\17\bin" }
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (-not (Test-Port $pgPort)) {
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

  if (-not (Test-Port 6380)) {
    $redisRoot = Join-Path $env:MDI_DATA_ROOT "redis"
    New-Item -ItemType Directory -Path $redisRoot -Force | Out-Null
    $redisConfig = Join-Path $env:MDI_RUNTIME_ROOT "redis.conf"
    @("bind 127.0.0.1", "port 6380", "save `"`"", "appendonly no", "dir $($redisRoot -replace '\\','/')", "logfile `"`"") | Set-Content -LiteralPath $redisConfig -Encoding ascii
    $redisExe = Join-Path $env:MDI_REDIS_BIN "memurai.exe"
    $state.services.redis = Start-OwnedProcess "redis" $redisExe @($redisConfig) $LocalRoot
    Write-State $state
    Wait-Port 6380
  }

  if (-not (Test-Port 9000)) {
    $minioData = Join-Path $env:MDI_DATA_ROOT "minio"
    New-Item -ItemType Directory -Path $minioData -Force | Out-Null
    $state.services.minio = Start-OwnedProcess "minio" $env:MDI_MINIO_BIN @("server", $minioData, "--address", "127.0.0.1:9000", "--console-address", "127.0.0.1:9001") $LocalRoot
    Write-State $state
    Wait-Port 9000
  }

  $python = if ($env:MDI_PYTHON -and $env:MDI_PYTHON -ne "python") { $env:MDI_PYTHON } else { Join-Path $Repo ".venv\Scripts\python.exe" }
  if (-not (Test-Port 8005)) {
    $state.services.api = Start-OwnedProcess "api" $python @("-m", "uvicorn", "mdi_api.main:app", "--host", "127.0.0.1", "--port", "8005") $Repo
    Write-State $state
    Wait-Port 8005
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
  if (-not (Test-Port 3023)) {
    $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
    $state.services.frontend = Start-OwnedProcess "frontend" $npm @("--prefix", "apps/web", "run", "dev", "--", "-p", "3023", "-H", "127.0.0.1") $Repo
    Write-State $state
    Wait-Port 3023 -Seconds 30
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
  $pgBin = if ($env:MDI_POSTGRES_BIN) { $env:MDI_POSTGRES_BIN } else { "E:\PostgreSQL\17\bin" }
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (Test-Port $pgPort) { & (Join-Path $pgBin "pg_ctl.exe") stop -D $pgData -m fast -w }
  if (Test-Path -LiteralPath $StateFile) { Remove-Item -LiteralPath $StateFile -Force }
  Show-Status
}

function Show-Status {
  $pgPort = Get-PostgresPort
  $rows = @(
    [pscustomobject]@{ Service = "PostgreSQL"; Port = $pgPort; Listening = Test-Port $pgPort },
    [pscustomobject]@{ Service = "Redis"; Port = 6380; Listening = Test-Port 6380 },
    [pscustomobject]@{ Service = "MinIO"; Port = 9000; Listening = Test-Port 9000 },
    [pscustomobject]@{ Service = "FastAPI"; Port = 8005; Listening = Test-Port 8005 },
    [pscustomobject]@{ Service = "Next.js"; Port = 3023; Listening = Test-Port 3023 }
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
    Wait-Port 8005 $false
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
    Wait-Port 3023 $false
  } finally {
    Start-Stack
  }
}

if ($Scope -ne "all" -and $Command -ne "restart") { throw "-Scope $Scope is supported only with restart" }
switch ($Command) {
  "start" { Start-Stack }
  "stop" { Stop-Stack }
  "restart" {
    if ($Scope -eq "app") { Restart-AppServices }
    elseif ($Scope -eq "frontend") { Restart-FrontendService }
    else { Stop-Stack; Start-Stack }
  }
  "status" { Import-LocalEnvironment; Show-Status }
}
