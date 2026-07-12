# Viewer Performance Evidence

`viewer-scene-performance-hardening-browser-evidence.mjs` executes the existing
production and periodic Playwright runners. Chromium, Firefox, WebKit, mobile,
near-cap, repeated lifecycle, periodic identity, context fallback, console, and
network assertions passed. Absolute GPU memory is intentionally not claimed;
bounded renderer.info and object-count proxies are recorded.
