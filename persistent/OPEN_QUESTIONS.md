# OPEN_QUESTIONS

## 2026-07-14 Phase 10H-4 Follow-ups

- Define and test a bounded commensurate-supercell solver before non-Gamma animation; the contract only fixes `2*pi*q.cell_image` phase.
- Cross-source degenerate modes require subspace/projector comparison rather than individual vector matching and remain deferred.
- Future adapters must declare atomic mass/isotope source and explicit source-to-canonical atom mapping; partial occupancy remains unsupported.
- Physical animation amplitude, zero-point motion, temperature dependence, parser formats, mode UI, and formal dynamic registration remain Phase 10H-5 or later decisions.

## 2026-07-14 Phase 10H-3 Follow-ups

- The static combined product is closed; simultaneous display of multiple projected DOS series is intentionally bounded and the initial UI selects one projection at a time.
- Physical assistive-technology and broad-device rendering remain outside automated browser evidence.
- Eigenvector normalization, complex phase/gauge, degeneracy, non-Gamma reconstruction, and animation remain Phase 10H-4/10H-5 work and are not inferred from band/DOS compatibility.
- Combined artifacts reference validated source artifacts; remote artifact loading and cross-project arbitrary artifact composition remain unauthorized.

## 2026-07-14 Phase 10H phonon contract closure

- **Closed: scientific data semantics.** Reciprocal `2*pi`, q-point path/discontinuity, THz conversion, negative-real imaginary modes, source-stable full `3N` branch identity, source-declared degeneracy, DOS normalization/projection identity, compatibility, and caps are fixed and validated.
- **Open: parser and producer.** No `phonopy.yaml`, `band.yaml`, DOS, or other source parser/adapter is implemented; future ingestion must convert explicitly into the canonical contract and retain atom/source lineage.
- **Open: product surfaces.** Band/DOS/combined plots, formal tools, planner routing, browser/API evidence, eigenvectors, mode animation, thermal/Raman/IR, and Brillouin-zone features require independent phases.
- **Open: mode identity.** `phase10h.phonon_mode_ref.v1` is reserved only; eigenvector phase, normalization, mass weighting, phase convention, and degenerate-subspace policy remain undefined.

## 2026-07-13 Phase 10G-3 trajectory product closure

- **Closed: formal trajectory product.** `structure.trajectory_viewer` is a unique planner-visible validated tool with canonical artifacts and persisted launch/capability provenance.
- **Closed: bounded browser performance baseline.** Chromium 150, Firefox 128, WebKit 18, mobile portrait/landscape, rapid seek, playback cycling, context recovery, artifact switching, accessibility, and external-network isolation are evidenced.
- **Open: local indexed/chunked storage.** The current canonical JSON path is bounded; a separately reviewed local indexed/chunk design is required for larger trajectories. Remote chunk streaming is not approved.
- **Open: topology and science.** Static-reference bonds remain `PARTIAL_READY`; dynamic bonds, reactive/variable-atom trajectories, RDF/MSD/VACF/diffusion, comparison, editing, and video export require independent contracts and evidence.
- **Open: npm audit endpoint.** The configured npmmirror registry does not implement the audit endpoint; retain lockfile/tree/CI review and do not claim a clean npm audit until an approved endpoint is available.

## 2026-07-13 Phase 10G-2 trajectory closure

- Formal planner-visible identity and bounded performance acceptance were closed by Phase 10G-3; static-reference bond playback remains explicitly partial.
- The configured npmmirror registry still does not implement the npm audit endpoint; current dependency risk must continue to use lockfile/tree review plus CI until an approved audit endpoint is available.

## 2026-07-13 Phase 10G-1 Follow-ups

- **Closed: first parser scope.** Multi-frame EXTXYZ and canonical JSON are supported with bounded deterministic normalization.
- **Open: plain/non-lattice trajectory contract.** Plain XYZ cannot become trajectory without a separately reviewed absent-lattice mode.
- **Open: additional formats/chunking.** ASE traj, LAMMPS, XDATCAR, binary formats, indexed chunks, and remote streaming remain deferred.
- **Open: product capability.** Internal import is not a formal planner-visible trajectory viewer; playback and browser performance remain future phases.

## 2026-07-13 Phase 10G Follow-ups

- **Closed: trajectory data identity and units.** Stable atom/frame index, row-vector lattice, coordinate/wrapping modes, time, vector/scalar units, and strict availability are fixed by v1.
- **Open: parser and storage implementation.** Format parsing and local indexed/chunk artifacts require a separate phase; v1 JSON is not a large-trajectory loading promise.
- **Open: product execution.** No adapter, planner route, formal tool, playback, renderer, or browser/performance readiness exists yet.
- **Open: future science.** Stress, partial PBC/occupancy, variable atom count, reactive trajectories, RDF/MSD/VACF/diffusion, and dynamic bonds need independent contracts.

## 2026-07-13 Phase 10F-24 Follow-ups

- Decide whether a later phase needs a capped internal cell grid; canonical and outer boundaries are complete.
- Camera preset/state productization and clipping remain the next real-space controls.
- Persisted supercell structures require a separate backend contract and are not implied by renderer-local expansion.

## 2026-07-12 Phase 10F-15 Follow-ups

- **Closed: formal minimal viewer identity.** `structure.viewer_3d` is the sole ordinary interactive viewer identity and emits canonical inert artifacts.
- **Closed: production cap and performance policy.** Caps align with the contract; species instancing and bounded line geometry are evidenced at 256 sites / 2048 bonds.
- **Closed: multi-browser and mobile baseline.** Chromium 149, Firefox 128, WebKit 18, portrait, and landscape evidence are complete.
- **Closed: legacy policy.** Phase 10D tools are retained as explicit direct-purpose JSON-only paths with no migration.
- **Still open: npm framework/test-tool debt.** Vitest/Vite and Next/PostCSS upgrades need a dedicated compatibility phase.
- **Still open: long-term legacy removal window.** No deletion or migration date is selected.
- **Still open: advanced scientific viewer scope.** Trajectory, phonon, Brillouin zone, volumetric data, editing, picking, and measurements require independent contracts and security reviews.
- **Still open: broader device GPU matrix.** Current evidence is software WebGL 2 on the tested Windows browsers and is not a universal hardware claim.

## 2026-07-11 Phase 10F-14 Follow-ups

- **Closed: renderer dependency decision.** Direct `three@0.185.1` is selected and pinned; R3F is rejected for excess abstraction and MatterViz remains deferred.
- **Closed: canonical renderer API and security gate.** Raw artifacts must pass frontend validation and whitelist mapping before renderer initialization.
- **Closed: renderer foundation and real graphics evidence.** Live adapter Si/NaCl/warning/bonds-disabled artifacts render in Chrome WebGL 2 with real interaction evidence.
- **Closed: lifecycle and context loss foundation.** Tab/artifact/unmount cleanup and synthetic context loss are evidenced.
- **Closed: renderer network isolation.** `NO_RENDERER_EXTERNAL_NETWORK_REQUESTS`.
- **Still open: production renderer hardening.** Consider atom instancing, richer accessibility, mobile layout and a cross-browser matrix.
- **Still open: npm framework/tooling audit debt.** Existing Vitest/Vite/Next/PostCSS findings require a separate dependency-upgrade phase.
- **Still open: old viewer schema compatibility debt.** Phase 10D retention/deprecation/migration remains undecided.
- **Still open: formal full viewer tool.** `structure.viewer_3d` is not registered and remains reviewer-gated.
- **Still open: official PASS evidence.** Official example provenance claims remain none.

## 2026-07-11 Phase 10F-13 Follow-ups

- **Closed: real job-backed browser evidence for adapter output.** Phase 10F-13 captures real Chrome evidence using adapter-generated live planner/job/runtime artifacts.
- **Closed: adapter-generated preview evidence.** The JSON-only preview surface now displays adapter-generated `viewer_scene.json` and `viewer_scene_manifest.json` in real Chrome.
- **Closed: live invalid request boundary evidence.** Multi-structure input fails before successful viewer artifact generation and exposes no misleading preview.
- **Closed: live external network isolation evidence.** Browser network capture reports `NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS`.
- **Documented: old/new viewer schema coexistence.** Phase 10D tools remain registered with old schemas and are not migrated or relabeled.
- **Still open: old viewer schema compatibility debt.** Reviewer should decide deprecation, retention, or migration policy for Phase 10D viewer tools.
- **Still open: renderer dependency decision.** No renderer dependency, WebGL, Three.js, MatterViz, or renderer bundle has been approved.
- **Still open: renderer API and sandbox plan.** Renderer API shape and malicious-scene sandboxing require a separate evaluation phase.
- **Still open: renderer implementation.** Renderer and full `structure.viewer_3d` remain `NOT_READY`.
- **Still open: official PASS evidence.** Official PASS claims remain none.

## 2026-07-11 Phase 10F-12 Follow-ups

