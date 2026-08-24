# AGENT2_PHASE9_RESULTS

## Verdict

PARTIAL — deterministic viewer/selection implementation and dedicated
PostgreSQL/Redis/MinIO qualification pass. Final current-head CI is green;
authenticated browser golden paths remain unverified because action-time
credential confirmation was not available in this run.

## Starting State

- Starting HEAD: `45cd88327da2b4b529d5394d41f11523b88f310a`
- Starting origin/master: `45cd88327da2b4b529d5394d41f11523b88f310a`
- Implementation HEAD before closure hardening: `e02a14caaf91b22d52d0bf13089bfbe70af66d6a`
- Starting Alembic head: `0024_agent2_scientific_reports`
- Phase 1–8 authorities were preserved; no Phase 10 capability expansion was
  started.

## Viewer Infrastructure Audit

Existing Workspace renderers are reused: MatterViz/Three structure, Plotly
diffraction/RDF/electronic, trajectory, phonon, Brillouin-zone, volumetric and
bounded table surfaces. The new backend projection and frontend registry are
normalization layers, not a second ScientificObject model. Legacy Workspace,
Report and Report/Recipe routes remain readable.

## Viewer Capability Matrix

| Type | Renderer / projection | Selection | Linked/evidence | Status |
|---|---|---|---|---|
| Table / composition | bounded scientific table | row/column contract | source row context | PROFESSIONAL |
| Structure | MatterViz structure adapter | site/environment | metadata/table contract | PROFESSIONAL |
| Trajectory | existing trajectory surface | frame/atom | bounded context | PROFESSIONAL |
| XRD | Plotly comparison surface | peak/match | table/evidence route contract | PROFESSIONAL |
| RDF | existing Plotly/result surface | peak/bin | finding/evidence route contract | PROFESSIONAL |
| Band / DOS | electronic panels | k-point/energy | result context | PROFESSIONAL |
| Phonon | phonon panels | q-point/branch | result context | PROFESSIONAL |
| Brillouin zone | existing BZ renderer | point/segment | band contract | SUPPORTED |
| Volumetric | bounded field projection | field/region | metadata fallback | SUPPORTED |
| Archive / generic | safe metadata/download fallback | none | no false semantic link | FALLBACK |

This is an implementation inventory; browser evidence for every family is not
claimed until the authenticated browser gate is run.

## Viewer Registry And Shell

`ScientificViewerRegistry` resolves deterministically from exact object type,
schema and semantic role. `ScientificViewerProjectionService` authorizes the
project before reading MinIO, verifies checksums, and bounds table rows (500),
trajectory frames (256) and volumetric arrays (262,144 values). Missing or
invalidated sources return metadata-only scientific states. Viewer reads make
no LLM, Plan, Job, ToolCall, Artifact or ScientificResult writes.

`ScientificViewerShell` presents title, exact version, relevance, metadata,
limitations, selection and a single primary research action; technical
provenance is progressively disclosed.

The closure hardening commit aligned backend and frontend registry coverage for
RDF and Brillouin-zone objects, preventing an exact-version backend process
from silently resolving either type to the generic fallback.

## Scientific Selection And Linked Selection

`ScientificSelectionContext 1.0` preserves exact object/version, viewer,
selection type, bounded semantic locator, display label and optional evidence
locator. Migration `0025_agent2_scientific_selection` stores the selection in
immutable `ResearchContextSnapshot`. Authorization is repeated before
persistence. Provider-facing selection envelopes use opaque labels and never
contain database, Artifact, Job, ToolCall or DOM identities.

The frontend resolver exposes deterministic compatibility states for Structure
metadata/table, RDF finding/evidence, XRD evidence/table and Report-to-viewer
links. Selection deep links are decoded on a fresh Data page load.

## Exact-version, Relevance And Authorization

