# Phase 10N-5 Band Structure Contract

`electronic.band_structure@0.1.0` consumes one exact Band Resource and emits
`phase10n5.electronic_band_structure.v1`. It validates eV, spin, k-points, path segments
and finite rectangular band arrays, preserves supplied order and breaks, and persists
backend-derived path/gap facts. It never interpolates, reconnects, disentangles or
generates bands.
