param([switch]$SkipBrowser)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    uv run python -m pytest -q tests/integration/test_phase10_product_closure.py -m "not integration"
    if ($LASTEXITCODE -ne 0) { throw "Phase 10 backend closure failed" }
    npm --prefix apps/web run test:phase10-closure
    if ($LASTEXITCODE -ne 0) { throw "Phase 10 frontend closure failed" }
    if (-not $SkipBrowser) {
        npm --prefix apps/web run test:phase10-browser-evidence
        if ($LASTEXITCODE -ne 0) { throw "Phase 10 browser closure failed" }
    }
    node apps/web/test/phase10-closure-evidence-check.mjs
    if ($LASTEXITCODE -ne 0) { throw "Phase 10 evidence integrity failed" }
    Write-Output "PHASE10_CLOSURE_REGRESSION_PACK_PASS"
} finally {
    Pop-Location
}
