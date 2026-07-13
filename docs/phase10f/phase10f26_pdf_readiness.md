# Phase 10F-26 PDF Readiness

Decision: `DEFERRED_BY_DESIGN`.

The current deterministic JSON and Markdown exports provide the scientific
content needed for a future report layout, and PNG provides a bounded raster
figure. PDF implementation is not approved because it still needs:

- page and section layout contracts;
- font embedding and licensing policy;
- vector versus raster figure policy;
- pagination, metadata, accessibility, and reproducibility rules;
- dependency, bundle, vulnerability, and browser support review;
- dedicated evidence and CI gates.

No PDF dependency, hidden browser print flow, server-side renderer, or fake PDF
artifact was added.