- **Closed: minimal production artifact producer.** Phase 10F-12 implements `structure.viewer_scene`, which produces canonical `viewer_scene.v1` artifacts through the existing registry and execution path.
- **Closed: adapter contract validation.** Generated `viewer_scene.json` and `viewer_scene_manifest.json` are validated before export.
- **Closed: minimal planner routing for inert scene JSON.** Mock Planner routes explicit inert viewer-scene JSON prompts to `structure.viewer_scene`.
- **Closed: JSON-only preview compatibility for adapter output.** Frontend regression uses adapter-generated evidence JSON.
- **Still open: old viewer schema compatibility debt.** Phase 10D `structure.viewer_scene_metadata` and `structure.viewer_export_package` remain registered with old schemas; reviewer should decide deprecation or migration policy.
- **Still open: real job-backed browser evidence for adapter output.** Phase 10F-11 browser evidence used fixtures; Phase 10F-12 adds adapter output preview regression but not a new real Chrome capture from a live adapter job.
- **Still open: renderer handoff details.** Renderer input API, renderer dependency evaluation, sandboxing, and malicious-scene tests remain future work.
- **Still open: renderer implementation.** Renderer, WebGL, Three.js, renderer bundles, and full `structure.viewer_3d` remain `NOT_READY`.
- **Still open: official PASS evidence.** Official PASS claims remain none.

## 2026-07-09 Phase 10F-10 Follow-ups

- **Closed: JSON-only preview surface.** Phase 10F-10 implements `viewer_scene.v1` and manifest JSON-only preview support in the existing Results/export artifact preview surface.
- **Closed: fixture-backed frontend evidence.** Tests cover valid, warning/caps, and invalid fixture samples through mock planner/job artifacts.
- **Closed: preview inertness assertions.** Tests assert no canvas, script element, iframe, real external URL pattern, WebGL marker, or Three.js marker is introduced by the preview samples.
- **Still open: real browser screenshot evidence.** Phase 10F-10 uses frontend/jsdom evidence and does not capture real browser screenshots.
- **Still open: production artifact producer.** No `structure.viewer_3d` adapter or runtime artifact producer exists.
- **Still open: renderer implementation.** Renderer, WebGL, Three.js, renderer bundles, and sandboxing remain `NOT_READY`.
- **Still open: planner routing.** Viewer routing remains planned only; no planner route was added.
- **Still open: official PASS evidence.** Official PASS claims remain none.

## 2026-07-09 Phase 10F-9 Follow-ups

- **Closed: contract fixture implementation.** Phase 10F-9 adds inert `viewer_scene.v1` fixtures, manifest fixtures, expected validation results, an isolated validator, and pytest replay tests.
- **Closed: implementation-time validator thresholds for the fixture slice.** The validator enforces the Phase 10F-8 caps for sites, bonds, species, cell expansion, and JSON byte size.
- **Closed: non-finite coordinate rejection.** Fixtures and tests cover `NaN` and `Infinity` string sentinels as invalid coordinates.
- **Closed: external resource and executable placeholder rejection.** Invalid fixtures use safe placeholders and the validator rejects them without using real external URLs or executable code.
- **Still open: JSON-only browser/API evidence.** Phase 10F-9 does not claim browser/API evidence; Phase 10F-10 should decide whether to replay these fixtures through an existing static preview surface.
- **Still open: production artifact producer.** No `structure.viewer_3d` adapter or runtime artifact producer exists.
- **Still open: renderer implementation.** Renderer, WebGL, Three.js, renderer bundles, and sandboxing remain `NOT_READY`.
- **Still open: bond policy.** Bonds remain optional in contract fixtures; future producer requirements remain deferred.
- **Still open: official PASS evidence.** Official PASS claims remain none.

## 2026-07-09 Phase 10F-8 Follow-ups

- **Closed: viewer_scene artifact identity planning.** Phase 10F-8 fixes `viewer_scene`, `viewer_scene.v1`, and `phase10f8.viewer_scene.v1` as the contract draft identity.
- **Closed: top-level JSON contract planning.** Required fields are planned: `kind`, `version`, `schema_version`, `source`, `metadata`, `scene`, `validation`, `caps`, `warnings`, `provenance`, and `security`.
- **Closed: validation contract draft.** Phase 10F-8 converts Phase 10F-7 caps into contract draft limits for sites, bonds, species, cell expansion, unit-cell edges, and JSON bytes.
- **Closed: JSON-only browser evidence model.** Static JSON/manifest preview evidence is allowed; renderer screenshot evidence remains deferred.
- **Still open: final implementation thresholds.** The draft caps are ready for contract planning, but implementation-time thresholds still need reviewer confirmation before validator code is added.
- **Still open: bond policy.** Bonds remain optional and advisory in v1; whether a future producer must infer bonds remains deferred.
- **Still open: coordinate canonicalization.** The v1 contract recommends Cartesian angstroms as renderer-facing basis with optional fractional coordinates, but final implementation must decide whether fractional coordinates are also required.
- **Still open: renderer library decision.** Renderer implementation, WebGL, Three.js, renderer bundles, and sandboxing remain `NOT_READY` and require explicit approval.
- **Still open: compressed payloads.** Compressed viewer artifacts are disallowed in v1; any future allowance requires security review.
- **Still open: multi-structure scenes.** Multi-structure scenes are out of v1 and require a future contract version.
- **Still open: official PASS evidence.** Official PASS claims remain none.

## 2026-07-09 Phase 10F-7 Follow-ups

- **Closed: advanced viewer readiness assessment.** Phase 10F-7 assessed the artifact contract, renderer architecture, security boundary, input caps, routing policy, browser evidence model, and readiness matrix.
- **Closed: next readiness decision.** `viewer_scene` artifact-contract readiness is `READY` for the next contract phase.
- **Still open: renderer implementation.** Renderer implementation is `NOT_READY`; sandboxing, dependency review, browser security tests, and console/network evidence remain required.
- **Still open: full viewer implementation.** Full `structure.viewer_3d` implementation is `NOT_READY` and not approved for direct implementation.
- **Still open: WebGL / Three.js.** WebGL and Three.js remain future scope requiring explicit approval.
- **Still open: artifact contract finalization.** Phase 10F-8 should decide the final `viewer_scene.json`, summary, recipe, params, warning, and security schema.
- **Still open: official PASS evidence.** Official static physics PASS remains none until eligible official provenance is replayed.
- **Still open: advanced structure.** Brillouin-zone 3D, phonon, and advanced local environment classification remain separate future scopes.

## 2026-07-09 Phase 10F-6 Follow-ups

- **Closed: fixture-pack replay evidence.** Phase 10F-6 records that the Phase 10F-5 replay PASS is complete for all three static physics fixture cases.
- **Closed: expected-contract replay values.** Candidate replay values are present for the selected coordination histogram, XRD, and RDF numeric checks.
- **Closed: fixture-pack vs official PASS boundary.** Fixture-pack PASS is valid; official PASS remains none because all cases have `internal_regression` provenance.
- **Still open: official PASS evidence.** Official static physics PASS still requires `official_direct` or approved `official_derived_manual` provenance plus direct platform replay.
- **Recommended next: advanced viewer readiness planning.** Phase 10F-7 should plan viewer security, renderer choice, artifact contracts, caps, screenshots, and routing before any implementation.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10F-5 Follow-ups

- **Closed: fixture-pack replay.** Phase 10F-5 replayed `coordination_hist_small_crystal`, `xrd_small_crystal`, and `rdf_small_crystal` through the platform/job flow.
- **Closed: selected tools.** Replayed cases selected `structure.coordination_hist`, `structure.xrd`, and `structure.rdf` respectively.
- **Closed: candidate expected values.** Expected contracts now contain replay-generated candidate values for the selected numeric checks.
- **Still open: official PASS evidence.** The replay is fixture-pack evidence only; all cases remain `internal_regression`.
- **Recommended next: evidence closure.** Phase 10F-6 should close the boundary and decide whether to move to viewer readiness or official-derived fixture approval planning.

## 2026-07-09 Phase 10F-4 Follow-ups

- **Closed: fixture-pack construction.** Phase 10F-4 constructs `docs/phase10f/static_physics_fixture_pack/` with three bounded candidate cases for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- **Closed: no-PASS boundary in pack metadata.** Pack and case contracts keep `official_pass_claim` / `official_pass_claims` set to `false`; provenance labels are `internal_regression`.
- **Still open: replay verification.** The pack has not yet been replayed through `/planner/jobs`, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- **Still open: numeric expected values.** Numeric contract fields remain `pending_replay_generation` until Phase 10F-5 replay produces reviewed candidate values.
- **Still open: official static physics PASS evidence.** No official PASS claim exists for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- **Recommended next: fixture-pack replay verification.** Phase 10F-5 should replay the candidate pack and report fixture-pack PASS/PARTIAL_PASS without promoting internal regression cases to official PASS.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10F-3 Follow-ups

