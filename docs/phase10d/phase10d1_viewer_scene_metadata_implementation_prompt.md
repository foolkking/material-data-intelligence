# Phase 10D-1 Viewer Scene Metadata / Export Package Implementation Prompt

Use this prompt for the next implementation phase. Do not execute it during Phase 10D planning.

## Goal

Implement the metadata-first advanced structure visualization layer:

- `structure.viewer_scene_metadata`
- `structure.viewer_export_package`

Optional, only if low-risk and schema-only:

- `structure.viewer_3d_contract`

Do not implement a full interactive 3D viewer.

## Current Baseline

- Phase 10A table/viz adapters: PASS.
- Phase 10B composition visualization adapters: PASS.
- Phase 10C lightweight structure adapters: PASS.
- Runtime path remains: natural language request -> AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `/planner/jobs` -> QueueWorkerRuntime -> Tool Registry + Adapter -> Artifact / Report / Recipe -> Phase 9C UI.

## Repository Confirmation

Run first:

```bash
cd "E:\1project\Material Data Intelligence"
git status --short
git log --oneline -8
git branch --show-current
git tag --points-at HEAD
```

Stop if the branch is not `master`, the workspace is dirty, or the Phase 10D planning baseline is not present.

## Execution Boundaries

Do not break:

- Phase 8B persisted plan exact execution.
- Phase 9D gated live LLM path.
- Phase 10A table/viz adapters.
- Phase 10B composition adapters.
- Phase 10C lightweight structure adapters.

Do not modify:

- QueueWorkerRuntime main semantics.
- AnalysisPlanRepository main semantics.
- `/planner/jobs` validate/persist/enqueue semantics.
- PlanValidator security boundary except for minimal schema registration.
- Default CI LLM gate.

Do not run real LLM.

## Allowed Adapter Scope

### `structure.viewer_scene_metadata`

Purpose:

Convert validated structures into static viewer scene metadata for future renderer consumption.

Input resource:

- Uploaded structure.
- Normalized structure dict.
- Structure collection.

Params schema:

```json
{
  "maxSites": 500,
  "includeBonds": false,
  "bondPolicy": "none",
  "bondCutoff": null,
  "cameraPreset": "auto",
  "elementStyle": "default",
  "maxStructures": 20
}
```

Output artifacts:

- `viewer_scene.json`
- `summary.md`
- `recipe.json`

`viewer_scene.json` must include:

```json
{
  "artifactType": "structure.viewer_scene_metadata",
  "sceneContractVersion": "1.0",
  "structureCount": 0,
  "structures": [],
  "atoms": [],
  "bonds": [],
  "latticeVectors": [],
  "boundingBox": {},
  "camera": {},
  "elementStyles": {},
  "resourceCaps": {},
  "truncated": false,
  "warnings": []
}
```

### `structure.viewer_export_package`

Purpose:

Package viewer scene metadata and static style metadata into a deterministic export manifest. This is not an executable viewer.

Input resource:

- Uploaded structure.
- Normalized structure collection.
- Existing `viewer_scene.json` if the platform supports artifact-to-tool input.

Params schema:

```json
{
  "includeStyles": true,
  "includeManifest": true,
  "maxPackageBytes": 5000000
}
```

Output artifacts:

- `viewer_scene.json`
- `viewer_assets_manifest.json`
- `summary.md`
- `recipe.json`

`viewer_assets_manifest.json` must include:

```json
{
  "artifactType": "structure.viewer_export_package",
  "sceneContractVersion": "1.0",
  "assets": [],
  "hashes": {},
  "sizes": {},
  "rendererCompatibility": [],
  "executableContent": false,
  "externalResources": [],
  "warnings": []
}
```

### Optional `structure.viewer_3d_contract`

Only implement if it remains schema-only and does not imply renderer support.

Output artifacts:

- `viewer_contract.json`
- `summary.md`
- `recipe.json`

## Explicitly Forbidden in Phase 10D-1

Do not implement:

- `structure.viewer_3d`
- `structure.brillouin_zone_3d`
- `structure.xrd`
- `structure.rdf`
- `phonon.bands`
- `phonon.dos`
- `phonon.band_dos`

