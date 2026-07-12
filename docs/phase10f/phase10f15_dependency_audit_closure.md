# Phase 10F-15 Dependency and Bundle Audit Closure

- Three.js: one direct copy, `0.185.1`, MIT.
- `@types/three`: `0.185.1`, development only.
- No renderer package or lockfile change was introduced in Phase 10F-15.
- Production build passes; route first-load JS is 127 kB. The renderer engine chunk is 25,466 bytes raw / 6,855 gzip / 6,115 Brotli. Three split chunks total 552,668 bytes raw / 137,560 gzip / 113,699 Brotli and remain lazy.
- No CDN, remote module, texture, font, worker, or source-map host is required by the viewer.

Official-registry `npm audit` reports the same seven pre-existing findings documented in Phase 10F-14: one critical Vitest, one high Vite, and five moderate findings across Vite/Vitest/Next/PostCSS chains. The Vitest/Vite findings are test/dev-server paths; Next/PostCSS remains application framework debt. None is introduced by Three.js or the renderer changes. Major upgrades require a separately scoped compatibility phase; audit is not claimed clean.