- **Closed: fixture-pack planning.** Phase 10F-3 defines the small direct-uploadable fixture pack layout, candidate matrix, provenance labels, expected-contract templates, numeric tolerance policy, and future replay protocol for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- **Closed: provenance labels.** `official_direct`, `official_derived_manual`, `official_like_curated`, `internal_regression`, `mapping_only`, `future_scope`, `unsupported`, and `unknown` are documented.
- **Closed: official PASS boundary.** Only `official_direct` and reviewer-approved `official_derived_manual` cases can become official PASS after direct platform replay; `official_like_curated` and `internal_regression` remain non-official regression evidence.
- **Still open: fixture construction approval.** No fixture pack has been constructed, approved, or replayed yet.
- **Still open: official static physics PASS evidence.** No official PASS claim exists for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf` until approved direct-uploadable fixtures are replayed and compared.
- **Recommended next: fixture-pack construction.** Phase 10F-4 should construct a small bounded fixture pack from the approved planning templates without running notebooks/scripts or claiming PASS.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10F-2 Follow-ups

- **Closed: coverage gap classification.** Phase 10F-2 records that the current official benchmark pack has zero direct-uploadable static physics cases for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- **Closed: fixture proposal.** Phase 10F-2 proposes small direct-uploadable CIF/POSCAR/Structure JSON fixture policies and expected artifact checks for the three completed static physics tools.
- **Closed: expected contract authoring plan.** Exact fields, tolerance fields, security-critical fields, metadata-only fields, allowed variance, and provenance labels are documented.
- **Still open: fixture approval.** No direct-uploadable static physics fixture pack has been approved or executed yet.
- **Still open: official PASS evidence.** No official static physics PASS claim exists until approved fixtures are executed through the platform and compared to expected contracts.
- **Recommended next: fixture-pack planning.** Phase 10F-3 should plan a small direct-uploadable expected-contract pack without executing notebooks/scripts or claiming PASS.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10F-1 Follow-ups

- **Closed: benchmark pack audit.** The local official examples benchmark pack was present and audited for static physics direct verification.
- **Closed: direct-uploadable gate.** Phase 10F-1 fixed the gate for official static physics PASS claims: local uploadable input, no notebook/script/API/network/new dependency, bounded input, deterministic artifact comparison, and mapping to `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- **Still open: official static physics coverage gap.** No current official direct-uploadable case maps to the three completed static physics tools, so Phase 10F-1 made no official static physics PASS claim.
- **Recommended next: coverage gap closure.** Phase 10F-2 should plan how to curate or approve direct-uploadable official/static-physics fixtures without executing notebooks/scripts or implementing new adapters.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10F Follow-ups

- **Closed: static physics family.** `structure.coordination_hist`, `structure.xrd`, and `structure.rdf` now have implementation, browser/API evidence, deterministic static artifacts, registry/planner coverage, and CI closure.
- **Recommended next: official static physics direct verification.** Phase 10F recommends direct-uploadable official-example verification before moving to higher-risk viewer/WebGL/phonon work.
- **Still open: official examples direct verification.** No mapping-only, notebook-only, script-heavy, external-API, missing-input, or screenshot-only case should be marked PASS without direct platform evidence.
- **Still open: rendered chart UI.** Static chart JSON artifacts are evidenced; rendered bar/stem/line chart preview polish remains a separate UI enhancement.
- **Still open: advanced structure.** Full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, and advanced local environment classification remain future readiness/planning items.

## 2026-07-09 Phase 10E-8 Follow-ups

- **Closed: Phase 10E-8 evidence.** Browser/API/artifact/security/negative-routing evidence is now complete for `structure.rdf`.
- **Still open: rendered RDF chart UI.** `rdf_plot.json` is verified as static chart JSON / artifact gallery evidence; a rendered line chart UI can be considered later without changing the adapter contract.
- **Still open: RDF scope extensions.** Trajectory RDF, time-averaged RDF, experimental PDF fitting, neutron scattering refinement, and X-ray total scattering analysis remain out of scope.
- **Still open: advanced local environments.** Voronoi, CrystalNN, bond valence, and oxidation-state-aware environment classification remain future planning items.
- **Still open: advanced visualization / phonon.** Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, notebook/script extraction, and external API workflows remain future work.

## 2026-07-09 Phase 10E-7 Follow-ups

- **Closed at adapter level: RDF.** `structure.rdf` now emits deterministic `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json` artifacts for periodic crystalline structures.
- **Closed: RDF numeric policy.** Phase 10E-7 implements fixed radial bins, `number_density` shell-volume normalization, ordered partial RDF pairs, and explicit site/bin/neighbor/partial-pair caps.
- **Closed: Phase 10E-8 evidence.** Browser/API/artifact evidence is complete for `structure.rdf`.
- **Still open: RDF scope extensions.** Trajectory RDF, time-averaged RDF, experimental PDF fitting, neutron scattering refinement, and X-ray total scattering analysis remain out of scope.
- **Still open: advanced local environments.** Voronoi, CrystalNN, bond valence, and oxidation-state-aware environment classification remain future planning items.
- **Still open: advanced visualization / phonon.** Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, notebook/script extraction, and external API workflows remain future work.

## 2026-07-08 Phase 10E-1 Follow-ups

- **Closed at adapter level: coordination histogram.** `structure.coordination_hist` now emits deterministic `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json` artifacts.
- **Closed: initial neighbor policy.** Phase 10E-1 uses a conservative `distance_cutoff` policy with deterministic ordering and rounded distances.
- **Still open: Phase 10E-2 evidence.** Browser/API/artifact evidence is still required for `structure.coordination_hist`.
- **Still open: XRD.** `structure.xrd` needs pinned radiation source defaults, peak merge tolerance, and fixture peak windows before implementation.
- **Still open: RDF.** `structure.rdf` needs normalization, cutoff, binning, finite-size warning, and species-pair policy before implementation.
- **Still open: advanced local environments.** Voronoi, CrystalNN, bond valence, and oxidation-state-aware environment classification remain future planning items.
- **Still open: advanced visualization / phonon.** Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, trajectory RDF, notebook/script extraction, and external API workflows remain future work.

## 2026-07-07 Phase 10C-1 Follow-ups

- **Closed at adapter level: lightweight structure tools.** The platform now has
  registry-gated implementations for `structure.summary`,
  `structure.lattice_summary`, `structure.spacegroup_summary`,
  `structure.composition_from_structure`, and `structure.preview_metadata`.
- **Closed: dependency policy for Phase 10C-1.** The current environment has
  `pymatgen`, `spglib`, and `ase`; symmetry detection uses pymatgen/spglib when
  available and must report typed dependency/detection errors rather than fake
  a space group.
- **Closed: 3D viewer boundary for routing.** Prompts that ask for true 3D
  rendering are not treated as supported `structure.viewer_3d` evidence in this
  phase. Preview metadata may be offered only with an explicit future-scope
  rationale.
- **Still open: Phase 10C-2 evidence.** The new structure adapters need
  browser/API/artifact evidence before becoming presentation-grade evidence.
- **Still open: parser hardening.** Complex CIF/POSCAR variants, disordered
  structures, partial occupancies, very large structures, and symmetry tolerance
  behavior need broader fixtures and acceptance criteria.
- **Still open: advanced structure and physics adapters.** 3D viewer, XRD, RDF,
  coordination histograms, phonon bands/DOS, and Brillouin zone rendering remain
  future phases.
- **Still open: notebook/script extraction.** Structure-related notebook/script
  official examples remain outside the current direct benchmark scope.

## 2026-07-06 Phase 10C Lightweight Structure Adapter Planning

- **Closed for planning: structure direction.** Phase 10C recommends lightweight structure summary adapters before 3D viewer, XRD/RDF, coordination, phonon, or Brillouin zone work.
- **Closed for planning: Phase 10C-1 recommended scope.** The next implementation prompt is scoped to `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- **Still open: structure fixture and parser policy.** Phase 10C-1 must confirm which CIF, POSCAR, pymatgen Structure JSON, or ASE-like JSON fixtures are stable enough for adapter and API execution tests.
- **Still open: optional dependency boundary.** `structure.spacegroup_summary` needs a concrete `pymatgen`/`spglib` availability and tolerance policy before implementation.
- **Still open: advanced structure and physics adapters.** 3D viewer, XRD, RDF, coordination histograms, phonon bands/DOS, and Brillouin zone rendering need separate Phase 10D+ planning.
- **Still open: notebook/script extraction.** Structure-related notebook/script official examples remain outside the current direct benchmark scope.

## 2026-07-06 Phase 10B Second Batch pymatviz Adapter Planning

- **Closed for planning: second-batch direction.** Phase 10B recommends composition visualization as the next implementation area rather than jumping directly to structure viewer, XRD/RDF, phonon, or Brillouin zone work.
- **Closed for planning: Phase 10B-1 recommended scope.** The next implementation prompt is scoped to `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- **Still open: evidence-grade composition adapters.** Existing registry entries for some composition tools need Phase 10B-1 hardening and Phase 10B-2 browser/API/artifact evidence before they can be treated as official direct-case evidence.
- **Still open: structure/physics adapters.** `structure.viewer_3d`, XRD, RDF, phonon, Brillouin zone, and related physics workflows need a separate Phase 10C+ planning/evidence strategy.
- **Still open: notebook/script extraction.** Extraction-required official examples remain outside the current direct benchmark scope.

## 2026-07-06 Phase 10A-2 Browser/API Evidence for First Batch Adapters

- **Closed: browser/API/artifact evidence for first-batch tools.** MatPES scatter, MatPES histogram, Ward distribution summary, Ward histogram, Ward correlation, and Ward composition summary now have project-local redacted API captures, artifacts, screenshots, summaries, and manifests.
- **Closed: first-batch Plotly JSON evidence contract.** `viz.scatter` and `viz.histogram` now write top-level chart metadata required by the benchmark evidence while keeping the nested Plotly figure for rendering.
- **Closed: composition prompt routing ambiguity.** Composition distribution prompts now route to `composition.summary` before generic histogram/distribution routing.
- **Still open: remaining official examples.** The other 59 official examples remain outside this browser/API evidence phase and keep their benchmark statuses from Phase 10A-0.
- **Still open: multi-step DAG/data-dependency execution.** The evidence verifies single-step adapter execution; combined workflows remain future work.
- **Still open: CI/browser evidence policy.** Browser/API evidence is committed as documentation evidence but is not a default CI gate.
- **Still open: broader adapter coverage.** Phonon, Brillouin zone, advanced widgets, XRD/RDF, classification curves, and richer report/export workflows remain future phases.

