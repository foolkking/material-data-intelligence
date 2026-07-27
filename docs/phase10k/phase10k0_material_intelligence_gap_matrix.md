# Phase 10K-0 Material Intelligence Gap Matrix

Status values are exact: `READY`, `REUSABLE_FOUNDATION`, `PARTIAL`,
`MISSING_INITIAL_RELEASE`, `DEFER_10L`, `DEFER_10M`, `DEFER_10N`, `FUTURE`, or
`NOT_PLANNED`.

| Domain | Capability | Current evidence | Status | Owner |
| --- | --- | --- | --- | --- |
| Input | CSV and limited JSON tables | Real parser/tests | READY | Existing |
| Input | CIF/POSCAR structures | Real parser/tests | READY | Existing |
| Input | XYZ/EXTXYZ | Real parser/tests | READY | Existing |
| Input | Approved trajectory inputs | Dedicated parser/product | READY | Existing |
| Input | Approved volumetric inputs | Dedicated parser/product | READY | Existing |
| Input | General phonon file discovery | Product-specific paths only | PARTIAL | 10K-1 discovery boundary |
| Profile | Basic table columns and roles | `DataProfile 0.1` | REUSABLE_FOUNDATION | Existing |
| Profile | Basic structure aggregate | `DataProfile 0.1` | REUSABLE_FOUNDATION | Existing |
| Profile | Trajectory/phonon/volumetric discovery | Metadata not surfaced | MISSING_INITIAL_RELEASE | 10K-1 |
| Profile | Capability and analysis availability | No canonical contract | MISSING_INITIAL_RELEASE | 10K-1 |
| Profile | Materials property semantics/units | No canonical contract | MISSING_INITIAL_RELEASE | 10K-1 |
| Profile | Regression/uncertainty/classification task model | Regression heuristic only | MISSING_INITIAL_RELEASE | 10K-1 |
| Identity | Stable dataset sample identity | No cross-artifact row reference | MISSING_INITIAL_RELEASE | 10K-1 |
| Dataset | Element and chemical-system aggregation | Real composition adapters | REUSABLE_FOUNDATION | 10K-2 reuse |
| Dataset | Formula statistics | Real composition adapter | REUSABLE_FOUNDATION | 10K-2 reuse |
| Dataset | Generic numeric/category distributions | Real table adapters | REUSABLE_FOUNDATION | 10K-2 reuse |
| Dataset | Structure aggregate statistics | Real lightweight structure adapters | REUSABLE_FOUNDATION | 10K-2 reuse |
| Dataset | Coherent materials overview | No product contract/UI | MISSING_INITIAL_RELEASE | 10K-2 |
| Dataset | Property distributions with units | No property contract | MISSING_INITIAL_RELEASE | 10K-2 |
| Dataset | Dataset/train-test comparison | No implementation | MISSING_INITIAL_RELEASE | 10K-2 |
| Dataset | Reliable duplicates | No implementation | MISSING_INITIAL_RELEASE | 10K-2 |
| Dataset | Near-duplicates | No reliable definition yet | PARTIAL | 10K-2 decision |
| Dataset | Linked sample/outlier inspection | No stable sample identity | MISSING_INITIAL_RELEASE | 10K-2 |
| ML | MAE/RMSE/R2 | Real adapter | REUSABLE_FOUNDATION | 10K-3 reuse |
| ML | Error distribution | Real adapter | REUSABLE_FOUNDATION | 10K-3 reuse |
| ML | Density scatter | Real adapter | REUSABLE_FOUNDATION | 10K-3 reuse |
| ML | Largest-error rows | Real adapter, no stable sample ref | PARTIAL | 10K-3 |
| ML | Parity/residual evaluation product | Manifest/planning is not executable | MISSING_INITIAL_RELEASE | 10K-3 |
| ML | Chemistry-conditioned errors | Manifest/planning is not executable | MISSING_INITIAL_RELEASE | 10K-3 |
| ML | Model comparison | No model identity contract | MISSING_INITIAL_RELEASE | 10K-3 |
| ML | Uncertainty calibration/filtering | No executable adapter | MISSING_INITIAL_RELEASE | 10K-3 |
| ML | Classification evaluation | No task/probability contract | MISSING_INITIAL_RELEASE | 10K-3 |
| Composition | Formula parsing and element fractions | pymatgen-backed adapters | REUSABLE_FOUNDATION | 10K-4 reuse |
| Composition | Deterministic vectorization | No canonical payload | MISSING_INITIAL_RELEASE | 10K-4 |
| Composition | PCA | No implementation | MISSING_INITIAL_RELEASE | 10K-4 |
| Composition | Clustering and linked inspection | Manifest/planning only | MISSING_INITIAL_RELEASE | 10K-4 |
| Composition | UMAP | No dependency or contract | FUTURE | Not required for 10K |
| Planner | Real profile retrieval | API path exists | REUSABLE_FOUNDATION | Existing |
| Planner | Profile-based column binding | Narrow mock behavior | PARTIAL | 10K foundation |
| Planner | Capability-aware multi-tool plans | Mostly keyword routing | DEFER_10L | 10L |
| Interpretation | Structured scientific findings | Generic report only | DEFER_10L | 10L |
| Frontend | Dataset selection/upload/profile | PlannerWorkbench | REUSABLE_FOUNDATION | 10K reuse |
| Frontend | Dataset intelligence result surfaces | No dedicated product | MISSING_INITIAL_RELEASE | 10K-2 through 10K-5 |
| Workspace | Unified cross-artifact workspace | Not implemented | DEFER_10M | 10M |
| Professional | CrystalNN/VoronoiNN and polyhedra | Planned initial release | DEFER_10N | 10N |
| Professional | Experimental XRD comparison | Planned initial release | DEFER_10N | 10N |
| Professional | Trajectory RDF/MSD/diffusion | Planned initial release | DEFER_10N | 10N |
| Professional | Electronic Band/DOS | Planned initial release | DEFER_10N | 10N |
| Advanced | Fermi Surface | Current canonical Future Scope | FUTURE | Unqueued |
| Platform | Enterprise SaaS/plugin/deployment products | Current canonical Not Planned | NOT_PLANNED | Unqueued |

## Readiness Decisions

```text
Material Data Profile 2.0: MISSING_INITIAL_RELEASE
Dataset Materials Explorer: MISSING_INITIAL_RELEASE
Materials ML Evaluation: PARTIAL foundation; product missing
Composition Space: MISSING_INITIAL_RELEASE
Phase 10K integrated flow: MISSING_INITIAL_RELEASE
Phase 10K-1 entry: READY after 10K-0 archive
```

No row in this matrix promotes Future or Not Planned scope into the executable
queue.
