# Phase 10F-12 Viewer Scene Adapter Readiness Matrix

| Area | Status | Evidence | Decision |
|---|---|---|---|
| `viewer_scene.v1` canonical contract | READY | Phase 10F-8/9 validator and fixtures | Contract remains canonical |
| Contract validator | READY | `validate_viewer_scene` and fixture replay tests | Ready |
| Minimal adapter implementation | READY | `StructureViewerSceneAdapter` | Ready |
| Tool Registry integration | READY | `structure.viewer_scene` manifest entry and registry tests | Ready |
| Params validation | READY | Strict params schema plus adapter-side validation | Ready |
| Execution-path integration | READY | `execute_tool_request` and `QueueWorkerRuntime` tests | Ready |
| Artifact generation | READY | `viewer_scene.json`, manifest, summary, recipe | Ready |
| Manifest generation | READY | Canonical manifest validator passes | Ready |
| Deterministic replay | READY | Evidence hashes match | Ready |
| JSON-only preview compatibility | READY | Frontend regression uses adapter-generated evidence JSON | Ready |
| Service-backed/API evidence | READY | In-memory planner/job/runtime execution test | Ready for current local service-backed scope |
| Real browser evidence regression | READY | Phase 10F-11 command remains the browser regression path | Ready |
| Renderer handoff | PARTIAL_READY | Contract, manifest, preview, and adapter exist; renderer API not designed | Partial |
| Renderer implementation | NOT_READY | No dependency/security review for renderer | Do not start directly |
| Full `structure.viewer_3d` | NOT_READY | Minimal adapter only | Do not start directly |

## Next-Scope Information for Reviewer

The adapter now runs through the registry and execution path and emits
preview-compatible artifacts. Remaining gaps are renderer-handoff details,
whether old Phase 10D viewer metadata/export tools should be deprecated or
migrated, and whether adapter Browser/API evidence should be hardened with a
real job-backed browser capture before dependency evaluation.
