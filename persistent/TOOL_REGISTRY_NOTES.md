# TOOL_REGISTRY_NOTES

## 2026-07-28 Phase 10K-1 Profile Eligibility Facts

- No tool manifest, adapter map, public identity, parameter schema, Planner
  route, PlanValidator rule, or QueueWorkerRuntime behavior changed.
- Profile 2.0 provides deterministic data-readiness facts for existing and
  future consumers. `platformStatus=AVAILABLE` is restricted to verified
  current Registry identities supplied as an explicit runtime snapshot; direct
  profiling without that snapshot returns `NOT_EVALUATED`. Regression/
  uncertainty/classification product,
  composition space, and dataset structure statistics remain
  `NOT_IMPLEMENTED` even when their data conditions are satisfied.
- The legacy `recommendedTasks` ML entry is retained for response compatibility
  but now has `availableNow=false`; it grants no execution authority.
- Phase 10K-2/3/4 may consume these facts only after their own coherent bounded
  product tools, artifact contracts, Registry closure, and reviewer gates.

## 2026-07-27 Phase 10K-0 Material Intelligence Inventory

- Real executable foundations are limited to the adapter registry closure:
  table numeric/distribution summaries; scatter/histogram/correlation;
  composition summary/formula/element/periodic-table/chemical-system outputs;
  basic regression metrics/error/outlier/density scatter; and lightweight
  structure summaries.
- Historical V1 manifest entries for parity, uncertainty calibration,
  chemistry-conditioned error, and composition clustering do not have matching
  runtime adapter classes and are `PLANNED / NON_EXECUTABLE`, not READY.
- Phase 10K implementation must test Registry-to-adapter closure before
  promoting a public capability. Product tools should group scientifically
  coherent bounded outputs rather than create one public tool per scalar metric.
- `DataProfile 0.1` does not yet expose the capability facts needed for truthful
  eligibility. Phase 10K-1 owns that deterministic fact layer; Phase 10L owns
  capability-aware multi-tool planning.
- This audit adds no Registry entry and changes no manifest, adapter, Planner,
  PlanValidator, QueueWorkerRuntime, artifact, or dependency.

## 2026-07-27 Gate J6-R Capability Surface Policy

- Tool Registry exists to expose stable, meaningful, non-overlapping materials
  analysis capabilities to the Agent, not to register every possible algorithm.
- Each future tool requires strict parameters, bounded execution, data-kind
  compatibility, inert artifacts, provenance, and an accurate user description.
- Initial-release candidates, still `NOT_IMPLEMENTED` unless separately noted,
  include CrystalNN/VoronoiNN, experimental XRD comparison, trajectory
  analytics, and Electronic Band/DOS. They enter the Registry only in their
  implementation phases.
- Fermi Surface is Future Scope. Enterprise, deployment, and plugin-marketplace
  capabilities are not Registry roadmap items.
- This gate changes no manifest, adapter map, Tool Registry entry, Planner,
  PlanValidator, or QueueWorkerRuntime behavior.

## 2026-07-27 Post-J6 Electronic Roadmap Freeze (Superseded)

- This gate adds no Tool Registry entry and changes no Planner, PlanValidator, adapter, or QueueWorkerRuntime behavior.
- Electronic Band/DOS public tool identities remained `NOT_IMPLEMENTED`; the
  implementation is now planned for Phase 10N-5.
- Fermi Surface public tool identity remains `NOT_IMPLEMENTED` and is now Future Scope.
- Existing `phonon.band`, `phonon.dos`, `phonon.band_dos`, and `structure.brillouin_zone` identities retain their current meanings and do not acquire electronic semantics.

## 2026-07-26 Phase 10J-6 Slice / Direct Volume Consumer

- No public tool was added. `structure.volumetric_data` remains the sole validated producer of canonical volumetric artifacts.
- Slice and Direct Volume are application-owned result modes over already validated artifacts. The ephemeral slice model and renderer display state are not AnalysisPlan inputs and grant no browser execution authority.
- Mock Planner recognizes explicit slice/direct-volume intent but still routes to `structure.volumetric_data`; negative routing excludes arbitrary slicing/filtering, vector/complex derivation, segmentation/Bader, calculations, scripts, and remote GPU rendering.
- Tool Registry, PlanValidator, QueueWorkerRuntime, adapter schemas, and backend job-success semantics are unchanged.

## 2026-07-24 Phase 10J-5 ELF / Orbital Product

- `structure.volumetric_data` remains the only public identity. No `structure.elf`, `structure.parchg`, `structure.orbital_density`, or orbital-viewer tool was registered.
- Explicit ELF/orbital/partial-density inspection prompts route to the existing strict volumetric tool. Calculation, topology/basin, HOMO/LUMO, wavefunction reconstruction/combination, external execution, and ambiguous orbital intent are excluded.
- The adapter keeps source-native ELFCAR/PARCHG semantics and emits additive inert summary/recipe disclosure only. QueueWorkerRuntime, PlanValidator, AnalysisPlan, artifact authority, and canonical schema semantics are unchanged.

## 2026-07-17 Phase 10I-3 Band-BZ Product Composition

- No `reciprocal.band_bz_link` public tool was registered. Linked View is an application-owned composition of independently validated artifacts from existing `phonon.band` and `structure.brillouin_zone` steps.
- Mock Planner may emit those two existing steps for explicit compatible linked-view intent. It retains strict PhononBand/Structure profile inputs and negative routes for electronic bands, DFT/Fermi, meshes, custom paths, magnetic/surface BZ, editing, and unrelated products.
- QueueWorkerRuntime, Tool Registry, PlanValidator, AnalysisPlan, artifacts, and backend job success semantics are unchanged. `phonon.animation` is consumed only through an exact existing mode binding.

## 2026-07-15 Phase 10I-2 Standalone Brillouin Product

- `structure.brillouin_zone` remains the unique recommended identity; no `structure.brillouin_zone_3d`, `structure.bz_viewer`, or reciprocal-viewer duplicate was added.
- The same adapter and six inert artifacts now have an application-owned lazy Three.js consumer. `renderer_included=false` remains accurate because renderer code is not embedded in the package.
- Mock Planner now routes explicit interactive/rotatable/3D Brillouin and reciprocal-axis requests to the canonical tool. Electronic/phonon calculation, trajectory, Fermi surface, Monkhorst-Pack mesh, magnetic/surface BZ, editing, XRD, and CrystalNN remain excluded.
- PlanValidator, QueueWorkerRuntime, input/params, providers, artifact versions, scientific caps, and network authority are unchanged.

## 2026-07-14 Phase 10I-1 Formal Brillouin Data Adapter

- Added one canonical identity: `structure.brillouin_zone` using `BrillouinZoneAdapter`; no overlapping `structure.kpath` or `structure.brillouin_zone_3d` tool is registered.
- Input is exactly one ordered, non-magnetic, 3D periodic `Structure`; params are closed to required artifacts, contract-default providers, time reversal, versioned tolerances, and no alternative variants.
- Outputs are `reciprocal_lattice_json`, `brillouin_zone_json`, `kpath_json`, `brillouin_zone_manifest_json`, `summary_md`, and `recipe_json` with exact Phase 10I contracts and hard caps.
- Mock Planner originally routed explicit BZ/reciprocal/k-path data generation only; Phase 10I-2 extends the same identity to interactive display intent while retaining scientific negative routes.
- QueueWorkerRuntime and PlanValidator semantics are unchanged. Artifacts contain no renderer, WebGL, executable content, external assets, or network authority.

## 2026-07-14 Phase 10I Brillouin Zone Contract

- Candidate `structure.brillouin_zone` is `PLANNED / NOT_REGISTERED / NOT_EXECUTABLE`.
- No Tool Registry manifest, adapter map, PlanValidator schema, QueueWorkerRuntime behavior, planner route, or API product was added.
- The contract family is inert JSON-only data. A future producer must bind a validated periodic structure, standardized primitive cell, local provider policy, exact hashes, and the Phase 10I security/cap contract before registration.
- Contract readiness does not imply a Brillouin-zone renderer, electronic/phonon calculation, user path editor, integration mesh, or reciprocal-space volumetric capability.

## 2026-07-14 Phase 10H-5 Formal Phonon Animation

- Added one canonical dynamic identity: `phonon.animation` using `PhononAnimationAdapter`.
- Requires exactly three unique role-bound inputs: `Structure`, `PhononBand`, and `PhononEigenvector`; a canonical 64-character mode ID is mandatory.
- Params are closed and bounded to phase/display/playback/supercell/vector/trail/bond/cell/axes controls. Output is `phonon_animation_json`, `phonon_animation_summary_json`, `phonon_animation_manifest_json`, and `recipe_json`.
- Mock Planner routes only explicit English/Chinese eigenmode animation intent when all compatible profile objects and mode ID exist. Calculation, thermal, trajectory, static viewer, Brillouin, XRD, editing, and video requests are excluded.
- Artifacts contain no renderer, frames, JavaScript, HTML, shader, URL, or remote asset. Existing static phonon and trajectory tool identities remain unchanged.

## 2026-07-14 Phase 10H-4 Eigenvector Contract Notes

- No Tool Registry entry, adapter, planner route, PlanValidator input, QueueWorkerRuntime behavior, API product, or frontend mode viewer was added.
- The eigenvector family is inert contract data bound to an existing canonical phonon band artifact.
- `phonon.band`, `phonon.dos`, and `phonon.band_dos` retain static product semantics and do not imply eigenvector availability.
- A future dynamic tool must pass an independent parser/adapter/animation/security/evidence phase and cannot execute artifact code or infer missing mass/phase semantics.

## 2026-07-14 Phase 10H-3 Combined Product Notes

- `phonon.band_dos` is the unique formal static combined product using `PhononBandDosAdapter`.
- It requires exactly one `PhononBand` and one `PhononDos` input with explicit `band`/`dos` roles; role order is irrelevant but duplicates and extra inputs are rejected.
- Params are closed to shared-domain/display/table/projection controls; outputs are six exact inert combined artifact types.
- Mock Planner routes explicit static combined band-plus-DOS intent only. Standalone band/DOS, eigenvector, animation, thermal, calculation, trajectory, and Brillouin requests remain separate.
- PlanValidator and QueueWorkerRuntime authority are unchanged; source artifact payloads are validated and hashed before composition.

## 2026-07-14 Phase 10H Phonon Contract

- No Tool Registry entry, adapter, planner route, PlanValidator capability, QueueWorkerRuntime behavior, or formal phonon product was added.
- Existing `phonon.band`, `phonon.dos`, and `phonon.band_dos` pymatviz inventory rows remain planning references only and do not gain execution authority from the new contract.
- A future producer must emit validated inert `phase10h.*` artifacts and pass a separate adapter/tool/security/evidence review before registration.

## 2026-07-13 Phase 10G-3 Formal Trajectory Viewer

