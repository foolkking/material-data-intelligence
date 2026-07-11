# Phase 10F-12 Viewer Scene Adapter Execution Evidence

## Evidence Location

Execution evidence is stored under:

`docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/`

The evidence pack contains:

- `sanitized_execution_request.json`
- `generated_viewer_scene.json`
- `generated_viewer_scene_manifest.json`
- `generated_recipe.json`
- `generated_artifact_metadata.json`
- `canonical_validator_result.json`
- `deterministic_replay_result.json`
- `preview_compatibility_result.json`
- `security_scan_result.json`
- `no_renderer_dependency_result.json`
- `command_log.md`

## Execution Path

The adapter was executed through `execute_tool_request` using Tool Registry
lookup and adapter creation. Automated tests also verify persisted
`planner_jobs` plus `QueueWorkerRuntime` execution.

## Evidence Decisions

| Area | Status | Evidence |
|---|---|---|
| Tool selected | READY | `generated_artifact_metadata.json` records `structure.viewer_scene` |
| Artifact generation | READY | `viewer_scene.json`, manifest, summary, and recipe produced |
| Canonical validator | READY | `canonical_validator_result.json` scene result is valid |
| Manifest validator | READY | `canonical_validator_result.json` manifest result is valid |
| Deterministic replay | READY | `deterministic_replay_result.json` hashes match |
| Preview compatibility | READY | `preview_compatibility_result.json` has `kind`, `version`, schema, caps, and `json_only` manifest |
| Security scan | READY | `security_scan_result.json` is PASS |

## Service-Backed/API Coverage

The test `test_persisted_viewer_scene_plan_executes_exactly_one_tool_call`
verifies the existing planner job and queue runtime path with in-memory
repositories. No production runtime route or core runtime semantic change was
added.
