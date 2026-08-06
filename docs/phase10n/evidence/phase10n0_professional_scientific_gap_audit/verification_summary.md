# Local Verification

- Focused N0 integrity: 6 passed.
- Full backend: 1162 passed, 44 skipped, 0 failed; skips require external services or local environment and are not represented as service-backed PASS.
- Full frontend: 411 passed.
- Typecheck: PASS.
- Production build: PASS with pre-existing Plotly/glslify dynamic-dependency warnings.
- Browser replay: Chromium, Firefox, WebKit and Chromium 390x844 PASS.
- `uv lock --check`: PASS.
- `npm audit`: UNAVAILABLE because the configured mirror returned 404 NOT_IMPLEMENTED.
