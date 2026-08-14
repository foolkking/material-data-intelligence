# Initial Release Documentation

Material Data Intelligence and Scientific Visualization Platform turns supplied materials data into validated, auditable analysis workflows. It is for scientists who need controlled dataset, structure, trajectory, phonon, volumetric, and electronic-data analysis without arbitrary code execution or hidden scientific authority in the browser or LLM.

## Current release authority

| Authority | Current value |
|---|---|
| Fact Model | `92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a` |
| Scope Baseline | `bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba` |
| Phase 12 product baseline | `29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4` |
| Registry | 62 Tools |
| DataProfile / Intent / Eligibility | `2.4` / `1.0` / `1.0` |
| AnalysisPlan | `0.1`, `0.2` |
| Migration head | `0007_phase10m1_workspace_domain` |
| Workspace caps | 32 panels, 128 layout revisions |

## Canonical architecture

`DataProfile -> AnalysisIntent -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> Recipe`

Registered Adapters and persisted Artifacts own scientific computation facts. The LLM plans, routes, and explains; it does not execute science. Artifacts are inert data. Recipes and recommendations are non-executable.

## Seven verified workflows

| [Demo 1: Dataset Intelligence + Composition Space](../reproducibility/demo1.md) | `dataset.composition_space, dataset.materials_explorer` |
| [Demo 2: Materials ML](../reproducibility/demo2.md) | `dataset.materials_explorer, ml.regression_evaluation` |
| [Demo 3: Structure + coordination + local environment + polyhedra + experimental XRD](../reproducibility/demo3.md) | `structure.coordination_crystalnn, structure.experimental_xrd_comparison, structure.local_environment_polyhedra, structure.xrd` |
| [Demo 4: Trajectory + RDF + MSD + diffusion](../reproducibility/demo4.md) | `trajectory.diffusion, trajectory.msd, trajectory.rdf` |
| [Demo 5: Phonon + Brillouin Zone](../reproducibility/demo5.md) | `phonon.band, phonon.band_dos, phonon.dos, structure.brillouin_zone` |
| [Demo 6: Volumetric](../reproducibility/demo6.md) | `structure.volumetric_data` |
| [Demo 7: Electronic Band + DOS](../reproducibility/demo7.md) | `electronic.band_structure, electronic.dos` |

Attempt 6 observed 18 ToolCalls, 85 persisted Artifacts, seven Workspaces, seven UI-finalized Reports, seven paired Recipes, and zero unreachable Artifacts. These are release evidence, not fixed future API cardinalities.

## Start here

- [Final archive and presentation package](../final/README.md)
- [Installation and quick start](quick-start.md)
- [Architecture and authority](architecture.md)
- [Input support](input-support.md)
- [API reference](api-reference.md)
- [Known limitations and claim boundaries](limitations.md)
- [Security model](security.md)
- [Provider policy](provider.md)
- [Troubleshooting](troubleshooting.md)
- [Deterministic reproducibility](../reproducibility/README.md)
- [Phase 13 forensic history](forensic-history.md)
