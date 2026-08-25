# AGENT2_PHASE9_RESULTS

## Verdict

`FUNCTIONAL_PHASE9_CLOSURE = PASS` locally. The same-stack PostgreSQL Report
-> exact Viewer path, exact-version stability, canonical Table desktop/mobile,
selection handoff, service-backed qualification and browser quality gates are
all verified. `AGENT2_PHASE9` remains `PARTIAL` only until Commit C exact-SHA
CI, Commit D exact-current-head CI and final origin alignment are complete.

## Starting State

- Starting HEAD: `bcdf0627127976b582480881eaf20bcfe7bd9d56`
- Starting origin/master: `bcdf0627127976b582480881eaf20bcfe7bd9d56`
- Starting Alembic head: `0025_agent2_scientific_selection`
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

## Closure Fixture Evidence

- Canonical table creation used `scripts/phase9_create_table_fixture.py` with
  the real upload session, parser/profile persistence, artifact manifest and
  `ScientificObjectService.create_table_from_dataset` authority path. No
  database row was inserted directly. Project `project_0001_35554660bba644a2`
  contains table object `d41fa155-3a4b-4b3b-b590-86e7faa17dd6`, version
  `dc0ffe60-5f97-4c2b-bcb2-e40e074c202d`, with 3 bounded rows.
- Browser table viewer rendered the three scientific columns (`formula`,
  `y_pred`, `y_true`), row selection and exact-version research link at both
  desktop and mobile widths.
- Selection handoff used a real authenticated `202` submission and a fresh
  RQ `SimpleWorker` on Windows. Turn `c9bdef8f-d8be-4b49-9425-b52e744542aa`
  reached `ANSWERED`; immutable snapshot `ad25e544-3550-42cb-8347-f0de97bc57a3`
  retained `Fe2O3`. A later turn selected `LiFePO4` and created a separate
  snapshot; the first snapshot remained unchanged.
- The first worker attempt failed because default RQ workers call
  `os.fork()` on Windows. The closure reran with `rq.worker.SimpleWorker`; no
  timeout inflation or fake completion was used.
- Local runtime defaults now resolve the SQLite authority and artifact root
  from the repository path rather than process cwd, preventing fresh API
  processes from losing persisted viewer payloads.

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
- Browser authenticated smoke: Structure desktop/mobile, canonical scientific
  table desktop/mobile, XRD data table,
  RDF result, XRD legacy report, historical STALE structure and unsupported
  fallback were exercised with the local acceptance session. Fatal console
  errors and unhandled rejections were zero on exercised pages; desktop
  document/body widths were 1265/1265 at 1280px and mobile widths were 375/375
  at 390px (RDF measured 390/390). The initial Phase 9 run was blocked pending
  action-time credential confirmation; this final closure run used the
  explicitly approved credential without persisting or logging it.
- Viewer selection regression: 35 focused Vitest tests passed after fixing the
  Structure viewer callback and API snake_case locator conversion. Typecheck
  passed. A production build was attempted after the fix but exceeded the
  local bounded wait with no diagnostic output; the previously green exact-head
  build remains the carried-forward implementation evidence.
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

Final closure commit `665eba51688229444d14508ea32da38757b455b5` was verified by
GitHub Actions run `32716917924` on the exact SHA. Unit Tests, Frontend
Typecheck & Build, PostgreSQL/Redis/MinIO Service-backed Integration, Linux
Replay and Windows Replay all succeeded. The service-backed job completed its
no-skip assertion successfully. This green CI closes the implementation-CI
gap, but does not change the product verdict: the canonical project still
lacks a scientific table object and a grounded Phase 8 report/evidence fixture.

## Legacy Compatibility

Existing Workspace renderer routes, legacy Report/Recipe reads, Scientific
Object APIs and Report evidence routes were extended rather than removed.

## Not Implemented In Phase 9

Full 62-tool mapping, new scientific algorithms, Data Management mutations,
external Tool/Parser/Viewer plugin ecosystem, global/cross-project memory,
internet literature research, multi-project meta-reports, collaborative report
editing, BYOK, deployment and ORCHESTRATING lease/reaper remain out of scope.

## Closure Status Override (2026-08-24)

