# Identity and Lineage Map

| Identity | Current authority | Version/hash binding | Frontend representation | Cross-artifact now | 10M decision |
|---|---|---|---|---|---|
| Project | project row | project ID | implicit/local | scope only | required Workspace FK |
| Dataset/version | dataset + Profile | dataset ID/version | header/sidebar | specialized | exact source ref |
| DataProfile | profile row | profile ID/semantic hash | profile summary | planning scope | exact immutable ref |
| Object/sample | Profile 2.0 | objectId/objectHash + sampleRef | dataset/ML panels | K5 products | selection kind |
| Structure | resource semantic | objectId/objectHash | viewer | structure products | selection kind |
| Periodic site | viewer contract | site index plus periodic image offset and scene hash | viewer inspector | viewer-local | exact typed selection |
| Atom | structure/trajectory contract | atom/site identity plus resource hash | viewers | product-local | exact typed selection |
| Trajectory frame | trajectory contract | trajectory hash + frame index/time | trajectory viewer | no | exact typed selection |
| Phonon q-point/branch/mode | phonon contract | source hashes + exact IDs/index and path variant | phonon/BZ | Band/BZ only | exact typed selection |
| Reciprocal point/segment | BZ contract | source hash + stable point/segment ID | BZ inspector | Band/BZ only | exact typed selection |
| Volumetric field/region | volumetric contracts | field ID/content hash/resource scope | volumetric panels | no | field selection; probes remain panel-local |
| Intent | AnalysisIntent 1.0 | intent ID/hash | planning panels | Job provenance | immutable source ref |
| Eligibility/decision | L2 contracts | resolution/decision IDs/hashes | capability panel | Job provenance | immutable source ref |
| Plan/step | Plan 0.1/0.2 | plan hash + stepId | plan/dependency panels | execution | immutable source ref |
| Dependency binding | Plan 0.2 | bindingId/graphHash | dependency panel | runtime lineage | immutable source ref |
| Job | jobs table | job ID, source Plan | header/timeline | main container | one Workspace per Job |
| ToolCall | tool_calls | jobId + stepId/idempotency | results/audit | artifact producer | inspector target |
| Artifact | artifacts | artifact ID/hash/checksum | gallery/renderers | lineage/specialized links | panel source ref |
| Artifact lineage | lineage record | lineage ID/hash | dependency audit | exact upstream refs | inspector link |
| Evidence item | EvidenceBundle 1.0 | evidence ID/bundle hash/field locator | drill-down | claims | selection kind |
| Claim/interpretation | interpretation contracts | claim/interpretation IDs/hashes | findings | evidence refs | selection kind |
| Report | reports table | report ID/version/job | static preview | no panel refs | reused first-class output |
| Recipe | recipe table/Recipe 0.1 | recipe ID/version/job/plan | static preview | no dependency-complete rerun | additive WorkspaceRecipe 1.0 |
| Workspace | absent | absent | absent | absent | Workspace 1.0 |

## Identity rules

**REVIEWER-SEALED RECOMMENDATION**

Cross-panel propagation requires exact kind, ID, source artifact hash, dataset/resource version, and an allowlisted mapper. Array index alone, row order, display label, fuzzy match, guessed unit, and implicit resource conversion are invalid.

Lineage remains owned by existing persisted records. Workspace stores references and never reconstructs lineage from panel order.
