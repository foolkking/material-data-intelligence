# Phase 10E-3 XRD / RDF Readiness Decision

## 1. Scope

- decision target: choose the next static structure physics implementation scope after `structure.coordination_hist`.
- candidates assessed: `structure.xrd` and `structure.rdf`.
- not implemented: XRD, RDF, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon bands/DOS, notebook extraction, script execution, and external API workflows.

## 2. Baseline

- Phase 10E-1: `2beb8b7 Implement coordination histogram adapter`.
- Phase 10E-2: `39e1929 Add coordination histogram browser API evidence`.
- current HEAD before Phase 10E-3 edits: `39e1929`.
- branch: `master`.
- git status before: clean.

## 3. Completed Static Physics Baseline

- `structure.coordination_hist`: implemented and registered.
- artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json`.
- browser/API evidence: completed under `docs/phase10e/browser_api_evidence/phase10e2_coordination_hist/`.
- CI: Phase 10E-2 recorded unit, frontend, service-backed integration, and no-skipped assertion success.
- boundaries: no XRD, RDF, full viewer, WebGL, Three.js, Brillouin-zone, phonon, notebook/script, or external workflow support was added.

## 4. Readiness Gate

Each candidate is assessed across these dimensions:

- dependency readiness
- input fixture readiness
- numeric determinism
- tolerance policy
- artifact contract clarity
- params schema clarity
- static chart compatibility
- planner routing safety
- negative routing safety
- browser/API evidence feasibility
- CI runtime risk
- security risk
- official examples mapping quality
- implementation complexity
- regression risk

Readiness values:

- READY: sufficient for implementation with existing project patterns.
- PARTIAL_READY: feasible but must be pinned in the implementation phase.
- NOT_READY: missing policy or fixtures would make implementation under-specified.
- UNKNOWN: cannot be confirmed from local repo state and must not be treated as READY.

## 5. `structure.xrd` Assessment

- dependency readiness: READY. Local checks show `pymatgen`, `pymatviz`, `numpy`, `scipy`, `plotly`, `spglib`, and `ase` available. `pymatgen.analysis.diffraction.xrd.XRDCalculator` imports successfully. `pymatviz.xrd_pattern` is also present.
- fixture readiness: READY. Current small periodic fixtures include `simple_cubic.cif`, `si.cif`, `nacl.poscar`, `POSCAR`, `fe2o3_like.cif`, and `structure_collection.json`.
- numeric determinism: PARTIAL_READY. XRD output can be deterministic if Phase 10E-4 fixes radiation, two-theta range, sorting, rounding, peak cap, and fixture tolerance windows.
- tolerance policy: PARTIAL_READY. Planning recommends a fixed CuKa source, `two_theta_min`, `two_theta_max`, `peak_merge_tolerance`, `intensity_threshold`, and `max_peaks`; exact fixture assertions must be pinned during implementation.
- params schema: READY. A strict whitelist schema is clear and matches existing adapter validation style.
- artifact contract: READY. Use static artifacts only: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- planner routing: READY. XRD/diffraction prompts can be routed explicitly after implementation; existing negative routing already prevents those prompts from being sent to `structure.coordination_hist`.
- browser/API evidence feasibility: READY. Phase 10E-2 evidence flow can be reused after implementation.
- risks: radiation source naming, hkl multiplicity, peak merge tolerance, floating point reproducibility, non-crystalline input, partial occupancy/disorder, large peak counts, and official example readiness.
- readiness: READY for a single-scope Phase 10E-4 implementation, with tolerance pinning included in that phase.

## 6. `structure.rdf` Assessment

- dependency readiness: PARTIAL_READY. `numpy`, `scipy`, `pymatgen`, and `pymatviz` are available, and `pymatviz.element_pair_rdfs` / `pymatviz.full_rdf` exist. The project still lacks a selected RDF computation policy.
- fixture readiness: READY. Periodic CIF/POSCAR/Structure JSON fixtures exist.
- numeric determinism: PARTIAL_READY. Bin edges can be deterministic, but `g(r)` values depend on normalization, periodic-image handling, finite-size corrections, and pair selection.
- cutoff / bin / normalization policy: NOT_READY. The repo has not yet fixed whether Phase 10E RDF should use number-density normalization, raw shell counts, partial RDF defaults, smoothing, or finite-size correction behavior.
- params schema: PARTIAL_READY. Draft params are clear, but they depend on the unresolved normalization policy.
- artifact contract: PARTIAL_READY. `rdf.json` and `rdf_plot.json` fields are drafted, but normalization metadata needs final semantics before implementation.
- planner routing: READY after implementation, but should remain future-scope until the numeric policy is fixed.
- browser/API evidence feasibility: READY after implementation because existing evidence infrastructure is reusable.
- risks: normalization ambiguity, finite-size effects, periodic image handling, cutoff sensitivity, bin width sensitivity, volume/density dependency, partial RDF pair expansion, large structure runtime, non-periodic input handling, floating point reproducibility, and official example readiness.
- readiness: NOT_READY for immediate adapter implementation. Defer RDF until normalization and fixture tolerance policy are hardened.

## 7. Official Examples Mapping

Local benchmark pack checked: `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`.

- total cases: 61.
- direct verified raw-data cases: 2.
- verification status summary from audit: `DIRECT_VERIFIED` 2, `EXTRACTION_REQUIRED` 27, `MAPPING_ONLY` 20, `FUTURE_SCOPE` 12.
- JSON contracts and manifest files do not contain direct XRD/RDF case hits.
- XRD/RDF terms appear in README, widget, notebook, or script source files such as `widgets_vscode_interactive_demo`, `widgets_jupyter_demo`, `widgets_marimo_demo`, `readme_widgets_structure_widget`, and broad README snapshots.
- These are mapping references only. They are not direct-uploadable PASS evidence.

| Candidate | Official Case | Case Type | Input Data | Direct Uploadable | Expected Artifact | Current Support | Risk | Use As PASS Evidence? |
|---|---|---|---|---:|---|---|---|---:|
| `structure.xrd` | `widgets_vscode_interactive_demo` | `future_scope_widget_or_structure` | script/widget source | false | `xrd_pattern.json`, `xrd_plot.json` | mapping reference only | script/widget workflow, no direct uploaded structure evidence | false |
| `structure.xrd` | `widgets_jupyter_demo` / `widgets_marimo_demo` | notebook/script demo | notebook or script source | false | XRD widget output | mapping reference only | notebook/script execution is forbidden in this phase | false |
| `structure.xrd` | README-wide example snapshots | `readme_function_demo` | README text | false | possible diffraction chart reference | mapping reference only | README aggregate text is not an executable case | false |
| `structure.rdf` | `widgets_vscode_interactive_demo` | `future_scope_widget_or_structure` | script/widget source | false | `rdf.json`, `rdf_plot.json` | mapping reference only | RDF widget semantics and data extraction unresolved | false |
| `structure.rdf` | `widgets_jupyter_demo` / `widgets_marimo_demo` | notebook/script demo | notebook or script source | false | RDF widget output | mapping reference only | notebook/script execution is forbidden in this phase | false |
| `structure.rdf` | README-wide example snapshots | `readme_function_demo` | README text | false | possible RDF chart reference | mapping reference only | README aggregate text is not an executable case | false |

## 8. Decision Matrix

See `docs/phase10e/phase10e3_static_physics_next_scope_matrix.md`.

## 9. Recommendation

Phase 10E-4 should be:

**Static Physics Adapter Implementation - XRD**

Recommended target:

- implement `structure.xrd` only.
- do not implement `structure.rdf`.
- do not add browser/API evidence in Phase 10E-4; reserve that for Phase 10E-5.
- pin CuKa defaults, two-theta range, peak sorting, rounding, and fixture tolerance windows as part of implementation.

RDF should remain deferred until its normalization, cutoff, binning, finite-size warning, and partial-pair policies are fixed.

## 10. Deferred Scope

- full interactive 3D viewer
- WebGL renderer
- Three.js
- `structure.viewer_3d`
- `structure.brillouin_zone_3d`
- `structure.rdf`
- phonon bands / DOS
- notebook extraction
- script execution
- external API workflows
- experimental XRD fitting
- crystallographic database lookup

## 11. Acceptance Criteria

- XRD and RDF readiness gates are recorded.
- Candidate matrix exists.
- Official examples are mapped without PASS claims.
- Phase 10E-4 implementation prompt exists.
- Recommended Phase 10E-4 scope is singular.
- No adapter, runtime semantic, planner job semantic, Tool Registry semantic, or PlanValidator boundary change is made in Phase 10E-3.

## 12. Conclusion

PASS.

Phase 10E-3 recommends `structure.xrd` as the single Phase 10E-4 implementation target. RDF remains deferred.
