# Phase 10 Closure Regression Pack

## Purpose

This pack is the long-lived regression boundary for Phase 10A through 10F. It
adds executable composition tests instead of renaming or copying historical
unit tests. No adapter, tool, artifact schema, scientific meaning, renderer
feature, runtime authority, or dependency is added.

## Architecture

1. Backend product closure executes six representative tools through Tool
   Registry, Mock Planner, PlanValidator, persisted plan/job,
   QueueWorkerRuntime, adapter, artifact store, retrieval, and validators.
2. Frontend product closure composes current v2 validation, periodic topology,
   bounded supercell, selection/measurement, clipping/camera state, performance
   refusal, scientific export, and legacy policy.
3. Browser closure runs the formal viewer product in Chromium, Firefox, WebKit,
   and mobile viewport, then records console, network, lifecycle, performance,
   fallback, accessibility, and screenshot evidence.

## Results

The representative portfolio is `table.distribution_summary`, `viz.scatter`,
`composition.summary`, `structure.summary`, `structure.xrd`, and
`structure.viewer_3d`. Current artifacts remain scene v2 and manifest v2;
legacy Phase 10D is read-only/JSON-only and canonical v1 remains same-cell.

Local entries:

```text
uv run python -m pytest -q tests/integration/test_phase10_product_closure.py -m "not integration"
npm --prefix apps/web run test:phase10-closure
npm --prefix apps/web run test:phase10-browser-evidence
powershell -File scripts/test_phase10_closure.ps1
```

Service-backed closure is part of the existing PostgreSQL/Redis/MinIO CI job
and the no-skipped threshold is 20 integration tests.

Observed local closure budget on the recorded Windows environment: backend
composition 8.3 seconds, frontend composition 1.8 seconds, and the real
three-browser/mobile suite 191 seconds. These are environment observations,
not universal performance thresholds.

Local regression result: 106 frontend tests passed; 372 backend tests passed,
22 were explicitly skipped, and 11 existing pymatgen/spglib warnings were
reported. The extra local skip is the service-backed closure because Docker is
not installed; required CI must execute it with zero integration skips.
