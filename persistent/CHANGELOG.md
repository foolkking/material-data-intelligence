# CHANGELOG

## 2026-07-17 - Phase 10I-3 Band-BZ Linked View

- Added a strict immutable reciprocal link model that binds existing phonon band and BZ/k-path artifacts by scientific identities and exact ordered geometry, never by display labels.
- Added point occurrence, segment, sample, branch, hover/pinned selection, reverse BZ selection, exact animation handoff, mismatch fallback, mobile tabs, and semantic table/inspector support.
- Extended the existing BZ surface with a controlled application-owned reciprocal-sample/segment selection while preserving standalone behavior and demand-render cleanup.
- Added focused frontend/backend/runtime tests plus real three-browser, mobile, performance, accessibility, console, network, screenshot, and hash evidence. Full local regression passed; commits `f81aedb`, `5b5873e`, and `f3fa177` closed ignored-artifact and cross-platform hash packaging, and current-HEAD CI run `29572530288` passed unit, frontend/typecheck/build, service-backed integration, and no-skipped gates.

## 2026-07-15 - Phase 10I-2 Brillouin Renderer / Evidence

- Added a strict Phase 10I artifact mapper, bounded outward-normal face triangulation, uniform reciprocal-space visual scaling, and typed pre-WebGL validation/resource fallbacks.
- Added a lazy Three.js standalone Brillouin Zone Viewer with translucent faces, canonical edges/vertices, reciprocal axes, points/labels/path, discontinuity preservation, point/face/vertex/segment picking, inspector/tables, projection/camera/layers/opacity, local PNG, mobile/accessibility, and complete lifecycle cleanup.
- Updated `structure.brillouin_zone` interactive planner routing and product description while retaining one tool identity and unchanged adapter/runtime/artifact semantics.
- Added real Chromium/Firefox/WebKit/mobile PlannerWorkbench evidence with runtime artifacts, nonblank WebGL, performance/context-loss/export captures, zero external requests, and no dependency changes.

## 2026-07-14 - Phase 10I-1 Brillouin Zone Adapter

- Added formal `structure.brillouin_zone`, `BrillouinZoneAdapter`, strict registry schemas/caps, four dedicated scientific artifact types, and deterministic planner routing.
- Added local primitive/conventional standardization, canonical reciprocal/BZ geometry, generator-plane binding, Setyawan-Curtarolo k-path generation, Phase 10I validation, six inert artifacts, persisted runtime execution, and typed failures.
- Added SC/BCC/FCC/hexagonal/lower-symmetry references, conventional/primitive equivalence, replay, API/runtime evidence, security checks, and fixed JSON-only reciprocal/BZ/k-path/manifest preview tabs.
- Added no dependency, frontend renderer, WebGL/Canvas, external network/resource, notebook/script, real LLM, electronic/phonon calculation, or custom path capability.

## 2026-07-14 - Phase 10I Brillouin Zone Contract

- Added reciprocal-lattice, first-Brillouin-zone, high-symmetry k-path, manifest, and tolerance contract schemas with deterministic canonical JSON and hashes.
- Added physics-`2*pi` row-vector duality, primitive/conventional transforms, closed convex manifold topology, oriented generator planes, provider/time-reversal identity, explicit discontinuities, and Phase 10H compatibility.
- Added six bounded fixture families, independent NumPy/SciPy references, replay/security evidence, and focused contract tests.
- Added no adapter, registered tool, planner/runtime path, frontend renderer, dependency, network resource, notebook/script, or real LLM capability.

## 2026-07-14 - Phase 10H-5 Phonon Animation

- Added unique formal `phonon.animation`, strict planner/registry/PlanValidator/runtime integration, and four inert animation artifact types.
- Added exact structure/band/eigenvector/mode compatibility, fixed-envelope mass-unweighted displacement reconstruction, Gamma and bounded diagonal non-Gamma supercells, imaginary/degenerate warnings, and hard caps.
- Reused the shared Three.js engine for one-RAF instanced playback, vectors, bounded trails, periodic picking, inspector, controls, reduced motion, context loss, responsive mobile layout, and exact hash-bound band handoff.
- Added real Chromium/Firefox/WebKit/mobile WebGL evidence with zero external requests and no new dependency.

## 2026-07-14 - Phase 10H-4 Phonon Eigenvector Contract

- Added canonical mode reference, complex eigenvector, eigenvector-set, summary, and manifest contracts.
- Added stable mode IDs, band/q-point/branch/frequency/NAC binding, canonical atom order, atomic mass provenance, mass-weighted unit normalization, global phase canonicalization, and scientific phase equivalence.
- Added bounded real-space display reconstruction with physics-`2*pi` non-Gamma cell phase and display-only maximum displacement scaling.
- Added Python and independent TypeScript checks, deterministic fixtures/evidence, NumPy comparison, security and no-network markers.
- Added no parser, adapter, registry/planner/API product, UI, animation, solver, dependency, remote resource, notebook/script, or real LLM path.

## 2026-07-14 - Phase 10H-3 Combined Band + DOS

- Added the formal `phonon.band_dos` adapter and strict two-artifact role binding through validated planner/runtime execution.
- Added compatibility, combined-reference, summary, shared-axis plot, bounded table, and manifest artifacts with deterministic hashes and security flags.
- Added unit conversion with DOS Jacobian/integral audit, structure/atom/lineage/NAC/normalization gates, projection policy, and union frequency domain.
- Added independent frontend validation, lazy local Plotly combined view, keyboard/mobile/accessibility behavior, local PNG/JSON export, and real Chromium/Firefox/WebKit evidence.
- Added no dependency, solver, eigenvector, animation, thermal-property, notebook/script, external API, remote artifact, or real LLM capability.

## 2026-07-14 - Phase 10H Phonon Contract

- Added the inert Phase 10H phonon band, DOS, summary, manifest, q-point, frequency, and source contract family with deterministic serialization and hard resource caps.
- Added physics-`2*pi` reciprocal math, THz/cm^-1/meV conversion, negative-real imaginary classification, explicit path/discontinuity validation, source-stable full `3N` branches, source-declared degeneracy, DOS normalization/projections, and band/DOS compatibility.
- Added 53 focused Python checks, 5 independent TypeScript checks, deterministic fixtures/evidence, NumPy/SciPy reference comparison, and no-network/no-secret security captures.
- Did not add a dependency, parser, adapter, Tool Registry capability, planner route, plot, renderer, eigenvector, animation, external API, notebook/script execution, or real LLM path.

## 2026-07-13 - Phase 10G-3 Trajectory Performance / Browser Evidence

- Added formal `structure.trajectory_viewer` registration, strict English/Chinese planner routing, negative capability routing, validated launch params, and persisted adapter provenance.
- Added application-owned desktop/mobile performance tiers, supercell-aware refusal, trajectory-scoped bounded LRU caching, one pending seek request, expanded renderer metrics, context retry, and mobile/200%-layout hardening.
- Added deterministic real parser/planner/runtime API captures and Chromium 150, Firefox 128, WebKit 18, mobile, accessibility, lifecycle, context-loss, degraded/refused, security, and evidence-integrity automation.
- Kept `phase10g.trajectory.v1`, parser semantics, static `viewer_scene.v2`, static `structure.viewer_3d`, and dependency tree unchanged; static-reference bonds remain partial and advanced trajectory science remains deferred.

## 2026-07-13 - Phase 10G-2 Trajectory Viewer

- Added a real validated trajectory viewer using one shared Three.js engine with bounded dynamic frame updates rather than per-frame renderer reconstruction.
- Added playback/navigation, variable lattice, stable identity, committed-frame inspection/measurement, canonical velocity/force display, cache/stale/lifecycle controls, detected mobile/accessibility UI and three-browser evidence.
- Added per-page console/network audits, composited-canvas pixel evidence, valid over-budget refusal, and a local inert application icon; frontend 132 passed, backend 413 passed / 22 skipped, and the Phase 10 closure pack passed locally.
- Kept static viewer semantics unchanged, bonds off by default, dynamic inference prohibited, and formal trajectory registration deferred.

## 2026-07-13 - Phase 10G-1 Trajectory Parser / Adapter

- Added bounded streaming multi-frame EXTXYZ and canonical trajectory JSON ingestion with deterministic canonical normalization.
- Added stable source-ID reorder, approved unit conversion, strict lattice/PBC/property/time policies, typed failures, cancellation, and no-partial-artifact behavior.
- Added planner-hidden internal trajectory import adapter, four unique JSON artifact types, runtime/API evidence, tests, and security documentation.

## 2026-07-13 - Phase 10G Trajectory Contract

- Added closed inert trajectory, frame, summary, and manifest contracts with stable identity and canonical serialization.
- Added bounded Python validation, small deterministic valid/invalid fixtures, independent TypeScript reference tests, and evidence hashes.
- Documented row-vector lattice, wrapping, units, strict properties, storage/cap/security policy, while deferring parser, adapter, tool, and viewer implementation.

## 2026-07-13 - Phase 10F-25 Clipping, Cell, and Camera Controls

- Added real axis-aligned clipping with matching WebGL material and raycast visibility semantics.
- Added lattice axes, independent cell boundaries, deterministic camera presets, and inert scene-bound view-state serialization.
- Added Chromium/Firefox/WebKit/mobile evidence with zero external requests and no dependency changes.

## 2026-07-13 - Phase 10F-24 Supercell Productization

- Added bounded supercell productization with deterministic periodic identity, canonical-bond replication, estimate/apply/reset UI, state download/replay, and independent unit-cell/supercell boundaries.
- Changed expansion rebuilds to replace GPU buffers in one renderer context, preventing active WebGL context growth.

## 2026-07-12 - Phase 10F-19 Periodic Scene Integration Hardening

- Added exact additive capability metadata to `viewer_scene.v2` without changing periodic bond semantics or v1.
- Added validator-compatible `phase10f19.viewer_assets_manifest.v2` with explicit periodic topology and absent renderer/WebGL assets.
- Added periodic topology/security status to the JSON artifact preview and integration evidence for orthogonal, triclinic, and self-periodic cases.

## 2026-07-12 - Phase 10F-18 Canonical Periodic Bond Topology

- Added `viewer_scene.v2` with strict periodic endpoints, stable identity, source/authority semantics, distance consistency, caps, and v1 compatibility.
- Updated both viewer adapters to emit bounded deterministic periodic neighbor topology.
- Added frontend v2 validation/mapping, complete-edge supercell replication, and periodic neighbor inspection/highlight.
- Added live orthogonal/triclinic API and browser evidence with no external topology service.

## 2026-07-12 - Phase 10F-15 Production Minimal Structure Viewer

- Formalized `structure.viewer_3d` as the canonical minimal interactive viewer job identity.
- Replaced legacy HTML-producing viewer execution with canonical scene, manifest, summary, and recipe artifacts.
- Added planner routing separation, strict registry params/caps, PlanValidator/runtime tests, and legacy policy.
- Added species instancing, bounded draw calls, metrics, chunk retry fallback, responsive/mobile and accessibility hardening.
- Added live formal-tool browser/API evidence in Chromium, Firefox, and WebKit with zero external viewer requests.
- Recorded existing npm audit debt without claiming it clean or attributing it to Three.js.

## 2026-07-11

### Phase 10F-14 Validated Viewer Scene Renderer Foundation

- Added pinned Three.js renderer dependencies and lockfile entries.
- Added isolated viewer-scene validation, mapper, geometry/camera, engine, React surface, types and errors.
- Added canonical-only renderer tabs to PlannerWorkbench while retaining JSON/manifest default preview and old-schema compatibility.
- Added real atoms, lattice, optional bonds, OrbitControls rotate/zoom/pan, deterministic reset, toggles, capability detection, error fallback, context loss and disposal.
- Added 35 focused/integration frontend tests and live Chrome/WebGL renderer evidence tooling.
- Added live adapter artifacts, screenshots, DOM/graphics/interaction/lifecycle/console/network evidence and Phase 10F-14 audits.
- Confirmed zero renderer external network requests and no artifact-controlled JavaScript, HTML, CSS, URL, texture, module or shader execution.
- Did not register full `structure.viewer_3d` or implement trajectory, phonon or Brillouin zone.
- Changed active frontend `dev`/`start` defaults and API CORS from port 3000 to 3050; browser evidence keeps isolated test ports.

### Phase 10F-13 Viewer Scene Live Adapter Browser/API Evidence

- Added `apps/web/test/generate-viewer-scene-live-adapter-evidence.py` to capture live adapter-backed planner/job/runtime artifacts.
- Added `apps/web/test/viewer-scene-live-adapter-browser-evidence.mjs` for real Chrome screenshots, DOM audit, console audit, and network audit.
- Added `tests/test_phase10f13_viewer_scene_live_adapter_evidence.py` for API/runtime, invalid request, compatibility, routing, and security assertions.
- Added live evidence under `docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/`.
- Added Phase 10F-13 browser/API evidence, security audit, schema compatibility audit, and renderer handoff readiness docs.
- Updated docs index and persistent records.
- Confirmed live adapter-generated artifacts, not Phase 10F-9 fixtures, enter the existing JSON-only preview surface.
- Confirmed old Phase 10D schemas remain unchanged and are not relabeled as canonical `viewer_scene.v1`.
- No renderer dependency, WebGL, Three.js, MatterViz, renderer bundle, canvas viewer, iframe viewer, external API, notebook/script execution, real LLM, artifact JavaScript, phonon, Brillouin-zone 3D, or full `structure.viewer_3d` implementation was added.

### Phase 10F-12 Viewer Scene Minimal Adapter Implementation

- Added `StructureViewerSceneAdapter` for canonical `structure.viewer_scene` execution.
- Registered `structure.viewer_scene` in Tool Registry with strict `viewer_scene.v1` params and Phase 10F caps.
- Added canonical `viewer_scene.json` generation using `phase10f8.viewer_scene.v1`.
- Added canonical `viewer_scene_manifest.json` generation using `phase10f9.viewer_scene_manifest.v1`.
- Added summary and recipe generation for the minimal adapter.
- Added canonical validator gates before adapter export.
- Added Mock Planner positive routing for explicit inert viewer-scene JSON prompts and negative routing coverage for full viewer, WebGL, Three.js, XRD, RDF, coordination, Brillouin, phonon, and trajectory prompts.
- Added `tests/test_phase10f12_viewer_scene_adapter.py` for adapter, registry, PlanValidator, routing, execution, deterministic replay, contract, manifest, and security coverage.
- Added frontend preview regression using adapter-generated evidence JSON.
- Added generated adapter execution/security evidence and Phase 10F-12 docs.
- Updated shared schema, docs index, and persistent records.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, MatterViz renderer, renderer bundle, 3D component, external API, notebook/script execution, real LLM, new dependency, phonon, Brillouin-zone 3D, or unsupported official PASS claim was added.

## 2026-07-09

### Phase 10F-10 Viewer Scene JSON-only Preview Surface Implementation / Evidence

