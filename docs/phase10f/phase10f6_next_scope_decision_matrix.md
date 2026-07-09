# Phase 10F-6 Next-Scope Decision Matrix

| Priority | Candidate Scope | Why Now | Depends On | Risk | Recommended Next Phase | Decision |
|---:|---|---|---|---|---|---|
| 1 | Static Physics Fixture Pack Evidence Closure | Phase 10F-5 replay is complete and needs a stable boundary record. | Phase 10F-5 PASS | Low | Phase 10F-6 | COMPLETE |
| 2 | Advanced Structure Viewer Readiness Planning | Static physics implementation, browser/API evidence, and fixture-pack replay are closed; viewer remains the major advanced structure capability gap. | Phase 10D/10E/10F closure docs | Medium | Phase 10F-7 | RECOMMENDED |
| 3 | Official-Derived Fixture Approval Planning | Official PASS evidence remains none, but fixture-pack replay already strengthened internal traceability. | Reviewer availability and candidate official-derived cases | Medium | Later Phase 10F scope | DEFER |
| 4 | Rendered Static Chart UI Polish | Static chart JSON artifacts are evidenced; rendered previews can improve UX without changing adapters. | Frontend scope approval | Medium | Later UI polish phase | DEFER |
| 5 | Official Examples Pack Augmentation | Could create official-derived traceability, but needs provenance review and no notebook/script execution. | Official-derived approval policy | Medium | Later coverage phase | DEFER |
| 6 | Full `structure.viewer_3d` Implementation | High-value but requires renderer/security/artifact planning first. | Viewer readiness plan | High | Not Phase 10F-7 implementation | NOT RECOMMENDED YET |
| 7 | WebGL Renderer Implementation | Would introduce browser renderer and security surface. | Renderer isolation/security decision | High | Not next | NOT RECOMMENDED YET |
| 8 | Phonon Bands / DOS Planning | Future science scope; not required for static physics closure. | Separate phonon policy/readiness | Medium | Later planning | DEFER |
| 9 | Brillouin Zone 3D Planning | Related to advanced viewer and renderer policy. | Viewer readiness and renderer decision | Medium | Later planning | DEFER |
| 10 | Advanced Local Environment Classification Planning | Separate scientific policy and validation scope. | Local-environment policy gate | Medium | Later planning | DEFER |

## Recommendation

Recommended path A: `Phase 10F-7：Advanced Structure Viewer Readiness Planning`.

Rationale:

- static physics implementation evidence is closed;
- browser/API evidence is closed;
- fixture-pack replay evidence is closed;
- full viewer remains the major open advanced structure capability;
- the project needs a security, renderer, artifact-loading, screenshot, and planner-routing plan before any full viewer implementation.

Path B, `Official-Derived Fixture Approval Planning`, remains valid if the project decides official PASS evidence must precede viewer readiness. It is not the default recommendation because no current official direct-uploadable static physics case exists.
