# Phase 10N-0 Current Capability Inventory

Status labels are intentionally conservative. A Registry manifest, parser, Viewer or
test fixture alone is not a production scientific capability.

| Domain / capability | Current Tool or surface | Current authority | Classification | N1-N5 consequence |
| --- | --- | --- | --- | --- |
| Composition statistics | `composition.*`, `dataset.composition_space` | registered Adapters and Artifacts | PRODUCTION_READY | reusable foundation |
| Materials Explorer | `dataset.materials_explorer` | typed table Artifact and adapted selection | PRODUCTION_READY | reusable identity/selection pattern |
| Materials ML regression/uncertainty/classification | `ml.*_evaluation` | evaluation Artifacts and Projectors | READY_WITH_EXPLICIT_LIMITS | no new science in N0 |
| Composition Space | `dataset.composition_space` | bounded table/plot Artifact | PRODUCTION_READY | reusable panel pattern |
| Structure parser/profile | `mdi_material_parsers`, `DataProfile 2.0` | parser and Profile | REUSABLE_FOUNDATION | N1/N2 input readiness |
| Structure summary/static tools | `structure.summary`, lattice, spacegroup, composition | registered Adapter | PRODUCTION_READY | no local environment claim |
| Static structure Viewer | `structure_json`, `viewer_scene*` | strict M4 renderer registry | READY_WITH_EXPLICIT_LIMITS | N1/N2 overlay consumer |
| Distance-cutoff coordination histogram | `structure.coordination_hist` | `phase10e1.coordination_hist.v1` | READY_WITH_EXPLICIT_LIMITS | foundation only; not CrystalNN/VoronoiNN |
| Theoretical XRD | `structure.xrd` | `XrdPatternAdapter` | READY_WITH_EXPLICIT_LIMITS | N3 theoretical input only |
| Static RDF | `structure.rdf` | `RdfAdapter` | READY_WITH_EXPLICIT_LIMITS | N4 comparison/foundation only |
| Coordination environment sunburst | `structure.chem_env_sunburst` | registry mapping / v2 tool entry | MAPPING_ONLY | no production scientific environment authority found |
| Trajectory import | `structure.trajectory_import` | `phase10g.trajectory.v1` parser and Artifact | READY_WITH_EXPLICIT_LIMITS | N4 input authority |
| Trajectory Viewer | `trajectory_json`, `structure.trajectory_viewer` | M4 adapted renderer | READY_WITH_EXPLICIT_LIMITS | no RDF/MSD/diffusion |
| Phonon bands/DOS/combined | `phonon.*` | Phonon Artifacts and renderers | PRODUCTION_READY | bounded existing capability |
| Brillouin Zone | `structure.brillouin_zone` | reciprocal/BZ/kpath Artifacts | PRODUCTION_READY | N5 reciprocal consumer pattern |
| Volumetric metadata/slices/isosurface | `structure.volumetric_data` | bounded volumetric Artifacts and Viewer | READY_WITH_EXPLICIT_LIMITS | no new electronic extraction |
| Grounded interpretation/evidence | M10L-4/5 interpretation | persisted Claims/Evidence | READY_WITH_EXPLICIT_LIMITS | future projectors only |
| Workspace | M10M Workspace 1.0 | server-persisted reference state | PRODUCTION_READY | reuse unchanged |
| Report/Recipe | M10M contracts | immutable pair and exports | PRODUCTION_READY | future source representations only |
| CrystalNN | no registered production Tool/Adapter/Artifact | none | MISSING_10N | N1 |
| VoronoiNN | no registered production Tool/Adapter/Artifact | none | MISSING_10N | N1 |
| Coordination polyhedra | no registered production Tool/Adapter/Artifact | none | MISSING_10N | N2 |
| Experimental XRD ingestion/comparison | no registered product contract | none | MISSING_10N | N3 |
| Trajectory RDF/MSD/diffusion | no registered product contract | none | MISSING_10N | N4 |
| Electronic Band/DOS | no registered product contract or renderer | none | MISSING_10N | N5 |

## Inventory boundaries

Current statuses are based on `packages/tool-registry`, `packages/adapters`,
`packages/material-parsers`, `packages/artifact-core`, `packages/schemas`, `apps/web`
and retained Phase 10K-M evidence. Future proposals are not included in the current
Registry snapshot of 53 tools.