- Added unique `structure.trajectory_viewer` using `TrajectoryViewerAdapter`, one validated `Trajectory` input, strict launch-only params, and the existing four inert trajectory JSON artifact types.
- Natural interactive trajectory requests route to the formal tool in English and Chinese; analytics, editing, dynamic-bond, URL/streaming, phonon, volumetric, and static-viewer requests are excluded.
- `structure.trajectory_import` remains the planner-hidden import identity, while `structure.viewer_3d` remains static. The identities are not aliases and do not share planner intent.
- Adapter provenance declares exact launch options, app-owned performance budgets, displayed-instance estimate, and capability truth. QueueWorkerRuntime preserves this metadata while retaining authority over plan/tool/call identity fields.
- The formal tool supports validated playback, picking/current-frame measurement, bounded renderer-local supercells, clipping/camera, and static-reference bonds at `PARTIAL_READY`; it does not claim dynamic bonds, trajectory analytics/editing, video export, or remote streaming.

## 2026-07-13 Phase 10G-1 Internal Import

- Added unique `structure.trajectory_import` using `TrajectoryImportAdapter`, `Trajectory` input, strict empty params, and four inert trajectory JSON artifact types.
- It is execution-stage registered so PlanValidator/QueueWorkerRuntime can validate it, but its description is planner-hidden and Mock Planner has no route.
- It does not represent formal trajectory viewer registration and emits no HTML, renderer, playback, JavaScript, or remote asset.

## 2026-07-13 Phase 10G Contract Boundary

- No Tool Registry entry, adapter, planner route, or runtime authority was added.
- The existing `trajectory.viewer` MatterViz manifest entry remains a V1 planning inventory item, not an executable product claim.
- Future trajectory producers must emit validated `phase10g.trajectory.v1` (or a separately reviewed chunked equivalent) before registration.
- Static `structure.viewer_3d` remains static and cannot be used to claim trajectory playback.

## 2026-07-13 Phase 10F-24

No Tool Registry change. `structure.viewer_3d` still emits canonical `phase10f18.viewer_scene.v2`; expansion is validated frontend view state and never a new adapter parameter, artifact topology, or structure resource.

## 2026-07-12 Phase 10F-15 Formal Viewer Notes

- `structure.viewer_3d` is the formal minimal interactive viewer identity.
- Its adapter is `StructureViewer3DAdapter`, implemented as a canonical `StructureViewerSceneAdapter` specialization.
- Artifacts are `structure_json`, `table_json`, `summary_md`, and `recipe_json`; `matterviz_html` is no longer declared or emitted.
- Params and resource limits match `structure.viewer_scene`: 256 sites, 2048 bonds, 32 species, and 1 MB JSON.
- Natural viewer prompts route to `structure.viewer_3d`; explicit inert scene JSON prompts route to `structure.viewer_scene`.
- `structure.viewer_scene_metadata` and `structure.viewer_export_package` remain explicit legacy direct-purpose tools.
- `structure.structure_3d` remains a separate static Plotly capability.
- Full scientific viewer, trajectory, phonon, Brillouin-zone, volumetric, and editing capability tags are not declared.

## 2026-07-11 Phase 10F-14 Renderer Foundation Notes

- No Tool Registry entry was added, removed or modified.
- `structure.viewer_scene` remains the only canonical `viewer_scene.v1` producer.
- The renderer is a frontend artifact consumer after canonical validation; it does not create execution authority.
- Existing Phase 10D `structure.viewer_scene_metadata` and `structure.viewer_export_package` remain registered and JSON-only in the new renderer surface.
- Formal `structure.viewer_3d` remains unregistered.
- Planner routing, PlanValidator, QueueWorkerRuntime, artifact storage and `/planner/jobs` semantics are unchanged.

## 2026-07-11 Phase 10F-13 Viewer Scene Live Adapter Evidence Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-13.
- `structure.viewer_scene` remains the canonical `viewer_scene.v1` adapter path.
- Live evidence confirms `structure.viewer_scene` executes through `planner_jobs`, persisted `AnalysisPlan`, `QueueWorkerRuntime`, Tool Registry lookup, and adapter artifact generation.
- Existing Phase 10D tools remain registered and unchanged:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Compatibility evidence confirms canonical prompts route to `structure.viewer_scene`, old metadata/export prompts route to old tools, and XRD/RDF/coordination/phonon/full-renderer prompts do not silently route to canonical viewer scene.
- No Tool Registry core semantics, QueueWorkerRuntime semantics, production runtime route, renderer dependency, WebGL, Three.js, MatterViz, artifact JavaScript, external API, real LLM path, phonon, or unsupported official PASS claim was added.

## 2026-07-11 Phase 10F-12 Viewer Scene Minimal Adapter Notes

- Added one Tool Registry entry:
  - `structure.viewer_scene`
- Registered adapter:
  - `StructureViewerSceneAdapter`
- Artifact types:
  - `structure_json`
  - `table_json`
  - `summary_md`
  - `recipe_json`
- Generated artifact names:
  - `viewer_scene.json`
  - `viewer_scene_manifest.json`
  - `summary.md`
  - `recipe.json`
- Params schema is strict and bounded to the Phase 10F contract caps.
- Existing Phase 10D tools remain registered and unchanged:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- `structure.viewer_scene` emits canonical `viewer_scene.v1` data, not the old `phase10d1.viewer_scene.v1` schema.
- Mock Planner routes only explicit inert viewer-scene JSON prompts to `structure.viewer_scene`.
- Full interactive viewer, WebGL, Three.js, MatterViz renderer, Brillouin-zone, phonon, RDF, XRD, and coordination prompts do not route to `structure.viewer_scene`.
- No Tool Registry core semantics, QueueWorkerRuntime semantics, production runtime route, renderer dependency, WebGL, Three.js, artifact JavaScript, external API, real LLM path, phonon, or unsupported official PASS claim was added.

## 2026-07-09 Phase 10F-9 Viewer Scene Contract Fixture Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-9.
- Phase 10F-9 implements inert `viewer_scene.v1` contract fixtures and an isolated validator only.
- The validator lives in `mdi_artifact_core` for contract replay tests; it does not register or activate `structure.viewer_3d`.
- Existing Phase 10D tools remain the only implemented viewer-scene-related runtime tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- No planner routing, Tool Registry runtime behavior, QueueWorkerRuntime behavior, runtime API route, renderer bundle, WebGL, Three.js, phonon, or unsupported official PASS claim was added.

## 2026-07-09 Phase 10F-8 Viewer Scene Contract Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-8.
- Phase 10F-8 plans an inert `viewer_scene` artifact contract only. It does not register or activate `structure.viewer_3d`.
- Existing Phase 10D tools remain the only implemented viewer-scene-related tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Historical `structure.viewer_3d` registry/adapter inventory remains unapproved for full implementation and is not evidenced by this phase.
- Future viewer-scene implementation must still execute through AnalysisPlan validation, `/planner/jobs`, QueueWorkerRuntime, Tool Registry lookup, params schema validation, adapter execution, artifact generation, and security checks.
- No Tool Registry main semantics, planner routing, runtime authority, renderer bundle, WebGL, Three.js, phonon, or unsupported official PASS claim was added.

## 2026-07-09 Phase 10F-7 Advanced Viewer Readiness Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-7.
- Existing static physics tools remain closed:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Existing Phase 10D static scene metadata/export tools remain the safe baseline for inert scene artifacts:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Historical `structure.viewer_3d` registry/adapter inventory exists, but Phase 10F-7 does not activate, extend, evidence, or approve full viewer implementation.
- Future viewer work must first harden an inert `viewer_scene.json` contract before any renderer implementation.
- Renderer implementation, WebGL, Three.js, renderer bundles, and phonon remain future scope and require explicit approval.
- No Tool Registry main semantics, runtime authority, planner routing, full viewer implementation, WebGL renderer, Three.js integration, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-6 Fixture Evidence Closure Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-6.
- Existing static physics tools remain:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Phase 10F-6 closes fixture-pack replay evidence only. It does not change registry schemas, planner routing, adapter behavior, or runtime authority.
- Fixture-pack PASS remains distinct from official PASS; all replayed cases use `internal_regression` provenance and all official PASS claims remain false.
- Recommended Phase 10F-7 registry-related work is readiness planning for a future viewer capability, not registering or implementing a new viewer tool.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-5 Fixture Replay Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-5.
- Fixture-pack replay validated the existing registry-gated tools:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Replay selected the expected tool for each fixture and generated the expected artifacts.
- Candidate replay values were added to expected contracts without promoting any case to official PASS.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-4 Fixture Pack Construction Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-4.
- Existing static physics tools remain:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Phase 10F-4 constructs a candidate fixture pack only. The pack references the existing tools and expected artifact names but does not alter registry schemas, planner routing, adapter behavior, or runtime authority.
- Future Phase 10F-5 replay must still execute through AnalysisPlan validation, `/planner/jobs`, QueueWorkerRuntime, Tool Registry lookup, params schema validation, adapter execution, artifact generation, and security checks.
- All fixture-pack official PASS claims remain false; `internal_regression` cases are regression candidates, not official examples PASS evidence.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-3 Fixture Pack Planning Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-3.
- Existing static physics tools remain:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Phase 10F-3 is fixture-pack planning only. It defines candidate fixture categories, provenance labels, expected-contract templates, numeric tolerance policy, and a future replay protocol.
- Future fixture replay must still execute through AnalysisPlan validation, `/planner/jobs`, QueueWorkerRuntime, Tool Registry lookup, params schema validation, adapter execution, artifact generation, and security checks.
- `official_like_curated` and `internal_regression` fixtures must not be promoted to official PASS evidence without eligible provenance and direct platform replay.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-2 Official Coverage Gap Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-2.
- Existing static physics tools remain:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Phase 10F-2 is coverage-gap planning only. It proposes future direct-uploadable static physics fixture and expected-contract policies but does not execute those fixtures.
- No official static physics PASS claim was added.
- Future official PASS evidence must still run through AnalysisPlan validation, `/planner/jobs`, QueueWorkerRuntime, Tool Registry lookup, params schema validation, adapter execution, artifact generation, and security checks.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F-1 Official Verification Notes

- No Tool Registry entries were added, removed, or modified in Phase 10F-1.
- Existing static physics tools remain:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- The official examples benchmark pack currently has no direct-uploadable case that maps to these three tools, so no official static physics PASS evidence was claimed.
- The two existing direct-verified official cases are table/ML/composition cases and do not alter static physics registry status.
- Structure-adjacent README/widget/Brillouin/phonon cases remain mapping/future/extraction references only.
- Future official PASS evidence for static physics must still execute through AnalysisPlan validation, `/planner/jobs`, QueueWorkerRuntime, Tool Registry lookup, params schema validation, adapter execution, artifact generation, and security checks.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or unsupported official example PASS claim was added.