- Added `viewer_scene.v1` JSON-only preview support to the existing PlannerWorkbench artifact preview surface.
- Added `phase10f9.viewer_scene_manifest.v1` manifest preview support.
- Added fixture-backed frontend tests for valid, warning/caps, invalid external-resource placeholder, invalid executable placeholder, invalid schema, and renderer-free sample coverage.
- Added stable selectors for evidence capture of kind, version, schema version, validation state, error codes, warning codes, caps, scene summary, and manifest metadata.
- Added Phase 10F-10 implementation, preview evidence, security evidence, browser/API boundary, readiness matrix, text evidence, and Phase 10F-11 next-scope docs.
- Updated `docs/index.md` and `docs/13_SHARED_SCHEMA_SPEC.md` with the implemented JSON-only preview surface.
- No full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, production runtime route, notebook/script execution, external API workflow, artifact JS, HTML renderer, real external URL dependency, phonon, or unsupported official PASS claim was added.

### Phase 10F-9 Viewer Scene Contract Fixture / Validator Implementation

- Added `docs/phase10f/fixtures/viewer_scene_v1/` with inert `viewer_scene.v1` fixture files, manifest fixtures, and `expected_results.json`.
- Added `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py` and exported the viewer scene validator utilities.
- Added `tests/test_viewer_scene_contract_fixtures.py` for fixture replay, manifest validation, expected error/warning matching, and no real external URL / no script marker assertions.
- Added Phase 10F-9 implementation, fixture matrix, validator result, manifest fixture, security evidence, evidence closure, and Phase 10F-10 next-scope docs.
- Updated `docs/index.md` and `docs/13_SHARED_SCHEMA_SPEC.md` with the implemented contract fixture and validator slice.
- No full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, runtime route, notebook/script execution, external API workflow, artifact JS, HTML renderer, real external URL dependency, phonon, or unsupported official PASS claim was added.

### Phase 10F-8 Viewer Scene Artifact Contract Planning

- Added `docs/phase10f/phase10f8_viewer_scene_artifact_contract_planning.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_json_contract.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_manifest_contract.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_validation_contract.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_security_contract.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_browser_evidence_contract.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_versioning_strategy.md`.
- Added `docs/phase10f/phase10f8_viewer_scene_contract_readiness_matrix.md`.
- Added `docs/phase10f/phase10f9_next_scope_prompt.md`.
- Updated `docs/index.md` and `docs/13_SHARED_SCHEMA_SPEC.md` with the Phase 10F-8 contract-planning docs and schema draft.
- Planned inert `viewer_scene` JSON, manifest, validation, security, browser evidence, and versioning contracts.
- Recorded readiness decisions: contract planning `READY`, JSON-only preview planning `READY`, renderer handoff `PARTIAL_READY`, renderer implementation `NOT_READY`, and full `structure.viewer_3d` implementation `NOT_READY`.
- Recommended Phase 10F-9: Viewer Scene JSON Preview Evidence / Contract Fixture Planning.
- No full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, notebook/script execution, external API workflow, artifact JS, external URL, phonon, or unsupported official PASS claim was added.

### Phase 10F-7 Advanced Structure Viewer Readiness Planning

- Added `docs/phase10f/phase10f7_advanced_viewer_readiness.md`.
- Added `docs/phase10f/phase10f7_viewer_artifact_contract_proposal.md`.
- Added `docs/phase10f/phase10f7_renderer_architecture_assessment.md`.
- Added `docs/phase10f/phase10f7_viewer_security_boundary.md`.
- Added `docs/phase10f/phase10f7_viewer_input_caps.md`.
- Added `docs/phase10f/phase10f7_viewer_routing_policy.md`.
- Added `docs/phase10f/phase10f7_viewer_browser_evidence_model.md`.
- Added `docs/phase10f/phase10f7_viewer_readiness_matrix.md`.
- Added `docs/phase10f/phase10f8_next_scope_prompt.md`.
- Updated `docs/index.md` with the Phase 10F-7 readiness docs and Phase 10F-8 prompt.
- Recorded that inert `viewer_scene` artifact-contract work is ready for the next phase, while renderer implementation and full `structure.viewer_3d` implementation are not ready and not approved.
- Recommended Phase 10F-8: Viewer Scene Artifact Contract Planning.
- No official PASS verification, notebook/script execution, benchmark extraction script, external API workflow, new adapter, runtime semantic change, full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, phonon, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-6 Static Physics Fixture Pack Evidence Closure

- Added `docs/phase10f/phase10f6_static_physics_fixture_pack_evidence_closure.md`.
- Added `docs/phase10f/phase10f6_evidence_boundary_matrix.md`.
- Added `docs/phase10f/phase10f6_next_scope_decision_matrix.md`.
- Added `docs/phase10f/phase10f7_next_scope_prompt.md`.
- Updated `docs/index.md` with the Phase 10F-6 closure docs and Phase 10F-7 prompt.
- Closed the fixture-pack replay evidence boundary: fixture-pack PASS is stable, official PASS remains none.
- Recommended Phase 10F-7: Advanced Structure Viewer Readiness Planning.
- No official PASS verification, notebook/script execution, benchmark extraction script, external API workflow, new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-5 Static Physics Fixture Pack Replay Verification

- Replayed the Phase 10F-4 fixture pack for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Confirmed all three cases selected the expected tools and generated expected artifacts.
- Added replay-generated candidate numeric values to each case's expected contract.
- Kept all official PASS claims false because the replayed cases use `internal_regression` provenance.
- Recorded fixture-pack replay result as `PASS`.
- No official PASS verification, notebook/script execution, benchmark extraction script, external API workflow, new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-4 Static Physics Direct-Uploadable Fixture Pack Construction

- Added `docs/phase10f/static_physics_fixture_pack/`.
- Added a candidate fixture pack manifest, local manifest schema, expected-contract schema, provenance policy, and tolerance policy.
- Added three small direct-uploadable candidate cases for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Added each case's input file, `input_manifest.json`, `expected_contract.json`, `provenance.json`, and `README.md`.
- Added `docs/phase10f/phase10f4_static_physics_fixture_pack_construction.md`.
- Added `docs/phase10f/phase10f5_next_scope_prompt.md`.
- Kept all official PASS claims false; numeric expected values are pending Phase 10F-5 replay generation.
- Recommended Phase 10F-5: Static Physics Fixture Pack Replay Verification.
- No official PASS verification, notebook/script execution, benchmark extraction script, external API workflow, new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-3 Static Physics Direct-Uploadable Fixture Pack Planning

- Added `docs/phase10f/phase10f3_static_physics_fixture_pack_planning.md`.
- Added `docs/phase10f/phase10f3_fixture_candidate_matrix.md`.
- Added `docs/phase10f/phase10f3_fixture_provenance_policy.md`.
- Added `docs/phase10f/phase10f3_expected_contract_templates.md`.
- Added `docs/phase10f/phase10f3_numeric_tolerance_policy.md`.
- Added `docs/phase10f/phase10f3_fixture_replay_protocol.md`.
- Added `docs/phase10f/phase10f4_next_scope_prompt.md`.
- Planned the direct-uploadable fixture pack structure, provenance labels, expected-contract templates, numeric tolerance rules, and future replay protocol for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Kept Phase 10F-1 as `PARTIAL_PASS`, Phase 10F-2 as `PASS`, and made no new official static physics PASS claim.
- Recommended Phase 10F-4: Static Physics Direct-Uploadable Fixture Pack Construction.
- No fixture replay, notebook/script execution, benchmark extraction script, external API workflow, new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-2 Official Examples Coverage Gap Closure

- Added `docs/phase10f/phase10f2_official_coverage_gap_analysis.md`.
- Added `docs/phase10f/phase10f2_coverage_gap_matrix.md`.
- Added `docs/phase10f/phase10f2_direct_uploadable_fixture_proposal.md`.
- Added `docs/phase10f/phase10f2_expected_contract_authoring_plan.md`.
- Added `docs/phase10f/phase10f3_next_scope_prompt.md`.
- Planned how to close the lack of direct-uploadable official static physics cases for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Kept Phase 10F-1 as `PARTIAL_PASS` and made no new official static physics PASS claim.
- Recommended Phase 10F-3: Static Physics Direct-Uploadable Fixture Pack Planning.
- No new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, notebook/script execution, external API workflow, real LLM path, dependency, or unsupported official PASS claim was added.

### Phase 10F-1 Official Examples Direct Verification

- Added `docs/phase10f/phase10f1_official_examples_direct_verification.md`.
- Added `docs/phase10f/official_examples_direct_verification/` with case selection, verification matrix, API/no-execution transcript, artifact comparison report, and security audit.
- Added `docs/phase10f/phase10f2_next_scope_prompt.md`.
- Audited the local official examples benchmark pack: 61 cases, 2 `DIRECT_VERIFIED`, 20 `MAPPING_ONLY`, 27 `EXTRACTION_REQUIRED`, 12 `FUTURE_SCOPE`, audit ok.
- Applied the direct-uploadable gate and found no direct-uploadable official static physics case for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- Made no official static physics PASS claim; MatPES and Ward remain direct verified for table/ML/composition scopes only.
- Recommended Phase 10F-2: Official Examples Coverage Gap Closure.
- No new adapter, runtime semantic change, full viewer, WebGL renderer, Three.js, phonon, notebook/script execution, external API workflow, real LLM path, or unsupported official PASS claim was added.

### Phase 10F Static Structure Physics Closure

- Added `docs/phase10f/phase10f_static_structure_physics_closure.md`.
- Added `docs/phase10f/phase10f_next_scope_decision_matrix.md`.
- Added `docs/phase10f/phase10f1_next_scope_prompt.md`.
- Closed the Phase 10E static structure physics family: `structure.coordination_hist`, `structure.xrd`, and `structure.rdf` now all have implementation, browser/API evidence, static artifacts, registry coverage, planner routing, negative routing, security evidence, and passing CI.
- Recommended Phase 10F-1: Official Examples Direct Verification for Static Structure Physics.
- No new adapter, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, experimental fitting, runtime semantic change, or official example PASS claim was added.

### Phase 10E-8 RDF Browser/API Evidence

- Added `docs/phase10e/phase10e8_rdf_browser_api_evidence.md`.
- Added `docs/phase10e/browser_api_evidence/phase10e8_rdf/` with redacted API captures, copied RDF artifacts, browser-rendered screenshots, audits, and evidence manifest.
- Verified `structure.rdf` through local FastAPI `/planner/jobs`, deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Captured six real frontend screenshots with system Chrome / Playwright.
- Verified no artifact JavaScript, no external artifact URLs, no WebGL, no Three.js, no real LLM, and `NO_SECRET_PATTERN_HITS`.
- No new adapter, full 3D viewer, WebGL renderer, phonon, experimental fitting, runtime semantic change, or official example PASS claim was added.

### Phase 10E-7 RDF Implementation

- Implemented `structure.rdf` as a deterministic static physics adapter for periodic crystalline structures.
- Added `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Updated the Tool Registry manifest and params schema for fixed `r_max_angstrom`, `bin_width_angstrom`, `number_density` normalization, ordered partial RDF pairs, and explicit resource caps.
- Updated Mock Planner routing for RDF / radial-distribution / pair-distribution prompts.
- Added tests for numeric artifact contracts, fixture support, deterministic bins, global and partial RDF behavior, resource caps, registry schema, planner routing, persisted execution, and no-JS/no-external-URL safety.
- Added `docs/phase10e/phase10e7_rdf_implementation.md`.
- Browser/API evidence is deferred to Phase 10E-8.
- No full 3D viewer, WebGL renderer, Three.js, Brillouin-zone, phonon, advanced local environment classification, experimental fitting, notebook/script execution, external API workflow, new dependency, real LLM path, or runtime main semantic change was added.

## 2026-07-08

### Phase 10E-1 Coordination Histogram Implementation

- Implemented `structure.coordination_hist` as a deterministic static physics adapter.
- Added `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Updated the Tool Registry manifest and params schema for a conservative `distance_cutoff` neighbor policy.
- Updated Mock Planner routing for coordination histogram / coordination number / neighbor count prompts.
- Added tests for numeric artifact contracts, fixture support, deterministic output, cutoff sensitivity, limits/warnings, registry schema, planner routing, persisted execution, and no-JS/no-external-URL safety.
- Added `docs/phase10e/phase10e1_coordination_hist_implementation.md`.
- Browser/API evidence is deferred to Phase 10E-2.
- No XRD, RDF, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone, phonon, notebook/script execution, external API workflow, new dependency, real LLM path, or runtime main semantic change was added.

## 2026-07-07

### Phase 10C-1 Lightweight Structure Adapter Implementation

- Added five registry-gated lightweight structure adapters:
  `structure.summary`, `structure.lattice_summary`,
  `structure.spacegroup_summary`, `structure.composition_from_structure`, and
  `structure.preview_metadata`.
- Added bounded structure resource loading for pymatgen Structure objects,
  pymatgen Structure dict/JSON, normalized structure dicts, CIF text,
  POSCAR/CONTCAR text, and small structure collections.
- Added deterministic JSON artifacts plus `summary.md` and `recipe.json` for
  the new structure tools.
- Added strict Tool Registry params schemas and registered all five tools in the
  platform builtin manifest and adapter registry.
- Updated Mock Planner routing so explicit structure prompts select structure
  tools before generic composition/table/viz routing, while 3D viewer prompts
  remain future-scope and do not claim `structure.viewer_3d` support.
- Added small structure fixtures and tests for parser/resource support, adapter
  output contracts, registry schema validation, planner routing, persisted job
  execution, and invalid-plan rejection.
- Generated adapter-level evidence under `docs/phase10c/adapter_evidence/`.
  Browser/API evidence is not included in Phase 10C-1.
- No real LLM was used. No QueueWorkerRuntime, AnalysisPlanRepository,
  `/planner/jobs` main semantics, or live LLM gate behavior changed.

## 2026-07-06

### Phase 10C Lightweight Structure Adapter Planning

- Added `docs/phase10c/phase10c_lightweight_structure_adapter_planning.md` to define the lightweight structure adapter strategy after Phase 10B-2.
- Added `docs/phase10c/phase10c_candidate_adapter_matrix.md` with prioritized candidates across lightweight structure summaries, advanced structure visualization, XRD/RDF, coordination, phonon, and Brillouin zone work.
- Added `docs/phase10c/phase10c1_lightweight_structure_adapter_implementation_prompt.md` for the future Phase 10C-1 implementation pass.
- Recommended Phase 10C-1 focus: `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- Documented that Phase 10C planning does not implement adapters, does not modify runtime semantics, and does not claim mapping-only or future-scope official structure examples as PASS.
- Confirmed the benchmark-pack basis: 61 official cases, 2 direct verified, 27 extraction required, 20 mapping only, 12 future scope, audit ok.

### Phase 10B Second Batch pymatviz Adapter Planning

- Added `docs/phase10b/phase10b_second_batch_adapter_planning.md` to define the second-batch adapter strategy after Phase 10A-2.
- Added `docs/phase10b/phase10b_candidate_adapter_matrix.md` with prioritized candidates across composition, structure, phonon, Brillouin zone, and later ML/materials plot work.
- Added `docs/phase10b/phase10b1_composition_adapter_implementation_prompt.md` for the future Phase 10B-1 implementation pass.
- Recommended Phase 10B-1 focus: `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- Documented that Phase 10B planning does not implement adapters, does not modify runtime semantics, and does not claim unsupported official examples as PASS.
- Confirmed the benchmark-pack basis: 61 official cases, 2 direct verified, 27 extraction required, 20 mapping only, 12 future scope, audit ok.

### Phase 10A-2 Browser/API Evidence for First Batch Adapters

