# AGENT2_PHASE10_RESULTS

## Canonical Fixture / Three-Family Recheck — 2026-08-25 (latest)

### Root-cause classification

`HISTORICAL_FIXTURE_PROFILE_MISMATCH`: the old silicon object was correctly
rejected because its historical profile did not expose coordination readiness.
Fresh current-generation inputs now pass the production profile contracts; no
eligibility prerequisite was weakened.

### Fixture readiness and real execution

- **Structure**: object `773089f9-3ce8-4645-92dd-2f62c64cba89`, version
  `65f56d10-008d-445d-ab2f-228aebf1835b`, profile `2.1`, coordination input
  `READY`. Real same-stack chain completed with Turn
  `cf329b23-d6ec-4aa9-a40e-7ab5457cabce`, Plan
  `plan_cb353bb65deb44ea9afb9ae7`, Job
  `job_agent2_cf329b23d6ec4aa9a40e7ab5457cabce`, 2 ToolCalls, 6 Artifacts,
  Result `93d6fe20-2452-43f9-8e53-bca1aeec1ba1`, and valid grounded
  interpretation `f1c342c8-be77-4dd8-97b4-7128092a1e73`.
- **Electronic band**: object `54017eba-e71e-4af0-8d79-763124bbd72d`,
  version `0a389623-928d-4500-8dd3-b1759921a940`, profile `2.4`, ready.
  Result `f6246dc8-39e1-405a-959d-c17e201af546` and follow-up grounded
  interpretation `f0252192-1c5b-4536-b98d-ea12af786637` are persisted.
- **Dataset table**: object `b8a1a55b-d32f-45f3-b421-df075dc3c05d`, version
  `622ef3d7-301c-420a-aa75-7dda551cf7ef`, profile `2.0`, 3 bounded rows with
  formula and stable `sample_id`. The final real chain is Turn
  `a4f6f737-c7e5-4999-8063-d6c1911f3bb0`, Plan
  `plan_58e97082a5954e509c10a8a8`, Job
  `job_agent2_a4f6f737c7e549998063d6c1911f3bb0`, 1 ToolCall, 4 Artifacts,
  Result `35bdb8fe-76e5-4f63-809d-e918b30ae483`, and valid grounded
  interpretation. This was fixed through the canonical profile/source bridge;
  direct database insertion was not used.

### Browser and release status

The supplied Chromium runner passed authenticated Table mobile (`390x844`),
Structure desktop, and Band desktop viewer smoke with zero fatal errors,
unhandled rejections, or critical request failures. A real authenticated
Structure click path reached the exact ContextSnapshot and a deterministic
two-capability `PLAN_READY` plan. The newly added existing-UI dispatch bridge
is typechecked, but repeated diagnostic reruns exhausted the local API
PostgreSQL connection pool before a clean dispatched browser Job/Result/Viewer
run could be captured. Therefore the three-family authenticated natural-language
browser gate is **not claimed**. No Commit A/B or exact-head CI was created.

Focused current changes: `55 passed, 1 skipped`; touched Ruff, compileall,
frontend focused test, typecheck, production build, and diff checks pass.
The authoritative verdict remains `FUNCTIONAL_PHASE10_CLOSURE = FAIL`,
`AGENT2_PHASE10 = PARTIAL`, `READY_FOR_PHASE11 = NO`.

### Stage 0 connection-pool diagnosis — 2026-08-25

`pg_stat_activity` captured approximately 98 idle PostgreSQL sessions after
the prior authenticated polling attempts, with one active diagnostic session
and no idle-in-transaction accumulation. The owner was the request lifecycle:
each API route call created a distinct SQLAlchemy Engine and therefore a new
pool. This was not fixed by increasing pool limits. `database.py` now reuses a
configuration-keyed process Engine and exposes explicit disposal for process/
test teardown; health checks using special connection arguments remain separate.
The regression test repeats the request-style factory eight times and verifies
one Engine/pool and zero checked-out connections after each scope. Targeted
tests are `46 passed, 1 skipped`; touched Ruff, compileall, typecheck, build and
diff checks pass. A clean post-fix browser dispatch and exact-SHA release
closure are still required.

## Canonical Fixture Closure Recheck — 2026-08-25 (authoritative update)

The fresh Structure chain is now complete through grounded interpretation:
Turn `cf329b23-d6ec-4aa9-a40e-7ab5457cabce`, exact object/version
`773089f9-3ce8-4645-92dd-2f62c64cba89` /
`65f56d10-008d-445d-ab2f-228aebf1835b`, Plan
`plan_cb353bb65deb44ea9afb9ae7`, Job
`job_agent2_cf329b23d6ec4aa9a40e7ab5457cabce`, 2 ToolCalls, 6 Artifacts,
Result `93d6fe20-2452-43f9-8e53-bca1aeec1ba1`, and DeepSeek grounded
interpretation `f1c342c8-be77-4dd8-97b4-7128092a1e73` (`VALID`). This is a
real PostgreSQL/Redis/MinIO fresh-worker execution and preserves exact source
refs. The earlier Result `440636e5-d4e6-4410-b2e4-6909399cde82` remains
SUCCESS/CURRENT and is retained as historical diagnostic evidence.

