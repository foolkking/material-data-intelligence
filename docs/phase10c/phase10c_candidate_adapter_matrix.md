# Phase 10C Candidate Adapter Matrix

| Priority | Adapter | Domain | Input | Output Artifacts | Official Example Candidate | Implementation Risk | Evidence Risk | Recommended Phase |
|---:|---|---|---|---|---|---|---|---|
| 1 | `structure.summary` | structure | CIF, POSCAR, pymatgen Structure JSON, normalized Structure | `structure_summary.json`, `summary.md`, `recipe.json` | `readme_structure_2d`, `readme_structure_3d` as mapping; future direct structure fixtures | Medium: parser normalization and object model needed | Medium: direct raw structure evidence not yet pinned in benchmark pack | Phase 10C-1 / 10C-2 |
| 1 | `structure.lattice_summary` | structure | Periodic Structure or structure collection | `lattice_summary.json`, `summary.md`, `recipe.json` | `readme_structure_2d`; Matbench structure datasets after extraction | Medium: missing/non-periodic lattice handling | Medium: fixtures need expected lattice tolerances | Phase 10C-1 / 10C-2 |
| 1 | `structure.spacegroup_summary` | structure | Periodic Structure or structure collection | `spacegroup_summary.json`, `spacegroup_bar.json`, `summary.md`, `recipe.json` | Matbench structure cases after extraction | Medium-high: optional symmetry dependency and tolerance behavior | Medium-high: expected values depend on dependency version and `symprec` | Phase 10C-1 / 10C-2 if dependency stable |
| 1 | `structure.composition_from_structure` | structure | Structure or structure collection | `structure_composition.json`, `summary.md`, `recipe.json` | `readme_structure_2d`, `readme_structure_3d` as mapping | Medium: composition extraction is simpler than geometry but parser input must be stable | Medium: can bridge to existing composition artifacts after direct structure evidence | Phase 10C-1 / 10C-2 |
| 1 | `structure.preview_metadata` | structure | One selected Structure | `structure_preview_metadata.json`, `summary.md`, `recipe.json` | `readme_structure_3d` as mapping | Medium: coordinate conversion and truncation policy | Medium: UI can show metadata without WebGL | Phase 10C-1 / 10C-2 |
| 2 | `structure.viewer_3d` | structure | Structure / Atoms | `matterviz_html`, `structure_json`, `summary.md`, `recipe.json` | `readme_widgets_structure_widget`, `readme_structure_3d` | High: WebGL/HTML sandbox, MatterViz behavior, screenshot stability | High: browser evidence fragile | Phase 10D or later |
| 2 | `structure.xrd` | structure | Periodic crystal structure | `xrd_pattern.json`, `xrd_pattern.html`, `summary.md`, `recipe.json` | Future extracted structure examples | High: physics assumptions, wavelength, peak tolerance | High: numeric assertions and fixtures needed | Phase 10D or later |
| 2 | `structure.rdf` | structure | Periodic structures or pair-distance data | `rdf.json`, `rdf.html`, `summary.md`, `recipe.json` | Future extracted RDF examples | High: cutoff/binning and periodic-boundary policy | High: numeric tolerance evidence needed | Phase 10D or later |
| 2 | `structure.coordination_hist` | structure | Periodic structures with neighbor strategy | `coordination_hist.json`, `coordination_hist.html`, `summary.md`, `recipe.json` | Future extracted structure examples | Medium-high: neighbor strategy/tolerance choices | Medium-high: evidence must pin strategy | Phase 10D or late 10C |
| 3 | `structure.brillouin_zone_3d` | structure/physics | Reciprocal lattice or periodic structure | `brillouin_zone.json`, `brillouin_zone.html`, `summary.md`, `recipe.json` | `readme_brillouin_zone_3d` | Very high: reciprocal-space semantics and 3D rendering | Very high: future-scope only | Future scope |
| 3 | `phonon.bands` | phonon | Phonon band data | `phonon_bands.json`, `phonon_bands.html`, `summary.md`, `recipe.json` | `readme_phonon_bands`, `phonons_mlip_phonons` | High: phonon data model and extraction required | High: not direct upload verified | Future scope |
| 3 | `phonon.dos` | phonon | Phonon DOS data | `phonon_dos.json`, `phonon_dos.html`, `summary.md`, `recipe.json` | `readme_phonon_dos`, `phonons_mlip_phonons` | High: phonon data model and extraction required | High: not direct upload verified | Future scope |
| 3 | `phonon.band_dos` | phonon | Phonon band + DOS data | `phonon_band_dos.json`, `phonon_band_dos.html`, `summary.md`, `recipe.json` | `readme_phonon_bands_and_dos` | High: combined layout and data model | High: future-scope only | Future scope |

## Recommendation

Phase 10C-1 should implement only the five priority-1 lightweight structure
adapters. Structure viewer, XRD, RDF, coordination histograms, Brillouin-zone
rendering, and phonon plots need a separate Phase 10D planning pass after parser
contracts and lightweight structure evidence are stable.