- Added project evidence under `docs/phase10a/browser_api_evidence/` for six scoped first-batch adapter scenarios: MatPES scatter, MatPES histogram, Ward distribution summary, Ward histogram, Ward correlation, and Ward composition summary.
- Each scenario includes redacted API captures, actual downloaded artifacts, Phase 9C UI screenshots, execution logs, platform result summaries, artifact manifests, and evidence manifests.
- Evidence totals: 6 PASS scenarios, 60 API capture JSON files, 30 PNG screenshots, and 23 artifact files.
- Security scan over the evidence directory found no `sk-`, `Bearer`, `Authorization`, `MDI_LLM_API_KEY`, `api_key`, `access_token`, or `refresh_token` hits.
- Updated `viz.scatter` and `viz.histogram` artifact JSON output so benchmark metadata such as `chartType`, `xColumn`, `yColumn`, `pointCount`, `column`, and `binCounts` is present at the top level, with the Plotly figure retained under `figure`.
- Updated Mock Planner routing so composition distribution prompts route to `composition.summary` before the broader histogram/distribution route.
- No real LLM was used; Mock Planner remained the evidence path and default CI remains real-LLM-free.
- No QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` persistence/enqueue semantics, PlanValidator bypass, or Tool Registry execution boundary changed.

### Phase 10A-1 First Batch Adapter Implementation

- Added the first official-examples adapter batch for the two `DIRECT_VERIFIED` direct cases only: MatPES and Ward metallic glasses.
- Added platform builtin adapters and registry entries for `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- Added `viz` to the shared ToolDomain definitions and registered strict params schemas for the new tools.
- Updated Mock Planner routing so MatPES scatter/distribution prompts and Ward distribution/correlation/composition prompts select semantically appropriate tools instead of forcing unrelated regression metrics.
- Updated runtime inputRef validation so `table.*` and `viz.*` tools require the normalized `ml_table` object.
- Updated Phase 9C result rendering and frontend tests so scatter, histogram, correlation, distribution summary, summary, and recipe artifacts are visible in the `结果与导出` tab while developer-only details remain hidden by default.
- Added adapter, manifest, planner-routing, persisted-plan execution, and frontend tests for the new tools.
- No QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` persistence/enqueue semantics, live LLM gating, or default CI LLM behavior changed.

## 2026-07-05

### Phase 9D True LLM Live Verification

- Captured redacted evidence for the gated OpenAI-compatible Gemini provider path without recording the API key.
- Captured redacted API evidence and Phase 9C browser screenshots under `docs/llm-live-verification/phase9d/`.
- Verified live provider output can become a validated persisted AnalysisPlan, bind through `jobs.plan_id`, load in QueueWorkerRuntime, and execute through Tool Registry + Adapter to produce ToolCalls, Artifacts, and Result provenance.
- Hardened PlanValidator to validate `AnalysisStep.params` against the selected registered tool `paramsSchema` before persistence.
- Updated planner prompt tool summaries with allowed parameter names so live providers are less likely to emit invalid aliases such as snake_case params for camelCase tool schemas.
- Omitted `response_format` for Gemini AI Studio's OpenAI-compatible endpoint, which returned HTTP 400 for that field.
- Checked the Antigravity model requested by the user; Gemini reports it only supports Interactions API, so it cannot satisfy the current OpenAI-compatible chat/completions provider contract without a future provider implementation.
- Fixed frontend API list handling for response envelopes that return `{ "value": [...] }` for datasets/secrets.
- Final gated live rerun passed with Gemini 3 Flash Preview: `python -m pytest -q -m llm_integration` -> 1 passed / 165 deselected.
- Gemini 2.5 Flash Lite was reachable but hit a provider-side HTTP 503 during one full-chain attempt; Gemini 3 Flash Preview is the verified model for Phase 9D evidence.
- Default CI remains real-LLM-free; live tests are still gated by `MDI_RUN_LLM_INTEGRATION=1`.

### Phase 9D LLM Configuration Path Repair

- Fixed OpenAI-compatible provider config resolution so explicit request/UI config is not overwritten by env model/timeout/token/temperature settings.
- Added `/planner/providers/resolve`, a no-network redacted status path for the current UI provider configuration.
- Updated the Planner workspace model status to show the current task provider resolution while keeping the default env provider status visible in the model dialog.
- Replaced corrupted provider-test messages in `planner_providers.py` with safe readable messages and kept response bodies redacted.
- Added a gated full-chain live LLM test that can verify live provider -> PlanValidator -> persisted AnalysisPlan -> queued worker execution -> ToolCall/Artifact/Result when `MDI_RUN_LLM_INTEGRATION=1` and required provider env are configured.
- No real LLM was called locally; the live integration file currently skips without env.

### Phase 9C Browser Visual QA and Official Direct Re-verification

- Ran browser-controlled visual QA for the Phase 9C workspace and saved six QA screenshots under `docs/ui-redesign/phase9c_browser_qa/`.
- Re-ran the two official direct-uploadable pymatviz examples through the Phase 9C UI after deleting old Desktop `results/` directories.
- MatPES fresh run: `dataset_0004`, `job_c6e8034a138f469da0d72f2e`, `plan_202acca0e0c74d5fa7a0f794`, `ml.basic_metrics`, `metrics.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
- Ward fresh run: `dataset_0005`, `job_3c6b5797a14e4732bf19c64d`, `plan_017cf930f0224728bb3850b5`, `table.numeric_summary`, `numeric_summary.json` / `summary.md` / `recipe.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
- Updated the Desktop official examples evidence pack only; no Desktop evidence files are intended for the project Git commit.
- No real LLM was used and no API key was entered or captured.

### Phase 9C UI/UX Redesign Implementation

- Reworked `PlannerWorkbench` to the Phase 9C layout: top global context bar, collapsible/resizable left data-context viewer, and main workspace tabs.
- Added top-bar dataset/profile and model/provider dialogs instead of keeping those controls in a permanent left control column.
- Replaced the old independent right status column and bottom result tabs with three mutually exclusive main tabs: `Agent 过程`, `对话与 Plan`, and `结果与导出`.
- Added conversation chunk selection and result-context routing into `结果与导出`.
- Moved report/recipe summary, 3D material result placeholder, metrics, table/numeric summary, Artifact Gallery, ToolCalls, and export controls into the main results tab.
- Updated i18n dictionaries and CSS for the new layout.
- Updated frontend tests to cover the Phase 9C layout, top dialogs, left data viewer, Secret no-leak behavior, mutually exclusive tabs, Agent event evidence, results/export content, and validation failure no plan/job/enqueue.
- No backend API, worker runtime, PlanValidator, AnalysisPlanRepository, Tool Registry, Adapter, migration, or real-LLM CI path changed.
- Verification: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C targeted 2 passed; Phase 9B API targeted 15 passed; backend full 138 passed / 21 skipped; frontend `npm test` 6 passed; typecheck passed; build passed; `git diff --check` passed with line-ending warnings only.

### Phase 9C UI/UX Redesign Docs Baseline

- Updated frontend design docs to make the AI assistant workspace the canonical UI direction.
- Replaced the old recommended three-column/right-panel/bottom-panel layout with a top global context bar, a collapsible/resizable left data-context viewer, and a main workspace with three mutually exclusive tabs.
- Documented the three main tabs: `Agent 过程`, `对话与 Plan`, and `结果与导出`.
- Documented that all results, including reports, 3D material views, metrics, table summaries, Artifacts, Recipe/provenance, exports, and downloads, belong to `结果与导出` rather than a separate right panel.
- Added UI-only view model notes to the shared schema spec for main tab, conversation chunk, data-context viewer, and selected result context.
- Updated README, MASTER_PROMPT, AGENTS, docs index, product requirements, and persistent files to keep future sessions aligned.
- No application code, backend API, worker runtime, Tool Registry, Adapter, migration, test, or CI behavior changed in this docs-only update.

## 2026-07-04

### Phase 9B Official Direct Examples Semantic Refinement

- Added `table.numeric_summary`, a minimal MVP platform builtin adapter that summarizes DataFrame row counts, column metadata, numeric column statistics, categorical value counts, and exports `numeric_summary.json`, `summary.md`, and `recipe.json`.
- Registered `table.numeric_summary` in Tool Registry and added `table` to shared `ToolDomain`.
- Updated Mock Planner routing so Ward metallic glass table-summary prompts generate a `table.numeric_summary` AnalysisPlan instead of incorrectly treating `D_max` and `dTx` as target/prediction columns for `ml.basic_metrics`.
- Preserved MatPES behavior: the official MatPES CSV still creates an `ml.basic_metrics` plan with `targetColumn=PBE` and `predictionColumn=r2SCAN`.
- Regenerated fresh browser evidence for `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz` after deleting old results. MatPES produced `metrics.json`; Ward produced `numeric_summary.json`, `summary.md`, and `recipe.json`.
- Updated each case's `expected_artifacts_schema.json`, platform summary, screenshots index, execution log, and the global official browser verification summary.
- Added regression coverage for `NumericSummaryAdapter` and Ward Mock Planner semantic routing.

### Phase 9B Official MatPES Example Blocker Repair

- Fixed the official MatPES evidence-pack blocker where Mock Planner produced `ml.basic_metrics` params for `y_true` / `y_pred` even when the real DataProfile columns were `element`, `PBE`, and `r2SCAN`.
- Mock Planner now selects `ml.basic_metrics` target/prediction params from DataProfile columns: explicit target/prediction roles first, then the first two numeric columns for role-less numeric tables.
- Added a Phase 9B regression for a MatPES-style uploaded CSV proving `/planner/jobs` persists a plan with `targetColumn=PBE` and `predictionColumn=r2SCAN`, executes through QueueWorkerRuntime and the real `ml.basic_metrics` adapter, creates one metrics artifact, and completes the job.
- Re-ran the failed browser evidence case with the full official MatPES CSV. The run completed with `job_b81c14bde6c3479599e19312`, `plan_4117360927074c8fad3ec8f3`, one completed ToolCall, one `metrics_json` artifact, and four screenshots under the Desktop evidence pack.
- Preserved Phase 8B/9A boundaries: no QueueWorkerRuntime redesign, no AnalysisPlanRepository change, no `/planner/jobs` persistence/enqueue bypass, no real LLM call, and no direct tool execution outside Tool Registry + Adapter.
- Verification: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C targeted 2 passed; Phase 9B targeted 14 passed; backend full 136 passed / 21 skipped; frontend `npm test` 6 passed; typecheck passed; build passed after stopping the old dev server that held `.next/trace`.

### Phase 9B Closure: Browser Verification and Durable Worker Object Loading

- Completed the previously missing browser click-through on the local Planner workspace. The browser loaded demo data, created and ran a Mock Planner job, reached completed status, displayed persisted-plan provenance, and showed one metrics artifact plus one completed `ml.basic_metrics` ToolCall.
- Added `MDI_ARTIFACT_ROOT` configuration and a shared `create_artifact_storage_from_settings()` helper.
- Added `DurableObjectStoreResolver`, which reconstructs worker `object_store` values from dataset `metadata.normalizedExports` and ArtifactStorage. It restores conventional refs such as `ml_table`, `structures`, and `formulas` without relying on API-process memory.
- Updated `run_queued_job(job_id)` so RQ workers construct repositories from settings, use configured artifact storage, and install the durable object-store resolver before calling `QueueWorkerRuntime.handle_job(job_id)`.
- Updated the PostgreSQL planner runtime path to use configured artifact storage and the same durable resolver.
- Added a regression that seeds a persisted dataset, normalized exports, persisted AnalysisPlan, and queued job, then calls `run_queued_job(job_id)` as a settings-driven worker. The test proves `ml.basic_metrics` executes exactly once through the real adapter and writes `data.loaded`, `plan.loaded`, ToolCall, Artifact, and completed job state.
- Verification: Phase 9B targeted 13 passed; Phase 9B + Phase 8B targeted 22 passed / 1 skipped locally; Phase 7 + Phase 8C targeted 34 passed; backend full 135 passed / 21 skipped; frontend tests/typecheck/build passed.

### Phase 9B Follow-up: Planner Runtime Data Binding and Local Demo Execution

- Added Phase2 runtime accessors for real uploaded dataset profiles and normalized object stores.
- Updated Planner preview/jobs to prefer the real Phase2 `DataProfile` for an existing dataset instead of relying on a minimal synthetic profile.
- Added executable inputRef validation for uploaded datasets so ML, structure, and composition plans must bind the available normalized objects (`ml_table`, `structures`, `formulas`) before an AnalysisPlan can be persisted or a Job can be created/enqueued.
- Added a `QueueWorkerRuntime` object-store resolver hook and a `data.loaded` JobEvent. The default local planner worker can now load uploaded/demo dataset objects by `dataset_id` before executing the persisted plan.
- Added a local-only in-memory auto-run path for `/planner/jobs` when no Redis queue is configured and no custom repository/runtime injection is active. This closes the demo case where `enqueue=true` stayed queued without a separate worker process, while preserving the Redis/worker production path.
- Updated the planner prompt with normalized inputRef conventions for `ml_table`, `structures`, and `formulas`.
- Added regression tests proving uploaded CSV planner jobs execute through the persisted-plan worker path with exactly one `ml.basic_metrics` ToolCall and proving missing inputRefs reject before plan/job/enqueue.
- Reorganized four supported pymatviz sample cases under `C:\Users\86182\Desktop\pymatviz-web-test-cases`, each with `raw_data/` and `results/`, and generated platform results for MatPES CSV metrics plus three structure JSON/CIF cases.
- Verification: Phase 9B API targeted 12 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 7 + Phase 8C + Phase 9B targeted 46 passed; backend full 134 passed / 21 skipped; frontend `npm test` 6 passed; frontend typecheck and build passed.

### Phase 9B Follow-up: Frontend/API CORS and Validation-Failure Redaction

- Added FastAPI CORS middleware so the browser workspace can complete `OPTIONS` preflight for runtime health, dataset, planner provider, demo dataset, provider test, and Secret UX APIs.
- Added configurable CORS origins through `MDI_CORS_ORIGINS` / `CORS_ORIGINS`, with local Next/Vite defaults for `localhost` and `127.0.0.1`.
- Upgraded `/health/runtime` from config-only reporting to light, read-only probes: SQLite/PostgreSQL `SELECT 1`, Redis `PING` when configured, and MinIO/S3 bucket reachability when configured. Probe failures return safe `unknown` component status instead of leaking URLs, passwords, or object-storage credentials.
- Closed the validation-failure response leak: `/planner/jobs` no longer returns the invalid raw plan when PlanValidator rejects it, preventing credential-like params from being echoed back to the frontend/API caller.
- Completed the Planner workbench i18n extraction follow-up: remaining user-facing Chinese labels in `PlannerWorkbench.tsx` were moved into `zh-CN` / `en-US` message files, and English mode now has regression assertions for key labels.
- Added Phase 9B tests proving browser preflight succeeds, health probe failures are redacted, missing SQLite databases are not created by health checks, and rejected credential-bearing plans still persist no plan, create no job, enqueue nothing, and do not echo the rejected secret value.
- Follow-up verification: Phase 9B API targeted 10 passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C targeted 2 passed; backend full 132 passed / 21 skipped; frontend `npm test` 6 passed, `npm run typecheck` passed, and `npm run build` passed.

### Phase 9B Demo-ready AI Planner Workspace

#### Added

- Added runtime health support at `/health/runtime` for API/database/Redis/artifact storage/worker/LLM provider status display.
- Added demo-ready dataset/profile support: dataset detail, demo dataset creation, and idempotent profile generation backed by the Phase2 runtime.
- Added planner provider catalog/status/test APIs for mock and OpenAI-compatible provider modes.
- Added a safer Secret UX response shape with alias/provider/status/masked preview/timestamps and no plaintext return.
- Added frontend i18n with default Chinese (`zh-CN`) and English toggle.
- Added LLM Provider Settings UI with mock/real mode, OpenAI/DeepSeek/custom presets, Secret save/delete/select, and provider connection test feedback.
- Added Data Context, Demo Workflow, Prompt Composer, System Health, Error Explainer, grouped Artifact Gallery, Report/Recipe Summary, and Developer Audit workspace surfaces.
- Added backend Phase 9B API tests in `tests/test_phase9b_demo_workspace_api.py`.
- Expanded frontend Vitest coverage for Chinese/default rendering, language switch, empty states, dataset/demo/profile flow, provider settings, Secret no-leak behavior, provider test success/failure, SSE timeline, grouped artifacts, report/recipe summary, developer audit, and validation failure no plan/job/enqueue.

#### Changed

- Reworked `PlannerWorkbench` from an engineering debug surface into a product-oriented four-zone workspace with bottom result tabs.
- Replaced broad `Not available yet` placeholders with region-specific localized empty states.
- Layered normal user mode and developer mode so raw IDs, plan hashes, raw JSON, and API responses are mostly hidden until developer mode is enabled.
- `/planner/preview` and `/planner/jobs` can accept provider configuration fields resolved through server-side Secret lookup by `secretId`; validation and persistence semantics remain unchanged.

#### Preserved

- QueueWorkerRuntime, AnalysisPlanRepository, and Phase 8B persisted-plan exact execution were not redesigned.
- `/planner/jobs` still validates first; invalid plans create no AnalysisPlan, no Job, and no enqueue.
- The frontend still creates work only through `/planner/jobs`; it never writes `analysis_plans`, directly enqueues work, or treats deterministic fallback as a product path.
- API keys are not stored in localStorage/sessionStorage, not returned by Secret lists, and not included in provider test responses.
- Raw prompt/completion is not persisted by default.
- Default CI remains real-LLM-free.

#### Verification

- `uv lock --check`: passed.
- Phase 7 targeted: 32 passed.
- Phase 8B persisted-plan targeted: 9 passed, 1 skipped locally.
- Phase 8C read API targeted: 2 passed.
- Phase 9B API targeted: 7 passed.
- Backend full: 129 passed, 21 skipped.
- Frontend: `npm test` (6 passed), `npm run typecheck`, and `npm run build` passed in `apps/web`.

## 2026-07-03

### Phase 9A True LLM Provider Gated Integration

#### Added

- Added a gated OpenAI-compatible planner provider path using `MDI_LLM_PROVIDER=openai_compatible` or explicit request provider selection.
- Added environment-driven provider configuration for `MDI_LLM_BASE_URL`, `MDI_LLM_API_KEY`, `MDI_LLM_MODEL`, `MDI_LLM_TIMEOUT_SECONDS`, `MDI_LLM_MAX_TOKENS`, and `MDI_LLM_TEMPERATURE`.
- Added safe provider error handling for missing API keys, unsupported providers, HTTP 401/429/5xx, network failures, timeouts, and malformed provider responses.
- Added fake-transport tests for OpenAI-compatible success, invalid/credential-bearing plans, provider failures, redaction, and persisted-plan handoff.
- Added `llm_integration` pytest marker and a gated live-provider smoke test that only runs when `MDI_RUN_LLM_INTEGRATION=1` and required provider env are present.

#### Changed

- `/planner/preview` and `/planner/jobs` can select the gated OpenAI-compatible provider while keeping mock/deterministic-safe behavior as the default.
- Provider failures are returned as validation-style safe failures; they do not persist plans, create jobs, or enqueue work.
- Valid provider output still passes through JSON parsing, schema construction, and PlanValidator before entering Phase 8B plan persistence.

#### Preserved

- Default unit tests and default CI do not call real external LLM services.
- QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry, and Adapter execution semantics remain unchanged.
- Raw prompts and raw completions are not persisted by default.
- API keys are not included in provider errors, AnalysisPlans, JobEvents, Artifacts, Results, or test assertions.
- Validation failure remains an all-or-nothing no-op: no plan, no job, no enqueue.

#### Verification

- `uv lock --check`: passed.
- Phase 7 targeted: 32 passed.
- Phase 8B persisted-plan targeted: 9 passed, 1 skipped locally.
- Phase 8C read API targeted: 2 passed.
- Backend full: 122 passed, 21 skipped.
- Frontend: `npm ci`, `npm test` (5 passed), `npm run typecheck`, and `npm run build` passed in `apps/web`.
- `python -m pytest -q -m llm_integration`: 1 skipped locally because live LLM env is not configured.

### Phase 8C-P1 UX Compliance Closure

#### Added

- Added read-only SSE replay for planner JobEvents at `/planner/jobs/{job_id}/events/stream`.
- Added EventSource-backed Agent Timeline behavior in the Planner workbench, with polling retained as a fallback.
- Added an independent `Report / Recipe Summary` frontend panel showing result summary, report artifacts, recipe artifacts, artifact references, `planId`, `planHash`, and persisted-plan provenance.
- Added an API-backed Dataset/Profile selector that uses existing `/datasets` and `/datasets/{dataset_id}/profile` reads while preserving manual ID fallback.
- Added frontend test coverage for SSE/EventSource timeline behavior, Report/Recipe Summary rendering, Dataset/Profile selector behavior, validation failure no-save/no-job/no-enqueue, loading state, and API error state.
- Added backend test coverage for the planner JobEvent SSE endpoint.

#### Changed

- Split the old combined artifact/result area into an `Artifact Gallery` plus a separate Report/Recipe summary area.
- Updated scaffold acceptance checks to assert the Phase 8C-P1 UI structure.

#### Preserved

- `/planner/jobs` still owns validation, plan persistence, job creation, and enqueue semantics.
- QueueWorkerRuntime and AnalysisPlanRepository were not changed.
- The frontend still never writes `analysis_plans`, directly creates jobs, directly enqueues work, computes authoritative plan hashes, or treats deterministic fallback as the normal path.
- Read-only planner APIs do not execute tools or mutate persisted plans/jobs.

#### Verification

- `uv lock --check`: passed.
- Phase 8C read API targeted: 2 passed.
- Phase 8B persisted-plan targeted: 9 passed, 1 skipped locally.
- Backend full: 112 passed, 20 skipped.
- Frontend: `npm test` (5 passed), `npm run typecheck`, and `npm run build` passed in `apps/web`.
- GitHub Actions run `28664159687` on Phase 8C-P1 implementation commit `4d0c241`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all passed. Integration summary: 19 passed, 0 skipped, 0 failed.

### Phase 8C Frontend Planner UX

#### Added

- Added a `PlannerWorkbench` frontend page as the user-facing Planner Job creation entry point.
- Added typed frontend planner API helpers for `createPlannerJob`, planner job detail, persisted AnalysisPlan detail, JobEvents, ToolCalls, Artifacts, and Result summary.
- Added read-only backend planner endpoints under `/planner/...` so the frontend can display persisted `planId`/`planHash` provenance without mutating state or triggering execution.
- Added Vitest + React Testing Library setup for the frontend and tests covering success, persisted provenance, `plan.loaded`, validation failure, loading, and API error states.
- Added `tests/test_phase8c_planner_read_api.py` for read-only planner API provenance behavior.

#### Changed

- Replaced the static frontend shell with a functional analysis planner workbench.
- `POST /planner/jobs` is now exposed through a FastAPI wrapper that preserves the existing injectable implementation while accepting the expected JSON HTTP body.
- Local non-PostgreSQL planner routes now share a module-level in-memory repository bundle so a created planner job can be read back by subsequent read-only planner API calls during local/dev frontend use.
- Updated the scaffold test to assert the Phase 8C Planner workbench content instead of the old static shell.

#### Preserved

- Frontend job creation still goes only through `/planner/jobs`.
- The frontend does not directly write `analysis_plans`, directly create jobs, directly enqueue work, compute authoritative plan hashes, or treat deterministic fallback as the production path.
- Read-only planner endpoints do not enqueue, execute, mutate plans/jobs, or call `build_phase2_plan`.
- QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry, and adapter execution semantics remain the Phase 8B baseline.

#### Verification

- `uv lock --check`: passed.
- Phase 8C backend targeted: 2 passed.
- Phase 8C + Phase 8B targeted: 11 passed, 1 skipped locally.
- Backend full: 112 passed, 20 skipped.
- Frontend: `npm ci`, `npm test` (4 passed), `npm run typecheck`, and `npm run build` passed in `apps/web`.
- GitHub Actions run `28646226271` on Phase 8C implementation commit `9967c5b`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all passed. Integration summary: 19 passed, 0 skipped, 0 failed.

### Phase 8B Persisted Plans + Queue Worker Runtime

#### Added

- Added Alembic revision `0002_phase8b_plans` for `analysis_plans` and nullable `jobs.plan_id`.
- Added `AnalysisPlanRepository` implementations for in-memory tests and SQLAlchemy/PostgreSQL runtime.
- Added stable canonical SHA-256 `plan_hash` for validated `AnalysisPlan` JSON.
- Added `tests/test_phase8b_persisted_plan_queue.py` covering repository round-trip/hash, planner persistence/enqueue behavior, validation-failure no-op, worker persisted-plan loading, exact 1-step execution, fallback behavior, and service-backed PostgreSQL + Redis + MinIO integration.

#### Changed

- `POST /planner/jobs` now validates first; invalid plans save no plan, create no job, and enqueue nothing.
- Valid `/planner/jobs` requests now persist the exact validated plan, create a Job linked by `plan_id`, return `plan_id`/`plan_hash`, and enqueue only `job_id` when requested.
- `QueueWorkerRuntime.handle_job(job_id)` now loads `job.plan_id` / `analysis_plans[plan_id]`, reconstructs `AnalysisPlan`, and executes exact persisted `steps`.
- Worker JobEvents, Artifact metadata, and `QueueWorkerResult` now include persisted plan provenance where available.
- QueueWorkerRuntime now initializes real adapter execution context from Tool Registry metadata for persisted-plan jobs, so the service-backed path can execute `ml.basic_metrics` without a fake executor.
- CI service-backed integration now runs Phase 6 plus Phase 8B integration and requires at least 19 passes with 0 skips.

#### Preserved

- LLM provider still only emits JSON plans and never executes code.
- PlanValidator remains the safety gate for unknown tools, non-MVP/V1/V2 tools, duplicate steps, empty steps, and credential-like params before persistence.
- Tool execution still goes through Tool Registry + Adapter; the deterministic fallback remains available only when no persisted plan is attached.

#### Verification

- `uv lock --check`: passed.
- Phase 8B targeted: 9 passed, 1 skipped locally (integration gated).
- Phase 8A targeted: 11 passed.
- Phase 7 targeted: 22 passed.
- Backend full: 110 passed, 20 skipped.
- Frontend: `npm ci`, `npm run typecheck`, `npm run build` passed in `apps/web`.
- Local service-backed integration: not run because Docker CLI is unavailable on this machine.
- CI run `28631817086` on Phase 8B code acceptance commit `962c429`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all passed. Integration summary: 19 passed, 0 skipped, 0 failed.

## 2026-06-27

### Phase 8A LLM Plan Execution Bridge

#### Added

- `tests/test_phase8a_plan_execution.py` (7 tests) — core proof: 1-step LLM plan → exactly 1 ToolCall (not deterministic 5).

#### Changed

- `Phase2ProductRuntime.create_job` accepts `analysis_plan` (execute this exact validated plan) and `execute` (False = planned-only) parameters.
- `POST /planner/jobs` executes the EXACT validated LLM plan when execute=True; planned-only when execute=False. Response now includes plan_source + executed.
- `MockLLMProvider` plan references the `ml_table` normalized object so the validated plan is executable end-to-end.

#### Preserved

- Deterministic `build_phase2_plan` remains the fallback when no analysis_plan is provided (Phase 2/3 loop unchanged).
- All execution still flows through Tool Registry + Adapter; PlanValidator unchanged (invalid/unknown/V1-V2 rejected before job).

#### Verification

- backend: 97 passed, 19 skipped, 0 failed
- Phase 7 targeted: 22 passed
- frontend typecheck/build: passed
- uv lock + git diff --check: clean

## 2026-06-27

### Phase 7 LLM JSON Planner + BYOK Secret Management

#### Added

- LLMPlannerProvider abstraction + MockLLMProvider + OpenAICompatibleProvider + DeterministicPlannerAdapter
- Planner prompt template (JSON-only, tool-aware, DataProfile context)
- PlanValidator (strict mode, 10 rules, structured errors)
- Planner API: POST /planner/preview, /planner/validate, /planner/jobs
- SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
- Secrets API: POST/GET/DELETE /me/secrets
- Secret redaction helpers (credential detection, value scrubbing)
- 19 Phase 7 tests (no real LLM key required)

#### Verification

- `python -m pytest -q`: 87 passed, 19 skipped
- Frontend typecheck/build: passed
- `uv lock --check`: passed

## 2026-06-26

### Phase 6: Service-backed Runtime Smoke & Integration Hardening

#### Added

- Added 18 service-backed integration smoke tests under `tests/test_phase6_integration.py`:
  - Docker compose services reachability (PostgreSQL, Redis, MinIO).
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle + index checks (not metadata.create_all).
  - PostgreSQL repository live integration: Project, Dataset, Job/ToolCall/Artifact, Recipe/Report, transaction rollback, status transition rejection.
  - PostgreSQL JobEvent seq live: monotonic seq, advisory lock strategy, 30-event concurrent correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with live PG repos.
  - Queue retry idempotency: duplicate job handle, crash+retry with live repos.
  - MinIO live: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter (not fake executor).
  - Alembic `metadata.create_all` live table creation verification against PostgreSQL.
  - PostgreSQL repository live integration: Project, Dataset, Job/ToolCall/Artifact, Recipe/Report, transaction rollback, and status transition rejection.
  - PostgreSQL JobEvent seq live integration: monotonic seq, advisory lock strategy, concurrent append seq correctness.
  - Redis queue live integration: enqueue/dequeue, QueueWorkerRuntime with live PG repos + Redis queue backend.
  - Queue retry idempotency live smoke: duplicate job handle, crash+retry with live repositories.
  - MinIO live integration: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + MVP Adapter end-to-end.
- Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with Phase 6 sections: integration test environment variables, per-category test descriptions, MinIO bucket cleanup, troubleshooting for common errors (connection refused, migration failed, bucket not found, signed URL invalid).
- Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL` opt-in variables.