## 2026-07-09 Phase 10F Static Physics Closure Notes

- The static structure physics family is closed at the registry/evidence level for:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- All three tools remain registry-gated `structure` tools with strict params schemas, bounded resource limits, deterministic static artifacts, summaries, and recipes.
- Mock Planner routing covers each static physics intent and preserves negative-routing boundaries for full viewer, WebGL, Brillouin-zone, phonon, advanced environment classification, and experimental fitting prompts.
- The recommended next registry-related work is direct official-example verification, not new tool registration.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, or official example PASS claim was added in Phase 10F.

## 2026-07-09 Phase 10E-8 RDF Evidence Notes

- `structure.rdf` remains registered as an MVP `structure` tool with static artifacts only.
- Evidence lives under `docs/phase10e/browser_api_evidence/phase10e8_rdf/`.
- Evidence confirms registry-gated execution and static artifact generation for `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Browser evidence confirms real frontend static viewing through Artifact Gallery and report/recipe previews. `rdf_plot.json` remains static chart JSON; rendered line chart UI is deferred.
- No Tool Registry main semantics, runtime authority, full viewer, WebGL renderer, Three.js, phonon, experimental fitting, or official example PASS claim was added.

## 2026-07-07 Phase 10C-1 Lightweight Structure Tool Notes

- Registered the Phase 10C-1 lightweight structure tool set:
  - `structure.summary`
  - `structure.lattice_summary`
  - `structure.spacegroup_summary`
  - `structure.composition_from_structure`
  - `structure.preview_metadata`
- All five tools use the `structure` domain, platform builtin implementation
  source, strict params schemas, bounded resource limits, deterministic artifact
  names, and JSON + `summary.md` + `recipe.json` outputs.
- Structure inputs are resolved only from platform-passed resources: pymatgen
  Structure objects, pymatgen Structure dict/JSON, normalized structure dicts,
  CIF text, POSCAR/CONTCAR text, or small collections of those resources.
  Adapters do not read arbitrary filesystem paths.
- `structure.spacegroup_summary` uses pymatgen/spglib when available. If the
  symmetry stack is unavailable or detection fails, the adapter reports typed
  dependency/detection errors or warnings; it must not fabricate `P1`,
  `Fm-3m`, or any other space group.
- Mock Planner structure routing runs before generic composition/table/viz
  routing. Explicit 3D viewer requests remain future-scope and are not treated
  as support for `structure.viewer_3d`.
- Phase 10C-1 evidence under `docs/phase10c/adapter_evidence/` is adapter-level
  only. Browser/API evidence is deferred to Phase 10C-2.
- No new tool may bypass AnalysisPlan validation, Tool Registry lookup, params
  schema validation, QueueWorkerRuntime, or Adapter execution.

## 2026-07-06 Phase 10C lightweight structure planning notes

- Phase 10C is planning-only and does not add, remove, or modify Tool Registry entries.
- Current evidence-grade adapter coverage includes table/viz first-batch tools and composition visualization tools. Structure tools remain a planning target until Phase 10C-1 implements and tests them.
- Recommended Phase 10C-1 tool scope: `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- Planned structure tools must use the `structure` domain, strict params schemas, bounded resource limits, deterministic artifact names, and the existing registry-gated execution path.
- Planned outputs should be JSON + `summary.md` + `recipe.json`; 3D HTML viewers and physics plots are deferred.
- No future structure adapter may execute shell, arbitrary Python, network calls, uncontrolled filesystem reads/writes, or browser-side execution.
- Mapping-only README structure demos and future-scope phonon/Brillouin/XRD/RDF examples must not be marked as PASS until real inputs and evidence exist.

## 2026-07-06 Phase 10B composition visualization planning notes

- Phase 10B is planning-only and does not add, remove, or modify Tool Registry entries.
- Current registry already contains several composition and structure/physics tools beyond the Phase 10A evidence baseline. Phase 10B separates registered tools from evidence-grade tools.
- Phase 10A evidence-grade tools remain `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- Phase 10B-1 is recommended to harden/productize composition visualization tools through the same registry-gated path: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Recommended Phase 10B-1 tool scope: `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- No future adapter may execute shell, arbitrary Python, network calls, uncontrolled filesystem reads/writes, or direct browser-side execution.
- Mapping-only README demos and extraction-required notebooks/scripts must not be marked as PASS until they have real inputs and evidence.

## 2026-07-06 Phase 10A-2 first-batch browser/API evidence notes

- The six Phase 10A-2 evidence scenarios all execute through the existing registry-gated path: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- `viz.scatter` and `viz.histogram` now export Plotly JSON artifacts with benchmark-facing metadata at the top level and the raw Plotly figure under `figure`. This keeps artifacts renderable while making evidence assertions deterministic.
- Mock Planner routing now checks composition-intent prompts before the generic histogram/distribution route, so Ward composition prompts select `composition.summary` instead of `viz.histogram`.
- No adapter executes shell, arbitrary Python, network calls, or uncontrolled filesystem writes.
- No real LLM is required for this evidence path, and default CI still does not call live providers.
- The official browser/API evidence is scoped to MatPES and Ward first-batch adapter scenarios. It must not be read as verification for extraction-required, mapping-only, or future-scope official examples.

## 2026-07-06 Phase 10A-1 first official table/viz adapter batch

