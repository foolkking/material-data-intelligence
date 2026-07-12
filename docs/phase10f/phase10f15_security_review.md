# Phase 10F-15 Security Review

Trust remains: uploaded structure and artifact JSON are untrusted; canonical validators, whitelist mapper, application palette, pinned Three.js, and renderer code are trusted.

Controls:

- strict tool params and canonical caps;
- no artifact HTML, JavaScript, CSS, callback, module path, shader, texture, or URL;
- no unsafe object merge or arbitrary property forwarding;
- renderer-owned colors, geometry segments, camera, controls, and DOM identifiers;
- DPR/site/bond/species/JSON limits and instancing;
- demand rendering and deterministic cleanup;
- chunk, unsupported, invalid, initialization, and context-loss fallbacks;
- no renderer fetch/XHR/WebSocket/Image/TextureLoader path;
- no raw stack, secret, private path, or source payload in normal UI errors.

Browser evidence reports `NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS`. Secret scan result is recorded during closure.
