# Phase 10F-27 structure.viewer_3d Browser Evidence

The formal product runner reuses the production viewer browser suite against
live `structure.viewer_3d` artifacts. It records Chromium, Firefox, and WebKit
desktop behavior plus mobile viewport interaction, renderer metrics,
accessibility semantics, lifecycle, screenshots, console output, and all
requests. The tested product path includes renderer and JSON fallback; artifact
generation itself remains renderer-free.

Required markers are:

```text
STRUCTURE_VIEWER_3D_PRODUCT_EVIDENCE_PASS
STRUCTURE_VIEWER_3D_API_EVIDENCE_PASS
NO_EXTERNAL_NETWORK_REQUESTS
```

Browser unavailability is reported honestly as an unsupported fallback, never
as fabricated rendering success.

Recorded result: Chromium 150, Firefox 128, and WebKit 18 each reached
`rendered`; all three reported zero console errors and zero external requests.
Desktop and mobile screenshots, metrics, lifecycle, and accessibility captures
are committed with the evidence manifest.
