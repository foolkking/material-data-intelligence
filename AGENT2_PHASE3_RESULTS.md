# Agent 2.0 Phase 3 Results

Date: 2026-08-22
Starting HEAD: `97ecfa3fcbee927dc32f6e4c5c730ec839c1e7b3`
Verdict: `COMPLETE`

## Scope

Implemented `PLAN_READY`, deterministic capability eligibility, immutable
resolution/plan persistence, nine manifests across five scientific families,
registered preconditions, stable fingerprints, deterministic fast-path
planning, bounded structured LLM planning with one repair, strict typed plan
validation, deterministic Tool binding, and existing AnalysisPlan 0.2
validation/attachment. No Job, ToolCall, Artifact or execution is created.
Historical Result reuse is supported when the persisted Result bundle exposes
an authorized exact-version `ScientificObjectRef` output; artifact-only legacy
results remain unbindable rather than being converted into runtime identities.

## Migration

`0019_agent2_capability_planning` follows
`0018_agent2_orchestration_decisions`. It extends the ResearchTurn status check
with `PLAN_READY` and creates `research_capability_resolutions` and
`research_capability_plans`, each unique and immutable per ResearchTurn.
The tables use `fk_rcr_turn`, `fk_rcp_turn`, `fk_rcp_resolution`, unique
constraints `uq_research_capability_resolutions_turn` and
`uq_research_capability_plans_turn`, plus validated planner-mode/status checks.

## Capability Registry and Eligibility

Registered manifests: `structure.rdf`, `diffraction.theoretical_xrd`,
`diffraction.experimental_theoretical_comparison`,
`ml.regression_evaluation`, `trajectory.msd`, `trajectory.diffusion`,
`phonon.band`, `phonon.dos`, and `phonon.band_dos`.

RDF is `ELIGIBLE` for an exact crystal structure. XRD comparison is
`CONDITIONAL` until the theoretical-XRD output is planned. Wrong object types,
missing producer chains and incompatible Tool versions are `INELIGIBLE`.

## Planning and Binding

Unique RDF/XRD/trajectory strategies use deterministic planning. Alternative
phonon strategies use the versioned LLM planner boundary. The planner input
uses typed input/output port views and never includes ToolBinding metadata.
It also receives deterministic opaque slot bindings and compatible producer
keys; multiple producer/result alternatives require LLM planning. Invalid
opaque refs receive one repair and then fail closed. Canonical bindings include:

- `structure.rdf -> structure.rdf -> AnalysisPlan 0.2`
- `diffraction.theoretical_xrd -> structure.xrd`
- `diffraction.experimental_theoretical_comparison -> structure.experimental_xrd_comparison`
- `trajectory.msd -> trajectory.msd -> trajectory.diffusion`
- `current ScientificResult output object -> PREVIOUS_RESULT -> exact normalized object version`

All successful bindings pass the existing dependency validator and
PlanValidator. Exact ScientificObjectVersion identity and explicit parameters
are retained.

## Tests

Local results at the implementation checkpoint:

- Phase 3 deterministic suite: `19 passed, 1 deselected` with explicit P3-C01
  through P3-C20 coverage (related cases share focused tests);
- Phase 3 live DeepSeek qualification: `1 passed`;
- combined Agent2 selection: `69 passed, 5 deselected`;
- full backend final current-source run: `1657 passed, 1 skipped, 90 deselected`;
- PostgreSQL/Redis service-backed Agent2 Phase 1/2/3: `3 passed`;
- frontend Vitest: `565 passed` across `84` files;
- frontend typecheck: passed;
- isolated production build: passed.

The live gate exposed two real integration defects: the versioned planner
prompt did not explicitly say `JSON` while the transport used JSON mode, and
compact colon-delimited port contracts allowed field shifting. The prompt now
requests one JSON object and the planner receives typed port views. Live
qualification then passed. `npm run lint` is not a valid automated gate in the
current repository because the obsolete `next lint` script opens interactive
ESLint initialization; no lint PASS is claimed. Implementation commit
`855fe3f46298882971227bda684f2529a5823469` passed current-HEAD GitHub
Actions run `32580235322`: Unit Tests, service-backed PostgreSQL/Redis/MinIO,
Frontend tests/typecheck/build/Phase 12-6/12-7, and Linux/Windows scientific
replay all completed successfully.

## No-execution Evidence

The end-to-end deterministic processor test persists one AnalysisPlan and
asserts `Job delta = 0`, `ToolCall delta = 0`, and `Artifact delta = 0`.
Duplicate delivery remains one resolution, one CapabilityPlan and one
AnalysisPlan.

## Not Implemented in Phase 3

Job creation/attachment, queue execution, Execution Supervisor, `PLAN_READY ->
QUEUED`, Job/ToolCall progress projection, incremental results, production
ScientificResult projection, Scientific Interpreter, final scientific answer,
long-session semantic memory, Report Composer, Data Management execution,
professional Viewer integration, full 62-Tool mapping and Tool Pack plugins.

Artifact-only historical Result reuse remains an explicit compatibility
boundary: AnalysisPlan 0.2 has no authorized source-binding form for a prior
runtime Artifact and forbids placing Artifact refs in step inputs. Results that
project an exact output ScientificObjectVersion are reusable; other legacy
results fail closed without smuggling Artifact IDs into plans or silently
recomputing.
