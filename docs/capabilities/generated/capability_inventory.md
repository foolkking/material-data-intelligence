# Generated Scientific Capability Inventory

> Generated from canonical Requirement, Capability Pack, Tool, Adapter,
> Artifact-port, Result-projector and Viewer registries. Do not edit by hand.

## Extension health

- Accepted: **YES**
- Capabilities: **17** (17 valid / 0 incomplete)
- Packs: **5**
- Tools: **62**
- Adapters: **50**
- Result projectors: **17**
- Viewer descriptors: **11**
- Duplicate capability authorities: **0**
- Inventory fingerprint: `035cfe4801fd885414f8eccf99d7b89b358212b220e2bc048ee7a76581a9a794`

## Capability contracts

| Capability | Pack | Status | Requirements | Tool → Adapter | Inputs | Results | Ports | Result projector | I/V/R | Qualification |
|---|---|---|---|---|---|---|---|---|---|---|
| `data.composition_space@1.0` | `core.data` | ACTIVE / VALID | `data.explore_composition_space` | `dataset.composition_space` → `CompositionSpaceAdapter` | `materials.dataset`<br>`materials.table` | `data.composition_space` | GENERIC | `agent2.data.composition_space` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |
| `data.materials_explorer@1.0` | `core.data` | ACTIVE / VALID | `data.explore_materials` | `dataset.materials_explorer` → `DatasetMaterialsExplorerAdapter` | `materials.dataset`<br>`materials.table` | `data.materials_explorer` | GENERIC | `agent2.data.materials_explorer` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |
| `diffraction.experimental_theoretical_comparison@1.0` | `core.other` | ACTIVE / VALID | `diffraction.compare_experimental_theoretical` | `structure.experimental_xrd_comparison` → `ExperimentalXrdComparisonAdapter` | `diffraction.xrd.experimental`<br>`diffraction.xrd.theoretical` | `diffraction.xrd.comparison` | REQUIRED | `agent2.diffraction.experimental_theoretical_comparison` | GENERIC/GENERIC/GENERIC | REFERENCE_VALIDATED |
| `diffraction.theoretical_xrd@1.0` | `core.other` | ACTIVE / VALID | `diffraction.generate_theoretical_pattern` | `structure.xrd` → `XrdPatternAdapter` | `structure.crystal` | `diffraction.xrd.theoretical` | SUPPORTED | `agent2.diffraction.theoretical_xrd` | GENERIC/SUPPORTED/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `electronic.band_structure@1.0` | `core.electronic` | ACTIVE / VALID | `electronic.inspect_band` | `electronic.band_structure` → `ElectronicBandStructureAdapter` | `electronic.band_structure` | `electronic.band_structure` | SUPPORTED | `agent2.electronic.band_structure` | GENERIC/SUPPORTED/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `electronic.dos@1.0` | `core.electronic` | ACTIVE / VALID | `electronic.inspect_dos` | `electronic.dos` → `ElectronicDosAdapter` | `electronic.dos` | `electronic.dos` | SUPPORTED | `agent2.electronic.dos` | GENERIC/SUPPORTED/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `ml.regression_evaluation@1.0` | `core.other` | ACTIVE / VALID | `ml.evaluate_regression` | `ml.regression_evaluation` → `RegressionEvaluationAdapter` | `materials.dataset`<br>`materials.table` | `ml.regression.evaluation` | GENERIC | `agent2.ml.regression_evaluation` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |
| `phonon.band@1.0` | `core.other` | ACTIVE / VALID | `phonon.inspect_band` | `phonon.band` → `PhononBandAdapter` | `phonon.band_structure` | `phonon.band` | SUPPORTED | `agent2.phonon.band` | GENERIC/SUPPORTED/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `phonon.band_dos@1.0` | `core.other` | ACTIVE / VALID | `phonon.inspect_band`<br>`phonon.inspect_dos` | `phonon.band_dos` → `PhononBandDosAdapter` | `phonon.band_structure`<br>`phonon.dos` | `phonon.band_dos` | REQUIRED | `agent2.phonon.band_dos` | GENERIC/GENERIC/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `phonon.dos@1.0` | `core.other` | ACTIVE / VALID | `phonon.inspect_dos` | `phonon.dos` → `PhononDosAdapter` | `phonon.dos` | `phonon.dos` | SUPPORTED | `agent2.phonon.dos` | GENERIC/SUPPORTED/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `structure.coordination_crystalnn@1.0` | `core.structure` | ACTIVE / VALID | `structure.inspect_coordination`<br>`structure.inspect_coordination_crystalnn` | `structure.coordination_crystalnn` → `CrystalNNCoordinationAdapter` | `structure.crystal` | `structure.coordination.crystalnn` | SUPPORTED | `agent2.structure.coordination_crystalnn` | GENERIC/GENERIC/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `structure.coordination_hist@1.0` | `core.structure` | ACTIVE / VALID | `structure.inspect_coordination_hist` | `structure.coordination_hist` → `CoordinationHistAdapter` | `structure.crystal` | `structure.coordination.hist` | GENERIC | `agent2.structure.coordination_hist` | GENERIC/GENERIC/GENERIC | REFERENCE_VALIDATED |
| `structure.coordination_voronoinn@1.0` | `core.structure` | ACTIVE / VALID | `structure.inspect_coordination`<br>`structure.inspect_coordination_voronoi` | `structure.coordination_voronoinn` → `VoronoiNNCoordinationAdapter` | `structure.crystal` | `structure.coordination.voronoi` | SUPPORTED | `agent2.structure.coordination_voronoinn` | GENERIC/GENERIC/GENERIC | EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED |
| `structure.rdf@1.0` | `core.structure` | ACTIVE / VALID | `structure.compute_rdf` | `structure.rdf` → `RdfAdapter` | `structure.crystal` | `structure.rdf` | GENERIC | `agent2.structure.rdf` | GENERIC/GENERIC/GENERIC | REFERENCE_VALIDATED |
| `trajectory.diffusion@1.0` | `core.trajectory` | ACTIVE / VALID | `trajectory.estimate_diffusion` | `trajectory.diffusion` → `TrajectoryDiffusionAdapter` | `trajectory.msd` | `trajectory.diffusion` | REQUIRED | `agent2.trajectory.diffusion` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |
| `trajectory.msd@1.0` | `core.trajectory` | ACTIVE / VALID | `trajectory.compute_msd` | `trajectory.msd` → `TrajectoryMsdAdapter` | `trajectory.atomic` | `trajectory.msd` | SUPPORTED | `agent2.trajectory.msd` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |
| `trajectory.rdf@1.0` | `core.trajectory` | ACTIVE / VALID | `trajectory.compute_rdf` | `trajectory.rdf` → `TrajectoryRdfAdapter` | `trajectory.atomic` | `trajectory.rdf` | SUPPORTED | `agent2.trajectory.rdf` | GENERIC/GENERIC/GENERIC | DOMAIN_VALIDATED |