- Added five registry-gated tools for the first two `DIRECT_VERIFIED` official pymatviz cases:
  `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- `table.distribution_summary` accepts a normalized DataFrame (`ml_table`) and emits `table_json`, `summary_md`, and `recipe_json` artifacts. It reports quantile distribution summaries, missing rates, categorical top values, recommended visualizations, and warnings.
- `viz.scatter` and `viz.histogram` use deterministic Plotly exports and emit named `plotly_json` / optional `plotly_html` artifacts plus summary and recipe artifacts.
- `viz.correlation` emits both `correlation_matrix.json` (`table_json`) and Plotly heatmap artifacts for numeric correlation analysis.
- `composition.summary` safely summarizes formula/composition columns only when such a column is present; it records parsed/failed formula counts and element/system summaries.
- Tool Registry manifests and params schemas are the enforcement boundary. The Mock Planner may route prompts to these tools, but PlanValidator still validates tool ID and params before persistence.
- Execution remains: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- No adapter executes shell, Python snippets, network calls, or arbitrary filesystem paths. No real LLM call is needed for these tools.

## 2026-07-05 Phase 9D live provider validation tightened params schema enforcement

- Phase 9D live verification showed that real provider output can select an allowed tool but still use invalid parameter aliases.
- PlanValidator now validates every step's `params` against the selected RegisteredTool `paramsSchema` before persistence, job creation, or enqueue.
- This is a Tool Registry boundary, not prompt trust: the planner prompt now lists allowed param names to guide models, but schema validation is the enforced rule.
- Valid live jobs still follow the registry-gated path: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- The Phase 9D evidence confirms a live Gemini plan executed through `ml.basic_metrics` and produced `metrics.json` / `summary.md` without secrets in JobEvent, Artifact, AnalysisPlan, or evidence files. The final gated full-chain verification passed with Gemini 3 Flash Preview.

## 2026-07-05 Phase 9D LLM config repair keeps execution registry-gated

- The Phase 9D repair changes provider configuration resolution, provider status reporting, UI status display, and gated live test coverage only.
- No Tool Registry manifest, adapter, PlanValidator rule, QueueWorkerRuntime behavior, or `/planner/jobs` persistence/enqueue semantics changed.
- Live provider output still must be JSON AnalysisPlan, then PlanValidator must approve it before persistence.
- Valid jobs still follow: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Secret/API key values remain prohibited in prompts, plans, JobEvents, Artifacts, Reports, Recipes, UI browser storage, and test output.

## 2026-07-05 Phase 9C UI redesign does not change the Registry gate

- The Phase 9C docs update changes frontend information architecture only.
- The Phase 9C implementation also changes frontend information architecture only: top dataset/model dialogs, left data-context viewer, and main Agent/conversation/results tabs.
- No Tool Registry manifest, adapter implementation, tool scope, PlanValidator rule, QueueWorkerRuntime behavior, provider behavior, or `/planner/jobs` persistence/enqueue semantics changed.
- The new UI may show Agent process, conversation/Plan, and results/export as main workspace tabs, but it must not create a browser-side execution path.
- Valid jobs still follow: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Developer mode may reveal tool IDs, step IDs, plan IDs, plan hash, raw AnalysisPlan JSON, safe JobEvent payloads, and API responses, but Secret/API key values remain prohibited in UI storage, prompts, JobEvents, Artifacts, Reports, Recipes, and export packages.

## 2026-07-05 Phase 9B - table.numeric_summary added for semantic table summaries

- Added `table.numeric_summary` as an MVP platform builtin tool with `NumericSummaryAdapter`.
- The tool accepts a normalized DataFrame (`ml_table`) and emits `table_json`, `summary_md`, and `recipe_json` artifacts. The primary browser evidence artifact is `numeric_summary.json`.
- This tool is for descriptive table statistics. It prevents non-regression tables such as Ward metallic glasses from being forced through `ml.basic_metrics` with arbitrary target/prediction columns.
- Execution remains registry-gated: Mock Planner emits AnalysisPlan JSON, PlanValidator validates the registered tool and params schema, QueueWorkerRuntime loads the persisted plan by `job.plan_id`, and Adapter execution writes ToolCall/Artifact/Result provenance.
- MatPES remains a valid `ml.basic_metrics` case because the request is explicitly PBE vs r2SCAN numeric comparison.

## 2026-07-04 Phase 9B - MatPES blocker repair keeps execution registry-gated

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this repair.
- The fix only changes Mock Planner parameter binding for `ml.basic_metrics`: it derives target/prediction params from the real DataProfile when available, then emits normal AnalysisPlan JSON.
- PlanValidator remains the enforced boundary before persistence; the plan is still persisted as an AnalysisPlan, bound by `jobs.plan_id`, loaded by QueueWorkerRuntime, and executed through Tool Registry lookup plus the `ml.basic_metrics` adapter.
- The repaired browser evidence proves `matpes_atomic_energies_csv` now executes one registry-approved `ml.basic_metrics` ToolCall with params `targetColumn=PBE` and `predictionColumn=r2SCAN`, creates one `metrics_json` artifact, and reaches `job.completed`.

## 2026-07-04 Phase 9B - durable worker object loading keeps execution registry-gated

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this closure.
- `DurableObjectStoreResolver` reconstructs dataset objects only. It does not select tools, alter persisted AnalysisPlans, bypass PlanValidator, or execute code.
- The settings-driven `run_queued_job(job_id)` path still calls `QueueWorkerRuntime.handle_job(job_id)`, loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, and executes each step through Tool Registry lookup and Adapter execution.
- The new regression proves an out-of-process-style worker can load `ml_table` from persisted normalized exports and execute exactly one `ml.basic_metrics` ToolCall through the real adapter.
- Browser verification showed the UI provenance chain still reports `Loaded from persisted AnalysisPlan`, `Executed through Tool Registry + Adapter`, and `No deterministic fallback used`.

## 2026-07-04 Phase 9B - runtime data binding still preserves the Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this follow-up.
- Dataset object-store resolution is an input-binding step before tool execution. It supplies normalized objects such as `ml_table`, `structures`, and `formulas` to the worker; it does not select tools, mutate the persisted plan, or execute outside the registry.
- The local in-memory auto-drain path still calls `QueueWorkerRuntime.handle_job(job_id)`, which loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, emits `plan.loaded`, then executes each step through Tool Registry lookup and Adapter execution.
- The new inputRef validation rejects missing or unresolved uploaded-dataset references before AnalysisPlan persistence, Job creation, or enqueue. It strengthens the existing PlanValidator boundary for executable dataset binding.
- The uploaded CSV regression proves the persisted one-step `ml.basic_metrics` plan produces exactly one ToolCall through the adapter path, with `data.loaded` and `plan.loaded` provenance.
- Production Redis/service-backed execution remains the authoritative Phase 8B path; this follow-up only adds a local development/demo auto-run behavior and a resolver seam for dataset objects.

## 2026-07-04 Phase 9B - demo workspace still routes execution through Planner validation and Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 9B.
- The new UI surfaces provider settings, dataset/profile selection, demo workflow, error explanations, artifacts, reports, and developer audit data; it does not create a frontend execution path.
- Planner jobs are still created only through `/planner/jobs`, and invalid plans still fail before AnalysisPlan persistence, Job creation, or queue enqueue.
- Provider connection tests may parse and validate a sample AnalysisPlan, but they do not execute tools, write ToolCalls, create Artifacts, or bypass PlanValidator.
- Demo dataset/profile support feeds the existing Phase2 runtime data/profile path. It does not allow the frontend to fabricate successful persisted plans or execution results.
- A valid planner job still follows the existing path: JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> Artifact/Result provenance.
- API keys are resolved server-side by `secretId` for provider tests and planner calls; they must never appear in ToolCall params, JobEvents, Artifacts, Recipes, Reports, or exported provenance.
- The Phase 9B follow-up only added browser CORS handling, safe runtime health probes, i18n cleanup, and invalid-plan response redaction. It did not change Tool Registry manifests, adapter routing, tool scope, or the persisted-plan execution gate.
- When PlanValidator rejects a credential-bearing plan, `/planner/jobs` now omits the rejected raw plan from the response, so credential-like params do not leak back to the browser or become pseudo-provenance.

## 2026-07-03 Phase 9A - true provider still stops at PlanValidator and Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 9A.
- The OpenAI-compatible provider only returns structured planner JSON. It cannot execute Python, shell, filesystem, network, or adapter actions.
- Provider output must parse as JSON and construct an `AnalysisPlan`, then pass PlanValidator before `/planner/jobs` can persist a plan, create a job, or enqueue work.
- Unknown tools, V1/V2/non-MVP tools, duplicate steps, empty steps, and credential-like params remain rejected before persistence and before any Tool Registry/Adapter execution.
- A valid true-provider plan still follows the Phase 8B path: persisted `AnalysisPlan` -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> Artifact/Result provenance.
- Provider failures and validation failures return safe errors and create no ToolCall, Artifact, JobEvent execution record, or queue message.

## 2026-07-03 Phase 8C-P1 - UX closure keeps Registry-gated execution unchanged

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8C-P1.
- The new EventSource timeline only replays persisted JobEvents; it does not create an execution path and does not bypass Tool Registry validation.
- The new Report/Recipe Summary panel displays existing ToolCall/Artifact/Result provenance (`planId`/`planHash`) and does not synthesize execution records.
- The Dataset/Profile selector only improves data-context entry. It does not allow the frontend to create or mutate persisted AnalysisPlans.

## 2026-07-03 Phase 8C - frontend displays Registry-gated execution provenance

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8C.
- The Planner workbench displays "Executed through Tool Registry + Adapter" as provenance text for persisted-plan jobs; it does not introduce a frontend execution path.
- Read-only planner APIs expose recorded ToolCall, Artifact, JobEvent, and Result provenance so the UI can show `planId`/`planHash` without bypassing registry validation.
- The frontend still creates work only through `/planner/jobs`; validation remains server-side and must pass before any plan is persisted or any job is created.
- The validation-failure UI explicitly states that no AnalysisPlan was saved, no Job was created, and nothing was enqueued.
- Deterministic fallback remains a dev/test fallback only for jobs without a persisted plan; Phase 8C does not reclassify fallback as a normal product path.

## 2026-07-03 Phase 8B - persisted plan execution still uses the Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8B.
- Phase 8B changed where the validated plan is stored and loaded from: `/planner/jobs` persists the exact validated `AnalysisPlan`, and `QueueWorkerRuntime` loads it by `job.plan_id`.
- Execution is still controlled by the same path: persisted `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- The persisted 1-step test proves `toolId=ml.basic_metrics` and `stepId=llm_step_1` come from the persisted plan and produce exactly 1 ToolCall, not the deterministic 5-tool fallback.
- The Phase 8B targeted suite now includes a real adapter regression for persisted-plan execution, and CI run `28631817086` proved the same path against PostgreSQL + Redis + MinIO with 19 integration tests passed and 0 skipped.
- Unknown tools, V1/V2/non-MVP tools, duplicate steps, empty steps, and credential-like params are still rejected by PlanValidator before the plan can be saved or enqueued.
- Explicit worker fallback with caller-provided `plan` remains only for dev/test jobs that have no persisted `plan_id`; it is not the Phase 8B service-backed acceptance path.

## 2026-06-27 Phase 8A — validated plan executes through the same Registry gate

- No Tool Registry manifest, adapter, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8A.
- Phase 8A only changed the *source* of the plan executed by `create_job`: a validated LLM AnalysisPlan can now be the execution plan instead of the deterministic one. The execution path is unchanged — every step still goes through `run_tool_call_job` → Tool Registry lookup → paramsSchema validation → Adapter.
- The validated LLM plan still cannot reference unknown or non-MVP tools: `PlanValidator` (Phase 7) rejects them before any job is created. The Tool Registry remains the single execution gate.

## 2026-06-27 Phase 7 LLM Planner — Tool Registry as Execution Gate

- The LLM JSON Planner can ONLY select tools that exist in the Tool Registry. `PlanValidator` (in `packages/tool-registry/mdi_tool_registry/plan_validator.py`) rejects any `step.toolId` not present in `registry.tools` with `UNKNOWN_TOOL`.
- The LLM planner is restricted to **MVP-stage tools only**. `PlanValidator` rejects any tool whose `stage != "mvp"` with `NON_MVP_TOOL`. V1/V2 tools cannot be planned even if they exist in the registry.
- The planner prompt (`services/llm/mdi_llm/planner_prompt.py`) only lists MVP tools to the LLM, but the prompt is advisory — the Tool Registry + PlanValidator are the enforced execution gate, not the prompt.
- No new Tool Registry manifest, adapter, MVP/V1/V2 tool scope, or pymatviz API mapping changed in Phase 7. The planner is a new caller of the existing registry, not a registry change.
- The controlled execution path is unchanged and still mandatory:
  `LLM AnalysisPlan` -> `PlanValidator` -> (job creation) -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- `params` containing credential-like keys (api_key/token/password/secret/credential/authorization) are rejected at the validator level (`CREDENTIAL_IN_PARAMS`) before any tool runs.

## 2026-06-26 Phase 6 Service-backed Runtime Smoke Notes (Final)

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 6.
- The service-backed product-loop integration test (`test_phase6_service_backed_product_loop`) was upgraded from fake executor to real Tool Registry + BasicMetricsAdapter execution via `execute_tool_request()`. A small in-memory DataFrame provides the regression input so no external fixture file is needed. All adapter validation (manifest paramsSchema check, Tool Registry lookup, adapter class instantiation) runs in the real path.
- The fake executor (`_fake_tool_executor`) remains available in the test file as a helper but is no longer used in the product-loop smoke test — it serves queue retry and idempotency tests where deterministic artifact shape matters more than adapter correctness.
- The product-loop smoke covers `ml.basic_metrics` through the same controlled execution path as the Phase 2/3/4/5 deterministic local tests:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Future phases that add real LLM or V1/V2 tools must extend the service-backed integration test to include those adapters through the same `execute_tool_request()` path.

## 2026-06-26 Phase 5 Runtime Infrastructure Notes

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 5.
- The new `QueueWorkerRuntime` default execution path still constructs a `ToolExecutionRequest` and calls `execute_tool_request`, preserving:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Phase 5 queue tests use an injected fake executor only to validate queue retry/idempotency behavior without requiring real object inputs or rendering. This is a test seam, not a production bypass.
- Runtime infrastructure changes are limited to PostgreSQL configuration, queue dispatch/handler shape, JobEvent seq locking, and MinIO/S3 artifact object storage.
- No real LLM output, direct arbitrary Python/shell/filesystem/network execution by the Agent, V1/V2 tool execution, or direct pymatviz wrapper surface was introduced.

## 2026-06-26 Phase 4 Production Persistence Hardening Notes

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 4.
- The controlled execution path remains:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Phase 4 only hardens persistence around the existing ToolCall and Artifact records: status validation, idempotent ToolCall writes, idempotent Artifact metadata writes, and transaction rollback behavior.
- The Phase 2 deterministic product loop still proves the same five registered MVP tools for the mixed CIF/POSCAR/CSV path; no real LLM output or direct executable action was introduced.
- Future queue workers must keep Tool Registry validation before writing ToolCall state and must not use the new repository idempotency hooks as a bypass around manifest validation.

## 2026-06-26 Phase 3 Persistence Foundation Notes

- No Tool Registry manifest, adapter class, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 3.
- Phase 3 repository and storage work preserves the controlled execution path:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- The Phase 2 deterministic product loop still selects the same five registered MVP tools for the mixed CIF/POSCAR/CSV path:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Phase 3 acceptance hardening did not change any manifest or adapter behavior; the product-loop regression still proves the same registry-approved MVP tool path.
- Artifact persistence now has local and S3/MinIO mapping metadata plus signed-url placeholder behavior, but registered visualization/analysis tools still produce artifacts through the existing adapter/exporter path.
- No V1/V2 tool execution, direct pymatviz exposure, real LLM tool execution, or bypass around Tool Registry validation was introduced.

## 2026-06-25 Phase 2 Acceptance Audit Notes

