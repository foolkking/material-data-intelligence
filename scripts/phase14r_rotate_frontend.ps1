[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [ValidateRange(1024, 65535)]
  [int]$CurrentPort = 3024,

  [int[]]$CandidatePorts = (3000..3023),

  [ValidatePattern("^/")]
  [string]$HealthPath = "/",

  [switch]$Apply
)

$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$nextBinaryFragment = [IO.Path]::Combine(
  $repo,
  "apps",
  "web",
  "node_modules",
  "next",
  "dist",
  "bin",
  "next"
)

function Test-FrontendHealth([int]$Port) {
  try {
    $response = Invoke-WebRequest `
      -Uri "http://127.0.0.1:$Port$HealthPath" `
      -UseBasicParsing `
      -TimeoutSec 10
    return $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
  } catch {
    return $false
  }
}

function Test-RepositoryNextListener(
  [Microsoft.Management.Infrastructure.CimInstance]$Process,
  [int]$Port
) {
  if ($null -eq $Process -or $Process.Name -ne "node.exe") {
    return $false
  }
  $commandLine = [string]$Process.CommandLine
  if (-not $commandLine.Contains($nextBinaryFragment, [StringComparison]::OrdinalIgnoreCase)) {
    return $false
  }
  if ($commandLine -notmatch "(?i)\bnext\b.*\bstart\b") {
    return $false
  }
  return $commandLine -match "(?i)(?:^|\s)-p(?:ort)?(?:\s+|=)$Port(?:\s|$)"
}

if (-not (Test-FrontendHealth $CurrentPort)) {
  throw "Current frontend did not pass the HTTP health check on port $CurrentPort."
}

$candidatePortSet = @(
  $CandidatePorts |
    Where-Object {
      $_ -ge 1024 -and $_ -le 65535 -and $_ -ne $CurrentPort
    } |
    Sort-Object -Unique
)
$listeners = @(
  Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in $candidatePortSet }
)
$processById = @{}
foreach ($listener in $listeners) {
  $processId = [int]$listener.OwningProcess
  if (-not $processById.ContainsKey($processId)) {
    $processById[$processId] = Get-CimInstance Win32_Process `
      -Filter "ProcessId = $processId" `
      -ErrorAction SilentlyContinue
  }
}

$eligible = @()
$skipped = @()
foreach ($listener in $listeners) {
  $processId = [int]$listener.OwningProcess
  $record = [ordered]@{
    port = [int]$listener.LocalPort
    pid = $processId
  }
  if (Test-RepositoryNextListener $processById[$processId] $listener.LocalPort) {
    $eligible += [pscustomobject]$record
  } else {
    $skipped += [pscustomobject]([ordered]@{
      port = [int]$listener.LocalPort
      pid = $processId
      reason = "NOT_REPOSITORY_NEXT_START"
    })
  }
}

$stopped = @()
if ($Apply) {
  foreach ($candidate in $eligible) {
    if (
      $PSCmdlet.ShouldProcess(
        "repository frontend PID $($candidate.pid) on port $($candidate.port)",
        "Stop obsolete frontend"
      )
    ) {
      Stop-Process -Id $candidate.pid -Force -ErrorAction Stop
      $stopped += $candidate
    }
  }
}

Start-Sleep -Milliseconds 250
if (-not (Test-FrontendHealth $CurrentPort)) {
  throw "Current frontend became unhealthy during rotation on port $CurrentPort."
}

[pscustomobject]([ordered]@{
  schemaVersion = "phase14r-frontend-rotation/1.0"
  mode = if ($Apply) { "apply" } else { "dry-run" }
  current = [ordered]@{
    port = $CurrentPort
    healthy = $true
  }
  eligible = @($eligible)
  stopped = @($stopped)
  skipped = @($skipped)
}) | ConvertTo-Json -Depth 5