## 2026-07-06 Phase 10A-1 First Batch Adapter Implementation

- **Closed: MatPES richer first-batch plot/table tools.** The platform now has registry-gated `viz.scatter`, `viz.histogram`, and `table.distribution_summary` tools that can serve MatPES scatter/distribution/table-summary prompts within the current single-step execution model.
- **Closed: Ward first-batch distribution/correlation tools.** The platform now has registry-gated `table.distribution_summary`, `viz.histogram`, and `viz.correlation` tools for Ward-style tabular distribution and numeric correlation prompts.
- **Closed at adapter level: safe composition summary.** `composition.summary` can summarize a stable formula/composition field when present, including Ward's `composition` column; it must not infer or fabricate composition results when no formula-like field exists.
- **Still open: browser evidence for new tools.** This phase adds adapters and tests; full browser-click evidence for scatter/histogram/correlation/distribution-summary outputs should be captured before freezing a demo evidence baseline for these new outputs.
- **Still open: multi-step DAG/data-dependency execution.** The new tools are single-step executable plans. Combined workflows such as metrics plus scatter plus report still require DAG/data-dependency scheduling or explicit multi-step support.
- **Still open: remaining official examples.** The 27 extraction-required, 20 mapping-only, and 12 future-scope official examples remain outside this phase.
- **Still open: broader visualization adapters.** Phonon, Brillouin zone, advanced widgets, XRD/RDF, classification curves, and richer report/table/export workflows remain future adapter phases.

## 2026-07-05 Phase 9D True LLM Live Verification

- **Closed: true live LLM full-chain evidence captured.** The Gemini OpenAI-compatible path produced redacted evidence from live provider output through PlanValidator, persisted AnalysisPlan, `jobs.plan_id`, QueueWorkerRuntime, Tool Registry + Adapter, Artifact/Result generation, and Phase 9C UI display.
- **Closed: final gated live rerun passed.** `python -m pytest -q -m llm_integration` passed with Gemini 3 Flash Preview, proving the current OpenAI-compatible Gemini path can run the full persisted planner job chain.
- **Open: Antigravity model requires a different provider contract.** Gemini reports `antigravity-preview-05-2026` only supports Interactions API, not OpenAI-compatible chat/completions. Supporting it would be a future provider path, not Phase 9D OpenAI-compatible verification.
- **Closed: live LLM parameter aliases could pass persistence and fail only at adapter runtime.** PlanValidator now validates each step's params against the registered tool `paramsSchema` before persistence.
- **Closed: Phase 9D evidence redaction.** The local evidence pack under `docs/llm-live-verification/phase9d/` was scanned for key/token strings and did not contain the API key or auth token header.
- **Still open: production secret encryption/KMS.** Phase 9D used env/SecretStore safely but does not implement production envelope encryption.
- **Still open: multi-step DAG/data-dependency execution.** Live verification covered a simple executable plan path, not DAG scheduling.
- **Still open: worker process supervision/dead-letter policy.** Queue semantics remain the existing Phase 8B/9C path.
- **Still open: broader pymatviz adapter coverage.** The live run verified metrics/report artifacts, not the full official visualization inventory.

## 2026-07-05 Phase 9D LLM Configuration Path Repair

- **Closed: UI provider config looked disconnected from planner jobs.** The UI already passed provider config into `/planner/jobs`; this repair adds an explicit no-network resolve API so the UI can show the current task provider status without relying on env-default status.
- **Closed: env settings could override explicit UI model/timeout settings.** Explicit `PlannerUserConfig` now wins when supplied; env remains the source for env-only live tests.
- **Still open: true live LLM verification.** The gated full-chain test exists but was not run because live LLM env is not configured in the current shell.
- **Still open: UI SecretStore and CLI env are separate paths.** This is acceptable for Phase 9D, but a later production config flow may unify operator-managed provider config and user BYOK secrets.
- **Still open: production secret encryption/KMS.** Secret UX remains dev/test in-memory and redacted, not production envelope encryption.

## 2026-07-05 Phase 9C UI/UX Redesign Docs Baseline

- **Closed: independent right-side Result Inspector.** The Phase 9C design explicitly does not use a persistent right result panel. Results belong to the main `结果与导出` tab.
- **Closed: old three-column frontend baseline as recommended direction.** The old right Agent panel and bottom result tabs are legacy context. The recommended direction is top global context bar, left data-context viewer, and main three-tab workspace.
- **Closed: where Agent process vs conversation vs results live.** All three live inside the main workspace as mutually exclusive tabs: `Agent 过程`, `对话与 Plan`, `结果与导出`.
- **Closed at baseline level: resize/collapse and main-tab implementation.** `PlannerWorkbench` now includes a collapsible/resizable left data-context viewer and mutually exclusive main tabs with tests.
- **Still open: responsive drawer polish.** The baseline is responsive, but a dedicated mobile drawer interaction can be refined later.
- **Still open: exact visual styling.** This docs baseline fixes information architecture, not final colors, typography, spacing, or component library details.

## 2026-07-05 Phase 9B Official Direct Examples Semantic Refinement

- **Closed: Ward direct-uploadable semantic blocker.** Ward metallic glass evidence no longer treats `D_max` and `dTx` as target/prediction regression columns. It now uses `table.numeric_summary` for independent numeric and categorical summaries.
- **Closed: MatPES stale prompt evidence.** Fresh MatPES browser evidence now uses the PBE vs r2SCAN prompt and no longer contains the stale `y_true` / `y_pred` request in the captured browser text.
- **Still open: richer official visualization coverage.** Ward composition/element distributions, periodic-table heatmaps, histograms/scatter plots, and richer reports remain future adapter/report work. MatPES histogram/table/report outputs also remain future work.
- **Still open: full official examples suite.** This pass only regenerated the two direct-uploadable cases requested by the user.

## 2026-07-04 Phase 9B Official MatPES Example Blocker Repair

- **Closed: MatPES official CSV metrics blocker.** The evidence-pack failure for `matpes_atomic_energies_csv` is fixed. Mock Planner now uses DataProfile columns and selected `PBE` / `r2SCAN` for `ml.basic_metrics`; the browser rerun completed with one ToolCall and one artifact.
- **Still open: complete official examples suite execution.** Only the previously failed MatPES direct-uploadable case was rerun in this repair pass. The remaining official examples, including `ward_metallic_glasses_csv_xz`, script/notebook cases, MVP/V1 mapped README demos, and future-scope cases still require separate evidence-pack execution.
- **Still open: richer non-ML prompt/tool routing.** The current fix handles metric plans for role-less numeric tables. Composition/structure datasets should later steer to composition or structure tools when the profile and user intent indicate those domains.

## 2026-07-04 Phase 9B Browser + Durable Worker Resolver Closure

- **Closed: browser verification after API/Web restart.** The in-app browser loaded the local workspace, ran the demo workflow with Mock Planner, showed completed status, plan provenance, timeline events, artifact gallery, report/recipe summary, and ToolCall details. No real API key was entered.
- **Closed: worker-side durable object-store resolver.** `run_queued_job(job_id)` now builds a settings-driven SQLAlchemy repository factory, configured ArtifactStorage, and `DurableObjectStoreResolver`, so an out-of-process worker can rebuild `ml_table`/`structures`/`formulas` from persisted normalized exports.
- **Closed: PostgreSQL planner runtime missing durable object resolver.** The PostgreSQL planner runtime construction path now installs the same artifact storage and resolver.
- **Still open: true LLM live verification.** The gated provider path remains implemented, but no live provider run was executed in this closure.
- **Still open: production upload service hardening.** The worker can now read persisted normalized exports, but the current demo upload path still goes through the Phase2 local runtime. A production upload path should persist dataset/profile/normalized exports directly through SQL and MinIO/S3.
- **Still open: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter, and advanced material viewer polish.**

## 2026-07-04 Phase 9B Runtime Data Binding Follow-up

- **Closed: local demo planner jobs staying queued without a worker process.** In the default in-memory development path, `/planner/jobs` now enqueues and auto-drains the job through `QueueWorkerRuntime.handle_job(job_id)` only when no Redis queue is configured and no custom repos/runtime are injected.
- **Closed: uploaded dataset objects not reaching the local queue worker.** `QueueWorkerRuntime` now supports an object-store resolver, and the default planner runtime resolves Phase2 uploaded/demo dataset objects by `dataset_id` before executing the persisted plan.
- **Closed: planner prompt/profile context did not expose real uploaded columns.** Planner preview/jobs now use the real Phase2 `DataProfile` when available, and the prompt describes normalized inputRef conventions.
- **Closed: executable plans could omit dataset inputRefs for uploaded data.** Uploaded dataset plans now fail before persistence/job/enqueue when their steps require an available normalized object but omit or misname the required inputRef.
- **Remaining: durable normalized-object loading for out-of-process Redis workers.** The current follow-up closes the local in-memory demo path and adds a resolver seam. Production Redis workers that run in a separate process still need durable normalized object storage/loading for uploaded datasets instead of relying on process-local Phase2 memory.
- **Remaining: browser automation after restart.** API E2E and frontend tests passed, but final browser click-through after restart could not be automated because the browser plugin native bridge was unavailable in this environment.