The minimal grounding correction now excludes opaque UUID/provenance tokens
from quantitative-token parsing and treats lowercase `k` labels as k-point
labels rather than Kelvin. Focused interpretation/Phase 10/worker tests are
`44 passed, 1 skipped`; touched Ruff and compileall pass. A fresh electronic
Agent chain also completed with Result `f6246dc8-39e1-405a-959d-c17e201af546`
and a valid follow-up interpretation `f0252192-1c5b-4536-b98d-ea12af786637`.

The dataset Agent path was attempted against the persisted materials table but
the current validator correctly rejected requirement `data.explore_materials`
for object type `materials.table` (the manifest requires `materials.dataset`).
This is an unresolved typed contract/input-bridge gap, not a reason to weaken
eligibility. DOS remains blocked by the existing source checksum guard.

The three-family browser closure and release gates therefore remain open:
dataset Agent execution, full result/viewer browser evidence, reuse/multiturn
qualification, final Commit A/B, push, and exact-head CI are not claimed.

## Closure Campaign Update — 2026-08-25

This update is authoritative for the current fixture-readiness and browser
closure attempt. It does not replace the historical failed-task records.

### Root-cause classification

`HISTORICAL_FIXTURE_PROFILE_MISMATCH`: the previous persisted silicon Structure
was correctly rejected because its profile did not contain the typed readiness
required by the coordination capabilities. A new current-generation Structure
profile produced through the upload/profile authority is `READY`; eligibility
was not weakened.

### Fixture readiness

The machine-readable admission matrix is
`docs/phase10/agent2_phase10_fixture_readiness.json`.

- Structure: `ADMITTED / READY`, object
  `773089f9-3ce8-4645-92dd-2f62c64cba89`, version
  `65f56d10-008d-445d-ab2f-228aebf1835b`, profile contract `2.1`,
  `coordinationInputStatus=READY`.
- Electronic band: `ADMITTED / READY`, object
  `54017eba-e71e-4af0-8d79-763124bbd72d`, version
  `0a389623-928d-4500-8dd3-b1759921a940`, profile contract `2.4`.
- Dataset table: `ADMITTED / READY`, object
  `b8a1a55b-d32f-45f3-b421-df075dc3c05d`, version
  `622ef3d7-301c-420a-aa75-7dda551cf7ef`, profile contract `2.0`,
  three bounded rows and stable `sample_id` values.
- Electronic DOS profile is ready, but its viewer projection currently fails
  the existing `VIEWER_SOURCE_CHECKSUM_MISMATCH` guard; no checksum or viewer
  contract was weakened.

### Authenticated Chromium Viewer smoke

Using the supplied Chromium executable, the same authenticated frontend/API
stack passed:

- Scientific Table at `390x844`: 3/3 bounded rows, scientific columns
  `formula`, `band_gap`, `density`, `sample_id`, row selection, document/body
  widths 390/390, fatal errors 0.
- Structure at `1280x720`: professional `scientific.structure-3d`, exact
  version context, formula/site/lattice metadata, no global overflow or
  console/page errors.
- Electronic band at `1280x720`: professional
  `scientific.band-structure`, eV/energy/Fermi metadata and no browser errors.

The reusable acceptance runner is
`apps/web/test/phase10-canonical-browser-acceptance.mjs`.

### Natural-language execution attempt

An authenticated Structure Turn using the exact new object/version and the
natural-language request “请分别使用 CrystalNN 和 VoronoiNN 两种独立的局部
配位算法分析这个结构，并比较它们的结果。” reached a real immutable
ContextSnapshot and a deterministic AnalysisPlan 0.2 containing both
coordination capabilities. The same-stack execution worker then completed both
registered tools: `2 ToolCalls`, `6 Artifacts`, and a persisted Result snapshot
`440636e5-d4e6-4410-b2e4-6909399cde82` for Turn
`f6107f89-ceda-4100-b895-e194adf81e38`. A minimal worker-side bridge correction
in `services/workers/mdi_workers/queue_runtime.py` allows an exact-version plan
to proceed to the existing exact ScientificObjectVersion hydrator when a stale
dataset export cannot be read; plans without exact refs still fail closed.
The subsequent grounded interpretation could not complete in the fresh worker
because its provider configuration was unavailable (`INTERPRETATION_PROVIDER_FAILED`),
so no grounded Assistant answer or three-family Agent browser gate is claimed.
No fake execution records were created and no capability prerequisite was
relaxed.

