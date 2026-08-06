# Phase 10N-0 Long-List Scope Classification

The following classification is a scope seal proposal. Only N1-N5 and N6 are reviewer-
authorized Initial Release candidates.

| Capability | Classification | Reason |
| --- | --- | --- |
| CrystalNN | INITIAL_RELEASE_10N / N1 | reviewer-frozen route; missing production authority |
| VoronoiNN | INITIAL_RELEASE_10N / N1 | reviewer-frozen route; missing production authority |
| ChemEnv or equivalent | FUTURE_SCOPE; N2 input candidate only | existing mapping/foundation is not a validated product |
| coordination polyhedra | INITIAL_RELEASE_10N / N2 | reviewer-frozen route |
| bond valence | NOT_NEEDED for N1-N6 | no approved authority or route |
| oxidation-state inference | NOT_NEEDED for N1-N6 | prohibited false-claim risk |
| experimental XRD comparison | INITIAL_RELEASE_10N / N3 | reviewer-frozen route |
| peak detection / matching | INITIAL_RELEASE_10N / N3 | bounded comparison only |
| Rietveld refinement | FUTURE_SCOPE | explicitly excluded from N3 |
| phase-fraction refinement | FUTURE_SCOPE | explicitly excluded from N3 |
| structure refinement | FUTURE_SCOPE | no optimization authority in N3 |
| trajectory RDF / time-window RDF | INITIAL_RELEASE_10N / N4 | reviewer-frozen route |
| MSD / directional MSD | INITIAL_RELEASE_10N / N4 | reviewer-frozen route |
| diffusion fitting | INITIAL_RELEASE_10N / N4 | diagnostics-bounded estimate only |
| trajectory unwrapping | INITIAL_RELEASE_10N / N4 | required policy, not optional browser behavior |
| variable-cell/reactive trajectory analytics | FUTURE_SCOPE | requires separate identity and scientific validation |
| electronic band structure / DOS | INITIAL_RELEASE_10N / N5 | consumer-only supplied-output route |
| projected DOS | INITIAL_RELEASE_10N / N5 conditional | element/orbital channels only when the sealed completeness contract is satisfied |
| projected bands | FUTURE_SCOPE | separate completeness and selection validation required |
| spin-polarized consumption | INITIAL_RELEASE_10N / N5 conditional | only with exact source channels |
| Fermi surface | FUTURE_SCOPE | no current contract or rendering authority |
| Bader analysis / charge topology | FUTURE_SCOPE | separate input and algorithm authority |
| defects / surfaces | FUTURE_SCOPE | not part of N1-N6 route |
| phase diagrams / reaction thermodynamics | FUTURE_SCOPE | separate domain scope |
| elastic/mechanical properties | FUTURE_SCOPE | separate domain scope |
| magnetic analysis / spectroscopy | FUTURE_SCOPE | separate domain scope |
| model training / AutoML / active learning | FUTURE_SCOPE | not a professional N1-N6 science route |

`NOT_PLANNED` remains reserved for capabilities excluded by the repository's existing
not-planned scope. This audit does not promote any Future Scope item to Initial Release.
