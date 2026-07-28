# Capability Status Matrix

Status: CURRENT

`READY` means delivered and validated within documented limits.
`PARTIAL_READY` means useful foundations exist but the initial-release product
boundary is incomplete. `PLANNED`, `FUTURE`, and `NOT_PLANNED` are not claims of
implementation.

| Domain | Capability | Current Status | Initial Release | Future | Tool / Product |
| --- | --- | --- | --- | --- | --- |
| Platform | Registry/Adapter validated execution | READY | Yes | No | Tool Registry, QueueWorkerRuntime |
| Platform | Artifact/Recipe/Report foundations | READY | Yes | No | Artifact platform |
| Data | Current parsing and normalization | READY | Yes | No | Existing registered parsers only |
| Data | Material Data Profile 2.0 | READY | Yes | No | Phase 10K-1 |
| Dataset | Materials explorer and comparisons | READY | Yes | No | `dataset.materials_explorer` within Phase 10K-2 limits |
| Dataset | Normalized atomic-fraction composition feature space | READY | Yes | No | `dataset.composition_space`; deterministic atomic-number basis |
| Dataset | Deterministic 2D PCA projection | READY | Yes | No | `dataset.composition_space`; center-only SVD with stable sign convention |
| Dataset | Bounded KMeans clustering | READY | Yes | No | Optional `dataset.composition_space` mode over the original feature matrix |
| Dataset | Property coloring | READY | Conditional | No | Profile 2.0 `material_property` semantics with compatible units |
| Dataset | ML error/uncertainty coloring | READY | Conditional | No | Explicit Phase 10K-3 artifact binding by `objectId + sampleRef` |
| Dataset | Shared composition-space dataset comparison | READY | Conditional | No | Explicit group/resource identity and one shared basis/PCA fit |
| Dataset | Composition-space sample inspection | READY | Yes | No | Stable object-qualified sample keys with numeric table fallback |
| Dataset | UMAP projection | FUTURE | No | Yes | No dependency or implementation in Phase 10K-4 |
| Dataset | t-SNE projection | FUTURE | No | Yes | Not implemented; no baseline requirement |
| Dataset | Learned material embeddings | FUTURE | No | Yes | No pretrained/foundation-model embedding authority |
| ML | Regression model-result evaluation | READY | Yes | No | `ml.regression_evaluation` within Phase 10K-3 limits |
| ML | Uncertainty evaluation | READY | Conditional | No | `ml.uncertainty_evaluation` when Profile 2.0 has an explicit binding |
| ML | Classification evaluation | READY | Conditional | No | `ml.classification_evaluation`; binary curves require explicit valid probabilities |
| ML | Chemistry-conditioned error | READY | Conditional | No | Phase 10K-3 descriptive element/system groups with small-group disclosure |
| ML | Common-sample model comparison | READY | Conditional | No | Phase 10K-3 shared-target finite-sample intersection |
| Agent | Structured validated planning | READY | Yes | No | AnalysisPlan/PlanValidator |
| Agent | Capability-aware planning | PARTIAL_READY | Yes | No | Phase 10L-2 |
| Agent | Bounded multi-tool analysis | PARTIAL_READY | Yes | No | Phase 10L-3 |
| Agent | Scientific result interpretation | PLANNED | Yes | No | Phase 10L-4 |
| Workspace | Phase 9C workspace foundation | READY | Yes | No | PlannerWorkbench |
| Workspace | Unified scientific workspace | PLANNED | Yes | No | Phase 10M |
| Structure | Production periodic viewer/inspection | READY | Yes | No | `structure.viewer_3d` |
| Structure | RDF/coordination/calculated XRD | READY | Yes | No | Existing structure tools |
| Structure | CrystalNN/VoronoiNN | PLANNED | Yes | No | Phase 10N-1 |
| Structure | Local environments/polyhedra | PLANNED | Yes | No | Phase 10N-2 |
| Experiment | Experimental XRD comparison | PLANNED | Yes | No | Phase 10N-3 |
| Experiment | Full Rietveld refinement | FUTURE | No | Yes | Unimplemented |
| Dynamics | Trajectory viewer | READY | Yes | No | Existing trajectory product |
| Dynamics | RDF/MSD/diffusion/time analytics | PLANNED | Yes | No | Phase 10N-4 |
| Phonon | Band/DOS/animation | READY | Yes | No | Existing phonon tools/products |
| Reciprocal | Brillouin zone | READY | Yes | No | `structure.brillouin_zone` |
| Electronic | Electronic Band/DOS/BZ link | PLANNED | Yes | No | Phase 10N-5; no current tool |
| Electronic | Fermi Surface | FUTURE | No | Yes | Unimplemented |
| Volumetric | Source-specific products and rendering | READY | Yes | No | Existing volumetric product |
| Volumetric | Bader/ELF topology/advanced fields | FUTURE | No | Yes | Unimplemented |
| Compute | External DFT/HPC execution | FUTURE | No | Yes | No current authority |
| Code | Optional sandboxed notebook/script | FUTURE | No | Yes | No current authority |
| Enterprise | SaaS/IAM/KMS/deployment products | NOT_PLANNED | No | No | Outside product |
| Ecosystem | Plugin marketplace | NOT_PLANNED | No | No | Outside product |

Scientific method limitations and source-format support remain authoritative in
the relevant contract and phase documents. A roadmap entry never upgrades a
capability status by itself.