### Current verdict

`FUNCTIONAL_PHASE10_CLOSURE = FAIL`

`AGENT2_PHASE10 = PARTIAL`

`READY_FOR_PHASE11 = NO`

Commit A/B and exact-head CI were not created or claimed because the required
three-family authenticated execution gate is not green.

## Verdict

`PARTIAL` — Batch 1 contracts, deterministic resolution, Result projection,
live semantic routing, service-backed execution, authenticated table browser
coverage and current-head backend regression are now evidenced. The mandatory
three-family authenticated execution/browser campaign and exact-head CI are
still open; no completion claim is made.

## Repository baseline

- Starting/final implementation baseline: `e8118ebfbdfff6c44e7e2b5f583c5f5a8dfb41a6`
- Alembic head remains `0025_agent2_scientific_selection`.
- Registered production tools: 62; planner-visible tools: 62.
- Agent2 baseline capabilities: 9; Batch 1 additions: 8; total active: 17.

## Current Tool Census

`agent2_tool_census.json` is the current-head machine-readable inventory. Each
tool records its version, family, stage, planner visibility and classification:
`AGENT2_ACTIVE`, `AGENT2_CANDIDATE`, or `FUTURE_SCOPE`. Registry membership alone
does not grant Agent2 authority.

## Batch 1 Manifest

`agent2_phase10_batch1_manifest.json` freezes eight additions:

| Capability | Existing binding | Contract | Family |
| --- | --- | --- | --- |
| `structure.coordination_hist` | `structure.coordination_hist` | `phase10e1.coordination_hist.v1` | structure |
| `structure.coordination_crystalnn` | `structure.coordination_crystalnn` | `phase10n1.crystalnn_coordination.v1` | structure |
| `structure.coordination_voronoinn` | `structure.coordination_voronoinn` | `phase10n1.voronoinn_coordination.v1` | structure |
| `trajectory.rdf` | `trajectory.rdf` | `phase10n4.trajectory_rdf.v1` | trajectory |
| `electronic.band_structure` | `electronic.band_structure` | `phase10n5.electronic_band_structure.v1` | electronic |
| `electronic.dos` | `electronic.dos` | `phase10n5.electronic_dos.v1` | electronic |
| `data.composition_space` | `dataset.composition_space` | `phase10k4.composition_space.v1` | dataset |
| `data.materials_explorer` | `dataset.materials_explorer` | `phase10k2.dataset_materials_explorer.v1` | dataset |

`structure.summary` and `composition.formula_statistics` remain backlog
candidates because their MVP primary payloads do not yet expose a versioned
Result contract. Technical viewer/export tools and phonon animation remain
outside Agent2 authority.

## Capability and planning contracts

New requirements are semantic, not Tool IDs. Resolution is deterministic,
input object types are checked before planning, exact object/version references
are preserved, and binding remains AnalysisPlan `0.2`. No raw Tool Registry is
sent to an LLM. Unknown or non-activated tools cannot be selected by Agent2.

## Result projection and provenance

Eight mature adapter schemas are accepted by the production payload validator
and mapped to canonical `agent2.*` projectors. Projectors create bounded result
items, tables/figures where supplied, evidence references and exact
`source_object_refs`; they do not infer new scientific numbers from curves or
raw artifacts. Units and declared limitations remain upstream-authoritative.

## Deterministic qualification

`tests/test_agent2_phase10_capabilities.py`: **24 passed**.

Covered: frozen Batch and family count, registry/tool binding validation, all
eight natural requirement mappings, wrong object types, typed multi-capability
planning, exact-version bindings, non-activated Tool rejection, all eight new
schema projectors, and malformed-schema fail-closed behavior.

Phase 3/contract/result focused regression after the change: **41 passed, 1
skipped**; the broader Agent2/Phase 10N focused set is **158 passed, 1
skipped**. The current full backend run is **1787 passed, 83 skipped**. The
post-fix focused contract run is **76 passed, 1 skipped**.

Frontend Vitest is **582 passed across 90 files**, typecheck and production build
are PASS. Ruff on all Phase 10 touched Python modules, compileall, `uv
lock --check` and `git diff --check` are PASS.

## Live / service / browser gates

- Live DeepSeek: the existing Agent2 qualification cases passed, and a fresh
  Phase 10 Batch-1 semantic routing matrix passed **8/8** with natural-language
  requests covering coordination histogram/CrystalNN/VoronoiNN, trajectory RDF,
  electronic band/DOS, composition space and materials exploration. These are
  provider decisions only; they intentionally create no Job.
