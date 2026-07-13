# Phase 10F-26 PNG Export

PNG capture uses the current camera, validated renderer scene, supercell,
clipping, and selected measurement overlays. Export options temporarily control
cell, axes, bonds, measurement overlays, background, size, and DPR. Renderer
size, DPR, clear color/alpha, camera aspect, and object visibility are restored
in `finally`.

The WebGL context is created with alpha support. Transparent output therefore
uses an RGBA PNG; light and dark outputs may be encoded as RGB or RGBA by the
browser. Evidence validates the PNG signature, IHDR dimensions, background
variation, a 2400 x 1800 high-DPI result, and one active canvas after ten
repeated exports.

The image is a rendered view and is never treated as structural source data.
There is no upload, server rendering, remote texture, external font, or network
request.
