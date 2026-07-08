# Phase 10E-3 Static Physics Next-Scope Matrix

Phase 10E-3 compares the remaining static structure physics candidates after `structure.coordination_hist` completed implementation and browser/API evidence.

| Priority | Candidate | Domain | Input Readiness | Dependency Readiness | Numeric Determinism | Tolerance Policy | Artifact Contract | Browser Evidence Feasibility | CI Risk | Security Risk | Official Example Mapping | Recommendation |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `structure.xrd` | structure | READY: small periodic CIF/POSCAR/Structure JSON fixtures exist and reuse the Phase 10C parser path | READY: `pymatgen`, `pymatviz`, `numpy`, `plotly`, and `XRDCalculator` are available without new dependencies | PARTIAL_READY: deterministic with fixed calculator, sorted peaks, and rounded fields; tests must pin fixture peak windows | PARTIAL_READY: CuKa, two-theta range, merge tolerance, intensity threshold, and max peaks can be fixed in Phase 10E-4 | READY: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, `recipe.json` schema is clear | READY: existing mock planner, job, artifact, and static preview evidence flow can be reused | LOW_MEDIUM: bounded fixtures and peak caps keep runtime low | LOW: static JSON/Markdown only, no JS or external URLs | MAPPING_ONLY: widget/README/notebook references exist, but no direct-uploadable PASS case | Recommended single Phase 10E-4 implementation target |
| 2 | `structure.rdf` | structure | READY: periodic fixtures exist | PARTIAL_READY: `numpy`, `scipy`, `pymatgen`, and `pymatviz` are available, but the exact RDF engine/policy is not selected | PARTIAL_READY: bins can be deterministic, but `g(r)` values depend on normalization and periodic image policy | NOT_READY: normalization, finite-size correction, cutoff, bin-center, and partial-pair policy remain unresolved | PARTIAL_READY: `rdf.json` and `rdf_plot.json` draft exists, but normalization fields need final policy | READY: evidence flow is reusable after implementation | MEDIUM: pair expansion and image handling need stronger caps | LOW: static artifacts only if implemented like existing adapters | MAPPING_ONLY: widget/notebook references only, no direct-uploadable PASS case | Defer; resolve normalization and cutoff/bin policy before implementation |
| 3 | `structure.coordination_hist` | structure | READY: implemented over CIF, POSCAR, and Structure JSON fixtures | READY: implemented with existing parser and no new dependency | READY: deterministic distance-cutoff ordering and rounding tested | READY: fixed `distance_cutoff` policy with bounded params | READY: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json` verified | READY: Phase 10E-2 browser/API evidence completed | LOW: already validated | LOW: artifacts verified no JS/no external URLs | NO_DIRECT_CASE: project fixtures used; no official PASS claim | Completed baseline, not a next implementation target |

## Decision

Phase 10E-4 should implement `structure.xrd` only.

Rationale:

- XRD has a stable local dependency path through `pymatgen.analysis.diffraction.xrd.XRDCalculator`.
- Existing small crystalline fixtures are sufficient for deterministic adapter tests.
- The artifact contract and static chart contract are clear.
- The remaining XRD risks are manageable inside implementation by pinning CuKa defaults, peak sorting, rounding, and fixture tolerance windows.
- RDF still needs a stricter normalization and periodic-image policy before coding.

## Non-Scope

- Do not implement `structure.rdf` in Phase 10E-4.
- Do not implement full `structure.viewer_3d`, WebGL, Three.js, Brillouin-zone 3D, phonon tools, notebook extraction, script execution, or external API workflows.
