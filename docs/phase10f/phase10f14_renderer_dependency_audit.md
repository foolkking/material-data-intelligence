# Phase 10F-14 Renderer Dependency Audit

`three@0.185.1` is MIT and has no runtime dependencies or install script. `@types/three@0.185.1` is development-only and adds seven type-support packages in the lockfile.

`npm audit` through the configured mirror was unsupported. The official registry audit reported 7 pre-existing findings: 1 critical Vitest, 1 high Vite and 5 moderate Vite/Next/PostCSS related findings. None names `three` or the new renderer dependency graph. The issues remain repository dependency debt and were not addressed by unrelated major upgrades in this phase.