- Re-verified manifest loading from `tool_registry/pymatviz_manifest.yaml`, `tool_registry/matterviz_manifest.yaml`, and `tool_registry/platform_builtin_manifest.yaml`.
- The merged registry reports version `0.1.0` and 10 MVP tools.
- Phase 2 deterministic planning still uses only registered MVP tools:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Phase 2 generated `AnalysisPlan.expectedArtifacts` now follows the shared schema `{name, type, fromStepId}`.
- Phase 2 generated Recipe steps now include `toolVersion` and `inputBindings: Record<string, string>`.
- Shared Python/TypeScript schemas now expose named `ExpectedArtifact` and `VisualizationRecipeStep` types.
- No V1/V2 tool execution, direct pymatviz exposure, or LLM-directed executable action was introduced.

## 2026-06-25 Phase 2 Product Loop Notes

- The Phase 2 deterministic planner uses only registered MVP tools and does not introduce any V1/V2 tool execution.
- The default mixed CIF/POSCAR/CSV path selects five tools:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Every Phase 2 executable step is converted to `ToolExecutionRequest` and executed through:
  Tool Registry lookup -> artifact type validation -> paramsSchema validation -> adapter registry -> Adapter execution.
- No new pymatviz, MatterViz, Plotly, or platform-builtin API signature mismatch was found during this round.
- Job-level `analysis_plan_json`, `recipe_json`, `report_md`, and `report_html` artifacts are generated by platform system tool IDs and do not bypass Adapter execution for registered visualization/analysis tools.
- The local API can query ToolCall, JobEvent, Artifact, Recipe, and Report records from in-memory/local-file state. Durable PostgreSQL/MinIO state remains a later phase.

## 2026-06-25 Phase 1 Acceptance Notes

- All 10 MVP tools are now exercised in the Phase 1 product-flow acceptance test through Tool Registry + Adapter + Worker runtime.
- No new pymatviz API signature mismatch was found during this round.
- `preview_png` behavior changed from optional omission to deterministic artifact generation:
  when Plotly/Kaleido image export is unavailable, the adapter export helper writes a minimal valid PNG fallback.
- `structure.viewer_3d` keeps the existing graceful fallback contract:
  if `pymatviz.StructureWidget.to_html()` is unavailable or fails, the adapter writes sandbox-safe `matterviz_html` fallback content and records fallback provenance.
- The Phase 1 demo planner requests only registered artifact types from each tool manifest and uses the same `paramsSchema` validation path as normal execution.
- The runtime-generated Analysis Plan is deterministic and local; it is not a real LLM output and does not bypass the "Agent JSON Plan only" rule.

## External Capability Baseline

官方来源核对基线：

- pymatviz：materials informatics visualization toolkit；当前规划基线按 `0.18.x`、Python `>=3.11` 处理，正式实现前需要再次锁版本。
- pymatviz 输出以 Plotly Figure、HTML、图片、widget/export 为核心。
- MatterViz / anywidget 路线用于更接近浏览器原生的 3D 结构、轨迹和交互材料 UI。
- 平台不直接暴露 pymatviz 原始函数给 Agent；必须通过 Tool Registry + Adapter。
- `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md` 是 pymatviz 原始能力到平台 Tool ID 的能力清单。
- `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md` 是 Adapter 实现顺序、接口和测试要求基线。

## Manifest-based Registry Baseline

正式实现时，Tool Registry 的首批工具来源为：

| Manifest | 作用 |
|---|---|
| `tool_registry/pymatviz_manifest.yaml` | pymatviz / pymatviz-composed capabilities such as `ptable_heatmap`, `structure_3d`, `coordination_hist`, and `density_scatter` |
| `tool_registry/matterviz_manifest.yaml` | MatterViz / widget 能力，例如 `StructureWidget` 和 `TrajectoryWidget` |
| `tool_registry/platform_builtin_manifest.yaml` | 平台内置分析和自定义 Plotly 能力，例如 `basic_metrics`、`outlier_table`、`error_distribution` |

每个 manifest tool entry 必须能映射到共享 Schema 中的 `RegisteredTool`，并保留：

- `tool_id`
- `implementation_source`
- `adapter`
- `display_target`
- `artifact_types`
- `stage`
- source package / source function / source class，如适用

`stage` 必须使用共享 Schema 允许的值：`mvp`、`v1`、`v2`。跨阶段探索能力不得写成组合枚举；例如 `structure.chem_env_sunburst` 默认登记为 `v2`，late V1 exploratory 只写入 `notes`。

## MVP Tool Source Split

| MVP Tool ID | Source |
|---|---|
| `composition.ptable_heatmap` | pymatviz `ptable_heatmap` |
| `composition.elements_hist` | pymatviz `elements_hist` |
| `composition.chem_sys_treemap` | pymatviz `chem_sys_treemap` |
| `structure.structure_3d` | pymatviz `structure_3d` |
| `structure.viewer_3d` | MatterViz / pymatviz `StructureWidget` |
| `structure.coordination_hist` | deterministic distance-cutoff static coordination histogram |
| `ml.density_scatter` | pymatviz `density_scatter` |
| `ml.error_distribution` | platform `plotly_custom` |
| `ml.basic_metrics` | platform builtin |
| `ml.outlier_table` | platform builtin |

## Initial Categories

### composition

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.cluster_2d`
- `composition.cluster_3d`

### structure

- `structure.viewer_3d`
- `structure.structure_3d`
- `structure.rdf`
- `structure.xrd`
- `structure.coordination_hist`
- `structure.spacegroup_bar`

### trajectory

- `trajectory.viewer`
- `trajectory.energy_curve`
- `trajectory.force_curve`

### phonon

- `phonon.band`
- `phonon.dos`
- `phonon.band_dos`

### ml

- `ml.parity_plot`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`
- `ml.uncertainty_calibration`
- `ml.confusion_matrix`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## Accepted Data Forms

| 数据类别 | 典型 Python 形式 | 平台标准化目标 |
|---|---|---|
| 化学式 / 组成 | string formula、`pymatgen.Composition` | `Composition[]`、formula column |
| 晶体结构 | `pymatgen.Structure`、`IStructure`、`ASE Atoms`、`PhonopyAtoms` | `Structure[]` + structure metadata |
| 结构文件 | CIF、POSCAR、CONTCAR、JSON limited | parsed structure collection |
| 表格数据 | `pandas.DataFrame` | typed dataframe + inferred field roles |
| 数值数组 | numpy/list/Series | metric arrays or chart series |
| 声子数据 | pymatgen / phonopy band、DOS objects | phonon band/DOS profile |
| 轨迹数据 | ASE traj、EXTXYZ、pymatgen trajectory JSON、XDATCAR | trajectory frames + per-frame properties |
| 模型结果 | `y_true`、`y_pred`、`y_std`、labels、probabilities | ML evaluation dataset |

## Data to Visualization Mapping

| 输入 | Tool IDs | 产物 |
|---|---|---|
| 化学式列表 | `composition.ptable_heatmap`、`composition.elements_hist`、`composition.chem_sys_treemap` | 周期表热力图、元素直方图、化学体系 treemap |
| 化学式 + 性质 | `composition.cluster_2d`、`composition.cluster_3d` | 组成嵌入 2D/3D 聚类图 |
| Structure collection | `structure.structure_3d`、`structure.viewer_3d`、`structure.spacegroup_bar` | Plotly 3D、MatterViz 3D、空间群分布 |
| Structure + local geometry | `structure.rdf`、`structure.xrd`、`structure.coordination_hist` | RDF、XRD、配位数分布 |
| Structure + force/magmom | `structure.structure_3d`、`trajectory.viewer` | 带向量箭头结构图、轨迹/优化过程 |
| phonopy / pymatgen phonon | `phonon.band`、`phonon.dos`、`phonon.band_dos` | 声子能带、声子 DOS、组合图 |
| `y_true` / `y_pred` | MVP：`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`；V1：`ml.parity_plot` | density scatter、误差分布、指标、离群表 |
| `y_true` / `y_pred` / `y_std` | `ml.uncertainty_calibration` | 不确定性校准、error decay |
| 分类标签 | `ml.confusion_matrix` | 混淆矩阵、分类指标图 |

## MVP Tool Set

MVP 优先封装以下工具，保证“结构数据 + 预测结果表格”两条核心路径闭环：

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `structure.structure_3d`
- `structure.viewer_3d`
- `structure.coordination_hist`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`

V1/V2 再扩展：

- `structure.rdf`
- `structure.xrd`
- `structure.spacegroup_bar`
- `composition.cluster_2d`
- `composition.cluster_3d`
- `ml.parity_plot`
- `phonon.band`
- `phonon.dos`
- `trajectory.viewer`
- `ml.uncertainty_calibration`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## 3D Rendering Routes

| 路线 | 适用场景 | 产物 |
|---|---|---|
| Plotly `structure_3d` | 快速结构图、图表卡片、HTML 交互图 | MVP：Plotly JSON、HTML、PNG preview；V1：SVG/PDF 论文图 |
| MatterViz `StructureWidget` | 浏览器结构查看、交互检查、材料 Viewer | viewer HTML、metadata、optional snapshot |
| MatterViz `TrajectoryWidget` | MD / relaxation 轨迹、帧属性曲线、force vectors | V1：trajectory HTML、optional snapshot、per-frame metadata |

所有 3D 工具必须支持结构大小分级策略：小结构完整显示，中结构默认减少 bonds，大结构启用 LOD / 抽样 / 手动展开，trajectory 默认抽帧。

## Tool Schema Draft

Phase 6 已将 Tool Schema 固化到 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`，共享枚举和跨模块类型收敛到 `docs/13_SHARED_SCHEMA_SPEC.md`。后续实现以这两个文档为准。

```ts
type RegisteredTool = {
  toolId: string;
  name: string;
  category: ToolCategory;
  domain: ToolDomain;
  implementationSource: ImplementationSource;
  description: string;
  version: string;
  adapter: string;
  inputSchema: ToolInputSchema; // uses inputOptions OR semantics
  paramsSchema: Record<string, unknown>;
  artifactTypes: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  timeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
};
```

## Artifact Requirements

每个工具输出不只保存最终图，还要保存复现与审计所需材料：

| Artifact | 说明 |
|---|---|
| `figure.json` | Plotly Figure JSON 或等价结构化图表描述 |
| `figure.html` | 可交互 HTML |
| `preview.png` | 卡片预览图 |
| `figure.svg` / `figure.pdf` | 论文/报告导出，V1 |
| `viewer.html` | MatterViz / 3D viewer HTML |
| `metadata.json` | MatterViz viewer 元数据 |
| `structure.json` | 标准化结构或结构引用 |
| `metrics.json` | MAE、RMSE、R2、error stats 等结构化指标 |
| `table.json` | outlier table、failed files、quality issues 等小表 |
| `table.csv` | 用户下载表格 |
| `quality_issues.json` | 解析失败、字段问题、结构质量问题 |
| `summary.md` | 图表解释、数据来源、关键参数 |
| `recipe.json` | 复现该工具调用的输入引用、参数、版本 |

## Agent Display Contract

