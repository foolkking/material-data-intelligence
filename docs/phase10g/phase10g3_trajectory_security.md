# Phase 10G-3 Trajectory Security Review

## Trust Boundary

Trajectory JSON remains untrusted until canonical frontend validation. Renderer launch values originate from strict persisted tool params and are independently whitelisted by the client. Artifact data cannot set fps, cache size, performance thresholds, shader, callback, module, URL, texture, HTML, or browser capability.

## Resource Controls

- Contract atom/frame/value/byte caps remain unchanged.
- Displayed instances include renderer-local supercell multiplication.
- Refused scenes allocate no canvas or context.
- Cache frames/bytes, pending mapping, prefetch, playback loop, canvas/context, and overlays are bounded.
- Frame cache contains CPU mapped data only and is trajectory-scoped.
- Context loss and artifact switching dispose the old engine and cancel pending work.

## Injection and Network

The browser runner blocks every non-local request and audits external scripts, iframe, JavaScript URI, inline handlers, console errors, page errors, and HTTP failures. Final result: `NO_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS`.

No dependency was added. `npm audit` availability and findings are reported honestly during closure; no clean result is inferred when the configured registry endpoint is unavailable.