The historical gap bullets below predate the final fixture rerun. GP9-B02 is
now closed by the persisted table object and authenticated browser evidence;
the selection worker handoff is also closed by the `ANSWERED` turn and two
immutable snapshots. The only remaining functional gap is GP9-B04: the
persisted RDF report has an empty `source_object_refs` list and legacy
placeholder evidence object refs, so its Figure/Evidence link intentionally
falls back to Research instead of silently substituting an unauthorized or
same-name object. A new report must be generated from a result with an exact
persisted ScientificObject/version before the Report -> Viewer gate can pass.

## Final Fixture Closure Evidence

The historical gap bullets below are retained for provenance. GP9-B02 and the
selection handoff are now closed by the persisted table object, authenticated
browser render and fresh SimpleWorker evidence recorded above. GP9-B04 remains
open because the existing grounded report cannot be rebound to a valid exact
ScientificObject/version; its fallback to Research is intentional and avoids
same-name or unauthorized substitution.

Current focused checks: `44 passed, 5 skipped`; viewer/selection focused:
`22 passed`; frontend: `90 files / 582 tests passed`; typecheck and production
build (`.next-phase9-closure`) passed; `uv lock --check`, compileall and
`git diff --check` passed. The dedicated service marker remains `3 skipped`
without the required local PostgreSQL credentials and is not claimed as a
fresh service pass.

## Remaining Gaps

1. Commit C exact-SHA CI and push.
2. Completion-record Commit D exact-current-head CI and final
   `HEAD == origin/master` verification.

## Provenance-first closure rerun

### Root-cause classification

`CASE_A — fixture/reuse defect.` The current Result producer already persisted
authoritative exact source refs. The repeated failure came from reusing a legacy
RDF Result whose `source_object_refs` were empty and whose Evidence contained
placeholder refs. No Result projector or Viewer resolver change was needed.

### Fresh production chain

The Docker service-backed Phase 4/5 pipeline created fresh Structure and
experimental-XRD ScientificObjects and immutable versions, then executed real
planning, Jobs, ToolCalls, Artifacts and Result projection. Fresh RDF and XRD
snapshots contained exact object/version refs. Phase 5 qualification: `2 passed`.

Fresh RDF Result example: `0d77c488-3bab-42f9-a0ee-241081a3a6b9`; its source
ref identifies the exact Structure object/version used by the execution.
Fresh XRD comparison Result: `0b8b2271-672e-4c87-980e-1c2b440d1f00`; both
Structure and experimental XRD refs are exact and project-authorized.

### Fresh grounded report

The Phase 8 service-backed pipeline created a new report through a fresh report
worker, not the legacy report idempotency key. New report:
`agent2_report_54b0bb264a565fd36229a57e786fdf53`, bound to Result
`870e16b9-856a-4b00-8e81-96965286b2c8`. Its API projection returned two
`viewer_sources`, each derived only from the persisted Result source refs.
Phase 8 qualification: `4 passed`; Phase 9 service qualification: `3 passed`.

The deterministic contract regression now asserts fresh provenance resolves to
exact viewer sources while an empty-ref legacy bundle resolves to no viewer
source. No name, filename, latest-version or project-local substitution is
allowed.

### Service evidence

The authoritative local service run used PostgreSQL at `127.0.0.1:55433`, Redis
at `127.0.0.1:56380` and MinIO at `127.0.0.1:59000`. Selected service tests:
Phase 5 `2 passed`, Phase 8 `4 passed`, Phase 9 `3 passed`, `0 skipped`.

The browser API still uses the separate local SQLite acceptance database, so
the Postgres fixture IDs were not injected into browser code or auth state.
The exact Viewer route is therefore proven at the service/API contract level;
an authenticated browser pass over the fresh Postgres report remains an
environment-level gap, not a license to guess a legacy source.

### Authenticated browser retry (in-app browser)

