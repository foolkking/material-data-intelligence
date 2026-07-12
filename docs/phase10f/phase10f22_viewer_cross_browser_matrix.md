# Viewer Cross-Browser Matrix

| Browser | Keyboard | Semantics | Mobile/resize | Result |
| --- | --- | --- | --- | --- |
| Chromium | rotate/pan/zoom/reset | summary/live region | touch targets, orientation | READY |
| Firefox | rotate/pan/zoom/reset | summary/live region | resize | READY |
| WebKit | rotate/pan/zoom/reset | summary/live region | touch policy, resize | READY |

Automated browser assertions do not replace physical screen-reader or broad
hardware testing.

Each engine also executes a real 200% document zoom usability assertion. The
runner requests forced-colors emulation where the engine supports it and records
the actual media-query state rather than treating unsupported emulation as a pass.