- PostgreSQL/Redis/MinIO service-backed Phase 10 execution: **6 selected, 6
  passed, 0 failed, 0 errors, 0 skipped** using the local Docker services
  (`mdi-agent2-phase7-postgres`, Redis and MinIO). This includes coordination,
  trajectory RDF, electronic band/DOS, professional inventory, materials-ML and
  composition-space closures.
- Authenticated browser smoke: the real Chromium path passed login, Console,
  Research Workbench navigation, and the same-stack 390x844 Scientific Table
  click/selection gate. A fresh authenticated structure request was also
  submitted through the product Research path and produced a new Agent2 Turn;
  this is request-path evidence only, not a claim that a complete new-family
  Job/Result/Viewer browser golden path has been qualified.
- Browser evidence details: desktop data click selected `Fe2O3` with no new
  errors and no global overflow; mobile selected `Si` with
  `documentWidth=375`, `bodyWidth=375`, and `innerWidth=390`. The browser used
  the user-provided Chromium executable and the normal authenticated product
  API, not mocked network responses.
- A minimal context bridge correction now carries deep-linked exact
  object/version refs in `explicit_object_refs` and suppresses lower-priority
  historical object candidates. The focused contract run is **54 passed**.
  A fresh authenticated session then resolved to exactly one Structure, but
  the persisted silicon fixture was correctly rejected as
  `CAPABILITY_REQUIREMENT_UNSATISFIED` because it lacks the typed semantic
  input contract required by the new coordination capability. No fake Job,
  ToolCall, Artifact or Result was created.
- Full backend: PASS as recorded above. Frontend tests, typecheck, production
  build, compileall, `uv lock --check` and `git diff --check` are PASS. Exact
  Commit A/B and current-head CI remain pending.

## Security and scope

No migration, arbitrary code execution, shell/filesystem authority, provider
network fetch, plugin loading, viewer redesign or Phase 11 work was added.
Parameter surfaces remain owned by existing typed adapters and exact-version
authorization remains unchanged.

## Remaining gaps

Functional Phase 10 release qualification is incomplete until at least three
newly activated scientific families complete authenticated same-stack
natural-language execution through Job/Result/grounded answer/Viewer, the
canonical fixtures satisfy their typed input contracts, and the implementation
plus completion record receive exact-SHA CI. Do not declare
`AGENT2_PHASE10 = COMPLETE` or enter Phase 11 from this record.

## Stage 0 Clean Runtime Closure Attempt — 2026-08-25

After the process-scoped Engine cache fix, the API and worker were restarted
against the same PostgreSQL/Redis/MinIO stack. PostgreSQL stabilized at
`active=1`, `idle=6`, `idle-in-transaction=0`; the lifecycle regression passed
and no pool timeout occurred. The terminal-progress supervisor regression also
passed, preserving idempotent re-projection after a completed turn.

Fresh authenticated Chromium used the same stack with no SQLite or mocked
network. Structure Turn `21d40ce4-c299-485f-8b34-db29f1416dc8` completed the
CrystalNN + VoronoiNN path for exact object/version
`773089f9-3ce8-4645-92dd-2f62c64cba89` /
`65f56d10-008d-445d-ab2f-228aebf1835b`. Electronic Turn
`e96b22af-0bf5-4ef2-962e-05d20a5afe93` completed supplied Band Structure for
exact object/version `54017eba-e71e-4af0-8d79-763124bbd72d` /
`0a389623-928d-4500-8dd3-b1759921a940`. Dataset Turn
`6d16ce68-6cf1-4d93-8147-6d76fa35a784` completed Materials Explorer/Table for
exact object/version `b8a1a55b-d32f-45f3-b421-df075dc3c05d` /
`622ef3d7-301c-420a-aa75-7dda551cf7ef`. Each reached Job/ToolCall/Artifact/
Result/VALID interpretation and the appropriate professional Viewer.

All three browser paths recorded zero fatal console errors, unhandled
rejections, critical failed requests and authorization failures. The optional
report lookup 404s on Structure/Electronic are expected absence responses.
The 390x844 Table gate remains PASS with 3/3 rows, scientific columns, row
selection and zero global overflow; Structure and Band smoke remain PASS at
1280x720.

Current-head checks: full backend `1791 passed, 83 skipped`; frontend `582
passed across 90 files`; typecheck/build/touched Ruff/compileall/
`uv lock --check`/`git diff --check` PASS; current service-backed Phase 10 set
`12 selected, 12 passed, 0 failed, 0 errors, 0 skipped`.

Functional browser and service evidence is complete for the three canonical
families, but no Phase 10 implementation/completion commits were created or
pushed and no exact-SHA CI exists for this uncommitted worktree. The release
gate remains intentionally open:
`FUNCTIONAL_PHASE10_CLOSURE = PARTIAL`, `AGENT2_PHASE10 = PARTIAL`,
`READY_FOR_PHASE11 = NO`.