#### Changed

- Fixed `docker-compose.yml` MinIO healthcheck to use `mc ready local` instead of `curl` for reliability.
- Fixed `tests/test_phase6_integration.py` Docker compose reachable test to use proper `SELECT 1` query and MinIO put+exists verification.
- Fixed `tests/test_phase6_integration.py` Alembic table test to remove broken dialect statement compilation.
- Added Phase 6 runbook sections 11-12: integration test guide and troubleshooting.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, BYOK UI, full auth, Kubernetes/Ray/autoscaling, plugin market work, or frontend redesign.
- All 18 integration tests skip cleanly when Docker services are not available or `MDI_RUN_INTEGRATION` is not set to `1`.
- Queue worker default execution still goes through `ToolExecutionRequest` -> Tool Registry validation -> Adapter execution.

#### Verification

- `python -m pytest -q`: 68 passed, 19 skipped, 50 third-party warnings.
- `python -m pytest tests/test_phase6_integration.py -q`: 18 skipped (Docker not available).
- `uv lock --check`: passed.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Integration Update

#### Added

- Added runtime config support for `DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, and `MINIO_*` variables while preserving existing `MDI_*` aliases.
- Added `apps/api/mdi_api/database.py` with SQLAlchemy engine and repository-factory helpers.
- Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` for PostgreSQL, Redis/RQ, MinIO, Alembic, and integration-test operations.
- Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend` under `services/workers/mdi_workers`.
- Added Phase 5 tests for config parsing, Alembic/runbook presence, PostgreSQL JobEvent advisory-lock strategy, queue retry idempotency, S3/MinIO live-client behavior, signed URLs, and `after_seq` regression.

#### Changed

- Updated `.env.example` and `docker-compose.yml` for local PostgreSQL, Redis, and MinIO runtime services.
- Updated Alembic env handling so configured runtime database URLs can drive `alembic upgrade head`.
- Extended `S3CompatibleArtifactStorage` from metadata mapping only to optional live boto3-compatible object operations and presigned URL generation.
- Hardened SQLAlchemy JobEvent seq allocation with a PostgreSQL transaction-scoped advisory lock while keeping SQLite tests on the existing local lock path.
- Refreshed `uv.lock` after adding Phase 5 runtime dependencies: boto3, psycopg, redis, and rq.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, BYOK UI, full auth, Kubernetes/Ray/autoscaling, plugin market work, or frontend redesign.
- Queue worker default execution still goes through `ToolExecutionRequest` -> Tool Registry validation -> Adapter execution.

#### Verification

- `python -m pytest tests/test_phase5_runtime_infrastructure.py -q`: 7 passed, 1 skipped.
- `python -m pytest -q`: 68 passed, 1 skipped, 50 third-party warnings.
- `python -m pytest -q -m integration`: 1 skipped because Docker-backed services were not enabled.
- `uv lock --check`: passed.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 4 Production Persistence Hardening Update

#### Added

- Added Alembic baseline files under `apps/api/alembic` and a Phase 4 migration baseline SQL string.
- Added `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` for explicit transaction boundaries.
- Added centralized Job and ToolCall status transition validation.
- Added Phase 4 persistence tests for migration smoke coverage, SQLAlchemy CRUD, rollback, status transitions, idempotent writes, concurrent JobEvent seq allocation, and stable `after_seq` ordering.

#### Changed

- Added `alembic` to Python dependencies and refreshed `uv.lock`.
- Hardened SQLAlchemy metadata with Job/ToolCall status constraints, ToolCall `idempotency_key` and `attempt`, `uq_tool_calls_job_step`, `uq_tool_calls_job_idempotency_key`, artifact storage-provider checks, and `uq_artifacts_job_storage_sha`.
- Made SQLAlchemy and InMemory ToolCall writes idempotent by stable job step/idempotency key.
- Made SQLAlchemy and InMemory Artifact metadata writes idempotent by stable job/storage/sha identity.
- Updated Python and TypeScript shared schemas with `ToolCallStatus`, `idempotencyKey`, and `attempt`.
- Updated worker runtime ToolCall status writes to use the shared enum.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tool execution, Celery/Ray/Kubernetes, full auth, live PostgreSQL runtime wiring, live S3/MinIO clients, or frontend rewrites.

#### Verification

- `python -m pytest tests/test_phase4_persistence_hardening.py -q`: 8 passed.
- `uv lock --check`: passed.
- `python -m pytest -q`: 61 passed, 50 third-party warnings.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `git diff --check`: passed with Windows line-ending notices only.

### Phase 3 Acceptance Hardening Update

#### Added

- Added `DataProfileRepository` and `ReportRepository` to InMemory and SQLAlchemy repository bundles.
- Added repository acceptance coverage for DataProfile, Report, concurrent JobEvent seq appends, ArtifactStorage helpers, S3/MinIO mapping metadata, SSE payload aliases, and API artifact routes.
- Added `apps/web/tsconfig.typecheck.json` so frontend typecheck no longer depends on `.next/types` being present.

#### Changed

- Hardened JobEvent seq allocation with in-process locks for repository and local worker append paths.
- Expanded artifact storage metadata with `storage_provider`, `bucket`, `content_type`, `sha256`, `size_bytes`, `preview_key`, and `created_at` coverage.
- Updated SQLAlchemy metadata, migration draft, Python/TypeScript schemas, and `docs/13_SHARED_SCHEMA_SPEC.md` for storage mapping fields.
- Phase 2 artifact summaries/details now expose local storage provider, content type, sha256, and created time metadata.

#### Fixed

- Fixed a frontend P0 where `npm run typecheck` failed in clean environments without pre-existing `.next/types`.
- Fixed an InMemory DataProfile project-listing gap when datasets were stored with `id` but no `datasetId` alias.

#### Verification

- `npm ci`: passed.
- `uv lock --check`: passed.
- `python -m pytest -q`: 53 passed, 50 third-party deprecation warnings.
- `npm run typecheck`: passed from clean `.next` state.
- `npm run build`: passed.

### Phase 3 Persistence Foundation Update

#### Added

- Added `apps/api/mdi_api/repositories.py` with Project, Dataset, Job, JobEvent, ToolCall, Artifact, and Recipe repository interfaces.
- Added InMemory repository implementations and SQLAlchemy Core repository implementations for SQLite-compatible tests and PostgreSQL-oriented persistence.
- Added `apps/api/mdi_api/artifact_storage.py` with local filesystem storage and S3/MinIO-compatible mapping interface.
- Added `apps/api/mdi_api/migrations.py` with Phase 3 SQL migration draft for projects, datasets, data_profiles, jobs, job_events, tool_calls, artifacts, visualization_recipes, and reports.
- Added `GET /jobs/{job_id}/stream` SSE smoke endpoint.
- Added `GET /artifacts/{artifact_id}/download` local signed-url/download placeholder.
- Added `tests/test_phase3_persistence.py` for repository, cursor, SSE, storage mapping, and Phase 2 regression coverage.

#### Changed

- Extended `job_events` metadata with `progress` and preserved unique `(job_id, seq)` cursor semantics.
- Extended `artifacts` metadata with storage mapping fields: `version`, `preview_key`, `size_bytes`, `content_type`, and `sha256`.
- Added `reports` metadata table and Phase 3 table list coverage.
- `GET /jobs/{job_id}/events` now supports `after_seq=N`.
- Phase 2 artifact summaries now point download links to `/artifacts/{artifact_id}/download`.
- `InMemoryJobStore` now supports `list_events_after_seq(job_id, after_seq)`.
- `npm run typecheck` now disables incremental cache reuse to avoid stale `.next/types` references from prior builds.

#### Scope Guard

- Did not add real LLM API calls, V1/V2 tools, Celery/Ray/Kubernetes, full auth, production PostgreSQL wiring, live S3/MinIO clients, or frontend rewrites.

#### Verification

- `uv lock --check`: passed.
- `python -m pytest -q`: 52 passed, 50 third-party deprecation warnings.
- `npm run typecheck`: passed.
- `npm run build`: passed.

## 2026-06-25

### Phase 2 Acceptance Hardening Update

#### Changed

- Aligned generated `AnalysisPlan.expectedArtifacts` with the shared schema shape `{name, type, fromStepId}`.
- Aligned Phase 2 job-level Recipe JSON with `VisualizationRecipe.steps`: each step now includes `toolVersion` and `inputBindings` as a string-to-string map.
- Added named shared schema types for `ExpectedArtifact` and `VisualizationRecipeStep` in Python and TypeScript.
- Local-path dataset uploads now parse the copied raw file under the Phase 2 artifact root instead of the caller's original path.
- Updated stale schema/status documentation in `docs/01_PRODUCT_REQUIREMENTS.md` and `README.md`.

#### Added

- Added Phase 2 regression assertions for planner expected artifacts and Recipe step shape.

#### Verification

- `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- Manifest audit: registry version `0.1.0`, 10 MVP tools.
- Phase 2 loop audit: completed with 5 tool calls and 25 artifacts.

