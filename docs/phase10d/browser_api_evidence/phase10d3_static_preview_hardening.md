# Phase 10D-3 Viewer Static Preview Hardening Evidence

## 1. Scope
- implemented: schema-aware static previews for `viewer_scene.json` and `viewer_assets_manifest.json`, plus hardened `summary.md` and `recipe.json` preview coverage.
- not implemented: full interactive 3D viewer, WebGL renderer, Three.js, XRD, RDF, coordination histogram, phonon, notebook/script extraction, or external API workflows.

## 2. Baseline
- Phase 10D-2 HEAD: `186ff049467a1a7573846cb840aa460bb3b4e52e`
- Phase 10D-2 commit: `186ff04 Add viewer scene browser API evidence`
- current HEAD: Phase 10D-3 working tree before commit
- branch: `master`
- git status before: clean

## 3. Preview Features
- viewer_scene overview: schema version, tool id, formula, site count, species, scene type, representation, and camera metadata.
- lattice / atoms / bonds: static lattice parameter view, lattice matrix table, atom preview table, and bond preview table or empty state.
- limits / warnings: max sites, max bonds, truncation flags, and warnings are shown without treating missing values as success.
- security: `contains_javascript`, `external_urls_allowed`, and `artifact_supplied_js_allowed` are visible as badges.
- manifest: package overview, artifact list, renderer status, limits, warnings, and security flags are visible.
- summary: Markdown content is previewed as static text; no artifact script execution is allowed.
- recipe: deterministic flag, tool id, schema, steps count, and raw JSON fallback are visible.
- fallback: raw JSON remains available for both schema-aware previews and recipe preview.

## 4. Browser Evidence
| Screenshot | View | Artifact | Desktop/Mobile | Result |
|---|---|---|---|---|
| `phase10d3_static_preview_hardening/browser_screenshots/01_viewer_scene_overview_desktop.png` | scene overview and display/camera | `viewer_scene.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/02_viewer_scene_lattice_atoms_desktop.png` | lattice, atoms, bonds | `viewer_scene.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/03_viewer_scene_limits_security_desktop.png` | limits and security badges | `viewer_scene.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/04_viewer_scene_raw_json_desktop.png` | raw JSON fallback | `viewer_scene.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/05_viewer_manifest_overview_desktop.png` | manifest overview and artifacts | `viewer_assets_manifest.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/06_viewer_manifest_security_desktop.png` | renderer and security status | `viewer_assets_manifest.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/07_recipe_preview_desktop.png` | recipe preview | `recipe.json` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/08_summary_preview_desktop.png` | summary preview | `summary.md` | desktop | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/09_viewer_scene_mobile.png` | scene mobile preview | `viewer_scene.json` | mobile | PASS |
| `phase10d3_static_preview_hardening/browser_screenshots/10_viewer_manifest_mobile.png` | manifest mobile preview | `viewer_assets_manifest.json` | mobile | PASS |

## 5. Tests
- frontend tests: `npm --prefix apps/web test` passed.
- typecheck: `npm --prefix apps/web run typecheck` passed.
- build: `npm --prefix apps/web run build` passed.
- pytest: `python -m pytest -q` passed with 203 passed, 21 skipped, and existing dependency warnings.
- CI: pending after commit/push.

## 6. Security
- no JS execution: static preview renders JSON and Markdown as React text content only.
- no external URL loading: URL-like artifact fields are shown as text only.
- no WebGL: no WebGL or canvas renderer is introduced.
- no Three.js: no Three.js dependency or renderer code is introduced.
- no full 3D viewer: the UI states static artifact preview only.
- no real LLM: Phase 10D-3 uses no live LLM path.

## 7. Deferred Scope
- full interactive 3D viewer: deferred.
- WebGL renderer: deferred.
- `structure.viewer_3d`: not implemented.
- Brillouin zone 3D: deferred.
- XRD: deferred.
- RDF: deferred.
- coordination histogram: deferred.
- phonon: deferred.

## 8. Result
PASS
