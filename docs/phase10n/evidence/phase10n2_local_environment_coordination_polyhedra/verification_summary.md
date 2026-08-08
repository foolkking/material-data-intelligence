# Phase 10N-2 Local Verification

- Focused backend N2/R0/runtime/reference/integrity: PASS.
- Full backend excluding service integration: 1196 passed, 1 documented local-environment skip, 45 integration tests deselected, 0 failed.
- Full frontend: 424 passed, 0 failed.
- Typecheck: PASS.
- Production build: PASS with pre-existing Plotly/glslify dynamic-dependency warnings.
- Browser: Chromium, Firefox, WebKit and Chromium 390x844 PASS.
- Chromium lifecycle: 50 cycles; listener, observer, RAF, WebGL, canvas, stale-overlay and payload-request growth all 0.
- Mobile: 390x844, horizontal overflow 0, minimum visible touch target 44 CSS px, focus trap/return PASS.
- Migration head: `0007_phase10m1_workspace_domain`.
- `uv lock --check`: PASS.
- Secret scan: PASS, zero configured pattern hits.
- Local service-backed: UNAVAILABLE because Docker is not installed; the integration test is not represented as local PASS. Exact-SHA CI requires at least 44 passed and zero skipped.
- `npm audit`: UNAVAILABLE because the configured npmmirror audit endpoint returned `404_NOT_IMPLEMENTED`.
- `NEW_LLM_CALL_SITES = 0`; `N2_REAL_LLM_CALLS = 0`.