### Phase 2 Local Product Loop Update

#### Added

- Added `apps/api/mdi_api/phase2_runtime.py`, a deterministic in-memory product runtime for Phase 2.
- Added local runtime support for:
  - project creation
  - dataset upload from local paths or inline small text files
  - parser/profile execution
  - deterministic AnalysisPlan generation
  - LocalWorkerRuntime ToolCall execution
  - Artifact export and lookup
  - JobEvent recording
  - job-level Recipe JSON generation
  - Markdown/HTML report generation
- Added Phase 2 API routes for dataset upload/profile, job create/query, job events, tool calls, job artifacts, and artifact detail lookup.
- Added `LocalFileArtifactStore` for local-file-backed artifact metadata/content retrieval.
- Added `tests/test_phase2_product_loop.py`, covering data pipeline, deterministic planner, job runtime, artifact store, API routes, and end-to-end product flow.

#### Changed

- `POST /projects`, `GET /projects`, and `GET /datasets` now read from the Phase 2 in-memory runtime instead of static stubs.
- `.gitignore` now ignores `material-data-intelligence-*.zip` handoff archives.

#### Scope Guard

- Did not add real LLM API calls, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, or frontend feature expansion.

#### Verification

- `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
- Frontend typecheck/build were not rerun because no frontend files changed in this Phase 2 round.

### Phase 1 Engineering Hardening Update

#### Added

- Added `uv.lock` for Python dependency locking.
- Added `apps/web/package-lock.json` for frontend dependency locking with npm.
- Added `.gitignore` coverage for `*.egg-info/`.

#### Changed

- Phase 1 verification now runs against an isolated uv-managed `.venv` instead of relying on the shared Anaconda environment.
- Frontend verification now uses lockfile-based install semantics via `npm ci`.

#### Verification

- `uv lock --check`: passed.
- `uv sync --extra test --frozen`: passed.
- `python -m pytest -q`: 42 passed from the uv-managed `.venv`.
- `npm ci`: passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.

### Phase 1 Product Acceptance Update

#### Added

- Added `apps/api/mdi_api/phase1_demo.py`, a deterministic Phase 1 product-flow runtime.
- Added Phase 1 API boundaries for:
  - `POST /projects`
  - `POST /projects/{project_id}/upload-sessions`
  - `POST /analysis-requests`
  - `GET /jobs/{job_id}/events`
  - `GET /jobs/{job_id}/events/stream`
  - `GET /jobs/{job_id}/artifacts`
- Added product-flow table metadata for data profiles, field mappings, sessions, messages, jobs, job events, tool calls, artifacts, visualization recipes, configs, secrets, and audit logs.
- Added `tests/test_phase1_product_acceptance.py`, covering CIF, POSCAR, CSV, ZIP, JSON limited, XYZ, EXTXYZ, Data Profile, AnalysisPlan, 10 MVP tools, artifacts, report, and JobEvents.

#### Changed

- Plotly preview export now writes a minimal valid PNG fallback when image export is unavailable, so Phase 1 preview artifacts are stable in environments without Kaleido/Chromium.
- Frontend workspace shell now includes visible Phase 1 surfaces for Agent Timeline, composition charts, 3D Viewer, ML Evaluation, Logs, Artifacts, Recipe, and Report.
- `mdi_schemas.__init__` now exports `InputRef` for shared-schema consumers.

#### Verification

- `python -m pytest -q`: 42 passed, 25 warnings from third-party deprecations.
- `npm run typecheck`: passed.
- `npm run build`: passed.

### Added

- 新增 Phase 1 API scaffold：`apps/api/mdi_api`，包含 FastAPI app factory、配置加载、health/auth/project/dataset/tools 路由边界。
- 新增基础 SQLAlchemy Core 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
- 新增本地基础设施配置：`docker-compose.yml` 覆盖 PostgreSQL、Redis、MinIO；`.env.example` 只保留占位符。
- 新增 Next.js workspace shell：`apps/web/package.json`、`next.config.mjs`、`tsconfig.json`、App Router 页面和三栏工作台样式。
- 新增 `pnpm-workspace.yaml`，将 `apps/web` 纳入前端 workspace。
- 新增 `tests/test_phase1_scaffold.py`，覆盖 API route、基础表 metadata、compose 服务和前端 shell 文件。
- 新增 `tests/test_manifest_loader.py::test_mvp_tools_reject_unregistered_params`，校验 10 个 MVP 工具的 `paramsSchema` 均拒绝未注册参数。
- 新增 Python/Pydantic `JobEvent` 共享模型，并从 `mdi_schemas` 包入口导出。
- 新增 TypeScript 共享核心类型：`JobStatus`、`JobEventStatus`、`JobEvent`、`InputRef`、`ToolExecutionRequest`、`ToolCall`、`ArtifactMetadata`、`Artifact`、`AnalysisStep`、`AnalysisPlan`、`DataProfile`、`VisualizationRecipe`。
- 新增 `tests/test_shared_schemas.py`，校验 Python 与 TypeScript schema 入口暴露本阶段要求的核心类型。
- 新增库层受控执行入口 `packages/adapters/mdi_adapters/executor.py`，提供 `execute_tool_request()` 和 `ToolExecutionResult`。
- 新增 `tests/test_tool_executor.py`，覆盖 Registry 路由、paramsSchema 拒绝、未注册工具拒绝和 in-memory cache hit。
- 新增最小 Worker runtime：`services/workers/mdi_workers/runtime.py`，提供 `run_tool_call_job()`、`InMemoryJobStore`、`WorkerRunResult` 和 `WorkerToolExecutionError`。
- 新增 `tests/test_worker_runtime.py`，覆盖 ToolCall 状态、JobEvent 序列、`artifact.ready` 事件和失败路径 Secret 脱敏。
- 新增 pytest workspace-local basetemp 配置：`--basetemp=.pytest_tmp`，避免受限运行环境访问系统临时目录失败。
- 新增 plain XYZ 非周期对象质量提示：`NON_PERIODIC_ATOMS`。
- 新增 `.extxyz` 检测与 ASE->Structure 周期转换支持测试。
- 新增 ZIP 安全解包回归测试。
- 新增 normalized object 稳定落盘 helper：`LocalArtifactExporter.export_normalized_object()`。
- 新增根级 `pyproject.toml`，配置 Python 包发现、pytest 路径和核心依赖。
- 新增工程骨架：`apps/web`、`apps/api`、`services/workers`、`packages/schemas`、`packages/tool-registry`、`packages/adapters`、`packages/material-parsers`、`packages/artifact-core`、`tests/fixtures`。
- 新增共享 Schema 实现：
  - `packages/schemas/mdi_schemas/models.py`
  - `packages/schemas/json/registered-tool.schema.json`
  - `packages/schemas/src/index.ts`
- 新增 Tool Registry manifest loader：`packages/tool-registry/mdi_tool_registry/loader.py`。
- 新增本地 Artifact exporter：`packages/artifact-core/mdi_artifact_core/exporter.py`。
- 新增 Adapter runtime：`BaseToolAdapter`、`ToolExecutionContext`、`ToolExecutionError`、adapter class registry 和 Plotly exporter。
- 新增前三个 MVP Adapter：
  - `PTableHeatmapAdapter`
  - `Structure3DAdapter`
  - `StructureViewer3DAdapter`
- 新增测试：
  - manifest loader 校验和计数测试。
  - BaseToolAdapter 生命周期、错误标准化和 Secret 参数拦截测试。
  - 三个 Adapter smoke tests。
  - Artifact storage key、metadata 和 recipe 测试。
- 新增 Data Pipeline 最小库层：
  - `detect_format()` 支持 CIF、POSCAR/CONTCAR、CSV、JSON limited、ZIP、XYZ/EXTXYZ 识别。
  - `parse_file()` / `parse_dataset()` 支持 CIF/POSCAR、CSV、JSON limited 解析。
  - `build_data_profile()` 生成 structure/table summary、quality issues 和 recommended tasks。
  - normalized object draft 记录 object type、metadata、hash、storage key 和 payload。
- 新增 Data Pipeline fixtures 和测试：`POSCAR`、`plain.xyz`、`ml_results.csv`、`tests/test_data_pipeline.py`。
- 新增剩余 7 个 MVP Adapter：
  - `ElementsHistAdapter`
  - `ChemSysTreemapAdapter`
  - `CoordinationHistAdapter`
  - `DensityScatterAdapter`
  - `ErrorDistributionAdapter`
  - `BasicMetricsAdapter`
  - `OutlierTableAdapter`
- 新增 ML adapter 公共校验与计算 helper：DataFrame / records 输入、target/prediction 字段推断、数值列校验、回归指标和 outlier 排序。
- 新增 10 个 MVP adapter class registry 覆盖测试和 7 个新增 Adapter smoke tests。

### Changed

- 将 Milestone 1 从 placeholder/scaffold 第一段推进为可验证 scaffold 完成：API、infra、Auth/Project/Dataset 表 metadata、Next.js shell 均有测试或构建证据。
- 更新 `pyproject.toml`，加入 `apps/api` package discovery / pytest path，并声明 `fastapi`、`sqlalchemy`、`uvicorn` 和 `starlette>=0.40,<0.47`。
- 更新 `README.md`、`apps/api/README.md`、`apps/web/README.md` 和 persistent 状态，记录 Phase 1 当前边界与验证结果。
- 收紧剩余 7 个 MVP 工具的 `paramsSchema`，从宽松 `additionalProperties: true` 改为平台批准参数白名单：
  `composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