## 2026-07-04 Phase 9B Frontend/API Follow-up

- **Closed: browser preflight 405 for Phase 9B workspace APIs.** The affected routes were implemented, but the FastAPI app lacked CORS middleware. Local/demo origins are now configured by default and overrideable through `MDI_CORS_ORIGINS` / `CORS_ORIGINS`.
- **Closed: invalid plan response echo for `/planner/jobs`.** Validation failure now returns no raw rejected plan, so credential-like params rejected by PlanValidator are not echoed to the frontend/API caller.
- **Closed: runtime health config-only reporting.** `/health/runtime` now runs safe light probes where a backend is configured and returns redacted `unknown` component status on probe failure.
- **Closed: full Planner workbench i18n string extraction for user-facing labels.** Remaining hard-coded Chinese labels in `PlannerWorkbench.tsx` were moved into the `zh-CN` / `en-US` message files, and English-mode regression assertions cover key labels.

## 2026-07-04 Phase 9B Follow-ups (Demo-ready AI Planner Workspace)

- **Phase 9B product workspace is implemented locally.** The Planner UI now has default Chinese i18n, provider settings, Secret UX, dataset/profile/demo workflow, region-specific empty states, error explanations, grouped artifacts, report/recipe summary, and user/developer mode layering.
- **Service-backed runtime verification for this commit is pending CI.** This local machine has no Docker CLI; PostgreSQL + Redis + MinIO integration must be confirmed by GitHub Actions for the Phase 9B commit. Local integration skips must not be treated as passed integration.
- **Live LLM verification is still not claimed.** Phase 9B did not run a live provider test. The Phase 9A gated path remains available only when explicit `MDI_RUN_LLM_INTEGRATION=1` and provider env are configured.
- **Production secret encryption/KMS remains deferred.** Phase 9B improves Secret UX and no-plaintext response shape, but does not implement production envelope encryption.
- **Multi-step DAG/data-dependency execution remains deferred.** The workbench previews steps and provenance but does not implement DAG scheduling, node editing, or data-dependency execution.
- **Worker process supervision and dead-letter policy remain deferred.** Phase 9B does not change queue worker core semantics.
- **Advanced material viewer polish remains deferred.** Artifact display is grouped and productized, but full material 3D viewer polish remains future work.

## 2026-07-03 Phase 9A Follow-ups (Gated True LLM Provider)

- **Gated OpenAI-compatible provider path is implemented locally.** The provider can be selected explicitly and configured by `MDI_LLM_*` environment variables while the default provider remains mock/deterministic-safe.
- **Live LLM verification is not claimed locally.** The gated `llm_integration` test exists, but local env does not include the required live provider settings, so `python -m pytest -q -m llm_integration` skips by design.
- **Default CI must remain real-LLM-free.** No default workflow should require `MDI_LLM_API_KEY` or call an external provider.
- **Service-backed runtime verification for this commit is pending CI.** This local machine has no Docker CLI; PostgreSQL + Redis + MinIO integration must be confirmed by GitHub Actions for the Phase 9A commit.
- **Prompt/completion debug logging remains deferred.** Raw prompts and completions are not persisted by default; any future debug path must be opt-in and redacted.
- **Production secret encryption/KMS remains deferred.** Phase 9A reads keys from env/config and preserves no-leak boundaries, but it does not implement production BYOK encryption.
- **Multi-step DAG/data-dependency execution remains deferred.** Phase 9A changes provider selection only; execution semantics remain Phase 8B persisted sequential plan execution.
- **Worker process supervision and dead-letter policy remain deferred.** Queue worker core behavior was not changed.
- **Advanced material viewer polish remains deferred.** No frontend visualization redesign was included.

## 2026-07-03 Phase 8C-P1 Follow-ups (UX Compliance Closure)

- **SSE/EventSource timeline P1 is locally closed.** The Planner workbench now opens an EventSource path for persisted JobEvents through `/planner/jobs/{job_id}/events/stream`, and polling remains only as fallback.
- **Report/Recipe Summary P1 is locally closed.** The UI now has a separate report/recipe summary area instead of relying on the artifact/result list alone.
- **Dataset/Profile selector P1 is locally closed.** The UI now offers API-backed dataset/profile selection using existing read endpoints and retains manual ID fallback when discovery/profile reads are unavailable.
- **Phase 8C-P1 CI gate is closed for the implementation commit.** GitHub Actions run `28664159687` on commit `4d0c241` succeeded, including service-backed PostgreSQL + Redis + MinIO integration with 19 passed, 0 skipped, 0 failed.
- **True LLM integration remains deferred.** No production LLM provider enablement or live LLM test gate was added.
- **Advanced multi-step DAG/data-dependency execution remains deferred.** No scheduler or DAG editor semantics were added.
- **Production secret encryption remains deferred.** No KMS/envelope encryption work was done.
- **Worker process supervision and dead-letter policy remain deferred.** Worker runtime semantics were not changed.

## 2026-07-03 Phase 8C Follow-ups (Frontend Planner UX)

- **Frontend Planner UX baseline is closed/frozen.** The frontend can create Planner Jobs through `/planner/jobs`, display the validated persisted plan, show `planId`/`planHash`, display `job.plan_id -> analysis_plans.id`, surface `plan.loaded`, and show ToolCall/Artifact/Result plan provenance. Implementation commit `9967c5b` passed GitHub Actions run `28646226271`.
- **Validation-failure UX is closed at the baseline level.** The frontend now clearly states that no AnalysisPlan was saved, no Job was created, and nothing was enqueued; it does not poll job status or show fake IDs after validation failure.
- **Phase 8C CI gate is closed for the implementation commit.** GitHub Actions run `28646226271` succeeded, including service-backed PostgreSQL + Redis + MinIO integration with 19 passed, 0 skipped, 0 failed.
- **True LLM integration remains deferred.** The frontend uses the existing backend planner provider path; production real-provider enablement and live LLM tests remain future work.
- **Advanced multi-step DAG/data-dependency execution remains deferred.** The UI previews steps and provenance, but it is not a drag/drop DAG editor and does not add scheduler semantics.
- **Production secret encryption remains deferred.** Phase 8C displays provenance and validation errors; it does not implement KMS/envelope encryption.
- **Worker process supervision and dead-letter policy remain deferred.** Phase 8C did not alter worker operations.
- **Advanced material viewer polish remains deferred.** Artifact display is provenance-oriented and does not yet implement a full material 3D viewer workflow.

## 2026-07-03 Phase 8B Follow-ups (Persisted Plans + Queue Runtime)

- **Closed/frozen: QueueWorkerRuntime + persisted AnalysisPlan execution.** The main worker path now loads `job.plan_id`, fetches the persisted `AnalysisPlan`, reconstructs it, and executes exact `steps`; tests prove a persisted 1-step plan creates exactly 1 ToolCall, not the deterministic 5-tool fallback.
- **Closed/frozen: PostgreSQL persisted plan schema.** Alembic revision `0002_phase8b_plans` adds `analysis_plans`, `jobs.plan_id`, and required indexes. CI verifies these through Alembic upgrade head against PostgreSQL.
- **Closed/frozen: service-backed Phase 8B gate.** This local machine has no Docker CLI, so the PostgreSQL + Redis + MinIO Phase 8B integration test could not be run locally. GitHub Actions run `28631817086` on Phase 8B code acceptance commit `962c429` ran Phase 6 + Phase 8B integration with 19 passed, 0 skipped, 0 failed.
- **Frontend Planner UX remains deferred to Phase 8C.** Do not start Phase 8C until Phase 8B is frozen by CI-backed service integration.
- **Multi-step dependency graph remains deferred.** Phase 8B executes persisted steps in order and preserves the existing `inputRefs`/`object_store` mechanism; it does not add DAG scheduling or inter-step artifact binding.
- **True LLM integration remains deferred.** Default tests continue to use MockLLMProvider/fake transport; real OpenAI/DeepSeek service tests need a separate opt-in gate and redaction policy.
- **Production secret encryption remains deferred.** Plan persistence rejects credential-like params, but the production `EncryptedSecretStore`/KMS path is still not implemented.

## 2026-06-27 Phase 8A Follow-ups (Plan Execution Bridge)

- **LLM→execution closed loop is now CLOSED at the local-runtime level.** `/planner/jobs` (execute=True) runs the EXACT validated LLM plan through `Phase2ProductRuntime` → Tool Registry → Adapter, proven by `test_runtime_executes_exact_provided_plan_one_tool_call` (1 step → 1 ToolCall, not deterministic 5).
- **Remaining: QueueWorkerRuntime + PostgreSQL plan persistence.** Execution currently uses the in-memory synchronous `Phase2ProductRuntime`. The validated plan is NOT yet persisted to PostgreSQL nor enqueued onto the Redis `QueueWorkerRuntime`. Wiring `analysis_plan` into the queue worker + a `persisted_plans` table (Alembic migration) is the next integration step.
- **Multi-step dependency graph deferred.** The bridge executes steps in plan order; there is no inter-step data-dependency resolution beyond the existing inputRefs/object_store mechanism. A real DAG executor is future work.
- **Plan input binding is still conventional.** The LLM plan must reference the conventional `ml_table` (or `formulas`/`structures`) normalized object refs. A general field-mapping/resolution layer between LLM logical refs and dataset objects is future work.
- Real LLM integration, production envelope encryption, frontend Planner UX, and plan auto-repair remain deferred (unchanged from Phase 7 records).

