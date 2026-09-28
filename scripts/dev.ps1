param(
  [Parameter(Position = 0)]
  [ValidateSet("start", "stop", "restart", "status")]
  [string]$Command = "status"
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
  foreach ($path in @($env:MDI_DATA_ROOT, $env:MDI_RUNTIME_ROOT, $env:MDI_LOG_ROOT, (Join-Path $LocalRoot "cache"), (Join-Path $LocalRoot "tmp"), (Split-Path $StateFile -Parent))) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
  }
}

function Test-Port([int]$Port) {
  return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
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
  return [ordered]@{ pid = $process.Id; startedAt = (Get-Date).ToString("o"); file = $File; cwd = $WorkingDirectory }
}

function Read-State {
  if (Test-Path -LiteralPath $StateFile) { return Get-Content -Raw -LiteralPath $StateFile | ConvertFrom-Json }
  return $null
}

function Write-State($State) {
  $State | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $StateFile -Encoding utf8
}

function Stop-OwnedTree([int]$RootPid, [string]$RecordedWorkingDirectory) {
  $root = Get-CimInstance Win32_Process -Filter "ProcessId=$RootPid" -ErrorAction SilentlyContinue
  if (-not $root) { return }
  $identity = "$($root.ExecutablePath) $($root.CommandLine)"
  $recordedOwner = $RecordedWorkingDirectory -and (
    $RecordedWorkingDirectory -eq $Repo -or
    $RecordedWorkingDirectory -eq $LocalRoot -or
    $RecordedWorkingDirectory.StartsWith("$Repo\", [System.StringComparison]::OrdinalIgnoreCase) -or
    $RecordedWorkingDirectory.StartsWith("$LocalRoot\", [System.StringComparison]::OrdinalIgnoreCase)
  )
  if (-not $recordedOwner -and $identity -notlike "*$Repo*" -and $identity -notlike "*$LocalRoot*") {
    throw "Refusing to stop PID $RootPid because ownership is not proven: $identity"
  }
  $all = Get-CimInstance Win32_Process
  $pending = @($RootPid); $owned = @()
  while ($pending.Count) {
    $current = $pending[0]; $pending = @($pending | Select-Object -Skip 1)
    $owned += $current
    $pending += @($all | Where-Object ParentProcessId -eq $current | Select-Object -ExpandProperty ProcessId)
  }
  foreach ($pidValue in ($owned | Sort-Object -Descending)) {
    Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
  }
}

function Start-Stack {
  Import-LocalEnvironment
  $state = [ordered]@{ localRoot = $LocalRoot; services = [ordered]@{} }
  $pgBin = if ($env:MDI_POSTGRES_BIN) { $env:MDI_POSTGRES_BIN } else { "E:\PostgreSQL\17\bin" }
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (-not (Test-Port 55434)) {
    & (Join-Path $pgBin "pg_ctl.exe") start -D $pgData -l (Join-Path $env:MDI_LOG_ROOT "postgres.log") -o "-p 55434 -h 127.0.0.1" -w
  }
  $state.services.postgres = [ordered]@{ data = $pgData; port = 55434 }

  if (-not (Test-Port 6380)) {
    $redisRoot = Join-Path $env:MDI_DATA_ROOT "redis"
    New-Item -ItemType Directory -Path $redisRoot -Force | Out-Null
    $redisConfig = Join-Path $env:MDI_RUNTIME_ROOT "redis.conf"
    @("bind 127.0.0.1", "port 6380", "save `"`"", "appendonly no", "dir $($redisRoot -replace '\\','/')", "logfile `"`"") | Set-Content -LiteralPath $redisConfig -Encoding ascii
    $redisExe = Join-Path $env:MDI_REDIS_BIN "memurai.exe"
    $state.services.redis = Start-OwnedProcess "redis" $redisExe @($redisConfig) $LocalRoot
    Wait-Port 6380
  }

  if (-not (Test-Port 9000)) {
    $minioData = Join-Path $env:MDI_DATA_ROOT "minio"
    New-Item -ItemType Directory -Path $minioData -Force | Out-Null
    $state.services.minio = Start-OwnedProcess "minio" $env:MDI_MINIO_BIN @("server", $minioData, "--address", "127.0.0.1:9000", "--console-address", "127.0.0.1:9001") $LocalRoot
    Wait-Port 9000
  }

  $python = if ($env:MDI_PYTHON -and $env:MDI_PYTHON -ne "python") { $env:MDI_PYTHON } else { Join-Path $Repo ".venv\Scripts\python.exe" }
  if (-not (Test-Port 8005)) {
    $state.services.api = Start-OwnedProcess "api" $python @("-m", "uvicorn", "mdi_api.main:app", "--host", "127.0.0.1", "--port", "8005") $Repo
    Wait-Port 8005
  }
  $queues = @("mdi-agent-turns", "mdi-agent-plans", "mdi-jobs", "mdi-agent-results", "mdi-agent-interpretations", "mdi-agent-reports")
  $state.services.worker = Start-OwnedProcess "worker" $python (@("-m", "mdi_workers.worker_entrypoint") + $queues + @("--url", $env:REDIS_URL, "--name", "mdi-dev-multiqueue")) $Repo
  if (-not (Test-Port 3023)) {
    $npm = (Get-Command npm.cmd -ErrorAction Stop).Source
    $state.services.frontend = Start-OwnedProcess "frontend" $npm @("--prefix", "apps/web", "run", "dev", "--", "-p", "3023", "-H", "127.0.0.1") $Repo
    Wait-Port 3023 30
  }
  Write-State $state
  Show-Status
}

function Stop-Stack {
  Import-LocalEnvironment
  $state = Read-State
  if ($state) {
    foreach ($name in @("frontend", "worker", "api", "minio", "redis")) {
      $entry = $state.services.$name
      if ($entry -and $entry.pid) { Stop-OwnedTree ([int]$entry.pid) ([string]$entry.cwd) }
    }
  }
  $pgBin = if ($env:MDI_POSTGRES_BIN) { $env:MDI_POSTGRES_BIN } else { "E:\PostgreSQL\17\bin" }
  $pgData = Join-Path $env:MDI_DATA_ROOT "postgres"
  if (Test-Port 55434) { & (Join-Path $pgBin "pg_ctl.exe") stop -D $pgData -m fast -w }
  if (Test-Path -LiteralPath $StateFile) { Remove-Item -LiteralPath $StateFile -Force }
  Show-Status
}

function Show-Status {
  $rows = @(
    [pscustomobject]@{ Service = "PostgreSQL"; Port = 55434; Listening = Test-Port 55434 },
    [pscustomobject]@{ Service = "Redis"; Port = 6380; Listening = Test-Port 6380 },
    [pscustomobject]@{ Service = "MinIO"; Port = 9000; Listening = Test-Port 9000 },
    [pscustomobject]@{ Service = "FastAPI"; Port = 8005; Listening = Test-Port 8005 },
    [pscustomobject]@{ Service = "Next.js"; Port = 3023; Listening = Test-Port 3023 }
  )
  $rows | Format-Table -AutoSize
  $state = Read-State
  if ($state -and $state.services.worker) {
    $worker = Get-Process -Id ([int]$state.services.worker.pid) -ErrorAction SilentlyContinue
    "Worker: " + $(if ($worker) { "running (PID $($worker.Id), six logical queues)" } else { "stopped" })
  }
}

switch ($Command) {
  "start" { Start-Stack }
  "stop" { Stop-Stack }
  "restart" { Stop-Stack; Start-Stack }
  "status" { Import-LocalEnvironment; Show-Status }
}