Viewer requests require exact object and version in the URL and reject
cross-project access before payload disclosure. Historical versions remain
historical; current-version changes do not upgrade an open Result, Report or
Evidence link. `CURRENT`, `STALE`, `SOURCE_MISSING` and `INVALIDATED` are
visible states. Missing and invalidated views retain safe metadata and
limitations without same-name substitution.

## No-computation Evidence

| Operation | Plan | Job | ToolCall | Artifact | Result | LLM |
|---|---:|---:|---:|---:|---:|---:|
| Viewer projection | 0 | 0 | 0 | 0 | 0 | 0 |
| Fresh RDF/XRD + selection gate | 0 | 0 | 0 | 0 | 0 | 0 |

## Service-backed Qualification

Dedicated Phase 9 selection: **3 passed, 0 skipped, 0 failed, 0 errors**.

- Fresh subprocess projection loaded persisted exact RDF and XRD source
  versions from PostgreSQL/MinIO with separate process IDs.
- A real ResearchTurn captured a semantic RDF selection in an immutable
  ContextSnapshot; all scientific counters remained unchanged.
- Redis/MinIO service settings and migration head `0025` were used; no fake
  Job, Artifact or Result was inserted by the qualification.

## Tests

- Phase 9 deterministic backend: `5 passed`.
- Agent2 Phase 1–9 focused: `140 passed, 13 skipped`.
- Frontend Vitest: `90 files / 581 tests passed`.
- Frontend typecheck: PASS.
- Production build: PASS (`.next-phase9-final`, 9/9 pages generated).
- `compileall`, targeted Ruff, `uv lock --check`, and `git diff --check`: PASS.
- Migration `0024 -> 0025 -> 0024` round-trip: PASS; fresh PostgreSQL service
  migration is covered by the service fixture.
- Full backend: `1759 passed, 83 skipped, 75 warnings`.
- Browser desktop/mobile: blocked pending action-time login confirmation in
  the in-app browser; no browser PASS is claimed.
- Viewer rendering and selection use zero LLM calls; no live provider gate is
  applicable to this read-only path.

## Product UX Acceptance

- `DATASET_FIRST_VIEW_DOMINATED_BY_DATA`: YES in the existing Data workbench
  layout (browser/context + large viewer + inspector).
- `EMPTY_STATUS_PANELS`: explicit loading/error/source-missing/unsupported
  states; no blank technical panel is introduced.
- `PRIMARY_ACTIONS_PER_VIEW`: one primary research action; technical actions
  remain secondary.
- `USER_VISIBLE_SYSTEM_TERMS`: minimized; IDs stay in technical details.
- `SCIENTIFIC_LIMITATIONS_VISIBLE`: YES.
- `TECHNICAL_DETAILS_PROGRESSIVELY_DISCLOSED`: YES.

## Current-head CI

Final exact-SHA CI: GitHub Actions run `32702466953` for
`3da0a04389438ec25b322339300350e27ebfc15c`; Unit Tests, Frontend Typecheck &
Build, PostgreSQL/Redis/MinIO Service-backed Integration, Linux Replay and
Windows Replay all succeeded. Service-backed integration summary was
`69 passed, 0 skipped, 0 failed, 0 errors`; the three Phase 9 tests were
explicitly selected and passed.

## Legacy Compatibility

Existing Workspace renderer routes, legacy Report/Recipe reads, Scientific
Object APIs and Report evidence routes were extended rather than removed.

## Not Implemented In Phase 9

Full 62-tool mapping, new scientific algorithms, Data Management mutations,
external Tool/Parser/Viewer plugin ecosystem, global/cross-project memory,
internet literature research, multi-project meta-reports, collaborative report
editing, BYOK, deployment and ORCHESTRATING lease/reaper remain out of scope.

## Remaining Gaps

1. Authenticated browser golden paths for Structure, Table, RDF, XRD, Report
   evidence, stale historical and unsupported fallback at 1280x720/390x844.
   The local app redirected to its login surface; no password was entered
   without action-time confirmation, so no browser PASS is claimed.