## 2026-06-27 Phase 7 Follow-ups (LLM Planner + BYOK)

- **Production envelope encryption is NOT implemented.** `EncryptedSecretStore` is a placeholder that raises `NotImplementedError`. Only `InMemorySecretStore` works, and it is for dev/test ONLY — it holds plaintext values in memory and must never be used in production. A real backend (KMS, Fernet, or HashiCorp Vault) is required before any production BYOK use.
- **LLM → execution closed loop is NOT complete.** `POST /planner/jobs` generates an LLM plan, validates it, and then creates a job via `Phase2ProductRuntime.create_job()`. However, that runtime internally regenerates its own **deterministic** plan (`build_phase2_plan`) — the validated LLM plan is currently NOT the plan that executes. The job status returned is "created" (in-memory Phase 2 path), not a real enqueue onto Redis/PostgreSQL. Wiring the validated LLM plan into the real QueueWorkerRuntime + Tool Registry + Adapter execution path is deferred to a later phase.
- **Real OpenAI/DeepSeek integration tests are optional and not in the default suite.** All Phase 7 tests use `MockLLMProvider` or a fake transport. A real LLM integration test (gated behind an env var like `MDI_RUN_LLM_INTEGRATION=1` + `OPENAI_API_KEY`) is future work; it must never run in the default `pytest -q`.
- **Prompt / completion logging policy is undecided.** Currently no prompt or completion is logged. If debug logging is added later, it MUST pass through `redact_credential_values()` and default to off. A formal policy (what to log, retention, redaction guarantees) is open.
- **Runtime full-chain secret-leak audit is not yet done.** Phase 7 has unit-level redaction tests and a secret-list-no-plaintext test, but no end-to-end audit proving secrets never reach JobEvent / Artifact metadata / Recipe / Report in the live runtime. The current code has no path that writes secrets to those sinks, but an explicit audit test is future work.
- **Plan auto-repair is intentionally not implemented.** PlanValidator is strict — invalid plans are rejected, not repaired. Auto-repair (ask the LLM to fix its own invalid plan) is deferred to avoid silently executing mutated plans.

## 2026-06-26 Phase 6 Follow-ups

- **Acceptance: CONDITIONAL PASS.** No P0 blocker in the code or test design. All 18 integration tests skip cleanly because Docker is not available on this machine. Git is clean at commit `e3c7a73`.
- P0-2 (integration tests all skipped) is unresolved at the infrastructure level: Docker must be installed and services started before live tests can run. This is by design — tests skip rather than fail on missing infrastructure.
- P0-3 (Alembic test) is resolved: the committed test calls real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle and index existence verification.
- P0-4 (service-backed loop) is resolved: the committed test uses real Tool Registry + BasicMetricsAdapter through `execute_tool_request()`, not a fake executor.
- **Cannot enter Phase 7** until: (1) Docker is installed, (2) `docker compose up -d postgres redis minio` succeeds with all services healthy, (3) `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` passes with zero skipped tests.
- Concurrent JobEvent seq test uses `ThreadPoolExecutor(max_workers=6)` with 30 concurrent appends — unit-level concurrency smoke; true multi-process/container stress testing remains a production-readiness task.
- Queue integration tests use synchronous `handle_job()` after enqueue (simulating worker process fetch). Real RQ multi-worker deployment remains later work.
- MinIO presigned URL HTTP GET verification requires the caller on the Docker network or localhost. The API-level test (URL contains bucket/key, expires, content_type) is in place.
- CI pipeline needs a service-backed job: `docker compose up -d postgres redis minio` → wait healthy → `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration`.

## 2026-06-26 Phase 5 Follow-ups

- No P0 blocker is open after the Phase 5 PostgreSQL runtime, queue worker, and MinIO integration pass.
- PostgreSQL runtime configuration, Alembic env override, Docker Compose infrastructure, and runbook now exist. A later deployment pass still needs pool sizing, migration rollback policy, backup/restore policy, and production secret injection.
- QueueWorkerRuntime now supports repository-backed job handling, duplicate enqueue stability, and retry idempotency tests. Later work still needs worker process supervision, dead-letter queues, exponential backoff policy, visibility timeout policy, and operational metrics.
- PostgreSQL JobEvent seq allocation now uses a transaction-scoped advisory lock keyed by `job_id`. Multi-process/container stress testing remains a production-readiness task beyond the default unit suite.
- S3/MinIO storage now supports live put/get/exists/presigned-url behavior when a boto3-compatible client or credentials are configured. Bucket creation policy, bucket lifecycle rules, object retention, access-control checks, and preview object policy remain open.
- Integration tests are intentionally opt-in with `MDI_RUN_INTEGRATION=1`; CI still needs a service-backed job that starts PostgreSQL, Redis, and MinIO and runs the integration marker.

## 2026-06-26 Phase 4 Follow-ups

- No P0 blocker is open after the Phase 4 production persistence hardening pass.
- Alembic baseline files and SQLAlchemy metadata now exist, but the runtime still needs a real PostgreSQL database URL, migration execution policy, pool sizing, and deployment runbook.
- Repository transaction boundaries are available through `RepositorySession` / `UnitOfWork`; application services still need to adopt them when the local Phase 2 runtime is replaced by durable workers.
- JobEvent seq allocation is concurrency-tested with repository-level in-process locking. Before multi-process workers, PostgreSQL should use row locking, advisory locking, or a per-job sequence allocation strategy.
- ToolCall and Artifact writes have idempotent repository behavior. A later queue phase still needs explicit worker attempt records, retry policy, crash recovery policy, and dead-letter handling.
- S3/MinIO metadata mapping remains clear, but live presigned URL generation, bucket policy, retention/lifecycle rules, and access-control checks remain future work.

## 2026-06-26 Phase 3 Follow-ups

- No new P0 blocker is open after the Phase 3 persistence foundation pass.
- Repository interfaces and SQLite-testable SQLAlchemy implementations now cover Project, Dataset, DataProfile, Job, JobEvent, ToolCall, Artifact, Recipe, and Report. A later phase still needs production transaction boundaries, Alembic adoption, PostgreSQL connection/session lifecycle, and idempotent worker writes.
- JobEvent seq cursor semantics are implemented for the local runtime and repository layer, including in-process duplicate-seq protection. A later phase still needs database-level multi-process locking strategy, production SSE backpressure, heartbeat, auth checks, and reconnect/load behavior under concurrent workers.
- Artifact storage mapping now covers local files and S3/MinIO-compatible metadata. A later phase still needs a live object-storage client, presigned URL policy, access-control checks, retention/lifecycle policy, and preview generation strategy.
- `reports` now has repository coverage and migration metadata. Report-specific API list/detail routes beyond artifact/report downloads remain future work.
- `S3CompatibleArtifactStorage.signed_url()` intentionally returns a `not_implemented` placeholder until live credentials, bucket policy, and signed URL expiry rules are decided.

## 2026-06-25 Phase 2 Acceptance Audit Follow-ups

- No new P0 blocker is open after the Phase 2 acceptance hardening pass.
- Phase 2 Recipe and AnalysisPlan schema shape is now aligned with the shared schema. Future schema changes should update `docs/13_SHARED_SCHEMA_SPEC.md`, Python schemas, TypeScript schemas, runtime emitters, and tests together.
- Ignored verification outputs (`node_modules`, `.next`, pytest cache/temp directories, Python bytecode, and TypeScript build info) are intentionally not part of Git or archive handoffs and should be cleaned before packaging.

## 2026-06-25 Phase 2 Follow-ups

- Phase 2 now proves the repository/API shape with in-memory state. A later phase still needs to decide the exact PostgreSQL repository interfaces and migration path for projects, datasets, jobs, tool calls, events, artifacts, recipes, and reports.
- Phase 2 artifact lookup reads local files directly. A later phase still needs to map the same API contract to MinIO/S3 signed URLs and access-control checks.
- Phase 2 job creation drains the LocalWorkerRuntime immediately for deterministic acceptance. A later phase still needs durable queue semantics, retry/cancel behavior, and SSE cursor persistence.
- Phase 2 supports local file paths and inline small text uploads for acceptance. Production upload sessions, object-storage direct upload, and file security limits remain future work.

## 2026-06-25 Phase 1 Acceptance Follow-ups

- Phase 1 now accepts `preview_png` as a required artifact family, but the MVP implementation may use a minimal valid PNG fallback when Kaleido/Chromium is unavailable. V1 still needs a decision on whether render workers must install and manage Kaleido/Chromium for real chart snapshots.
- Phase 1 product-flow acceptance is currently proven by an in-memory deterministic runtime. Next phase must decide the exact repository/API shape for replacing demo project/dataset/job/artifact state.
- The `/jobs/{job_id}/events/stream` route now exposes an SSE-style boundary without `sse-starlette`. Next phase must decide whether to keep plain `StreamingResponse` or introduce a Starlette-compatible SSE dependency.
- Phase 1 engineering reproducibility is now fixed on `uv.lock` for Python and `apps/web/package-lock.json` for frontend npm installs. Future dependency changes should update those lockfiles in the same commit as dependency declarations.

## Product

- 产品正式名称优先采用 Material Insight Studio、MatViz Agent Platform，还是 LabPilot Materials Workspace？
- V1 是否支持公开分享、匿名报告链接和外部协作者查看？
- V1 是否支持 PDF 报告导出？
- Guided / Expert 模式的最小可用范围是什么？

