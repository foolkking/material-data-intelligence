# Local Verification

The final pre-commit local verification recorded:

```text
Phase 11-0 governance tests = 11 passed
Backend = 1263 passed, 50 skipped integration/service cases
Frontend = 449 passed
Phase 10 closure backend = 3 passed, 6 deselected
Phase 10 closure frontend = 2 passed
Phase 10 retained evidence integrity = PASS
Typecheck = PASS
Production build = PASS (existing Plotly/glslify dynamic dependency warnings)
uv lock --check = PASS
git diff --check = PASS
npm audit = UNAVAILABLE (configured mirror returned 404_NOT_IMPLEMENTED)
```

The skipped backend cases are service-marked tests and are not reported as the
required service-backed zero-skip result. PostgreSQL/Redis/MinIO and the full
Chromium/Firefox/WebKit/mobile replay remain exact-SHA CI gates because this
Windows environment has no Docker runtime.