- 更新 persistent 状态，记录新会话恢复核验、Git 工作区状态、测试命令和 Tool Registry 参数白名单补强。
- 将共享 Schema 实现从 Python 优先补齐为 Python + TypeScript 双入口覆盖；JSON Schema 当前仍以 `registered-tool.schema.json` 作为 manifest loader 校验基线。
- Adapter 执行路径从“测试直接实例化 Adapter”补强为可通过 `execute_tool_request()` 统一完成 Registry lookup、输入解析、参数校验、cache key 计算和 Adapter 路由。
- Worker 服务从 placeholder 推进为最小库层语义基线，可记录 Job / ToolCall / JobEvent，但仍不声明 Celery、PostgreSQL 或 SSE 已完成。
- plain XYZ Data Pipeline 语义从“unsupported”对齐为“解析成功的非周期 `Atoms`”，但仍不允许进入 `periodic_required` 的结构工具。
- `.extxyz` 现在按扩展名优先识别，避免落入 unknown。
- 将 Milestone 0 / Milestone 1 第一段从设计基线推进到可运行代码闭环。
- 采用 packages-first 实现结构：API、Web、Worker 先保留运行入口壳，可复用逻辑进入 `packages/`。
- 将 `composition.ptable_heatmap` 的平台参数先通过 adapter 聚合为 element value map，再调用真实 `pymatviz.ptable_heatmap(values)`。
- 将 `structure.viewer_3d` 的 snapshot 保持 optional，MVP 输出 `viewer.html` / `structure.json` / `summary.md` / `recipe.json`。
- 将 `DataProfile` Pydantic model 补齐 `structureSummary`、`tableSummary`、`phononSummary`、`trajectorySummary` 可选字段。
- `pyproject.toml` 显式加入 `pandas>=2.2`。
- 将所有 10 个 MVP manifest adapter 注册到 `ADAPTER_CLASSES`，让 Registry 中的 MVP 工具都能实例化执行库层 smoke path。
- `composition.elements_hist` 的标题设置改为 `fig.update_layout(title_text=...)`，避免将无效 `title` 传给 Plotly `go.Figure(**fig_kwargs)`。

### Fixed

- 修复当前运行环境中 `fastapi 0.115.12` 与 `starlette 1.0.0` 不兼容导致 API app 无法创建的问题；当前 Starlette 运行版本为 `0.46.2`。
- 修复 MVP 工具中 7 个 Adapter 仍允许任意未知参数通过 Tool Registry `paramsSchema` 的缺口。
- 修复受限 sandbox 下 `pytest tmp_path` 访问系统临时目录导致的测试失败。
- 修复 Data Pipeline 测试与设计语义不一致的问题：plain XYZ 不再被期待为 parser failure，而是作为非周期 Atoms 边界处理。
- 修复 `.extxyz` 无法被识别的问题。
- 修正 JSON Schema 中 `ToolInputSchema.periodicity`，允许可选字段导出为 `null`。
- 解决当前运行环境中 `pymatviz` 与 NumPy 2.x 相关二进制依赖导入问题：升级 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely`、`scikit-image`。
- 修正 pandas dtype 检测，避免使用即将移除的 `is_categorical_dtype`。

### Verification

- `python -m pytest -q`：41 passed，20 warnings；新增 Phase 1 scaffold 后通过。
- `npm run typecheck`：passed。
- `npm run build`：passed；Next.js 15.5.19 production build succeeded。
- `python -m pytest -q`：36 passed，20 warnings；恢复核验基线。
- `python -m pytest -q`：37 passed，20 warnings；新增 MVP paramsSchema 白名单测试后通过。
- `python -m pytest`：17 passed。
- `python -m pytest`：25 passed。
- `python -m pytest`：25 passed。
- `python -m pytest -q`：30 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。
- `python -m pytest -q`：34 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。
- `python -m pytest -q`：36 passed，20 warnings；warnings 为 matplotlib/Jupyter/ipywidgets 依赖弃用提示。

## 2026-06-24

### Added

- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 创建 `docs/index.md`。
- 创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 创建 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md` 作为仓库入口和 Agent 工作规则。
- 创建 `docs/03A_FRONTEND_COMPONENT_SPEC.md`。
- 创建 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`。
- 创建 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 创建 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`。
- 创建 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`。
- 创建 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`。
- 在共享 Schema 中补充 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 新增 ADR-041：MVP Worker 沙箱采用 Docker/容器隔离，进程级隔离不足。
- 新增 ADR-042：MVP 支持用户级 BYOK，组织级共享 Key 推迟到 V1。
- 新增 ADR-043：Secret 使用 envelope encryption，明文不进入日志、prompt、Artifact 或导出包。
- 新增 ADR-044：Prompt injection MVP 使用规则检测 + 上下文隔离 + Plan Validator。
- 新增 ADR-045：插件默认无网络、无 Secret、无 shell，必须显式声明能力。
- 新增 ADR-046：MVP 实现顺序按“数据闭环优先于高级功能”。
- 新增 ADR-047：专业材料领域扩展单独成文，但不改变 MVP 实现顺序。
- 新增 ADR-048：`docs/` 和 `persistent/` 必须进入 Git 版本管理。
- 新增 ADR-049：统一 ArtifactType / DisplayTarget / ToolCategory / ToolDomain。
- 新增 ADR-050：ToolInputSchema 使用 inputOptions 表达 OR 输入。
- 新增 ADR-051：MVP table/metrics artifact 是一等产物。
- 新增 ADR-052：plain XYZ 不进入周期性结构工具，除非有 lattice。
- 新增 ADR-053：MVP MatterViz snapshot 可选，viewer.html + metadata.json 为必需。
- 新增 ADR-054：Redis 不作为任务事实源，PostgreSQL 是唯一状态源。
- 新增 ADR-055：用户级 BYOK 按 job runner 解析，不写入 Recipe。
- 新增 ADR-056：V1 phonon 优先支持 phonopy.yaml + band.yaml，DOS 第二批。
- 新增 ADR-057：V1 composition clustering 默认 Magpie + PCA baseline，UMAP 可选。
- 新增 ADR-058：pymatviz 作为 primary visualization kernel。

### Changed

