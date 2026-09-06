# Product Maturity — Route Continuity Batch (2026-09-01)

## Scope

Close the user-visible Dataset/project navigation seam without changing
scientific authority, worker execution, or the existing route architecture.

## Root cause

The dedicated `DatasetWorkbenchPage` used root-level `/` and `/analysis`
links, and the project home used the legacy `/analysis` compatibility entry
even after a concrete project had been loaded. Those links made normal
project-scoped data work feel like a dead end and could discard the user's
project context.

## Fix

- Dataset workbench breadcrumb and “返回项目” now resolve to the current
  project route.
- Dataset workbench “导入其他数据” now resolves to the current project's
  dataset upload route.
- Project home import actions now resolve to the current project's dataset
  upload route once the project identity is known, while retaining `/analysis`
  only as the no-project compatibility fallback.
- All links continue through `ProductLink`/`ProductNavigation`; no full-page
  reload or new navigation framework was introduced.

## Verification

- `DatasetWorkbenchPage.test.tsx`: 1 passed.
- `ProjectHome.test.tsx`: 3 passed.
- `ProductPages.test.tsx`: 40 passed.
- TypeScript typecheck: PASS.
- `git diff --check`: PASS (existing LF/CRLF normalization warnings only).
- Existing API, frontend, PostgreSQL, Redis, MinIO, worker processes remain
  running; the stateless `3000 → 3013` compatibility alias was also restored
  after a transient process exit and now listens on port 3000. No service or
  browser tab was closed.

## Authority safety

No ScientificObject, ScientificObjectVersion, ScientificResult, Artifact,
Report, provenance, authorization, or queue contract was changed.