前端展示的是结构化可审计过程，不展示 LLM 原始隐藏思维链：

```text
Data Detection -> Data Quality -> Plan Generated -> Tool Started -> Artifact Ready -> Result Explanation
```

每个 ToolCall 至少展示：

- 为什么选择该工具。
- 使用哪些输入数据。
- 关键参数是什么。
- 输出了哪些 Artifact。
- 是否命中缓存。
- 是否有 Warning / Error。

## Open Tool Design Issues

- V1 是否将 pymatviz 函数签名半自动转换为 Tool Schema？
- V1 phonon、trajectory 工具的首批 Tool ID 如何排序？
- V2 VASP、LAMMPS 工具的首批 Tool ID 如何排序？
- Expert 模式是否允许用户编辑 Recipe 和受限 Python 代码片段？

## Implementation Notes 2026-06-25

### Verified Runtime Versions

本轮以当前可安装运行版本核对前三个 Adapter：

| Package | Version |
|---|---|
| `pymatviz` | `0.18.0` |
| `pymatgen` | `2026.5.4` |
| `ase` | `3.29.0` |
| `plotly` | `6.8.0` |

为兼容当前全局环境的 NumPy 2.x，还升级了 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely` 和 `scikit-image`。后续建议改为项目专用 virtualenv/lockfile。

### API Signature Mapping

| Tool ID | Verified source | Observed signature note | Adapter mapping |
|---|---|---|---|
| `composition.ptable_heatmap` | `pymatviz.ptable_heatmap` | `values` 为首参，真实参数为 `count_mode`、`colorscale`、`heat_mode` 等 | 平台参数 `colorScale` -> `colorscale`；`countMode` 和 `normalize` 先由 adapter 侧聚合/归一化元素值，再调用 `ptable_heatmap(values)` |
| `composition.elements_hist` | `pymatviz.elements_hist` | 首参为 `formulas`；`fig_kwargs` 会直接传给 `go.Figure(**fig_kwargs)`，不能用 `{"title": ...}` | 平台参数 `countMode` -> `count_mode`、`keepTop` -> `keep_top`、`logY` -> `log_y`、`showValues` -> `show_values`；标题通过 `fig.update_layout(title_text=...)` 设置 |
| `composition.chem_sys_treemap` | `pymatviz.chem_sys_treemap` | 接受 formula、Composition、Structure 序列；参数为 `show_counts`、`max_cells` 等 | 平台参数 `showCounts` -> `show_counts`、`maxCells` -> `max_cells`；Adapter 负责从 Structure 派生 composition 输入 |
| `structure.structure_3d` | `pymatviz.structure_3d` | 支持 `Structure`、`dict[str, Structure]`、`Sequence[Structure]`；参数为 `show_cell`、`show_bonds` 等 | 平台参数 `showCell` -> `show_cell`；`showBonds: "auto"` 在 MVP 映射为 `False`；先校验周期 lattice 和 atom limit |
| `structure.coordination_hist` | deterministic distance-cutoff coordination count | Supports platform-passed periodic Structure objects, Structure dicts, CIF/POSCAR text, and bounded structure sequences through the Phase 10C parser | Emits `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`; params are `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`; no HTML, no artifact JS, no advanced local-environment classification |
| `structure.viewer_3d` | `pymatviz.StructureWidget` | 构造函数为 `(structure=None, **kwargs)`，实例提供 `to_html()` | 优先输出 `StructureWidget.to_html()`；如 widget 渲染失败，输出 sandbox-safe fallback HTML 并在 provenance 中标记 `mattervizFallback=true` |
| `ml.density_scatter` | `pymatviz.density_scatter` | 参数为 `x`、`y` 和可选 `df`；`n_bins=False` 可用于小型 smoke test 禁用分箱 | 平台参数 `targetColumn` / `predictionColumn` 解析到 DataFrame 列名，`nBins` -> `n_bins`、`identityLine` -> `identity_line`、`bestFitLine` -> `best_fit_line` |
| `ml.error_distribution` | `plotly.express.histogram` | 平台自定义 Plotly 工具，无 pymatviz 原生函数依赖 | Adapter 计算 `prediction - target` 的 error 列，输出 histogram、metrics_json 和 top outlier table_json |
| `ml.basic_metrics` | platform builtin | 平台内置计算 MAE、RMSE、R2、meanError、maxAbsError | Adapter 使用 DataFrame target/prediction 列，输出 canonical `metrics_json` |
| `ml.outlier_table` | platform builtin | 平台内置按 `abs_error` 降序生成 top-k 表 | Adapter 输出 `table_json` 和 `table_csv`，不依赖 Plotly |

### Optional / Fallback Notes

- `preview_png` 仍按 MVP optional 处理；当前 exporter 仅在请求 `preview_png` 且 Plotly/Kaleido 可用时生成，不作为测试阻塞项。
- `structure.viewer_3d` 已输出 `matterviz_html`、`structure_json`、`summary_md`、`recipe_json`；snapshot 仍推迟到 V1 或后续 render-worker。
- 10 个 MVP manifest adapter 现在均已注册到 `ADAPTER_CLASSES` 并有 smoke tests；V1/V2 adapter 仍通过 registerable class name 校验，待对应阶段实现。

### Data Pipeline Contract Notes

- `packages/material-parsers` 现在可产生 `MaterialObjectType.Structure` 和 `MaterialObjectType.DataFrame` normalized object draft，字段与 Tool Registry inputOptions 对齐。
- `structure.structure_3d` 仍要求 periodic `Structure`；plain XYZ 当前会解析为非周期 `Atoms` normalized object，并生成 `NON_PERIODIC_ATOMS` quality warning，不会被误路由到周期结构工具。
- `.extxyz` 文件现在按扩展名直接识别为 `extxyz`，由 ASE 解析并在具备 lattice 时转换成周期 `Structure`。
- ZIP 容器解析已具备安全 member path 过滤：`../`、绝对路径和过深路径会被拒绝，保留安全 member 继续解析并标记 partial。
- `DataFrame` parser 会推断 `formula`、`target`、`prediction`、`uncertainty`、`structure_id` 字段角色，为后续 ML MVP tools 的 Tool Registry 校验做准备。

### Shared Schema Verification Notes

- Python/Pydantic 入口 `mdi_schemas` 已导出本阶段要求的核心类型；本轮补充了 `JobEvent` 以对齐 SSE / Timeline 设计。
- TypeScript 入口 `packages/schemas/src/index.ts` 已补齐 `JobStatus`、`JobEventStatus`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile`、`VisualizationRecipe` 等核心类型。
- 新增 `tests/test_shared_schemas.py`，防止 Python 与 TypeScript schema 入口再次出现核心类型覆盖差异。
- 当前未发现新的 pymatviz API 签名差异；`preview_png` 仍因 Kaleido/Chromium 作为 optional artifact 处理。

### Tool Executor Notes

- 新增 `mdi_adapters.execute_tool_request()` 作为库层受控执行入口，后续 Worker 不应直接实例化 adapter 跳过 Registry。
- 当前执行入口会校验 tool 是否存在于 manifest、请求 artifact type 是否属于 `RegisteredTool.artifactTypes`、`params` 是否符合 `paramsSchema`，再通过 adapter registry 创建 Adapter。
- cache key 由 `toolId`、tool version、adapter name、input hashes、params 和 artifact types 计算；当前仅支持可选 in-memory cache，占位后续 Redis / Artifact cache。
- 当前尚未接入 ToolCall 数据库状态更新和 JobEvent `artifact.ready`；这属于 Job Queue / SSE 阶段。

### Worker Runtime Notes

- 新增 `mdi_workers.run_tool_call_job()`，将 `execute_tool_request()` 的结果投射为 ToolCall 状态和 JobEvent 事件序列。
- 成功路径事件顺序为 `tool.started` -> `artifact.ready`* -> `tool.completed`，每个 Artifact 单独产生 `artifact.ready`。
- 失败路径事件顺序为 `tool.started` -> `tool.failed`，Job 和 ToolCall 均标记为 failed。
- 当前 `InMemoryJobStore` 仅用于开发和测试；生产仍需 PostgreSQL 状态源、SSE publisher、Worker retry/cancel 和幂等写入。
- ToolCall params 在写入状态前会脱敏 secret-like keys，避免 BYOK/API key 进入状态记录。

### MVP Params Schema Notes

