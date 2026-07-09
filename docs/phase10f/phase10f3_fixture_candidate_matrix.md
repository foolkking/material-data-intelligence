# Phase 10F-3 Fixture Candidate Matrix

| Candidate ID | Target Tool | Input Type | Proposed Provenance | Periodic Required | Direct Uploadable | Expected Numeric Contract | Size Risk | Execution Risk | Official PASS Eligible | Recommended |
|---|---|---|---|---:|---:|---|---|---|---:|---:|
| `coordination_hist_small_cif` | `structure.coordination_hist` | CIF | `official_like_curated` or approved `official_derived_manual` | true | true | exact site count and histogram counts | low | low | false until provenance approved and replayed | true |
| `coordination_hist_small_poscar` | `structure.coordination_hist` | POSCAR | `official_like_curated` or `internal_regression` | true | true | exact site count and histogram counts | low | low | false unless approved official-derived | true |
| `xrd_small_cif` | `structure.xrd` | CIF | `official_like_curated` or approved `official_derived_manual` | true | true | selected peak count, two-theta, intensity | low | low | false until provenance approved and replayed | true |
| `xrd_small_poscar` | `structure.xrd` | POSCAR | `official_like_curated` or `internal_regression` | true | true | selected two-theta and relative intensity | low | low | false unless approved official-derived | true |
| `rdf_small_cif` | `structure.rdf` | CIF | `official_like_curated` or approved `official_derived_manual` | true | true | bin count, r grid, selected `g(r)` values | low | low | false until provenance approved and replayed | true |
| `rdf_small_poscar` | `structure.rdf` | POSCAR | `official_like_curated` or `internal_regression` | true | true | bin count, counts, selected `g(r)` values | low | low | false unless approved official-derived | true |
| `phase10e_simple_cubic_cif` | all three static physics tools | existing internal CIF fixture | `internal_regression` | true | true | tool-specific exact/tolerance checks | low | low | false | true as regression only |
| `phase10e_nacl_poscar` | all three static physics tools | existing internal POSCAR fixture | `internal_regression` | true | true | tool-specific exact/tolerance checks | low | low | false | true as regression only |
| `phase10e_generated_structure_json` | all three static physics tools | generated Structure JSON | `internal_regression` | true | true | tool-specific exact/tolerance checks | low | low | false | true as regression only |
| `readme_structure_2d` | none for static physics | README function demo | `mapping_only` | unknown | false | none | n/a | n/a | false | false |
| `readme_structure_3d` | none for static physics | README function demo | `mapping_only` | unknown | false | none | n/a | n/a | false | false |
| `readme_widgets_structure_widget` | none for static physics | widget demo | `future_scope` | unknown | false | none | n/a | high | false | false |
| `readme_brillouin_zone_3d` | none for static physics | Brillouin-zone demo | `future_scope` | true | false | none | n/a | high | false | false |
| `widgets_jupyter_demo` | none for static physics | notebook/widget demo | `future_scope` | unknown | false | none | n/a | high | false | false |
| `widgets_marimo_demo` | none for static physics | script/widget demo | `future_scope` | unknown | false | none | n/a | high | false | false |
| `widgets_vscode_interactive_demo` | none for static physics | script/widget demo | `future_scope` | unknown | false | none | n/a | high | false | false |
| `matbench_phonons` | none for static physics | phonon dataset/script case | `future_scope` | unknown | false | none | n/a | high | false | false |
| `phonons_mlip_phonons` | none for static physics | phonon workflow | `future_scope` | unknown | false | none | n/a | high | false | false |
| `readme_phonon_bands` | none for static physics | README phonon demo | `future_scope` | n/a | false | none | n/a | high | false | false |
| `readme_phonon_dos` | none for static physics | README phonon demo | `future_scope` | n/a | false | none | n/a | high | false | false |
| `readme_phonon_bands_and_dos` | none for static physics | README phonon demo | `future_scope` | n/a | false | none | n/a | high | false | false |

## Rules

- `Official PASS Eligible` can become true only for `official_direct` or reviewer-approved `official_derived_manual` cases.
- `official_like_curated` and `internal_regression` candidates are useful for regression and fixture-pack hardening, but they are not official PASS evidence by themselves.
- `mapping_only`, `future_scope`, `unsupported`, and `unknown` candidates must not be marked PASS.
- Phase 10F-3 does not execute any row and does not create official PASS claims.