The Codex in-app browser was started against the production build with the
approved local acceptance session. The persisted canonical table project was
opened through `/projects/project_0001_35554660bba644a2/data` and rendered by
the Scientific Table viewer. At `1280x720`, `document.scrollWidth` and
`body.scrollWidth` were `1265`; at `390x844`, both were `375`. The mobile
table showed all bounded `3 / 3` rows and scientific columns, and the first
row selection opened the semantic `Si` detail region. Console error logs were
empty. The UI exposes column display controls but no separate column-selection
commit action, so column selection is recorded as `NOT_EXPOSED` rather than
claimed.

The same authenticated SQLite project has zero fresh grounded reports and one
legacy report with empty `source_object_refs`. The fresh PostgreSQL report
cannot be injected into the browser database; Report -> exact Viewer therefore
remains unverified at browser level and continues to use the safe legacy
fallback contract.

## Post-closure compatibility fix

The authenticated rerun exposed a separate legacy-history defect: an older
`AnalysisPlan` row without `analysis_plan_json` made the project history route
return HTTP 500. The history projection now treats that row as a readable job
with no plan payload, while new-plan validation remains strict. Focused
project-history regression: `34 passed, 1 skipped`.

## Same-stack PostgreSQL Browser Closure Retry

The final retry used one shared authenticated stack:

```text
Browser -> Next production server :3002
       -> API :8000
       -> PostgreSQL 127.0.0.1:55433/mdi_phase7
       -> Redis 127.0.0.1:56380
       -> MinIO 127.0.0.1:59000
```

`/health/runtime` reported PostgreSQL, Redis, MinIO and the Redis worker
backend healthy. SQLite was not used by this canonical Report test.

Gate 0 identity audit classified Result `870e16b9-856a-4b00-8e81-96965286b2c8`
as a current-generation fresh XRD Result. Its Report
`agent2_report_54b0bb264a565fd36229a57e786fdf53` resolves through the exact
Turn, Job, ToolCalls, Artifacts and two exact source object/version refs. A
second fresh current-generation RDF report in the authenticated owner project
was used for the browser path:

```text
Report: agent2_report_1f4b8c9558f9602c0b1769ef0e731676
Result: e5628121-21e0-4f3f-a303-b5006b269e92
Object: de3dbb42-2690-44b0-bf82-c38f931f2b63
Version: bf49c2e3-4a25-4e8c-944b-833ca76318f5
Viewer: exact Structure Viewer
```

Authenticated browser evidence:

```text
Project Reports -> fresh grounded report: PASS
Report Figure -> scientific viewer link: PASS
Result source object/version: PASS
Historical version warning: PASS
Newer current object version was not substituted: PASS
Structure metadata and rendered 3D scene: PASS
Table object and bounded 3/3 rows: PASS
Table scientific columns: PASS
Browser error logs: []
```

The Report URL retained the exact `object` and `version` query parameters and
the Viewer displayed the historical-version warning while the logical object
had a newer current version. No name or latest-version lookup was used.

The in-app browser did not expose a viewport override capability in this run,
so a fresh same-stack 390x844 mobile capture could not be produced. Previous
SQLite mobile evidence remains historical only and is not claimed as this
closure's same-stack mobile evidence. Consequently Phase 9 remains `PARTIAL`
pending fresh mobile capture and final exact-head CI/provenance commits.

## Fresh Same-stack 390x844 Table Acceptance

The repository's existing Playwright runner was used with the supplied
Chromium executable at:

```text
C:\Users\86182\Desktop\wkkk\playwright-browsers\chromium-1228\chrome-win64\chrome.exe
```

The acceptance script used a real authenticated login and the same production
stack as the canonical Report test. No mocked API or static HTML was used.

```text
viewport: 390x844
Table: PASS
rows: 3 / 3
columns: formula, y_pred, y_true
bounded payload: PASS
row selection: PASS
document scrollWidth <= clientWidth: PASS
body scrollWidth <= clientWidth: PASS
global overflow: 0
fatal console errors: 0
unhandled rejections: 0
critical API failures: 0
```

The initial unauthenticated `/api/auth/me` probe was cleared after the normal
login response; no protected-route failure occurred after authentication.

`FUNCTIONAL_PHASE9_CLOSURE = PASS` is now established locally. Product code
was not changed for this gate; the only new artifact is the reusable
Playwright acceptance script. Release provenance still requires Commit C,
exact C CI, Commit D, and exact current-head D CI.
