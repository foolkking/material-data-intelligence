# Phase 10J-5 ELF / Orbital Volumetric Product Evidence

This evidence consumes real ELFCAR, PARCHG, and explicitly identified CUBE artifacts produced through Mock Planner, QueueWorkerRuntime, the canonical volumetric adapter, and job-scoped artifact content routes. Browser evidence uses the existing application-owned Worker and Three.js renderer; source field bytes are not clamped, squared, normalized, or reinterpreted from filenames.

## Replay

```powershell
uv run python apps/web/test/generate-elf-orbital-evidence.py
npm --prefix apps/web run build
node apps/web/test/elf-orbital-product-browser-evidence.mjs
```
