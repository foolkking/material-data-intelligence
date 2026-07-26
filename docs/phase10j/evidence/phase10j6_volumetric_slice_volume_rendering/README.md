# Phase 10J-6 Volumetric Slice / Volume Rendering Evidence

Real committed CHGCAR, LOCPOT, ELFCAR, PARCHG, and triclinic CUBE inputs are routed through Mock Planner, /planner/jobs, QueueWorkerRuntime, the canonical adapter, artifact persistence, frontend validation, the application-owned Slice Worker, and the WebGL2 direct-volume renderer.

## Replay

```powershell
uv run python apps/web/test/generate-volumetric-slice-volume-evidence.py
npm --prefix apps/web run build
node apps/web/test/volumetric-slice-volume-browser-evidence.mjs
```
