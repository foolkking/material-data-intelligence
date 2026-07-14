# Phase 10H-5 Security Review

## Trust boundary

Untrusted structure, band, eigenvector, labels, provenance, and params pass closed Python validators before adapter output and an independent TypeScript validator before renderer initialization. Application code owns colors, geometry, renderer modules, shaders, playback loop, caps, DPR, and network policy.

## Controls

- Unknown params and fields are rejected.
- Mode identity cannot be frequency-only and stale hashes fail.
- Values must be finite; supercell, atoms, vectors, trails, bytes, amplitude, speed, and phase input are bounded.
- Artifacts cannot provide JavaScript, HTML, CSS, callbacks, formulas to execute, shaders, modules, textures, URLs, iframes, workers, or external assets.
- No fetch/XHR/WebSocket/external worker or remote renderer service is used.
- Reduced motion, hidden tabs, context loss, and unmount cancel the sole RAF.
- Error UI exposes typed codes and safe summaries, not stack traces, paths, secrets, or raw credentials.

Browser request interception found zero external requests. Secret scanning records `NO_SECRET_PATTERN_HITS`. No dependency or lockfile change is introduced. npm audit availability/results must be reported independently and are not represented as clean when the configured registry endpoint is unavailable.