- 将设计进度推进到 Phase 11：MVP Roadmap。
- 将 Phase 10 标记为完成。
- 将 Phase 11 移入任务看板 In Progress。
- 将 Phase 11 标记为完成。
- 将设计阶段标记为完成，下一步进入代码实现准备。
- 根据目标文件清单补齐专业材料领域扩展文件。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，与 ADR 和 Roadmap 保持一致。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，修正产品需求和前端设计中的 MVP/V1 工具表述。
- 更新 `persistent/PROJECT_BRIEF.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md` 和 `persistent/TOOL_REGISTRY_NOTES.md`，记录领域扩展补充文件和逐文件审核结果。
- 修正 `.gitignore`，确保 `docs/` 和 `persistent/` 被 Git 跟踪。
- 统一 MVP/V1 工具范围：MVP 为 10 个核心工具，V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD。
- 将 `ToolInputSchema` 改为 `inputOptions` 多输入方案，并增加 `implementationSource`、`ToolDomain` 和 `periodicity` 约束。
- 将 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json` 纳入 Artifact 类型。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属。
- 补充 JobEvent 数据库索引、事件保留和日志保留策略。
- 修改 BYOK 规则：用户级 Secret 按 job runner 解析，Recipe 只保存 provider 能力需求。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 将 Phase 0 旧 Schema 草案替换为共享 Schema 引用。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`。
- 修正 Phase 4 `job_events` 表字段，增加 `seq`、`progress`、`created_at`，并说明同一 job 内 seq 单调递增。
- 修正 Phase 12 Milestone 3 的工具数量冲突，统一为 10 个 MVP Tool Executor / Adapter。
- 将 Phase 7 推荐任务补充 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义。
- 将 Phase 2 / Phase 8 的异步任务列表拆分为 MVP 与 V1。
- 统一 Redis 表述为 broker/cache/transient state；Celery result backend 不作为业务事实源。
- 在 `README.md` 增加对外交付压缩包排除 `.git/` 的说明。
- 统一 JobEvent status 为 `info/running/success/warning/error`，移除产品/架构草案中的 `pending`。
- 移除 retry 专用 JobStatus，改为 ToolCall retry 创建新的 attempt record。
- 将用户配置中的导出偏好改为 `defaultDownloadFormats` / `default_download_formats`，避免和内部 `ArtifactType` 混淆。
- 明确 Plotly Adapter MVP 推荐输出 `figure.html` 与 `preview.png`，SVG/PDF 进入 V1。
- 拆分 MVP 工具实现标准与端到端演示标准：10 个 MVP 工具均需注册、校验并可执行，Demo 至少覆盖 6 个核心工具且包含 composition、structure、ml。
- 统一 Plotly MVP 输出口径：`figure.json` 为必需；需要前端交互展示的 Adapter 必须提供 `figure.html` 或可直接渲染的 `plotly_json`，`preview.png` 为 MVP 推荐输出。
- 修正 Phase 2 `JobEvent`，补齐 `seq` 和 `progress`；`ArtifactRecord` 改为引用共享 `Artifact`。
- 补齐 Phase 4 数据库表字段：`jobs`、`tool_calls`、`artifacts`、`audit_logs` 等加入索引依赖的时间字段。
- 修正 MVP Secret API：使用 `/me/secrets` 管理用户级 BYOK，项目级共享 Secret API 推迟到 V1；项目只配置 LLM provider policy。
- 修正 Agent Timeline 事件结构，加入 `info` status、`id`、`jobId`、`seq` 和 `createdAt`，并声明其为 `JobEvent` 前端投影视图。
- 修正 Phase 1 MVP 验收标准，使其与 Phase 12 一致：10 个 MVP 工具均需注册、校验并可执行，端到端演示至少覆盖 6 个并包含 composition、structure、ml，且必须出现 metrics/table Artifact。
- 修正 Phase 1 上传格式验收范围，补齐 POSCAR/CONTCAR、ZIP 容器、JSON limited 与 XYZ/EXTXYZ 基础解析边界。
- 将 Phase 6 / Phase 9 Artifact 元数据从重复 Schema 定义改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`。
- 复核 Phase 6 缓存策略，确认 `用户要求 refresh 的工具` 条目无重复。
- 补充 pymatviz capability inventory，明确 Level 0-5 能力分层、9 类能力分类、原始 pymatviz 函数/类到平台 Tool ID 的映射表，以及 `composition.ptable_heatmap`、`structure.structure_3d`、`structure.viewer_3d` 的完整 capability 示例。
- 补充 manifest-based Tool Registry 基线，将首批工具来源拆分为 pymatviz、MatterViz/widget、platform_builtin 和 plotly_custom。
- 新增 Adapter implementation plan，明确 BaseToolAdapter 接口、Adapter 执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 Phase 6 Tool Registry 文档，声明初始工具来源于 `tool_registry/*.yaml`，并要求每个工具可追溯 source package / source function / implementationSource。
- 更新 Phase 11 Roadmap，加入 Milestone 0：pymatviz Capability Inventory & Adapter Baseline，并调整代码实现顺序为 manifest loader -> BaseToolAdapter -> MVP 前 3 个 Adapter -> Data Pipeline。
- 清理 `tool_registry/1project.lnk` 本地快捷方式，并在 `.gitignore` 增加 `*.lnk`、`desktop.ini`、`Thumbs.db`。
- 修正 `structure.chem_env_sunburst` 阶段标记：manifest 与 capability inventory 统一为 `v2`，late V1 仅作为 exploratory 备注。
- 更新 ADR-046，使 MVP 实现顺序与 `docs/12_MVP_ROADMAP.md` 的 Milestone 0 和新版实现路线一致。

### Decisions

- 配置优先级为 system defaults < user_config < project_config < recipe/job params。
- MVP 使用 Docker/容器化 Worker 沙箱。
- MVP BYOK 只支持用户级，组织级共享 Key 推迟到 V1。
- 插件默认最小权限，并通过 Tool Registry 和沙箱执行。
- 明确 MVP / V1 / V2 范围、开发里程碑、优先级、风险和验收标准。
- 明确领域扩展阶段：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 明确 pymatviz 是 primary visualization kernel，MatterViz 是 3D/widget 展示内核，Tool Registry + Adapter 是 LLM-friendly 能力抽象层。

## 2026-06-23

### Added

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 创建 `persistent/DESIGN_PROGRESS.md`。
- 创建 `persistent/TASK_BOARD.md`。
- 创建 `persistent/ARCHITECTURE_DECISIONS.md`。
- 创建 `persistent/TOOL_REGISTRY_NOTES.md`。
- 创建 `persistent/OPEN_QUESTIONS.md`。
- 创建 `persistent/CHANGELOG.md`。
- 补充独立系统定位：自然语言输入 + 材料数据文件 -> 交互式图表、3D 结构模型、过程展示和 Artifact。
- 补充 pymatviz / MatterViz / Plotly / pymatgen / ASE / phonopy 的平台内角色。
- 补充数据类型到可视化工具的映射表。
- 补充 MVP Tool Set 和 V1/V2 扩展工具边界。
- 补充 3D 渲染路线：Plotly `structure_3d` 与 MatterViz `StructureWidget` / `TrajectoryWidget`。
- 新增 ADR-003、ADR-004、ADR-005。
- 新增 ADR-006：MVP 默认 Auto 模式，Guided / Expert 推迟到 V1。
- 新增 ADR-007：MVP 只支持登录用户，公开分享推迟到 V1。
- 新增 ADR-008：前端产品形态是材料工作台，不是普通聊天页。
- 新增 ADR-009：MVP API 采用 FastAPI，保留 NestJS / LabPilot BFF 集成边界。
- 新增 ADR-010：MVP 采用模块化单体 + 独立 Celery Worker。
- 新增 ADR-011：MVP 异步任务采用 Celery + Redis，复杂编排后续升级 Temporal。
- 新增 ADR-012：PostgreSQL / S3-MinIO / Redis 三层存储职责。
- 新增 ADR-013：MatterViz 和重型 Plotly HTML 通过 sandboxed artifact iframe 展示。
- 新增 ADR-014：MVP Dashboard 使用固定响应式布局，拖拽布局推迟到 V1。
- 新增 ADR-015：Agent Plan 默认摘要展示，完整 JSON 可展开。
- 新增 ADR-016：Code 面板展示脱敏复现代码和 Recipe。
- 新增 ADR-017：MVP 上传采用对象存储预签名直传，分片/断点续传推迟到 V1。
- 新增 ADR-018：Artifact 和 Recipe 使用不可变记录 + version 字段。
- 新增 ADR-019：权限模型采用组织 + 项目 RBAC。
- 新增 ADR-020：API 错误采用统一 Problem Details 风格。
- 新增 ADR-021：Agent 只能输出 JSON Analysis Plan，不能执行代码。
- 新增 ADR-022：MVP 使用单模型配置，不做自动多模型路由。
- 新增 ADR-023：MVP 不做完整工具文档 RAG，使用版本化 Tool Registry 摘要。
- 新增 ADR-024：Prompt injection 进入 Timeline warning，并阻止高风险计划。
- 新增 ADR-025：MVP 工具参数 Schema 手写维护，V1 再评估半自动生成。
- 新增 ADR-026：Plotly 工具必须输出 `figure.json`。
- 新增 ADR-027：MatterViz 工具输出 `viewer.html` + `metadata.json`，snapshot 可选。
- 新增 ADR-028：Phonon / trajectory 高级工具推迟到 V1。
- 新增 ADR-029：Data Profile 必须由确定性解析管线生成，Agent 不直接猜文件内容。
- 新增 ADR-030：MVP 不执行 phonon 分析，保留识别和 Schema 扩展点。
- 新增 ADR-031：VASP 输出和 LAMMPS dump 推迟到 V2。
- 新增 ADR-032：代表性 3D 结构 MVP 使用规则采样，聚类代表点推迟到 V1。
- 新增 ADR-033：MVP 使用 SSE 推送 JobEvent，WebSocket 推迟到 V1。
- 新增 ADR-034：Worker 按任务类型拆分队列。
- 新增 ADR-035：PostgreSQL 是任务状态事实源，Redis 只做 broker/cache/短期状态。
- 新增 ADR-036：大数据图表和 3D 模型默认启用降采样与 LOD。
- 新增 ADR-037：Artifact、Recipe、Report 默认不可变，重跑生成新版本。
- 新增 ADR-038：Report Markdown 是 canonical，HTML 是派生产物，PDF 推迟到 V1。
- 新增 ADR-039：MVP 不支持公开分享，只支持项目成员访问和授权导出。
- 新增 ADR-040：Job export package 异步生成，且必须脱敏。

### Changed

- 将设计进度推进到 Phase 1：产品需求与用户流程。
- 将 Phase 0 标记为完成。
- 明确不 fork 大改 pymatviz，采用 Adapter + Visualization Service 隔离上游变化。
- 明确前端展示 Agent Timeline，不展示原始隐藏思维链。
- 将设计进度推进到 Phase 2：总体系统架构。
- 将 Phase 1 标记为完成。
- 将 Phase 2 移入任务看板 In Progress。
- 将设计进度推进到 Phase 3：前端工作台设计。
- 将 Phase 2 标记为完成。
- 将 Phase 3 移入任务看板 In Progress。
- 将设计进度推进到 Phase 4：后端服务与数据库设计。
- 将 Phase 3 标记为完成。
- 将 Phase 4 移入任务看板 In Progress。
- 将设计进度推进到 Phase 5：Agent 编排设计。
- 将 Phase 4 标记为完成。
- 将 Phase 5 移入任务看板 In Progress。
- 将设计进度推进到 Phase 6：工具注册表与 Adapter。
- 将 Phase 5 标记为完成。
- 将 Phase 6 移入任务看板 In Progress。
- 将设计进度推进到 Phase 7：数据解析与 Data Profile。
- 将 Phase 6 标记为完成。
- 将 Phase 7 移入任务看板 In Progress。
- 将设计进度推进到 Phase 8：高并发任务系统。
- 将 Phase 7 标记为完成。
- 将 Phase 8 移入任务看板 In Progress。
- 将设计进度推进到 Phase 9：Artifact / Recipe / Report。
- 将 Phase 8 标记为完成。
- 将 Phase 9 移入任务看板 In Progress。
- 将设计进度推进到 Phase 10：用户配置、安全与扩展。
- 将 Phase 9 标记为完成。
- 将 Phase 10 移入任务看板 In Progress。

### Fixed

- 无。

### Decisions

- 系统定位为材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- LLM 不直接执行任意代码；采用 JSON Plan + Tool Registry + Schema 校验的受控执行模式。
- MVP 优先覆盖文件上传、格式识别、Data Profile、Agent JSON Plan、白名单工具调用、Plotly/MatterViz Artifact、Recipe/Report 基础链路。
- 项目按独立系统设计，同时保留后续作为 LabPilot / ResearchOps 子系统集成的能力。
- MVP 默认 Auto 模式；用户可审查计划摘要，但不直接编辑 JSON Plan。
- MVP 仅支持登录用户和项目成员访问；公开分享推迟到 V1。
- MVP 报告导出支持 Markdown / HTML；PDF 推迟到 V1。
- MVP 架构采用 Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 所有耗时任务必须异步执行，通过 JobEvent 推送进度。
- Redis 不作为唯一持久化状态源，Job/ToolCall/Artifact 状态必须落 PostgreSQL。
- 前端采用三栏式工作台 + 底部面板。
- MVP 使用固定响应式 Dashboard，不做拖拽自定义布局。
- Code 面板只展示脱敏复现代码和 Recipe，不展示 Worker 内部脚本。
- MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- Artifact、Recipe、Report 采用不可变记录和 version 字段。
- 后端权限以 organization + project RBAC 为基础。
- Agent 只负责计划、解释和报告；执行必须经过 Execution Controller。
- MVP 使用项目默认模型，不做自动多模型路由。
- MVP 不做完整工具文档 RAG，先使用版本化 Tool Registry 摘要。
- Tool Registry 是 Agent 可执行能力的唯一白名单。
- MVP Tool Set 固定为 composition / structure / ml 的核心 10 个工具。
- Adapter 负责输入校验、上游调用、Artifact 输出、错误标准化和缓存。
- Agent 规划必须基于 Data Profile，不能直接猜文件内容。
- MVP 数据解析聚焦结构文件、CSV/JSON 和 ZIP；phonon/trajectory 深度支持后移。
- 代表性 3D 结构 MVP 使用规则采样。
- MVP 使用 SSE 作为任务进度事件流。
- Worker Pool 按 parse/profile/llm/viz/render/export 分队列。
- 大数据图表和 3D 模型默认启用降采样和 LOD。
- Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 是 canonical 产物。
- MVP 不支持公开分享，导出包异步生成且必须脱敏。
- 共享 Schema 是实现阶段的类型基线，未来 `packages/schemas/` 应从该文件拆分 JSON Schema、TypeScript 类型和 Python Pydantic model。
- `artifactTypes` 是统一产物类型字段名；不再使用 format 语义表达业务产物。
## 2026-07-04

### Added

- Added global official pymatviz example evidence outputs under `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`.
- Added API/artifact/browser evidence for `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz`.
- Added regression coverage for DataProfile-driven Mock Planner column selection and Ward CSV sparse-column handling.

### Changed

- CSV parsing now coerces numeric-looking string columns when at least 95 percent of non-null values are numeric.
- Mock Planner metrics column selection now filters sparse `Unnamed:` columns and no longer falls back to hard-coded `y_true/y_pred` when usable numeric DataProfile columns exist.
- Official example expected schemas now separate current verified outputs from richer `future_expected_*` outputs.

### Verification

- `python -m pytest tests/test_phase9b_demo_workspace_api.py -q`: 15 passed.
- Direct browser evidence generated with Mock Planner only; no real LLM was used.

## 2026-07-06

### Added

- Added deterministic composition parsing/statistics helper module for adapter reuse.
- Added `composition.formula_statistics` adapter.
- Added `composition.chem_sys_sunburst` adapter.
- Added lightweight Ward adapter evidence for formula statistics, elements histogram, periodic-table heatmap, chemical-system treemap, and chemical-system sunburst under `docs/phase10b/adapter_evidence/`.

### Changed

- Upgraded `composition.elements_hist`, `composition.ptable_heatmap`, and `composition.chem_sys_treemap` to use table/formula-column input and structured top-level artifact metadata.
- Extended Tool Registry schemas and manifests for the Phase 10B-1 composition visualization tools.
- Extended Mock Planner routing so explicit composition prompts are handled before generic visualization routing.

### Verification

- Added or updated adapter, manifest, planner-routing, and persisted execution coverage for the five Phase 10B-1 tools.
- Real LLM was not used; browser/API evidence remains deferred to Phase 10B-2.

## 2026-07-06 Phase 10B-2

### Added

- Added `docs/phase10b/browser_api_evidence/` with browser/API/artifact evidence for the five composition visualization adapters.
- Added per-case evidence manifests, execution logs, platform summaries, security scan files, API captures, screenshots, and artifact copies for:
  - `ward_formula_statistics`
  - `ward_elements_hist`
  - `ward_ptable_heatmap`
  - `ward_chem_sys_treemap`
  - `ward_chem_sys_sunburst`

### Changed

- Updated `composition.ptable_heatmap` artifact naming from generic `figure.json` to contract-specific `ptable_heatmap.json`.
- Updated adapter test coverage to require `ptable_heatmap.json`, `ptable_heatmap.html`, `summary.md`, and `recipe.json`.

### Verification

- Evidence totals: 50 redacted API captures, 25 browser screenshots, 19 artifact files, and 5 manifests.
- Security scan: `NO_SECRET_PATTERN_HITS`.
- Evidence uses Mock Planner only; no real LLM was used.
- Runtime main semantics were not changed.

## 2026-07-07 Phase 10C-2

### Added

- Added `docs/phase10c/browser_api_evidence/` with browser/API/artifact evidence for the five lightweight structure adapters.
- Added per-case evidence manifests, execution logs, platform summaries, security scan files, API captures, screenshots, and artifact copies for:
  - `simple_cubic_structure_summary`
  - `simple_cubic_lattice_summary`
  - `simple_cubic_spacegroup_summary`
  - `simple_cubic_composition_from_structure`
  - `simple_cubic_preview_metadata`

### Verification

- Evidence totals: 45 redacted API captures, 25 browser screenshots, 15 artifact files, and 5 manifests.
- Security scan: `NO_SECRET_PATTERN_HITS`.
- Evidence uses Mock Planner only; no real LLM was used.
- Runtime main semantics were not changed.
- No 3D viewer, XRD, RDF, phonon, Brillouin zone, or unsupported official example support is claimed.

## 2026-07-07 Phase 10D

### Added

- Added `docs/phase10d/phase10d_advanced_structure_visualization_planning.md`.
- Added `docs/phase10d/phase10d_candidate_adapter_matrix.md`.
- Added `docs/phase10d/phase10d1_viewer_scene_metadata_implementation_prompt.md`.

### Planning Decisions

- Advanced structure capability is split into viewer metadata/export package, static physics plots, interactive 3D, and phonon layers.
- Recommended next phase is `structure.viewer_scene_metadata` and `structure.viewer_export_package`, with optional schema-only `structure.viewer_3d_contract`.
- Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, XRD/RDF implementation, phonon tools, notebook extraction, and script execution remain deferred.

### Verification

- Planning-only phase; no adapters or runtime semantics were changed.
- Default CI remains gated away from real LLM calls.

## 2026-07-07 Phase 10D-1

### Added

- Added `structure.viewer_scene_metadata`.
- Added `structure.viewer_export_package`.
- Added `docs/phase10d/phase10d1_viewer_scene_metadata_implementation.md`.
- Added adapter-level evidence under `docs/phase10d/adapter_evidence/`.

### Changed

- Extended Tool Registry manifest, strict params schema generation, adapter exports, adapter registry, and Mock Planner routing for static viewer scene metadata/export package tools.
- Added frontend tool labels for the two new static viewer metadata tools.

### Verification

- Added tests for artifact contracts, no JavaScript / no external URL assertions, registry schemas, planner routing, deferred prompt boundaries, and persisted execution.
- Browser/API evidence remains deferred to Phase 10D-2.
- No full 3D viewer, WebGL renderer, XRD, RDF, coordination histogram, Brillouin-zone, phonon, notebook extraction, or script execution was added.

## 2026-07-08 Phase 10D-2

### Added

- Added `docs/phase10d/browser_api_evidence/` with Browser/API/artifact evidence for:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Added per-case redacted API captures, browser-rendered static preview screenshots, copied artifact files, evidence manifests, execution logs, platform summaries, and security scan files for:
  - `scene_metadata_cif`
  - `scene_metadata_poscar`
  - `scene_metadata_structure_json`
  - `export_package_cif`
  - `export_package_poscar`
  - `export_package_structure_json`

### Verification

- Evidence totals: 99 redacted API captures, 30 browser-rendered static preview screenshots, 21 artifact files, and 6 manifests.
- Security scan: `NO_SECRET_PATTERN_HITS`.
- Evidence uses Mock Planner only; no real LLM was used.
- Runtime main semantics and the Phase 10D-1 artifact contract were not changed.
- No full 3D viewer, WebGL renderer, XRD, RDF, coordination histogram, Brillouin-zone, phonon, notebook extraction, script execution, or unsupported official example support is claimed.

## 2026-07-08 Phase 10D-3

### Added

- Added schema-aware static frontend previews for `viewer_scene.json` and `viewer_assets_manifest.json`.
- Added frontend coverage for viewer scene overview, lattice, atoms, bonds, display/camera metadata, limits, warnings, security badges, manifest artifact list, renderer status, and raw JSON fallback.
- Added Phase 10D-3 static preview evidence under `docs/phase10d/browser_api_evidence/phase10d3_static_preview_hardening/`.

### Changed

- Hardened `summary.md` and `recipe.json` previews so static report text and deterministic recipe fields are visible without executing artifact content.
- Renamed the material artifact result panel title to avoid implying a full 3D viewer.

### Verification

- Added frontend tests asserting no canvas/WebGL renderer, no script node, no Three.js label, and no `structure.viewer_3d` claim.
- Phase 10D-3 evidence includes 10 browser-rendered static preview screenshots.
- No new adapter, Tool Registry semantic change, runtime authority change, full 3D viewer, WebGL renderer, XRD, RDF, coordination histogram, phonon, notebook extraction, script execution, or unsupported official example support was added.

## 2026-07-08 Phase 10E

### Added

- Added `docs/phase10e/phase10e_static_structure_physics_plot_planning.md`.
- Added `docs/phase10e/phase10e_candidate_adapter_matrix.md`.
- Added `docs/phase10e/phase10e1_static_physics_adapter_implementation_prompt.md`.

### Planning Decisions

- Recommended Phase 10E-1 start with `structure.coordination_hist` using a deterministic distance-cutoff neighbor policy.
- `structure.xrd` is the second candidate once fixture peak windows and numeric tolerances are pinned.
- `structure.rdf` is deferred until normalization and cutoff policy are explicit.
- Official XRD/RDF widget examples remain mapping-only/future-scope references and are not PASS evidence.

### Verification

- Planning-only phase; no adapter, registry, runtime, planner execution semantics, browser/API evidence, or real LLM path was changed.

## 2026-07-08 Phase 10E-1

### Added

- Added `structure.coordination_hist`.
- Added `docs/phase10e/phase10e1_coordination_hist_implementation.md`.
- Added deterministic artifacts for the adapter: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.

### Changed

- Extended Tool Registry manifest, adapter exports, adapter registry, frontend tool labels, and Mock Planner routing for `structure.coordination_hist`.

### Verification

- Added tests for fixtures, deterministic coordination bins, by-element aggregation, pair counts, site details, params validation, artifact contracts, no JavaScript / no external URL assertions, registry schemas, planner routing, deferred prompt boundaries, and persisted execution.
- Browser/API evidence remains deferred to Phase 10E-2.
- No XRD, RDF, full 3D viewer, WebGL renderer, Brillouin-zone, phonon, notebook extraction, script execution, or advanced local environment classification was added.

## 2026-07-08 Phase 10E-2

### Added

- Added `docs/phase10e/browser_api_evidence/phase10e2_coordination_hist/` with redacted API captures, copied artifacts, static browser preview pages, screenshots, audits, and evidence manifest.
- Added `docs/phase10e/phase10e2_coordination_hist_browser_api_evidence.md`.

### Verification

- Evidence totals: 43 redacted API captures, 6 browser-rendered static preview screenshots, and 12 artifact capture files.
- Verified small CIF, small POSCAR, and generated pymatgen Structure JSON cases.
- Security scan: `NO_SECRET_PATTERN_HITS`.
- Artifact scan: no script, JavaScript URL, external URL, CDN, Three.js, or eval patterns.
- Negative routing confirms XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts do not route to `structure.coordination_hist`.
- No new adapter, XRD, RDF, full 3D viewer, WebGL renderer, phonon, notebook/script workflow, unsupported official example claim, runtime semantic change, or real LLM path was added.

## 2026-07-08 Phase 10E-3

### Added

- Added `docs/phase10e/phase10e3_xrd_rdf_readiness_decision.md`.
- Added `docs/phase10e/phase10e3_static_physics_next_scope_matrix.md`.
- Added `docs/phase10e/phase10e4_static_physics_adapter_implementation_prompt.md`.

### Planning Decisions

- Recommended Phase 10E-4 implement `structure.xrd` only.
- Marked XRD ready for a single-scope implementation because existing dependencies, fixtures, artifact contracts, and evidence flow are sufficient if peak tolerances are pinned in implementation.
- Marked RDF not ready for immediate implementation because normalization, cutoff/binning, periodic image, finite-size warning, and partial RDF policies remain unresolved.
- Official examples for XRD/RDF remain mapping references only and are not PASS evidence.

### Verification

- Planning-only phase; no adapter, Tool Registry semantic change, runtime semantic change, browser/API evidence, frontend runtime change, dependency change, or real LLM path was added.
- Local checks: `git diff --check` passed with line-ending warnings only, `uv lock --check` passed, `npm --prefix apps/web run typecheck` passed, and `uv run python -m pytest -q` passed with 254 passed / 21 skipped / 9 warnings.
- Security scan: `NO_SECRET_PATTERN_HITS`.

## 2026-07-08 Phase 10E-4

### Added

- Added `structure.xrd`.
- Added `docs/phase10e/phase10e4_xrd_implementation.md`.
- Added deterministic artifacts for the adapter: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.

### Changed

- Extended Tool Registry manifest, adapter exports, adapter registry, and Mock Planner routing for `structure.xrd`.
- Added a Phase 10E-4 shared schema addendum for static XRD artifacts.

### Verification

- Added tests for CIF/POSCAR/Structure dict fixtures, deterministic peak ordering, numeric rounding, range filtering, intensity filtering, peak limits, HKL include/exclude behavior, params validation, artifact contracts, no JavaScript / no external URL assertions, registry schemas, planner routing, deferred prompt boundaries, and persisted execution.
- Browser/API evidence remains deferred to Phase 10E-5.
- No RDF, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone, phonon, notebook/script workflow, experimental fitting, Rietveld refinement, unsupported official example claim, runtime semantic change, or real LLM path was added.

## 2026-07-08 Phase 10E-5

### Added

- Added `docs/phase10e/browser_api_evidence/phase10e5_xrd/` with redacted API captures, copied artifacts, local static preview pages, audits, and evidence manifest for `structure.xrd`.
- Added `docs/phase10e/phase10e5_xrd_browser_api_evidence.md`.

### Verification

- Evidence totals: 40 redacted API captures, 12 artifact capture files, 6 local static preview pages, and no fabricated screenshots.
- Verified small CIF, small POSCAR, and generated pymatgen Structure JSON cases.
- Verified artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Security scan: `NO_SECRET_PATTERN_HITS`.
- Negative routing confirms RDF, coordination histogram, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, CrystalNN, experimental fitting, Rietveld, and broadening prompts do not route to `structure.xrd`.
- Browser screenshot capture is blocked in this environment because no browser-control Node REPL tool is exposed and no Chrome/Edge/Firefox/Playwright/Puppeteer runtime is installed. No browser screenshot was fabricated.
- No new adapter, RDF, full 3D viewer, WebGL renderer, Three.js, phonon, notebook/script workflow, unsupported official example claim, runtime semantic change, or real LLM path was added.

## 2026-07-08 Phase 10E-5R2

### Changed

- Upgraded Phase 10E-5 XRD browser/API evidence from `PARTIAL_PASS` to `PASS`.
- Added six real browser-rendered frontend screenshots under `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/`.
- Updated `browser_preview_audit.md`, `README.md`, `evidence_manifest.json`, and `evidence_manifest.csv` with system Chrome / Playwright capture metadata.

### Verification

- Browser executable: `C:/Program Files (x86)/Google/Chrome/Application/chrome.exe`.
- Browser version: `149.0.7827.201`.
- Automation: existing Playwright package with system Chrome `executablePath`; no managed browser download.
- External request audit: `NO_EXTERNAL_REQUESTS`.
- No RDF, full viewer, WebGL renderer, Three.js renderer, phonon, experimental fitting, Rietveld refinement, runtime semantic change, or real LLM path was added.

## 2026-07-09 Phase 10E-6

### Added

- Added `docs/phase10e/phase10e6_rdf_policy_hardening.md`.
- Added `docs/phase10e/phase10e6_rdf_policy_matrix.md`.
- Added `docs/phase10e/phase10e7_rdf_next_scope_prompt.md`.

### Planning Decisions

- Fixed RDF as periodic-crystalline-only for the first implementation.
- Fixed `number_density` normalization with shell-volume scaling, all-site global RDF, exact zero-distance self-pair exclusion, ordered partial pairs, and deterministic binning.
- Fixed params schema and artifact contracts for `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Marked `structure.rdf` READY for Phase 10E-7 implementation, with browser/API evidence deferred to Phase 10E-8.
- Official RDF README gallery examples remain mapping references only and are not PASS evidence.

### Verification

- Planning-only phase; no adapter, Tool Registry semantic change, runtime semantic change, browser/API evidence, frontend runtime change, dependency change, or real LLM path was added.

## 2026-07-09 Phase 10F-5

### Added

- Added `docs/phase10f/phase10f5_static_physics_fixture_pack_replay_verification.md`.
- Added `docs/phase10f/static_physics_fixture_pack_replay/` with validation, replay transcript, artifact contract validation, numeric candidate values, replay matrix, and security audit.
- Added `docs/phase10f/phase10f6_next_scope_prompt.md`.

### Changed

- Updated the Phase 10F-4 fixture pack expected contracts with Phase 10F-5 replay-generated candidate numeric values.
- Extended `expected_contract.schema.json` to allow Phase 10F-5 candidate replay metadata while keeping `official_pass_claim` constrained to false.

### Verification

- Replayed `coordination_hist_small_crystal`, `xrd_small_crystal`, and `rdf_small_crystal` through the platform planner/job/runtime path.
- Verified selected tools, generated artifacts, schema versions, deterministic recipe metadata, and security flags.
- Fixture-pack replay result: `PASS`.
- Official examples PASS claims remain none.
- No notebook, external script, external API, real LLM, new dependency, new adapter, full viewer, WebGL/Three.js renderer, or phonon scope was added.

## 2026-07-10 Phase 10F-11

### Added

- Added `apps/web/test/viewer-scene-browser-evidence.mjs` for reproducible real browser evidence.
- Added Phase 10F-11 browser evidence docs, readiness matrix, replay notes, screenshots, DOM snapshot, and network audit.

### Changed

- Hardened `PlannerWorkbench` JSON-only preview so `kind: viewer_scene` payloads with expected schema failures still display inert summary, validation, and error details.
- Added frontend coverage for invalid schema JSON-only preview.

### Verification

- Real browser evidence command passed with system Chrome.
- Evidence shows no canvas, iframe, WebGL marker, Three.js marker, renderer claim, or external request for covered cases.
- No renderer, WebGL, Three.js, adapter, planner routing, runtime route, notebook, external API, or artifact JavaScript was added.

## 2026-07-12 Phase 10F-16

### Added
- Instanced atom picking, canonical site inspector and bounded-bond neighbor summary.
- Cartesian distance, angle and signed dihedral measurement with bounded history.
- Current-view PNG and attached viewer artifact downloads.
- Multi-browser scientific inspection runner and evidence.

### Security
- Selection is capped at four, history at twenty, PNG at 4096 squared pixels.
- No artifact execution, external viewer network, remote asset, or schema change.

## 2026-07-12 Phase 10F-17

### Added
- Periodic site refs, replica picking and periodic inspector fields.
- Bounded exact minimum-image math with triclinic reference fixtures.
- Renderer-local supercell controls, derived caps, and supercell-aware PNG names.

### Security
- Added determinant, condition, offset, repeat, candidate, site, and bond limits.
- No canonical schema change, backend supercell resource, external periodic service, or artifact execution.

## 2026-07-12 Phase 10F-20

### Added
- Code-owned compatibility registries for three viewer scene and three manifest versions.
- Typed Phase 10D renderer rejection and schema-specific JSON preview status.
- Current-producer redirects for legacy Mock Planner viewer intents.

### Security
- No topology inference, dependency change, executable artifact content, or external resource.

## 2026-07-13 Phase 10F-21

### Added
- Renderer performance budgets, degraded/refused policy, generation cancellation, and resource metrics.
- Near-cap/stale-generation tests and real multi-browser performance runner.

### Security
- Performance thresholds remain application-owned; over-budget input cannot initialize WebGL.
- No dependencies, external telemetry, artifact execution, or canonical schema changes.

## 2026-07-13 Phase 10F-22

### Added
- Keyboard rotate/pan/zoom/reset, deterministic focus restoration, semantic scene/topology summaries, and bounded live announcements.
- Semantic periodic-neighbor table controls, mobile 44px targets, vertical scroll preservation, reduced-motion and forced-colors styles.
- Real Chromium/Firefox/WebKit accessibility, mobile, orientation, zoom, console, and network evidence.

### Security
- Accessibility roles, shortcuts, event handling, and focus remain application-owned and cannot be supplied by artifacts.
- No dependency, artifact schema, backend authority, external request, or remote asset change.

## 2026-07-13 Phase 10F-23

### Added
- Real canonical bond picking over shared Three.js line geometry and fixed bond highlight.
- Ordered endpoint selection, undo, keyboard atom/bond traversal, and accessible bond inspector.
- Deterministic local `viewer_measurement.json` with periodic points and no-mutation policy.
- Three-browser/mobile advanced picking, math, lifecycle, console, and network evidence.

### Security
- Fixed application-owned thresholds/caps and on-demand raycasting; no artifact callbacks or screen-space science.
- No dependency, backend runtime, canonical scene topology, or external network change.

## 2026-07-13 Phase 10F-26

### Added
- Strict scientific export controls for PNG, JSON view state, and Markdown summary.
- Transparent/light/dark and high-DPI capture over current camera, clipping, supercell, and measurement state.
- Ordered SHA-256 export manifest and three-browser/mobile evidence runner.

### Security
- Added dimension/DPR/pixel/memory, concurrency, stale-generation, filename, and Blob URL controls.
- No dependency, backend runtime, canonical scene, external request, remote asset, artifact execution, or PDF implementation.

## 2026-07-13 Phase 10F-27

### Changed
- Moved the unique `structure.viewer_3d` registration from the MatterViz manifest to the platform built-in manifest.
- Added exact formal product capability text while preserving adapter, params, artifacts, and runtime behavior.
- Added live API, topology, browser, mobile, performance, accessibility, network, and hash evidence.

### Security
- No dependency, canonical schema, QueueWorkerRuntime, PlanValidator, external request, artifact execution, or advanced scientific capability was added.

## 2026-07-13 Phase 10 Closure Regression Pack

### Added
- Executable backend portfolio, frontend composition, and real browser closure entries.
- Machine-readable invariant, compatibility, capability, determinism, fallback, lifecycle, network, and hash evidence.
- Required CI steps for backend/frontend evidence integrity and service-backed formal viewer execution.

### Security
- No dependency, schema, adapter, renderer feature, runtime authority, external network, real LLM, or deferred scientific capability was added.

## 2026-07-14 Phase 10H-1

### Added
- Static `phonon.band` adapter for strict canonical JSON and bounded phonopy band.yaml.
- Four dedicated phonon artifact types plus inert plot, table, and recipe outputs.
- Planner/job/runtime persistence and a canonical-validated lazy local Plotly frontend preview.
- Real Chromium, Firefox, WebKit, mobile, accessibility, determinism, API, network, and screenshot evidence.

### Security
- Added safe YAML alias/tag/depth/node/byte guards, exact field mapping, explicit preview budgets, and Plotly cleanup.
- No new dependency, remote asset, solver, artifact execution, DOS, eigenvector, animation, notebook/script, external API, or real LLM path.

## 2026-07-14 Phase 10H-2

### Added
- Static `phonon.dos` adapter for canonical JSON and bounded phonopy total/projected text wrappers.
- Unit/density conversion, normalization, integration audit, projections, DOS-specific summary/manifest, plot, table, and recipe.
- Validated local Plotly preview and Chromium/Firefox/WebKit/mobile evidence.

### Security
- Exact fields/columns, byte/value caps, no smoothing or inference, preview refusal, and Plotly cleanup.
- No dependency, network, solver, artifact execution, combined view, eigenvector, animation, notebook/script, external API, or real LLM path.
