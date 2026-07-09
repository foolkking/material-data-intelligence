# Phase 10F Next-Scope Decision Matrix

| Priority | Candidate Scope | Type | Depends On | Implementation Risk | Evidence Risk | Security Risk | CI Risk | Recommended Next Phase | Decision |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Official static physics direct verification | evidence/planning | Phase 10E closure, direct-uploadable fixtures or official-example-like local cases | Low | Medium: must avoid mapping-only PASS claims | Low | Low | Phase 10F-1 | Recommended |
| 2 | Static physics rendered chart UI enhancement | frontend polish | Existing static chart JSON artifacts and preview components | Medium | Medium: screenshot comparison and browser stability required | Low if no artifact JS/CDN is added | Medium | Later Phase 10F polish | Defer until direct verification or explicit UI-priority decision |
| 3 | `structure.viewer_3d` readiness planning | architecture planning | Phase 10D static viewer metadata/export package, security model, browser evidence approach | Low for planning | Medium | Medium: artifact loading and renderer sandbox must be designed | Low | Later planning phase | Acceptable alternative if viewer is prioritized |
| 4 | `structure.viewer_3d` prototype | implementation | Completed readiness plan, renderer choice, sandbox model, WebGL policy, screenshot strategy | High | High | High | High | Not Phase 10F-1 | Not recommended directly |
| 5 | `structure.brillouin_zone_3d` planning | planning | Full structure symmetry policy, reciprocal-lattice contract, renderer/evidence decision | Medium | Medium | Medium | Medium | Later planning phase | Defer |
| 6 | `phonon.bands` planning | planning | Phonon input policy, dependency availability, unit/path conventions, artifact schema | Medium | Medium | Low to Medium | Medium | Later planning phase | Defer |
| 7 | `phonon.dos` planning | planning | Phonon DOS input policy, dependency availability, units, artifact schema | Medium | Medium | Low to Medium | Medium | Later planning phase | Defer |
| 8 | Advanced local environment classification planning | planning | Voronoi/CrystalNN policy, chemistry warnings, tolerance fixtures, dependency behavior | Medium | Medium | Low | Medium | Later planning phase | Defer |

## Decision Notes

- Do not directly enter full `structure.viewer_3d` implementation from Phase 10F.
- Do not directly enter WebGL renderer implementation from Phase 10F.
- Do not directly enter phonon implementation from Phase 10F.
- If advanced viewer work is selected later, first perform readiness and architecture planning covering renderer choice, sandboxing, artifact loading, external URL policy, screenshot stability, and CI risk.
- If official examples work is selected, only direct-uploadable cases with local reproducible inputs may become PASS evidence. Mapping-only, notebook-only, script-heavy, external-API, missing-input, or screenshot-only cases must remain mapping/future references.

## Recommendation

Recommended Phase 10F-1:

```text
Official Examples Direct Verification for Static Structure Physics
```

Rationale: Phase 10E already completed implementation and platform evidence for coordination histogram, XRD, and RDF. Direct verification is lower risk than viewer/WebGL/phonon implementation and strengthens traceability before expanding the advanced structure stack.
