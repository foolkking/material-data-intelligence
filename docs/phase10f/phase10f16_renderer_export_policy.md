# Phase 10F-16 Renderer Export Policy

PNG capture renders the current application-owned Three.js scene and camera, then
reads the local opaque canvas into an `image/png` Blob. Width/height are each
limited to 4096 and total pixels to 16,777,216. Formula-derived names are NFKD
normalized, allowlisted, bounded to 80 characters, and suffixed
`-structure-viewer.png`. No upload, server renderer, URL input, external service,
or artifact-selected MIME/background is used. Object URLs are revoked in a
microtask. Scene, manifest, summary, and recipe downloads reuse attached API data.
