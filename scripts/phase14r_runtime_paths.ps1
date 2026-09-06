function Get-MdiManagedRuntimeRoot([string]$RepositoryRoot) {
  $repo = [IO.Path]::GetFullPath($RepositoryRoot)
  return [IO.Path]::GetFullPath(
    (Join-Path $repo ".runtime_services\managed")
  )
}

function Get-MdiApiRuntimeDirectory([string]$RepositoryRoot) {
  return Join-Path (Get-MdiManagedRuntimeRoot $RepositoryRoot) "api"
}

function Get-MdiWorkerRuntimeDirectory([string]$RepositoryRoot) {
  return Join-Path (Get-MdiManagedRuntimeRoot $RepositoryRoot) "workers"
}
