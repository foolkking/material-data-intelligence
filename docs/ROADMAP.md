# Canonical Product Roadmap

Status: CURRENT

This is the only authoritative roadmap for work after Phase 10J-6. Historical
phase plans remain useful records, but they do not authorize future work.

## Completed Foundation

* Phase 1-9: platform, data, execution, artifact, and workspace foundations.
* Phase 10A-E: general visualization, composition, lightweight structure, and
  static scientific products.
* Phase 10F: production periodic structure viewer.
* Phase 10G: trajectory product.
* Phase 10H: phonon bands, DOS, and animation.
* Phase 10I: Brillouin zone and reciprocal-space linking.
* Phase 10J through 10J-6: volumetric contracts, parsing, isosurfaces,
  charge/spin, potential, ELF/orbital, Slice, and Direct Volume.
* Phase 10K: Material Data Profile 2.0, Dataset Materials Explorer, Materials
  ML Evaluation, Composition Space, and exact Browser/API product integration.

Phase 10J-6 is archived. The implementation, completion record, exact-SHA CI,
result history, and evidence are retained.

## Initial Complete Product - Remaining

### Phase 10L - Intelligent Analysis Agent

* 10L-0: Agent and Planner capability audit.
* 10L-1: Analysis Intent contract.
* 10L-2: capability-aware planning from intent, DataProfile, and Registry.
* 10L-3: bounded, typed, deterministic multi-tool analysis.
* 10L-4: bounded scientific result interpretation.
* 10L-5: natural-language end-to-end evidence across dataset, structure, ML,
  phonon, and volumetric cases.

Current status: 10L-0 through 10L-3 are archived. Phase 10L-4 corrected
implementation `02a9e33` passed exact-SHA CI run `30606774006` and is
`COMPLETE / AWAITING_ARCHIVE_CI`; completion record `45af09e` passed exact-SHA
CI run `30607509775`. Phase 10L-5 was explicitly supplied by the reviewer and
remains queued behind the Phase 10L-4 archive CI gate.

### Phase 10M - Unified Scientific Workspace

* 10M-0: workspace information architecture and identity contract.
* 10M-1: one analysis task, one unified workspace.
* 10M-2: cross-artifact navigation and canonical identity binding.
* 10M-3: scientific artifact gallery.
* 10M-4: report, recipe, and export productization.
* 10M-5: user-facing workspace browser and UI closure.

### Phase 10N - Professional Scientific Completion

* 10N-1: CrystalNN and VoronoiNN with explicit algorithm provenance.
* 10N-2: local environments and coordination polyhedra.
* 10N-3: experimental XRD comparison and peak matching.
* 10N-4: trajectory RDF, MSD, diffusion, and basic time analytics.
* 10N-5: electronic band, total/projected DOS, spin, and BZ-linked view.
* 10N-6: professional scientific capability evidence closure.

Fermi Surface is not part of Phase 10N or the initial release.

### Phase 11 - Scientific Validation and Honest Coverage

* 11A: benchmark governance.
* 11B: safe static example and fixture extraction.
* 11C: reference validation for initial-release capabilities.
* 11D: official capability coverage closure using explicit states:
  `OFFICIAL_VERIFIED`, `DIRECT_VERIFIED`, `REFERENCE_VERIFIED`,
  `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, or `UNSUPPORTED`.

### Phase 12 - Final Product Closure

* 12-1: five complete end-to-end demo packs.
* 12-2: user and scientific documentation.
* 12-3: focused final UI polish.
* 12-4: full platform regression.
* 12-5: final readiness and baseline freeze.

## Scope Authority

* Initial release: [01_PRODUCT_REQUIREMENTS.md](01_PRODUCT_REQUIREMENTS.md)
* Future, non-blocking extensions: [FUTURE_SCOPE.md](FUTURE_SCOPE.md)
* Capabilities outside the current product: [NOT_PLANNED_SCOPE.md](NOT_PLANNED_SCOPE.md)
* Current capability truth: [CAPABILITY_STATUS_MATRIX.md](CAPABILITY_STATUS_MATRIX.md)

Future Scope cannot enter `TASKS.md` without explicit reviewer/user approval.
Not Planned capabilities cannot return to the roadmap merely because they are
technically possible.

## Historical Numbering Reconciliation

An earlier plan assigned J-5 to Electronic Band/DOS and J-6 to Fermi Surface.
Actual delivery assigned J-5 to ELF/Orbital Volumetric Product and J-6 to
Volumetric Slice/Volume Rendering. A short-lived post-J6 freeze then proposed
J-7 through J-12 for electronic/Fermi work. Gate J6-R supersedes that proposal:
Electronic Band/DOS is now 10N-5, while Fermi Surface is Future Scope. Completed
phase names and historical evidence are unchanged.