- 本轮恢复核验后，将全部 10 个 MVP 工具的 `paramsSchema` 收紧为白名单，统一使用 `additionalProperties=false`。
- 受控执行入口 `execute_tool_request()` 现在可对所有 MVP 工具拒绝未注册参数，而不只覆盖前三个 Adapter。
- 当前已显式声明的平台批准参数包括：
  - composition：`countMode`、`colorScale`、`normalize`、`keepTop`、`logY`、`showValues`、`showCounts`、`maxCells`、`title`
  - structure: `showCell`, `showBonds`, `selectedStructureIds`, `selectedStructureId`, `cameraPreset`, `maxStructures`, `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, `plot_kind`
  - ml：`targetColumn`、`predictionColumn`、`nBins`、`density`、`xLabel`、`yLabel`、`identityLine`、`bestFitLine`、`stats`、`topK`、`title`
- 新增测试确保 MVP 工具未知参数会触发 JSON Schema `Additional properties are not allowed`。
- 未发现新的 pymatviz API 与 manifest 差异；`preview_png` 继续作为 optional/fallback artifact 处理。

### Phase 1 API Boundary Notes

- `apps/api/mdi_api` 已提供 FastAPI app factory，并通过 `/tools` 与 `/tools/mvp` 暴露 Tool Registry 的只读查询边界。
- 工具查询 route 只返回 manifest-normalized registry view，不执行 adapter，不绕过 `execute_tool_request()`。
- 后续执行类 API 必须继续走 Tool Registry lookup、paramsSchema 校验和 adapter registry，不允许 API route 直接实例化 pymatviz 函数。
## 2026-07-04 Official Example Evidence Notes

- Direct official browser evidence currently validates the Tool Registry + Adapter path for `ml.basic_metrics` only.
- MatPES evidence selected `PBE` and `r2SCAN` from the DataProfile and produced a `metrics_json` artifact.
- Ward metallic glasses evidence now routes to `table.numeric_summary`; `D_max` and `dTx` are summarized as independent numeric properties instead of being treated as target/prediction metrics columns.
- Official richer tools such as `plotly_custom.histogram`, `composition.ptable_heatmap`, `composition.elements_hist`, classification curves, phonon tools, Brillouin zone, and MatterViz widgets were not downgraded into current PASS. They are preserved as future expected tools in the evidence pack.
- No evidence path bypassed Tool Registry or Adapter execution.

## 2026-07-06 Phase 10B-1 Composition Visualization Tool Notes

- Registered or upgraded the executable composition visualization set:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- These tools use DataFrame input with deterministic formula column resolution. Explicit `formulaColumn` takes priority; otherwise the resolver checks `formula`, `composition`, `reduced_formula`, `pretty_formula`, `material_formula`, and `chemical_formula`.
- `paramsSchema` remains a whitelist. Unknown params are rejected through Tool Registry validation before adapter execution.
- Required artifacts are deterministic JSON plus `summary.md` and `recipe.json`; Plotly HTML is produced when supported.
- Adapter execution does not access network, execute shell, read arbitrary paths, or use a real LLM.
- Mock Planner routing now checks explicit composition keywords before generic histogram/correlation/table routing to avoid misrouting composition prompts.

## 2026-07-06 Phase 10B-2 Composition Browser/API Evidence Notes

- Browser/API evidence confirms all five composition visualization tools execute through persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Verified tools:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- Evidence artifacts live under `docs/phase10b/browser_api_evidence/` and include redacted API captures, screenshots, copied artifact files, manifests, and platform summaries.
- `composition.ptable_heatmap` now emits `ptable_heatmap.json` to match the registered artifact contract and evidence expectations.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.
- No new adapter was added in Phase 10B-2.

## 2026-07-07 Phase 10C-2 Structure Browser/API Evidence Notes

- Browser/API evidence confirms all five lightweight structure tools execute through persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Verified tools:
  - `structure.summary`
  - `structure.lattice_summary`
  - `structure.spacegroup_summary`
  - `structure.composition_from_structure`
  - `structure.preview_metadata`
- Evidence artifacts live under `docs/phase10c/browser_api_evidence/` and include redacted API captures, screenshots, copied artifact files, manifests, and platform summaries.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.
- No new adapter was added in Phase 10C-2.
- Phase 10C-2 does not claim support for `structure.viewer_3d`, XRD, RDF, coordination histogram, phonon, or Brillouin zone tools.

## 2026-07-07 Phase 10D Advanced Structure Planning Notes

- Phase 10D is planning-only and does not register new tools.
- Future advanced structure tools must still enter through Tool Registry validation, whitelist params schemas, resource limits, and Adapter execution.
- Recommended Phase 10D-1 executable candidates are:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
  - optional schema-only `structure.viewer_3d_contract`
- Full `structure.viewer_3d`, `structure.brillouin_zone_3d`, `structure.xrd`, `structure.rdf`, `phonon.bands`, `phonon.dos`, and `phonon.band_dos` remain unregistered future-scope tools until their schemas, dependencies, and evidence plans are approved.
- Viewer artifacts must be static and deterministic. Artifact-provided JavaScript execution, external URL loading, arbitrary local file reads, notebook execution, and script execution remain forbidden.

## 2026-07-07 Phase 10D-1 Viewer Scene Metadata Tool Notes

- Registered executable tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Both tools use domain `structure`, strict params schemas, Tool Registry validation, and Adapter execution.
- `structure.viewer_scene_metadata` emits `viewer_scene.json`, `summary.md`, and `recipe.json`.
- `structure.viewer_export_package` emits `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- Artifacts are static JSON/Markdown only. They do not include renderer bundles, artifact-supplied JavaScript, external URLs, or WebGL code.
- Mock Planner routing for full interactive viewer, XRD, RDF, coordination, Brillouin-zone, and phonon prompts remains deferred and does not route to Phase 10D-1 tools.

## 2026-07-08 Phase 10D-2 Viewer Scene Evidence Notes

- No new Tool Registry tools were added in Phase 10D-2.
- Browser/API evidence confirms the existing `structure.viewer_scene_metadata` and `structure.viewer_export_package` tools execute through Mock Planner, PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Evidence artifacts live under `docs/phase10d/browser_api_evidence/` and include redacted API captures, browser-rendered static preview screenshots, copied artifact files, manifests, and platform summaries.
- Verified artifacts:
  - `viewer_scene.json`
  - `viewer_assets_manifest.json`
  - `summary.md`
  - `recipe.json`
- The evidence confirms static metadata/export package behavior only. It does not register or claim `structure.viewer_3d`, `structure.brillouin_zone_3d`, `structure.xrd`, `structure.rdf`, `structure.coordination_hist`, `phonon.bands`, or `phonon.dos`.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.

## 2026-07-08 Phase 10D-3 Static Preview Notes

- No new Tool Registry tools were added in Phase 10D-3.
- Existing registered tools remain:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Frontend artifact preview now recognizes the static artifact contracts emitted by those tools:
  - `viewer_scene.json`
  - `viewer_assets_manifest.json`
  - `summary.md`
  - `recipe.json`
- Preview hardening does not change adapter execution, Tool Registry validation, PlanValidator, QueueWorkerRuntime, or `/planner/jobs`.
- Static previews must not be interpreted as support for `structure.viewer_3d`, WebGL rendering, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon, notebook extraction, or script execution.

## 2026-07-08 Phase 10E Static Physics Planning Notes

- No new Tool Registry tools were added in Phase 10E.
- Planned future tool ids:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Planned domain for all three is `structure`.
- Planned outputs follow existing artifact boundaries: deterministic numeric JSON, optional static Plotly-compatible chart JSON/HTML, `summary.md`, and `recipe.json`.
- Recommended first implementation is `structure.coordination_hist`; it must require periodic structures and a strict params schema.
- `structure.xrd` and `structure.rdf` must not be registered until numeric tolerance and fixture policies are pinned.
- Full `structure.viewer_3d`, Brillouin-zone 3D, phonon tools, notebook/script execution, external API workflows, and experimental fitting remain outside Tool Registry scope.

## 2026-07-08 Phase 10E-1 Coordination Histogram Tool Notes

- `structure.coordination_hist` is now implemented and executable through Tool Registry + Adapter.
- The adapter uses a deterministic `distance_cutoff` neighbor policy and does not call `pymatviz.coordination_hist` directly.
- Registered artifacts are:
  - `coordination_hist.json` as `table_json`
  - `coordination_hist_plot.json` as `plotly_json`
  - `summary.md` as `summary_md`
  - `recipe.json` as `recipe_json`
- The strict params schema allows only `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`.
- The tool does not emit HTML, executable JavaScript, external URLs, WebGL renderer assets, or full 3D viewer artifacts.
- XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, CrystalNN, bond-valence, notebook/script, and external API workflows remain out of scope.

## 2026-07-08 Phase 10E-2 Coordination Histogram Evidence Notes

- No new Tool Registry tools were added in Phase 10E-2.
- Browser/API evidence confirms the existing `structure.coordination_hist` tool executes through Mock Planner, PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Evidence artifacts live under `docs/phase10e/browser_api_evidence/phase10e2_coordination_hist/` and include redacted API captures, browser-rendered static preview screenshots, copied artifact files, audits, and evidence manifest.
- Verified artifacts:
  - `coordination_hist.json`
  - `coordination_hist_plot.json`
  - `summary.md`
  - `recipe.json`
- Negative routing evidence confirms XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts do not route to `structure.coordination_hist`.
- The evidence confirms static coordination histogram behavior only. It does not register or claim `structure.xrd`, `structure.rdf`, `structure.viewer_3d`, `structure.brillouin_zone_3d`, `phonon.bands`, `phonon.dos`, or advanced local environment classification.

## 2026-07-08 Phase 10E-3 XRD / RDF Readiness Notes

- No new Tool Registry tools were added in Phase 10E-3.
- `structure.xrd` is recommended as the single Phase 10E-4 implementation target.
- `structure.rdf` remains deferred until normalization, cutoff/binning, periodic-image, finite-size warning, and partial-pair policies are fixed.
- Existing manifest entries for XRD/RDF are still planning/inventory references until executable adapters, strict params schemas, registry tests, planner routing, and artifact contracts are implemented.
- Future `structure.xrd` registration should declare static artifacts only: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Future `structure.xrd` description must not claim RDF, full 3D viewer, WebGL rendering, phonon support, Rietveld refinement, experimental fitting, or database lookup.
- Full viewer, WebGL, Brillouin-zone, phonon, notebook/script, and external API workflows remain outside executable Tool Registry scope.

## 2026-07-08 Phase 10E-4 XRD Tool Notes

- `structure.xrd` is now implemented and executable through Tool Registry + Adapter.
- The adapter uses `pymatgen.analysis.diffraction.xrd.XRDCalculator` with a CuKa-only deterministic static pattern policy.
- Registered artifacts are:
  - `xrd_pattern.json` as `table_json`
  - `xrd_plot.json` as `plotly_json`
  - `summary.md` as `summary_md`
  - `recipe.json` as `recipe_json`
- The strict params schema allows only `radiation`, `two_theta_min`, `two_theta_max`, `intensity_threshold`, `peak_merge_tolerance`, `max_peaks`, `include_hkl`, and `plot_kind`.
- The tool does not emit HTML, executable JavaScript, external URLs, WebGL renderer assets, full 3D viewer artifacts, RDF artifacts, phonon artifacts, experimental fitting artifacts, or Rietveld refinement artifacts.
- RDF, full viewer, WebGL, Brillouin-zone, phonon, notebook/script, external API workflows, experimental fitting, and Rietveld refinement remain out of scope.

## 2026-07-08 Phase 10E-5 XRD Evidence Notes

- No new Tool Registry tools were added in Phase 10E-5.
- Browser/API evidence confirms the existing `structure.xrd` tool executes through Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Evidence artifacts live under `docs/phase10e/browser_api_evidence/phase10e5_xrd/` and include redacted API captures, copied artifact files, local static preview pages, audits, and evidence manifest.
- Verified artifacts:
  - `xrd_pattern.json`
  - `xrd_plot.json`
  - `summary.md`
  - `recipe.json`
- Negative routing evidence confirms RDF, coordination histogram, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, CrystalNN, experimental fitting, Rietveld, and broadening prompts do not route to `structure.xrd`.
- The evidence confirms static XRD behavior only. It does not register or claim `structure.rdf`, `structure.viewer_3d`, `structure.brillouin_zone_3d`, `phonon.bands`, `phonon.dos`, experimental fitting, or Rietveld refinement.

## 2026-07-08 Phase 10E-5R2 XRD Browser Screenshot Notes

- No Tool Registry changes were made in Phase 10E-5R2.
- The existing `structure.xrd` registry entry and artifact contract remain unchanged.
- Browser screenshots now confirm the frontend can display the XRD job, artifact list, `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json` evidence.
- The screenshots do not add or claim RDF, full viewer, WebGL, Three.js, phonon, experimental fitting, or Rietveld refinement support.

## 2026-07-09 Phase 10E-6 RDF Policy Notes

