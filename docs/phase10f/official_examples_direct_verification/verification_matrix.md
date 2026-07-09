# Verification Matrix

| Case ID | Candidate Tool | Case Type | Direct Uploadable | Input Present | Executed | Selected Tool | Artifacts Verified | Numeric Compared | Result | Notes |
|---|---|---|---:|---:|---:|---|---|---:|---|---|
| `matpes_atomic_energies_csv` | none for Phase 10F-1 | `direct_uploadable_data` | true | true | false | n/a | false | false | `UNSUPPORTED` | Direct verified benchmark case, but it is a table/ML case, not static structure physics. |
| `ward_metallic_glasses_csv_xz` | none for Phase 10F-1 | `direct_uploadable_data` | true | true | false | n/a | false | false | `UNSUPPORTED` | Direct verified benchmark case, but it is a table/composition case, not static structure physics. |
| `readme_structure_2d` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | README structure rendering demo, not `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`. |
| `readme_structure_3d` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | README structure rendering demo; full viewer remains out of scope. |
| `readme_widgets_structure_widget` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Interactive widget demo; not direct-uploadable static physics evidence. |
| `readme_brillouin_zone_3d` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Brillouin-zone 3D is deferred. |
| `widgets_jupyter_demo` | none | `future_scope_widget_or_structure` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Jupyter widget demo; notebook/widget execution is excluded. |
| `widgets_marimo_demo` | none | `future_scope_widget_or_structure` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Marimo widget demo; external script/workflow execution is excluded. |
| `widgets_vscode_interactive_demo` | none | `future_scope_widget_or_structure` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Interactive viewer/trajectory widget demo; out of scope. |
| `matbench_phonons` | none | `future_scope_widget_or_structure` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Phonon/data exploration case; not RDF/XRD/coordination official direct evidence. |
| `phonons_mlip_phonons` | none | `future_scope_widget_or_structure` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Phonon bands/DOS future scope. |
| `readme_phonon_bands` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Phonon future scope. |
| `readme_phonon_dos` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Phonon future scope. |
| `readme_phonon_bands_and_dos` | none | `readme_function_demo` | false | false | false | n/a | false | false | `FUTURE_SCOPE` | Phonon future scope. |
| official static physics coverage | `structure.coordination_hist` | n/a | false | false | false | n/a | false | false | `MAPPING_ONLY` | No current official direct-uploadable case maps to this tool. |
| official static physics coverage | `structure.xrd` | n/a | false | false | false | n/a | false | false | `MAPPING_ONLY` | No current official direct-uploadable case maps to this tool. |
| official static physics coverage | `structure.rdf` | n/a | false | false | false | n/a | false | false | `MAPPING_ONLY` | No current official direct-uploadable case maps to this tool. |

No row is marked `PASS` because no official static physics case was directly executed and verified in Phase 10F-1.
