# Phase 10I-3 Band-BZ Linked View Evidence

## Source and replay

Evidence is under
`docs/phase10i/evidence/phase10i3_band_bz_linked_view/`. The generator executes
one persisted two-step `QueueWorkerRuntime` plan using existing `phonon.band`
and `structure.brillouin_zone` tools. Captured BCC Fe artifacts include an
18-sample, six-segment, six-branch band and matching reciprocal lattice, BZ,
k-path, and manifest. A bounded H4/H5-compatible animation package proves exact
mode handoff; it is not a calculation.

API records contain the validated AnalysisPlan, job, tool calls, and artifact
inventory. Backend compatibility independently reports compatible scientific
bindings and expected undeclared provider/time-reversal warnings. Random
runtime identifiers are sanitized.

```text
uv run python scripts/generate_phase10i3_band_bz_evidence.py
node apps/web/test/band-bz-linked-view-browser-evidence.mjs
uv run python -m pytest tests/test_phase10i3_band_bz_link_routing.py tests/test_phase10i3_band_bz_link_evidence.py -q
```

## Browser and graphics

Real Chromium 150.0.7871.115, Firefox 128.0, and WebKit 18.0 runs each created
one WebGL2 canvas/context through Three.js 0.185.1, rendered 14 vertices, 24
edges, 12 faces, 24 triangles, four path points, and six segments, and issued
zero external requests. Chromium linked selection used eight draw calls, seven
geometries, eight materials, and zero textures.

Captured Chromium interaction measured hover-to-BZ at 302 ms, pinned
band-to-BZ at 108 ms, and BZ-to-band at 169 ms. These describe the evidence
environment, not universal guarantees. Firefox and WebKit completed real
bidirectional interaction and nonblank canvas pixel checks.

The near-cap smoke maps 198 samples and 1,188 numeric values with 12 point
occurrences and six segments. Captured Chromium validation took 9 ms and
mapping 1.6 ms. No timeout, unbounded allocation, second context, or external
request occurred.

## Cases and security

Eighteen PNG screenshots cover compatible startup, endpoint/interior band
selection, BZ reverse selection, segment selection, repeated occurrence,
discontinuity, imaginary mode, exact/unavailable animation handoff, path and
primitive mismatch, semantic table, keyboard selection, mobile tabs, and
near-cap mapping.

Mobile evidence proves zero canvas on Band, one on BZ, zero on Inspector, no
horizontal overflow, and safe disposal/recreation. Accessibility evidence
records the linked region, polite status, semantic table, keyboard samples, and
non-color identity.

Console captures contain no uncaught, React, WebGL, feedback-loop, resource, or
disposal error. Network captures contain no CDN, remote texture, font, module,
worker, analytics, or API request. Artifact/screenshot hashes are recorded in
`artifact_hashes.json`.

```text
BAND_BZ_LINKED_VIEW_BROWSER_EVIDENCE_PASS
BAND_BZ_BIDIRECTIONAL_SELECTION_EVIDENCE_PASS
BAND_BZ_LINK_PERFORMANCE_EVIDENCE_PASS
BAND_BZ_LINK_ACCESSIBILITY_EVIDENCE_PASS
NO_BAND_BZ_LINK_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

No artifact JavaScript, HTML, CSS, shader, callback, external URL, renderer
bundle, browser profile, private path, or secret is present.