## Architecture

- 何时从 FastAPI 模块化单体拆分为独立 Data / Agent / Visualization 服务？
- LabPilot 集成时采用 NestJS BFF、API Gateway 代理，还是 iframe / embedded workspace？

## Frontend

- V1 是否支持用户自定义 Dashboard 拖拽布局？
- V1 是否评估 native MatterViz React 集成，替代部分 iframe artifact？
- 3D Viewer 的全屏、截图和结构选择器交互细节如何设计？

## Backend

- V1 分片上传和断点续传的最大文件规模目标是多少？
- Artifact / Recipe 何时需要独立 version tree 和 diff 视图？
- Artifact 生命周期和自动清理策略如何定义？

## Agent

- V1 Expert 模式是否允许用户手动编辑 JSON Plan 后再执行？
- V1 多模型路由按哪些任务类型拆分：Planner、Explainer、Report，还是按成本等级？
- V1 工具文档 RAG 使用 pgvector 还是 Qdrant？

## Materials Domain

- V2 VASP 输出优先解析 vasprun.xml、OUTCAR、XDATCAR 还是 DOSCAR？
- V1 代表结构聚类使用 composition embedding 还是 structure fingerprint？
- V1 首批高级工具优先实现 phonon、trajectory、RDF/XRD，还是 ML error-by-domain？
- V1/V2 外部生态集成优先级如何排序：Materials Project、OPTIMADE、AiiDA、atomate2，还是内部数据库 connector？
- 电子结构工具是否进入 V2 核心范围，还是作为专业插件优先接入？

## Security

- V1 组织级 BYOK 的继承、撤销和预算模型如何设计？
- V1 Prompt injection 模型辅助检测使用哪类评估集？
- V2 是否需要 gVisor / Firecracker / Kubernetes Jobs 等更强隔离？

## Implementation

- MVP 是否接受 `preview_png` 继续保持 optional，还是在 render-worker 里显式安装并管理 Kaleido/Chromium？
- ZIP 安全解包的 MVP 限制值如何定：最大文件数、最大展开大小、最大嵌套层级？
- EXTXYZ with lattice：已决定优先通过 ASE 解析后转 pymatgen Structure，不再单独实现轻量 parser。
- V1/V2 manifest 工具在进入可执行阶段前，是否要求先补齐与 MVP 同等级的 `additionalProperties=false` paramsSchema？
- 下一阶段实现 SSE 时需要选择与 `fastapi 0.115.x` / `starlette 0.46.x` 兼容的 SSE 方案；当前全局环境中的 `sse-starlette 3.4.1` 要求 `starlette>=0.49.1`，不能直接作为项目依赖锁定。
## 2026-07-04 Official pymatviz Examples Evidence Pack Follow-ups

- Source provenance still needs official commit pinning for a final publication-quality report. Current evidence marks `source_commit: unresolved` and `source_commit_status: TODO_PIN_BEFORE_FINAL_REPORT`.
- Official examples that require script/notebook execution remain `PARTIAL_PASS`; decide whether a future phase should build a controlled script/notebook import path or keep them as reference-only mappings.
- Composition and structure adapters exist, but Planner tool routing for official example workflows is not yet productized. Decide whether Phase 10 should add prompt/profile-based routing beyond `ml.basic_metrics`.
- Phonon, Brillouin zone, advanced MatterViz widgets, classification curves, and richer Plotly/table/report outputs remain future adapter/tool work.

## 2026-07-06 Phase 10B-1 Follow-ups

- Phase 10B-1 closes adapter-level implementation for the first composition visualization batch, but browser/API evidence is still required in Phase 10B-2.
- Current formula parsing intentionally supports common formula strings and reports warnings for malformed, unsupported, or unknown-element inputs. Complex formula grammar remains a future hardening area.
- HTML artifacts are generated when Plotly export is available; JSON, summary, and recipe remain the required deterministic evidence.
- Structure viewer polish, XRD, RDF, phonon, Brillouin zone, and notebook/script extraction remain out of scope for this phase.

## 2026-07-06 Phase 10B-2 Follow-ups

- Phase 10B-2 closes browser/API/artifact evidence for the five composition visualization adapters on the Ward direct-uploadable case.
- Formula parsing hardening remains open for complex formulas, malformed values, and unknown-element edge cases beyond current warning behavior.
- Remaining material-domain questions now move to structure and physics planning: lightweight structure summaries, 3D viewer polish, XRD, RDF, phonon, Brillouin zone, and notebook/script extraction.
- Browser/API evidence still does not claim Matbench, MP, CAMD, WBM, notebook-only, script-only, or external-data official examples are verified.

## 2026-07-07 Phase 10C-2 Follow-ups

- Phase 10C-2 closes browser/API/artifact evidence for the five lightweight structure adapters on deterministic simple cubic fixtures.
- Spacegroup handling was verified through the available symmetry path; future work should still harden tolerance policy and dependency diagnostics across malformed or lower-symmetry structures.
- Remaining material-domain questions now move to advanced structure and physics planning: 3D viewer, XRD, RDF, coordination histogram, phonon, Brillouin zone, and notebook/script extraction.
- Browser/API evidence still does not claim unsupported official structure examples, notebook-only cases, script-only cases, or external-data cases are verified.

## 2026-07-07 Phase 10D Follow-ups

- Phase 10D closes the planning decision that advanced structure visualization should start with viewer scene metadata and export packages, not full interactive 3D.
- Open implementation question: should `structure.viewer_3d_contract` be implemented as a schema-only optional tool in Phase 10D-1, or remain documentation-only until renderer work begins?
- Static physics tools still need dependency and numeric policy decisions: coordination neighbor strategy, XRD wavelength/tolerance, RDF cutoff/binning/normalization.
- Full interactive viewer work still needs renderer choice, WebGL fallback, screenshot determinism, sandboxing, and artifact-size policy.
- Phonon tools still need input data contracts, unit policy, phonopy/pymatgen dependency policy, and direct-uploadable fixtures.
- Official advanced structure examples remain mapping or future-scope references; no new official examples are verified by Phase 10D.

## 2026-07-07 Phase 10D-1 Follow-ups

- Phase 10D-1 closes implementation of static viewer scene metadata and export package artifacts.
- Browser/API evidence for these two tools remains open for Phase 10D-2.
- Optional `structure.viewer_3d_contract` remains open; it was not needed to ship the static `viewer_scene.json` contract.
- Bond inference is intentionally simple and deterministic; future full viewer work should revisit bond policy and element styling before interactive rendering.
- Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon, notebook extraction, and script execution remain open.

## 2026-07-08 Phase 10D-2 Follow-ups

- Phase 10D-2 closes Browser/API/artifact evidence for `structure.viewer_scene_metadata` and `structure.viewer_export_package`.
- Browser screenshots currently validate static artifact preview pages and generated artifacts; a future Phase 10D-3 can harden the product Artifact Gallery preview before any WebGL renderer work.
- Optional `structure.viewer_3d_contract` remains open; it was still not required for the static `viewer_scene.json` / `viewer_assets_manifest.json` evidence contract.
- The generated pymatgen Structure JSON input fixture is a small Phase 10D-2 evidence fixture, not an official benchmark claim.
- Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon, notebook extraction, script execution, and unsupported official example verification remain open.

## 2026-07-08 Phase 10D-3 Follow-ups

- Phase 10D-3 closes static frontend preview hardening for `viewer_scene.json` and `viewer_assets_manifest.json`.
- Static preview evidence now covers desktop and mobile screenshots, but it still does not validate any WebGL renderer because no renderer exists.
- Optional `structure.viewer_3d_contract` remains open; current frontend preview consumes the `viewer_scene.json` and `viewer_assets_manifest.json` contracts directly.
- Next material-domain planning should move to Phase 10E static structure physics plot planning for XRD, RDF, and coordination histogram policies.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, and unsupported official example verification remain open.

## 2026-07-08 Phase 10E Follow-ups

- Coordination histogram implementation still needs final cutoff defaults, tolerance defaults, and expected counts for simple cubic / NaCl fixtures.
- XRD implementation still needs pinned radiation source defaults, peak merge tolerance, and fixture peak windows before coding.
- RDF remains open until normalization, cutoff, binning, finite-size warnings, and species-pair policy are fixed.
- Official widget/script examples for XRD/RDF remain mapping references only; direct-uploadable benchmark evidence is still absent.
- Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, trajectory RDF, experimental XRD fitting, notebook extraction, script execution, and external API workflows remain open.

## 2026-07-08 Phase 10E-2 Follow-ups

- Phase 10E-2 closes browser/API/artifact evidence for `structure.coordination_hist` on bounded small CIF, POSCAR, and generated Structure JSON cases.
- `coordination_hist_plot.json` is currently verified as static chart JSON / static preview evidence; richer chart rendering can be considered later without changing the adapter contract.
- XRD remains open until radiation source defaults, peak merge tolerance, and fixture peak windows are pinned.
- RDF remains open until normalization, cutoff, binning, finite-size warning, and species-pair policy are fixed.
- Advanced local environment classification remains deferred; current evidence only covers deterministic distance-cutoff coordination counts.
- Full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and unsupported official example verification remain open.

## 2026-07-08 Phase 10E-3 Follow-ups

