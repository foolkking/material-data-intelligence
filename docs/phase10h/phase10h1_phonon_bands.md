# Phase 10H-1 Phonon Bands

Phase 10H-1 implements the static band-only product path:

```text
approved PhononBand input -> phonon.band -> QueueWorkerRuntime
-> canonical phase10h.phonon_band.v1 -> persisted artifacts
-> frontend canonical validation -> local Plotly preview/table/JSON
```

The adapter emits canonical band, canonical summary, parse report, canonical
manifest, static Plotly JSON, bounded table JSON, and recipe JSON. The unique
tool ID is `phonon.band`; explicit static band prompts route only when a
`PhononBand` object is profiled. DOS, eigenvectors, animation, phonon
calculation, Brillouin-zone rendering, and external resources remain absent.

Browser evidence covers Chromium, Firefox, WebKit, and a mobile viewport. The
preview preserves source branch order, negative frequencies, labels, and
segment discontinuities.
