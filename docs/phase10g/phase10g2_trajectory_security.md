# Trajectory Viewer Security

Only independently validated inert trajectory JSON reaches the mapper. Artifact fields cannot control code, callback, shader, module, URL, texture, FPS, cache size, timer, topology inference, or DOM identity. No external frames, CDN, workers, telemetry, notebook, script, filesystem, or network access are used.

The 768 displayed-instance hard cap and 2,000,000 coordinate-value viewer cap run before WebGL allocation. A validator-valid 780-atom evidence artifact returns `TRAJECTORY_VIEWER_BUDGET_EXCEEDED` with zero canvas allocation. Supercells remain renderer-local and inherit axis/cell caps. Errors contain typed safe codes without raw payload, stack, private path, or secret.

Unsupported WebGL, initialization failure, frame failure, budget refusal, and context loss use distinct application-owned codes. The local application icon removes the only Chrome favicon 404; every browser evidence page must have zero console errors, page errors, external requests, external scripts, JavaScript URIs, inline handlers, and iframes.
