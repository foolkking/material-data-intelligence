# Task Queue

Phase 10N-2:
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10N-3:
PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT

Phase 10N-4:
IMPLEMENTED / AWAITING_IMPLEMENTATION_CI

---TASK---
Task: Phase 10N-4 Trajectory RDF / MSD / Diffusion
Status: IN_PROGRESS
Reviewer authority：Phase 10N-4 Reviewer Prompt；N3 archive `0a33d84ea7c97b423f825f0c9784c57f1acfac3b` / CI `31289319532` success。
Baseline：Registry 57；DataProfile 2.2；migration `0007_phase10m1_workspace_domain`；N5 NOT QUEUED / NOT EXECUTABLE。
Approved tools：`trajectory.rdf@0.1.0`、`trajectory.msd@0.1.0`、`trajectory.diffusion@0.1.0`；expected Registry 60；不得新增第四个 N4 Tool。
Acceptance：N4-A01 BASELINE_TRAJECTORY_AUTHORITY_AND_EXACT_CONTRACT_CLOSURE；N4-A02 TRAJECTORY_FRAME_ATOM_TIME_CELL_IDENTITY_VALIDITY_AND_UNWRAPPING；N4-A03 WHOLE_WINDOW_AND_SPECIES_PAIR_TRAJECTORY_RDF；N4-A04 TOTAL_SPECIES_AND_DIRECTIONAL_MSD；N4-A05 DIFFUSION_FIT_WINDOW_DIAGNOSTICS_AND_SCIENTIFIC_CLAIM_BOUNDARY；N4-A06 PROFILE_ELIGIBILITY_PLANNER_PLANVALIDATOR_DEPENDENCY_RUNTIME_AND_PERSISTENCE；N4-A07 WORKSPACE_TRAJECTORY_RDF_MSD_DIFFUSION_SELECTION_AND_INSPECTOR；N4-A08 GROUNDED_INTERPRETATION_REPORT_RECIPE_AND_PROVENANCE；N4-A09 REFERENCES_TOLERANCES_PERFORMANCE_ACCESSIBILITY_SECURITY_AND_SERVICE_EVIDENCE；N4-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_N5_REVIEWER_GATE。
Scientific seals：MSD only from validated server-side unwrapped coordinates；Diffusion only from exact persisted MSD Artifact；explicit fit window；no automatic window optimization；ballistic/transient windows cannot qualify silently；physical time required；no frontend scientific recomputation。
Change seals：database/API family/dependencies/lockfile unchanged；migration remains `0007_phase10m1_workspace_domain`；DataProfile 2.3 only as additive versioned JSON if required。
Lifecycle：implementation exact-SHA CI → completion-record exact-SHA CI → queue-archive exact-SHA CI；task remains until verified archive；Phase 10N-5 stays REVIEWER_GATE and no executable task may be created.
---END---