Do not add:

- Three.js renderer.
- WebGL renderer.
- MatterViz widget runtime.
- Artifact-supplied JavaScript execution.
- External URL loading.
- Notebook/script execution.
- Browser/API evidence.

## Tool Registry Registration

Each implemented tool must:

- Use domain `structure`.
- Have whitelist params schema with `additionalProperties=false`.
- Have resource limits for sites, structures, bonds, and package size.
- Declare deterministic output artifacts.
- Route through Tool Registry + Adapter execution.
- Emit `summary.md` and `recipe.json`.

## Mock Planner Routing

Add routing for:

- "generate viewer scene metadata" -> `structure.viewer_scene_metadata`
- "prepare structure viewer metadata" -> `structure.viewer_scene_metadata`
- "export viewer package" -> `structure.viewer_export_package`
- "package structure viewer scene" -> `structure.viewer_export_package`

For prompts asking to "render 3D", "show 3D viewer", or "interactive structure viewer":

- Do not route to `structure.viewer_3d`.
- Either return a future-scope planner explanation or route to `structure.viewer_scene_metadata` only if the rationale clearly says it prepares metadata, not a renderer.

## Artifact and Recipe Rules

- Artifact file names must be deterministic.
- JSON artifacts must include top-level `artifactType`.
- `summary.md` must be human-readable.
- `recipe.json` must include tool id, params, input resource hash or id, adapter version/git HEAD, resource caps, and artifact list.
- No artifact may contain secrets.
- No artifact may contain executable JavaScript.
- No artifact may reference external URLs.

## Tests

Add or update:

- Structure scene metadata unit tests.
- Export manifest unit tests.
- Registry/schema tests.
- Planner routing tests.
- API execution tests for plan validate, persisted plan, job completed, ToolCall status, and artifacts.
- Regression tests for Phase 8B, Phase 9D, Phase 10A, Phase 10B, and Phase 10C.
- Frontend tests only if new artifact types require display changes.

Run:

```bash
uv lock --check
python -m pytest tests/test_phase7_llm_planner.py -q
python -m pytest tests/test_phase8b_persisted_plan_queue.py -q
python -m pytest tests/test_phase8c_planner_read_api.py -q
python -m pytest tests/test_phase9b_demo_workspace_api.py -q
python -m pytest -q
npm test
npm run typecheck
npm run build
git diff --check
```

Do not run real LLM.

## Lightweight Evidence

Phase 10D-1 may include adapter-level evidence only:

```text
docs/phase10d/adapter_evidence/
```

Each evidence record must state:

```text
Evidence level: Tool Registry + Adapter execution only
Browser/API evidence: not included in Phase 10D-1
```

## Commit / CI

If implementation and tests pass:

```bash
git status --short
git diff --stat
git add .
git commit -m "Add viewer scene metadata adapters"
git push origin master
```

Wait for GitHub Actions current HEAD:

- unit success
- frontend success
- service-backed integration success
- no-skipped assertion passed
- default CI does not call real LLM

## Final Output Format

```markdown
# Phase 10D-1 Viewer Scene Metadata / Export Package Implementation Result

## 1. Conclusion
PASS / PARTIAL_PASS / FAIL

## 2. New adapters
- structure.viewer_scene_metadata:
- structure.viewer_export_package:
- structure.viewer_3d_contract:

## 3. Artifact outputs
- viewer_scene.json:
- viewer_assets_manifest.json:
- viewer_contract.json:
- summary.md:
- recipe.json:

## 4. Planner routing
- scene metadata prompt:
- export package prompt:
- 3D viewer prompt boundary:

## 5. Tests
List local test results.

## 6. Boundaries
- full 3D viewer:
- WebGL renderer:
- artifact JS:
- external URL loading:
- real LLM:
- runtime semantics:

## 7. Commit / CI
- commit:
- HEAD:
- CI run:
- git status:

## 8. Next phase
Phase 10D-2 Browser/API Evidence for Viewer Scene Metadata
```
