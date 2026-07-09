# Phase 10F-2 Coverage Gap Matrix

| Tool | Official Candidate | Current Case Type | Has Input | Has Expected Numeric Output | Direct Uploadable | Blocker | Closure Option | Recommended Action |
|---|---|---|---:|---:|---:|---|---|---|
| `structure.coordination_hist` | none in current pack | n/a | false | false | false | No official small structure case with coordination expected artifacts. | Curate approved small CIF/POSCAR plus expected contract. | Plan fixture pack; do not claim PASS. |
| `structure.xrd` | none in current pack | n/a | false | false | false | No official crystalline input with XRD peak expectations. | Curate approved crystalline fixture and tolerance-pinned peak contract. | Plan fixture pack; do not claim PASS. |
| `structure.rdf` | none in current pack | n/a | false | false | false | No official periodic structure with RDF grid/value expectations. | Curate approved periodic fixture and RDF bin/normalization contract. | Plan fixture pack; do not claim PASS. |
| `structure.coordination_hist` | `readme_structure_2d` | `readme_function_demo` | false | false | false | Rendering demo, not coordination histogram evidence. | Mapping reference only. | Keep excluded from PASS. |
| `structure.xrd` | `readme_structure_2d` | `readme_function_demo` | false | false | false | No XRD input/output contract. | Mapping reference only. | Keep excluded from PASS. |
| `structure.rdf` | `readme_structure_2d` | `readme_function_demo` | false | false | false | No RDF input/output contract. | Mapping reference only. | Keep excluded from PASS. |
| `structure.coordination_hist` | `readme_structure_3d` | `readme_function_demo` | false | false | false | Structure renderer demo, not static physics. | Viewer readiness planning later. | Keep future scope. |
| `structure.xrd` | `readme_structure_3d` | `readme_function_demo` | false | false | false | No diffraction expected contract. | Not a static XRD case. | Keep future scope. |
| `structure.rdf` | `readme_structure_3d` | `readme_function_demo` | false | false | false | No RDF expected contract. | Not an RDF case. | Keep future scope. |
| n/a | `readme_widgets_structure_widget` | `readme_function_demo` | false | false | false | Interactive widget example; widget execution excluded. | Advanced viewer planning only. | Keep future scope. |
| n/a | `readme_brillouin_zone_3d` | `readme_function_demo` | false | false | false | Brillouin-zone 3D is not implemented and requires future planning. | Brillouin readiness phase. | Keep future scope. |
| n/a | `widgets_jupyter_demo` | `future_scope_widget_or_structure` | false | false | false | Notebook/widget execution excluded. | Widget/viewer planning later. | Keep future scope. |
| n/a | `widgets_marimo_demo` | `future_scope_widget_or_structure` | false | false | false | Script/widget workflow excluded. | Widget/viewer planning later. | Keep future scope. |
| n/a | `widgets_vscode_interactive_demo` | `future_scope_widget_or_structure` | false | false | false | Interactive viewer/trajectory scope excluded. | Viewer readiness planning later. | Keep future scope. |
| n/a | `matbench_phonons` | `future_scope_widget_or_structure` | false | false | false | Phonon data/script workflow; not static structure physics. | Phonon planning later. | Keep future scope. |
| n/a | `phonons_mlip_phonons` | `future_scope_widget_or_structure` | false | false | false | Phonon bands/DOS future scope. | Phonon planning later. | Keep future scope. |
| n/a | `readme_phonon_bands` | `readme_function_demo` | false | false | false | Phonon bands not implemented. | Phonon planning later. | Keep future scope. |
| n/a | `readme_phonon_dos` | `readme_function_demo` | false | false | false | Phonon DOS not implemented. | Phonon planning later. | Keep future scope. |
| n/a | `readme_phonon_bands_and_dos` | `readme_function_demo` | false | false | false | Combined phonon plot not implemented. | Phonon planning later. | Keep future scope. |
| n/a | `examples_root_matbench_dielectric_eda` | `external_api_required` | false | false | false | Notebook and external data dependency. | Do not execute; extraction planning only if later approved. | Keep extraction-required. |
| n/a | `ricci_convert_dtype_add_structs` | `script_generated_data` | false | false | false | Script-generated structure preprocessing; not direct-uploadable. | Do not execute; possible provenance reference only. | Keep extraction-required. |

No row is a PASS claim. Rows identify gaps and future closure actions only.