- Phase 10E-3 recommends `structure.xrd` as the Phase 10E-4 implementation target.
- XRD implementation still needs pinned CuKa defaults, two-theta range, peak merge tolerance, intensity threshold, peak sorting, rounding, and fixture peak windows.
- RDF remains open until normalization, periodic-image handling, cutoff, binning, finite-size warning, and partial-pair policy are fixed.
- Official XRD/RDF examples remain mapping references only; direct-uploadable benchmark evidence is absent.
- XRD/RDF browser/API evidence remains future work after implementation.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and unsupported official example verification remain open.

## 2026-07-08 Phase 10E-4 Follow-ups

- Phase 10E-4 closes implementation of `structure.xrd` with a deterministic CuKa-only XRD policy.
- Browser/API/artifact evidence for `structure.xrd` remains open for Phase 10E-5.
- XRD fixture tolerance can be broadened later, but Phase 10E-4 pins deterministic sorting, rounding, intensity filtering, two-theta filtering, and peak limits.
- RDF remains open until normalization, periodic-image handling, cutoff, binning, finite-size warning, and partial-pair policy are fixed.
- Experimental XRD fitting, Rietveld refinement, profile broadening, texture correction, and database lookup remain out of scope.
- Official XRD/RDF examples remain mapping references only; direct-uploadable PASS evidence is absent.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and unsupported official example verification remain open.

## 2026-07-08 Phase 10E-5 Follow-ups

- Phase 10E-5 closes API/artifact/security/negative-routing evidence for `structure.xrd`.
- Real browser screenshot capture remains open for this phase because the local environment did not expose the in-app browser Node REPL tool and did not have an installed browser automation runtime. No screenshot was fabricated.
- `xrd_plot.json` is verified as static chart JSON / static preview evidence; rendered stem chart UI remains deferred.
- RDF remains open until normalization, periodic-image handling, cutoff, binning, finite-size warning, and partial-pair policy are fixed.
- Experimental XRD fitting, Rietveld refinement, profile broadening, texture correction, and database lookup remain out of scope.
- Official XRD/RDF examples remain mapping references only; direct-uploadable PASS evidence is absent.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and unsupported official example verification remain open.

## 2026-07-08 Phase 10E-5R2 Follow-ups

- Phase 10E-5R2 closes the XRD browser screenshot blocker with real browser-rendered frontend screenshots.
- `xrd_plot.json` is still verified as static JSON / static chart metadata preview; rendered stem chart UI remains deferred.
- RDF remains open until normalization, periodic-image handling, cutoff, binning, finite-size warning, and partial-pair policy are fixed.
- Experimental XRD fitting, Rietveld refinement, profile broadening, texture correction, and database lookup remain out of scope.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and unsupported official example verification remain open.

## 2026-07-09 Phase 10E-6 Follow-ups

- Phase 10E-6 closes the RDF policy blocker: periodic-image, cutoff, binning, number-density normalization, partial-pair, finite-size/resource cap, and deterministic ordering policies are now fixed.
- RDF implementation is still not complete; Phase 10E-7 is the recommended single-scope implementation phase.
- RDF browser/API evidence remains deferred until after implementation, expected as Phase 10E-8.
- Official RDF examples remain mapping references only; no official RDF case is direct-upload PASS evidence.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, trajectory RDF, experimental fitting, notebook extraction, script execution, and external API workflows remain open.

## 2026-07-09 Phase 10F-5 Follow-ups

- Phase 10F-5 closes fixture-pack replay for the internal static physics direct-uploadable fixture pack.
- Official examples PASS evidence remains open because all replayed fixture cases are `internal_regression`, not `official_direct` or approved `official_derived_manual`.
- Future official PASS work requires eligible provenance, reviewer approval where needed, and direct replay verification.
- Phase 10F-6 should close the fixture-pack evidence boundary and decide whether to proceed to official-derived fixture approval planning or advanced viewer readiness planning.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, notebook extraction, script execution, external API workflows, and advanced local environment classification remain open.

## 2026-07-10 Phase 10F-11 Follow-ups

- Phase 10F-11 closes real browser evidence for JSON-only `viewer_scene.v1` preview.
- Phase 10F-12 remains reviewer-selected; reasonable options are minimal adapter implementation, additional preview evidence hardening, or runtime integration planning.
- Direct full `structure.viewer_3d`, WebGL renderer, Three.js integration, and phonon implementation remain not approved.

## 2026-07-12 Phase 10F-16 Follow-ups

- Decide whether the next inspection increment should implement explicit periodic images/minimum-image measurements or first close npm tooling upgrades.
- Keyboard orbit, advanced picking, measurements across periodic images, and persisted measurement reports remain open.
- The seven npm audit nodes require review during the next compatible Next/Vitest upgrade; none is newly renderer-reachable.
- Phase 10D legacy removal remains deferred until a separate migration/deprecation decision.
- Future adapter work must preserve inert JSON artifact boundaries and must not introduce renderer execution.

## 2026-07-12 Phase 10F-17 Follow-ups

- Decide whether canonical bonds need optional endpoint image offsets; current renderer intentionally supports same-cell replication only.
- Periodic identity and bounded supercells provide partial foundations for trajectory and phonon animation, but no time/frame contract exists.
- Persisted supercells, structure mutation, minimum-image chemical inference, CrystalNN/VoronoiNN, defects, surfaces, and volumetric data remain open.

## 2026-07-12 Phase 10F-18 Follow-ups

- Decide whether a future explicit-input topology source needs a separate provenance sub-contract before authoritative connectivity is accepted.
- Distance-cutoff periodic topology is complete for visualization but remains non-authoritative; CrystalNN/VoronoiNN, bond order, and valence are open.
- Periodic identity/topology can support trajectory or phonon contract planning, but no frame/time/displacement contract exists yet.

## 2026-07-12 Phase 10F-20 Follow-ups

- Define artifact retention and regeneration windows before removing Phase 10D direct compatibility tools.
- Decide whether any future explicitly lossy archival converter is preferable to regeneration; none is currently authorized.

## 2026-07-13 Phase 10F-21 Follow-ups

- Validate accessibility and touch interaction under degraded mode in Phase 10F-22.
- Absolute hardware GPU memory remains outside browser-portable evidence; retain bounded proxy metrics.

## 2026-07-13 Phase 10F-22 Follow-ups

- Physical NVDA, JAWS, VoiceOver, TalkBack, and broad device gesture testing remain outside automated CI evidence.
- Forced-colors emulation support differs by browser; retain CSS plus recorded media-query evidence and schedule physical Windows high-contrast review.
- Keyboard orbit is bounded and deterministic; keyboard-only atom traversal belongs to the separately reviewed advanced picking scope.

## 2026-07-13 Phase 10F-23 Follow-ups

- Decide whether measurement artifacts should become persisted backend artifacts; current downloads are deterministic local inert JSON only.
- Lasso/box selection and persisted annotations remain intentionally absent.
- Supercell view-state productization, clipping, camera presets, and vector export remain separate queued scopes.

## 2026-07-13 Phase 10F-26 Follow-ups

- Decide whether a future PDF/report phase should use browser-native layout or a reviewed local PDF dependency.
- Define font embedding, pagination, metadata, accessibility, and vector/raster policies before PDF implementation.
- Decide whether local export state should ever become a persisted backend artifact; it currently grants no execution authority.

## 2026-07-13 Phase 10F-27 Follow-ups

- Formal minimal viewer product registration is closed; trajectory, phonon, Brillouin-zone, volumetric, and editing require independent contracts and reviews.
- Distance-cutoff periodic topology remains non-authoritative; explicit-input authoritative topology provenance remains an open scientific contract decision.
- Broad physical GPU/device and assistive-technology lab coverage remains outside automated browser evidence.

## 2026-07-13 Phase 10 Closure Follow-ups

- Phase 11 must define official benchmark/reference certification separately from current candidate scientific outputs.
- Fresh real browser evidence remains required when product browser behavior changes; CI currently validates committed browser evidence integrity without installing a new browser dependency.
- Trajectory, phonon, Brillouin-zone, volumetric, defects/surfaces, and editing remain independent future contracts.
- **Open after Phase 10G-2: formal trajectory product closure.** G-3 must finish long-trajectory performance/browser acceptance, decide static-reference topology completion, and formalize planner-visible registration.
- **Closed in Phase 10G-2: dynamic display foundation.** Validated frame mapping, playback, identity, variable lattice, bounded cache, fallback, accessibility/mobile, and initial browser matrix are implemented.

## 2026-07-14 Phase 10H-1 Follow-ups

- Decide whether a stable persisted pymatgen phonon-band object deserves a separate approved source adapter; no arbitrary object deserialization is authorized.
- Phase 10H-2 must define DOS production independently and preserve the established band structure identity/unit/source lineage.
- Combined band+DOS, eigenvectors, mode animation, LO-TO directional visualization, and phonon calculation remain open and must not be inferred from the static band tool.
- Physical assistive-technology and broad device rendering remain outside automated browser evidence.

## 2026-07-14 Phase 10H-2 Follow-ups

- Decide whether stable pymatgen phonon-DOS serialization deserves a separately approved source adapter; arbitrary deserialization remains forbidden.
- Directional projections require an explicit coordinate-basis contract.
- Phase 10H-3 may combine independently validated band and DOS but must not renormalize either source.
- Physical assistive-technology and broad-device rendering remain outside automated evidence.
