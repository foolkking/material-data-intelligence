# Scientific Surface / Viewer Coverage Matrix

Source of truth: `apps/api/mdi_api/research_agent/capabilities/defaults.py`,
`apps/api/mdi_api/research_agent/capabilities/packs.py`,
`apps/api/mdi_api/scientific_viewers/`, `apps/api/mdi_api/scientific_results/`,
and the corresponding `apps/web/app/components/` renderers.

`NOT_QUALIFIED` means the repository has a declared capability or renderer
but Phase 14-R has not yet produced a fresh real-data browser and
PostgreSQL/Redis/MinIO evidence package for that row.

| Capability ID | Pack | Input | Tool binding | Result projector | Presentation | Viewer/Figure/Table | Evidence/Report | Current status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `structure.rdf` | core.structure | `structure.crystal` | `structure.rdf` | `agent2.structure.rdf` | metric/figure | RDF viewer/figure | supported | NOT_QUALIFIED |
| `structure.coordination_hist` | core.structure | `structure.crystal` | `structure.coordination_hist` | `agent2.structure.coordination_hist` | finding/table | table | supported | NOT_QUALIFIED |
| `structure.coordination_crystalnn` | core.structure | `structure.crystal` | `structure.coordination_crystalnn` | `agent2.structure.coordination_crystalnn` | finding/table | Structure Viewer | supported | PARTIAL |
| `structure.coordination_voronoinn` | core.structure | `structure.crystal` | `structure.coordination_voronoinn` | `agent2.structure.coordination_voronoinn` | finding/table | Structure Viewer | supported | PARTIAL |
| `diffraction.theoretical_xrd` | core.other | `structure.crystal` | `structure.xrd` | `agent2.diffraction.theoretical_xrd` | figure | XRD figure | supported | NOT_QUALIFIED |
| `diffraction.experimental_theoretical_comparison` | core.other | experimental + theoretical XRD | `structure.experimental_xrd_comparison` | `agent2.diffraction.experimental_theoretical_comparison` | finding/figure/table | XRD comparison | supported | NOT_QUALIFIED |
| `trajectory.rdf` | core.trajectory | `trajectory.atomic` | `trajectory.rdf` | `agent2.trajectory.rdf` | figure/table | trajectory viewer | supported | NOT_QUALIFIED |
| `trajectory.msd` | core.trajectory | `trajectory.atomic` | `trajectory.msd` | `agent2.trajectory.msd` | metric/figure/table | trajectory viewer | supported | NOT_QUALIFIED |
| `trajectory.diffusion` | core.trajectory | trajectory + MSD | `trajectory.diffusion` | `agent2.trajectory.diffusion` | finding/metric | N/A (derived metric) | supported | NOT_QUALIFIED |
| `phonon.band` | core.other | `phonon.band_structure` | `phonon.band` | `agent2.phonon.band` | figure/table | Phonon Band Viewer | supported | NOT_QUALIFIED |
| `phonon.dos` | core.other | `phonon.dos` | `phonon.dos` | `agent2.phonon.dos` | figure/table | Phonon DOS Viewer | supported | NOT_QUALIFIED |
| `phonon.band_dos` | core.other | band + DOS | `phonon.band_dos` | `agent2.phonon.band_dos` | figure/table | combined viewer | supported | NOT_QUALIFIED |
| `electronic.band_structure` | core.electronic | `electronic.band_structure` | `electronic.band_structure` | `agent2.electronic.band_structure` | figure/finding | Band Viewer | supported | PARTIAL |
| `electronic.dos` | core.electronic | `electronic.dos` | `electronic.dos` | `agent2.electronic.dos` | figure/finding | DOS Viewer | supported | NOT_QUALIFIED |
| `data.composition_space` | core.data | `materials.dataset`/`materials.table` | `dataset.composition_space` | `agent2.data.composition_space` | figure/table | Materials Explorer | supported | NOT_QUALIFIED |
| `data.materials_explorer` | core.data | `materials.dataset`/`materials.table` | `dataset.materials_explorer` | `agent2.data.materials_explorer` | table/finding | Scientific Table | supported | PARTIAL |
| `ml.regression_evaluation` | core.data | `materials.dataset` | `ml.regression_evaluation` | `agent2.ml.regression_evaluation` | metric/table | N/A | supported | NOT_QUALIFIED |

For every row the intended authority chain is:

```text
exact ScientificObjectVersion
→ validated ToolCall
→ persisted Artifact
→ ScientificResult projector
→ bounded Presentation block
→ read-only Viewer/Table/Figure
→ Evidence and Report
```

No row permits frontend scientific computation, arbitrary renderer loading, or
silent current-version substitution. Desktop/mobile, historical, archived,
performance and security columns remain `NOT_QUALIFIED` until the
corresponding real-user evidence is recorded.