## Issues

- None.

## Classified non-Capability-reachable components

These entries are classifications, not deletion candidates.

| Kind | Component | Classification | Reason |
|---|---|---|---|
| TOOL | `composition.chem_sys_sunburst` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.chem_sys_treemap` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.cluster_2d` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.cluster_3d` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.elements_hist` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.formula_statistics` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.ptable_heatmap` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.ptable_heatmap_splits` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.ptable_hists` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.ptable_scatter` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `composition.summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.basic_metrics` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.classification_evaluation` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.density_scatter` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.error_by_chem_sys` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.error_by_element` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.error_distribution` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.outlier_table` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.parity_plot` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.uncertainty_calibration` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `ml.uncertainty_evaluation` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `phonon.animation` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.brillouin_zone` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.chem_env_sunburst` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.composition_from_structure` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.lattice_summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.local_environment_polyhedra` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.preview_metadata` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.spacegroup_summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.structure_2d` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.structure_3d` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.trajectory_import` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.trajectory_viewer` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.viewer_3d` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.viewer_export_package` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.viewer_scene` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.viewer_scene_metadata` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `structure.volumetric_data` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `table.distribution_summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `table.numeric_summary` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `trajectory.viewer` | FUTURE_OR_EXPERIMENTAL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `viz.correlation` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `viz.histogram` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| TOOL | `viz.scatter` | PUBLIC_LOW_LEVEL_TOOL | Registered executable Tool is not currently Agent Capability-reachable. |
| VIEWER | `scientific.scientific-table` | SOURCE_VIEWER | Viewer is reached from a scientific source type rather than a Capability output binding. |
| VIEWER | `scientific.scientific-table` | SOURCE_VIEWER | Viewer is reached from a scientific source type rather than a Capability output binding. |
| VIEWER | `scientific.structure-3d` | SOURCE_VIEWER | Viewer is reached from a scientific source type rather than a Capability output binding. |
| VIEWER | `scientific.trajectory` | SOURCE_VIEWER | Viewer is reached from a scientific source type rather than a Capability output binding. |
| VIEWER | `scientific.volumetric` | PRESENTATION_EXTENSION | Viewer descriptor is not currently reached by Capability input/output types. |
