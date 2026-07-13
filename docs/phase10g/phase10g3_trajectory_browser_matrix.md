# Phase 10G-3 Trajectory Browser Matrix

The final evidence run used the same capture generation and browser runner invocation for all browsers.

| Browser | Version | Fixed/many frames | Variable lattice | Degraded | Refused | Context retry | Mobile |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chromium | 150.0.7871.115 | PASS | PASS | PASS | PASS | PASS | PASS |
| Firefox | 128.0 | PASS | PASS | PASS | PASS | PASS | Not run |
| WebKit | 18.0 | PASS | PASS | PASS | PASS | PASS | PASS |

Rendered cases require a nonblank composited canvas, a WebGL context, positive draw calls, one canvas/context, formal tool identity, and zero browser audit errors. Refused and invalid cases require zero canvas. Synthetic `webglcontextlost` dispatch verifies controlled teardown and one-engine retry in each desktop browser.

Timing is semantic: ordered frame progression, bounded seek completion, zero pending requests, and stable resources. Absolute milliseconds are recorded but are not the sole PASS criterion.
