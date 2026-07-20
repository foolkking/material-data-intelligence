# Phase 10J-3 Charge / Spin Density Product Evidence

The browser runner consumes real collinear CHGCAR artifacts produced through Mock Planner, QueueWorkerRuntime, the canonical adapter, and job-scoped content routes. Source total/spin fields and allowlisted derived up/down fields remain inert; the application-owned Worker and Three.js renderer execute no artifact code or remote resource.

## Replay

```powershell
uv run python apps/web/test/generate-charge-spin-density-evidence.py
npm --prefix apps/web run build
node apps/web/test/charge-spin-density-browser-evidence.mjs
```

The captures cover source total and spin difference, fixed `COLLINEAR_SPIN_UP_V1`/`COLLINEAR_SPIN_DOWN_V1` derivations, full-cell integrals, augmentation warning, explicit signed charge, Chromium/Firefox/WebKit, mobile layout, accessibility, performance, console, and network isolation.
