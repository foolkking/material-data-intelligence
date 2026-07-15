# Phase 10I-2 Brillouin Renderer Evidence

## Replay

```bash
node apps/web/test/brillouin-zone-browser-evidence.mjs
```

The runner uses Phase 10I-1 QueueWorkerRuntime artifact copies for simple cubic,
BCC, hexagonal, and triclinic product flows. FCC and no-k-path inputs are marked
contract fixtures; invalid and cap cases are synthetic negative tests. Each
page enters through PlannerWorkbench and the artifact listing, not a standalone
renderer route.

The evidence directory is
`docs/phase10i/evidence/phase10i2_brillouin_renderer/`. It contains sanitized
plan/runtime source records, mapper and triangulation policy, Chromium/Firefox/
WebKit results, portrait and landscape mobile records, accessibility semantics,
performance and lifecycle metrics, local PNG metadata, console/network/security
audits, 18 real captures, and SHA-256 inventory.

## Acceptance

- Chromium 150.0.7871.115, Firefox 128.0, and WebKit 18.0 each created one
  nonblank local WebGL surface with nonzero draw calls.
- Chromium verified rotate, zoom, pan, deterministic reset, reciprocal camera
  presets, orthographic projection, layers, opacity, point and face picking,
  local PNG, context loss/reinitialize, and artifact cases.
- Portrait 390x844 and landscape 844x390 touch contexts rendered without page
  overflow and retained controls, selection, inspector, and text tables.
- Simple cubic recorded 8 vertices, 12 edges, 6 faces, 12 triangles, 6 draw
  calls, no textures, and one canvas/context. Triclinic recorded the bounded
  physical-complexity case. Exact timings remain environment observations, not
  universal performance claims.
- Invalid manifest binding allocated no canvas. The no-k-path fixture retained
  the polyhedron with zero points/segments and an explicit warning.
- Console/page-error/failed-local-request audits are empty and external requests
  are zero. Labels use text content and artifacts cannot control code, modules,
  shaders, materials, textures, URLs, or renderer budgets.

Expected markers:

```text
BRILLOUIN_ZONE_RENDERER_BROWSER_EVIDENCE_PASS
BRILLOUIN_ZONE_RENDERER_PERFORMANCE_EVIDENCE_PASS
BRILLOUIN_ZONE_RENDERER_ACCESSIBILITY_EVIDENCE_PASS
BRILLOUIN_ZONE_RENDERER_API_EVIDENCE_PASS
NO_BRILLOUIN_RENDERER_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

Three.js remains `0.185.1` with one installed copy and no dependency or lockfile
change. `npm audit` is reported according to the configured registry result and
is never inferred from the browser evidence.

## Local closure

- Frontend: 209 tests passed; typecheck and production build passed.
- Backend: 654 passed, 23 skipped, and 56 warnings. The skips are reported and
  are not counted as passes.
- Focused Phase 10I replay after lint cleanup: 49 passed with 45 upstream
  spglib deprecation warnings.
- Existing Phase 10 product closure: 2 unit tests plus Chromium, Firefox,
  WebKit, mobile, accessibility, performance, network, and secret evidence
  passed.
- Ruff, `uv lock --check`, `git diff --check`, and the npm dependency tree
  passed. Three.js remains one installed copy.
- The configured npm audit registry returned `404 NOT_IMPLEMENTED`; audit is
  unavailable, not clean. Docker CLI is unavailable locally; implementation
  commit `b5469c35cc39f096037036309a37aab160c9593c` passed CI run `29420821864`,
  including unit, frontend typecheck/build, service-backed integration, and the
  no-skipped assertion.
