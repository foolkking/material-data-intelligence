# Phase 10F-26 Test Capture

- export and renderer component focus: `29 passed`
- frontend full suite: `104 passed`
- frontend typecheck: passed
- frontend production build: passed
- backend full suite: `366 passed, 21 skipped, 11 warnings`
- Chromium/Firefox/WebKit scientific export runner: passed
- all historical viewer browser runners: passed
- `uv lock --check`: passed
- npm dependency tree: one `three@0.185.1`
- npm audit: unavailable because configured npmmirror audit endpoint returns `NOT_IMPLEMENTED`
- local service-backed integration: unavailable because Docker CLI is not installed; current-HEAD CI is required for closure

The backend skips are reported as skipped, not passed.
