# Phase 10E-6 RDF Policy Matrix

| Policy Area | Decision | Default | Limits | Determinism Rule | Test Requirement | Risk | Status |
|---|---|---|---|---|---|---|---|
| periodic image | Support only fully periodic crystalline `pymatgen Structure` inputs; use periodic neighbor search. | `pbc == [true, true, true]` | reject non-periodic or invalid lattice/volume | process structures and sites in stable order | non-periodic input rejects; periodic fixture succeeds | wrong image counting changes RDF | READY |
| `r_max_angstrom` | finite radial cutoff recorded in all artifacts | `8.0` | `0.5..30.0` | same cutoff gives same neighbors/bins | invalid cutoff rejected; cutoff affects counts | cutoff-sensitive interpretation | READY |
| `bin_width_angstrom` | fixed-width bins | `0.1` | `0.01..1.0` | bin count `ceil(r_max/bin_width)`; deterministic edges/centers | invalid bin width rejected; bin edge snapshot tests | bin assignment drift | READY |
| `max_bins` | reject too many bins | `1000` | `1..5000` | no implicit truncation | `ceil(r_max/bin_width) > max_bins` rejects | runaway artifact size | READY |
| normalization | number-density shell-volume normalization only | `number_density` | enum `["number_density"]` | fixed formula using cell volume, site counts, shell volume | global RDF expected values for small fixtures | normalization ambiguity | READY |
| global centers/neighbors | all sites as centers and all sites as neighbors | all sites | exclude exact zero-distance self-pairs | center sites by index, neighbors sorted | counts deterministic; self-pairs absent | double-count interpretation | READY |
| partial pairs | ordered center-element to neighbor-element pairs | enabled | `max_partial_pairs=64`, range `1..256` | sort by center element then neighbor element | binary fixture has deterministic ordered pairs | pair explosion | READY |
| site cap | reject structures above cap | `500` | `1..5000` | no silent site truncation | site limit error test | large runtime | READY |
| neighbor cap | reject if periodic neighbor records exceed cap | `200000` | `1..2000000` | fail before writing partial artifacts | neighbor cap error/warning path | runtime/memory blowup | READY |
| volume validation | require positive cell volume | existing `_BaseStructureAdapter` plus RDF-specific check | volume must be `> 0` | same structure volume serialized with fixed rounding | invalid volume error path | invalid normalization | READY |
| non-periodic handling | typed error, no fallback molecular RDF | none | reject | deterministic error code | XYZ/non-periodic fixture rejects | accidental molecular workflow | READY |
| warnings | stable warnings list | sensitivity and scope warnings emitted | de-duplicated | stable ordering via de-duplication | warning snapshot tests | unsupported claims | READY |
| rounding | fixed numeric precision | 6 decimals | applies to r, g(r), density, shell volume, distances | stable JSON output | deterministic output hash/snapshot | floating-point drift | READY |
| artifact contract | JSON/Markdown only | `rdf.json`, `rdf_plot.json`, `summary.md`, `recipe.json` | no HTML/app bundle | `stable_json_dumps` and stable filenames | artifact contract tests | frontend preview mismatch | READY |
| security | no executable artifacts | no JS, no external URLs | security flags false/empty | static payload only | scan for script/url patterns | artifact execution risk | READY |
| browser/API evidence | implementation phase excludes evidence; evidence next phase | Phase 10E-8 | use existing evidence flow | no fabricated screenshots | evidence prompt requires API/browser artifacts after implementation | evidence cost | READY |
| official examples | mapping references only | none | no PASS unless directly verified | table documents unsupported status | docs assert no official PASS | false PASS claims | PARTIAL_READY |
