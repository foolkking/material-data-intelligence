# Phase 10D Candidate Adapter Matrix

This matrix is planning-only. No listed adapter is implemented by Phase 10D.

| Priority | Adapter | Layer | Domain | Input | Output Artifacts | Official Example Candidate | Implementation Risk | Evidence Risk | Recommended Phase |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | `structure.viewer_scene_metadata` | Layer 1 | structure | Uploaded structure or normalized structure collection | `viewer_scene.json`, `summary.md`, `recipe.json` | `readme_structure_3d` as mapping reference | Medium: scene schema, caps, bond policy | Medium: artifact summary is stable, no renderer required | Phase 10D-1 |
| 2 | `structure.viewer_export_package` | Layer 1 | structure | Structure resource or `viewer_scene.json` | `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, `recipe.json` | `readme_widgets_structure_widget` as mapping reference | Medium: package manifest, hash/size accounting | Medium: static package evidence is feasible | Phase 10D-1 |
| 3 | `structure.viewer_3d_contract` | Layer 1 | structure | None or structure contract examples | `viewer_contract.json`, `summary.md`, `recipe.json` | Widget/readme examples as contract references | Low: schema-only artifact | Low: adapter evidence only | Optional Phase 10D-1 |
| 4 | `structure.coordination_hist` | Layer 2 | structure | Periodic structure or collection | `coordination_hist.json`, optional `coordination_hist_plot.json`, `summary.md`, `recipe.json` | No direct verified official case | Medium: neighbor definition ambiguity | Medium: fixture evidence feasible | Phase 10E candidate |
| 5 | `structure.xrd` | Layer 2 | structure | Periodic structure | `xrd_pattern.json`, optional `xrd_plot.json`, `summary.md`, `recipe.json` | No direct verified official case | Medium/high: pymatgen dependency and numeric tolerances | Medium/high: tolerance assertions needed | Phase 10E candidate |
| 6 | `structure.rdf` | Layer 2 | structure | Periodic structure or collection | `rdf.json`, optional `rdf_plot.json`, `summary.md`, `recipe.json` | No direct verified official case | High: cutoff/binning/normalization policy | High: numeric evidence can be sensitive | Phase 10E candidate |
| 7 | `structure.viewer_3d` | Layer 3 | structure | `viewer_scene.json` or structure resource | `viewer.html`, `viewer_scene.json`, `summary.md`, `recipe.json` | `readme_structure_3d`, widget demos | High: renderer, WebGL, sandboxing | High: browser screenshots nondeterministic | Phase 10F planning/prototype |
| 8 | `structure.brillouin_zone_3d` | Layer 3 | structure | Periodic structure with reciprocal lattice | `brillouin_zone_scene.json`, optional future viewer artifact | `readme_brillouin_zone_3d` | High: reciprocal geometry, symmetry, renderer | High: 3D screenshot and dependency risk | Phase 10F/10G candidate |
| 9 | `phonon.bands` | Layer 4 | phonon | Phonon band data or normalized phonon object | `phonon_bands.json`, optional `phonon_bands_plot.json`, `summary.md`, `recipe.json` | `readme_phonon_bands`, `phonons_mlip_phonons`, `matbench_phonons` | High: input contracts and phonopy/pymatgen dependency | High: examples are not direct-uploadable | Phase 10G planning |
| 10 | `phonon.dos` | Layer 4 | phonon | Phonon DOS table or normalized object | `phonon_dos.json`, optional `phonon_dos_plot.json`, `summary.md`, `recipe.json` | `readme_phonon_dos`, `phonons_mlip_phonons` | High: units, grid, partial DOS schema | High: extraction needed | Phase 10G planning |
| 11 | `phonon.band_dos` | Layer 4 | phonon | Combined band and DOS inputs | `phonon_band_dos.json`, optional plot artifact, `summary.md`, `recipe.json` | `readme_phonon_bands_and_dos` | High: depends on stable band and DOS contracts | High: combined evidence depends on two validated inputs | After standalone phonon tools |

## Recommendation

Phase 10D-1 should implement `structure.viewer_scene_metadata` and `structure.viewer_export_package`, with `structure.viewer_3d_contract` optional. It should not implement full `structure.viewer_3d`, Brillouin-zone 3D, XRD, RDF, or phonon tools.
