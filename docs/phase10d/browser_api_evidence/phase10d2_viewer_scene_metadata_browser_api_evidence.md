# Phase 10D-2 Browser/API Evidence for Viewer Scene Metadata

## 1. Scope
- covered tools: `structure.viewer_scene_metadata`, `structure.viewer_export_package`
- not covered: full interactive 3D viewer, WebGL renderer, Brillouin zone 3D, XRD, RDF, coordination histogram, phonon, notebook extraction, script execution

## 2. Baseline
- Phase 10D-1 HEAD: `b5fed28c25bc7ff0081baa04c1c5fefc6d6221f8`
- Phase 10D-1 commit: `b5fed28 Implement structure viewer scene metadata`
- current branch: `master`
- git status before: clean

## 3. Evidence Matrix
| Case | Tool | Input Type | Job Status | API Captures | Artifacts | Browser Screenshots | Result |
|---|---|---|---|---:|---:|---:|---|
| scene_metadata_cif | `structure.viewer_scene_metadata` | CIF | `completed` | 16 | 3 | 5 | PASS |
| scene_metadata_poscar | `structure.viewer_scene_metadata` | POSCAR | `completed` | 16 | 3 | 5 | PASS |
| scene_metadata_structure_json | `structure.viewer_scene_metadata` | Pymatgen Structure JSON | `completed` | 16 | 3 | 5 | PASS |
| export_package_cif | `structure.viewer_export_package` | CIF | `completed` | 17 | 4 | 5 | PASS |
| export_package_poscar | `structure.viewer_export_package` | POSCAR | `completed` | 17 | 4 | 5 | PASS |
| export_package_structure_json | `structure.viewer_export_package` | Pymatgen Structure JSON | `completed` | 17 | 4 | 5 | PASS |

## 4. API Evidence
Per-case redacted API captures are stored under each `api_redacted/` directory. Captures cover upload/resource, profile inspection, planner request/response, validation, job creation, job status, events, tool calls, artifact list, result, and artifact fetch payloads.

## 5. Browser Evidence
Per-case screenshots are stored under each `browser_screenshots/` directory. Screenshots show the static resource profile, plan preview, completed job process, results/artifact list, and redacted developer audit preview.

## 6. Artifact Evidence
Per-case actual platform artifacts are stored under each `artifacts/` directory. The evidence covers `viewer_scene.json`, `viewer_assets_manifest.json` for export package cases, `summary.md`, and `recipe.json`.

## 7. Security / Redaction
- no secrets: yes
- no artifact JavaScript: yes
- no external URLs: yes
- no renderer bundle: yes
- no real LLM: yes

## 8. Deferred Scope
- full interactive 3D viewer: deferred
- WebGL renderer: deferred
- structure.viewer_3d: deferred
- Brillouin zone 3D: deferred
- XRD: deferred
- RDF: deferred
- coordination histogram: deferred
- phonon: deferred

## 9. Known Limitations
- Browser evidence previews static artifacts and redacted provenance only.
- No actual 3D rendering is claimed.
- No WebGL screenshot stability claims are made.
- No official advanced examples are marked PASS by this phase.

## 10. Result
PASS