- No Tool Registry changes were made in Phase 10E-6.
- Planned future tool: `structure.rdf`.
- Planned domain: `structure`.
- Planned artifact types: `table_json`, `plotly_json`, `summary_md`, and `recipe_json`.
- Planned filenames: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Planned params schema is strict and RDF-specific: `r_max_angstrom`, `bin_width_angstrom`, `normalization`, `include_partial_pairs`, `max_partial_pairs`, `max_sites`, `max_bins`, `max_neighbors_total`, and `plot_kind`.
- Planned description must state static RDF only and must not claim trajectory RDF, experimental PDF fitting, phonon, full 3D viewer, WebGL, or advanced local environment classification.
- Phase 10E-7 may register `structure.rdf` only if it implements the policy fixed in `docs/phase10e/phase10e6_rdf_policy_hardening.md`.

## 2026-07-09 Phase 10E-7 RDF Tool Notes

- `structure.rdf` is now implemented and executable through Tool Registry + Adapter.
- The adapter uses periodic `pymatgen Structure.get_all_neighbors(r_max)` records with deterministic radial bins and `number_density` shell-volume normalization.
- Registered artifacts are:
  - `rdf.json` as `table_json`
  - `rdf_plot.json` as `plotly_json`
  - `summary.md` as `summary_md`
  - `recipe.json` as `recipe_json`
- The strict params schema allows only `r_max_angstrom`, `bin_width_angstrom`, `normalization`, `include_partial_pairs`, `max_partial_pairs`, `max_sites`, `max_bins`, `max_neighbors_total`, and `plot_kind`.
- The tool does not emit HTML, executable JavaScript, external URLs, WebGL renderer assets, full 3D viewer artifacts, phonon artifacts, experimental PDF fitting artifacts, or local-environment classification artifacts.
- Browser/API evidence for RDF is deferred to Phase 10E-8.
- Full viewer, WebGL, Brillouin-zone, phonon, notebook/script, external API workflows, trajectory RDF, experimental fitting, and scattering refinement remain out of scope.

## 2026-07-09 Phase 10F-5 Fixture Replay Notes

- No Tool Registry changes were made in Phase 10F-5.
- Fixture-pack replay used existing registered tools only:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Each fixture replay selected exactly the expected tool through a persisted plan/job path and QueueWorkerRuntime execution.
- Expected static artifacts were generated and validated for each tool.
- The replay confirms internal fixture-pack behavior only. It does not add official examples PASS evidence and does not register or claim full viewer, WebGL/Three.js renderer, phonon, experimental fitting, notebook/script, or external API support.
# 2026-07-09 Phase 10F-10 Viewer Scene JSON-only Preview Surface

- Added frontend-only JSON preview support for already-defined `viewer_scene.v1` artifacts in the existing artifact preview surface.
- No Tool Registry tool registration was added.
- No `structure.viewer_3d` adapter was added.
- No planner routing, QueueWorkerRuntime, AnalysisPlanRepository, or `/planner/jobs` runtime behavior changed.
- `structure.coordination_hist`, `structure.xrd`, and `structure.rdf` remain unchanged.
- Renderer implementation, WebGL, Three.js, Brillouin-zone 3D, and phonon remain future scope.

# 2026-07-10 Phase 10F-11 Viewer Scene Browser Evidence Notes

- No Tool Registry changes were made in Phase 10F-11.
- No `structure.viewer_3d` adapter was registered.
- Existing `viewer_scene.v1` preview support remains a frontend JSON-only artifact preview surface, not a runtime executable tool.
- Real browser evidence used fixture-backed mock API responses and did not alter planner routing, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or Tool Registry behavior.
- Full viewer, renderer bundle, WebGL, Three.js, Brillouin-zone 3D, phonon, notebook/script execution, and external API workflows remain out of scope.

# 2026-07-12 Phase 10F-16 Scientific Inspection Notes

- No Tool Registry or params schema change was made.
- `structure.viewer_3d` remains the formal backend artifact-generation tool; picking, measurement, and PNG export are client viewer actions, not new executable tools.
- Explicit scene JSON requests still use `structure.viewer_scene`; Phase 10D legacy tools remain direct-compatible and JSON-only.
- Measurement prompts do not add arbitrary backend execution authority.

# 2026-07-12 Phase 10F-17 Periodic Inspection Notes

- No Tool Registry, planner, PlanValidator, adapter, or QueueWorkerRuntime semantics changed.
- `structure.viewer_3d` still emits one canonical inert single-cell scene; supercell and periodic images are frontend-only view state.
- No backend measurement or supercell tool was added.

# 2026-07-12 Phase 10F-18 Periodic Topology Notes

- `structure.viewer_scene` and `structure.viewer_3d` now emit the same inert `viewer_scene.v2` periodic topology semantics.
- Params, planner identities, PlanValidator authority, QueueWorkerRuntime, and backend success/client renderer separation remain unchanged.
- Phase 10D tools remain direct-compatible and JSON-only. v1 bonds remain same-cell only.
- No topology service, CrystalNN/VoronoiNN tool, trajectory tool, or artifact execution authority was added.

# 2026-07-12 Phase 10F-20 Viewer Producer Policy

- `structure.viewer_scene` and `structure.viewer_3d` are current v2 producers selected by Mock Planner.
- `structure.viewer_scene_metadata` and `structure.viewer_export_package` remain registered only for deprecated direct compatibility.
- Legacy output is never relabeled, migrated, or interpreted as periodic topology.

# 2026-07-13 Phase 10F-21 Viewer Performance Notes

- No Tool Registry, planner, adapter, PlanValidator, QueueWorkerRuntime, or artifact contract semantics changed.
- Performance tiers are frontend-local validated-render-model policy and cannot be selected by artifact data.

# 2026-07-13 Phase 10F-22 Viewer Accessibility Notes

- No Tool Registry, planner, adapter, PlanValidator, QueueWorkerRuntime, AnalysisPlan, or artifact contract semantics changed.
- Keyboard, focus, semantic summaries, live announcements, and mobile interaction are frontend-local consumers of validated scenes.
- Artifact content cannot register shortcuts, roles, callbacks, event handlers, or focus behavior.

# 2026-07-13 Phase 10F-23 Picking and Measurement Notes

- No Tool Registry, planner, adapter, PlanValidator, QueueWorkerRuntime, AnalysisPlan, or canonical scene semantics changed.
- Picking and measurement are bounded frontend actions over independently validated scene/topology data.
- `viewer_measurement.json` is a local inert download, not a newly registered executable tool or persisted backend artifact.

# 2026-07-13 Phase 10F-26 Scientific Export Notes

- No Tool Registry, planner, adapter, PlanValidator, QueueWorkerRuntime, AnalysisPlan, or canonical scene semantics changed.
- PNG, export-state JSON, Markdown, and export manifest are bounded frontend-local downloads over an independently validated scene.
- No PDF/report tool, server renderer, external upload, script, renderer asset, or new execution authority was registered.

# 2026-07-13 Phase 10F-27 Formal Viewer Registration Notes

- `structure.viewer_3d` is registered exactly once and is owned by `platform_builtin_manifest.yaml`.
- The adapter remains `StructureViewer3DAdapter`; outputs remain canonical scene v2, manifest v2, summary, and recipe.
- Natural interactive viewer intent selects `structure.viewer_3d`; explicit inert scene JSON selects `structure.viewer_scene`.
- Legacy tools remain direct compatibility only. Unsupported advanced domains are explicit negative capabilities.
- Phase 10G-2 consumes `structure.trajectory_import` artifacts in a client viewer but keeps that tool planner-hidden. `structure.viewer_3d` remains static; no formal trajectory product ID is added before G-3 performance closure.

# 2026-07-14 Phase 10H-1 Phonon Band Notes

- `phonon.band` is the unique MVP-stage static band tool and uses `PhononBandAdapter`.
- Input is exactly one profiled `PhononBand`: canonical `phase10h.phonon_band.v1` or bounded `phonopy_band_yaml` wrapper.
- Params are closed to source format/unit, table row cap, and `plot_kind=line`; outputs are seven exact inert artifact types.
- Mock Planner routes explicit static band/dispersion requests only. DOS, combined view, eigenvectors, animation, thermal properties, solver execution, and Brillouin requests do not route here.
- PlanValidator, QueueWorkerRuntime, and AnalysisPlan authority are unchanged.

# 2026-07-14 Phase 10H-2 Phonon DOS Notes

- `phonon.dos` is the unique MVP-stage static DOS tool using `PhononDosAdapter`.
- Input is exactly one `PhononDos`: canonical v1 or bounded phonopy total/projected text wrapper with explicit metadata.
- Params cover only source format/unit/normalization, table/plot caps, and line plot; outputs are seven exact inert types.
- Mock Planner routes static DOS only. Bands, combined, eigenvectors, animation, thermal properties, calculations, and Brillouin requests do not route here.
- PlanValidator, QueueWorkerRuntime, and AnalysisPlan authority are unchanged.

# 2026-07-17 Phase 10J Volumetric Contract Notes

- Phase 10J registers no Tool Registry entry and adds no planner route, params schema, adapter, or QueueWorkerRuntime path.
- The five `phase10j.volumetric_*` schemas are inert artifact contracts only.
- Generic JSON preview is sufficient for metadata; no parser or renderer capability may be inferred from contract validity.
- A future `structure.volumetric_data` tool requires the separate Phase 10J-1 parser/adapter review and must reuse these contracts.

## Phase 10J-1

- Registered one public parser tool, `structure.volumetric_data`; no overlapping CHGCAR/LOCPOT/CUBE tool IDs were added.
- Input is exactly one bounded normalized `VolumetricData` object. Params are fixed format/quantity/selection/dtype/compression enums and required validation booleans.
- Current outputs are canonical grid, payload metadata, field metadata, numeric binary, dataset, manifest, summary, and recipe artifacts.
- Mock Planner routes explicit parsing/normalization intent only. Renderer, isosurface, slice, VASP execution, trajectory, phonon, and Brillouin requests are excluded.
# Phase 10J-2

- `structure.volumetric_data` remains the sole public generic volumetric tool. Isosurface is a validated frontend consumer capability, not a second parser/calculation tool.
- The adapter now emits an additive inert `volumetric_structure_overlay_json` artifact; existing canonical Phase 10J contracts and tool execution semantics remain unchanged.

## Phase 10J-3

- `structure.volumetric_data` remains the sole public tool. Charge/spin is a typed product consumer, not a new overlapping registry entry.
- Planner accepts explicit density/isodensity/spin-density product intent while rejecting Bader, atomic charge, potential, slices, volume, trajectory, and phonon requests.
- Derived collinear fields are inert canonical artifacts with allowlisted formula IDs and relationship validation; no renderer code or external resource is registered.

## Phase 10J-4

- `structure.volumetric_data` remains the sole public parser tool; potential inspection is an application-owned consumer.
- Natural LOCPOT/local-potential/equipotential/planar-profile/point-difference requests route to the existing tool.
- Work function, vacuum/Fermi detection, cross-potential alignment, electric-field calculation, DFT, macro-average, arbitrary slice/path, and direct volume requests remain rejected.
