[CmdletBinding()]
param(
  [string[]]$CheckPath = @(),

  [Nullable[long]]$MinimumFreeBytes,

  [Nullable[long]]$WarningFreeBytes
)

$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$arguments = @(
  (Join-Path $repo "scripts\phase14r_disk_preflight.py")
)
foreach ($path in $CheckPath) {
  $arguments += @("--check-path", $path)
}
if ($PSBoundParameters.ContainsKey("MinimumFreeBytes")) {
  $arguments += @("--minimum-free-bytes", [string]$MinimumFreeBytes)
}
if ($PSBoundParameters.ContainsKey("WarningFreeBytes")) {
  $arguments += @("--warning-free-bytes", [string]$WarningFreeBytes)
}
if (-not [string]::IsNullOrWhiteSpace($env:MDI_DISK_FALLBACK_PATH)) {
  $arguments += @("--fallback-path", $env:MDI_DISK_FALLBACK_PATH)
}

& python.exe @arguments
exit $LASTEXITCODE
