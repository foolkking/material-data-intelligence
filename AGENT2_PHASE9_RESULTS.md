# AGENT2_PHASE9_RESULTS

## Verdict

PARTIAL - deterministic viewer/selection implementation and dedicated
PostgreSQL/Redis/MinIO qualification pass. Authenticated browser qualification
was run with the approved local acceptance session. Structure, table, XRD/RDF,
historical STALE and unsupported fallback paths rendered without fatal browser
errors or global overflow. The canonical scientific table is now created and
persisted through the normal upload/parse/promotion path, and a fresh
Windows-compatible Agent2 worker now persists immutable semantic selection
snapshots. The closure remains PARTIAL because the existing grounded RDF report
was generated before an exact ScientificObject source reference was available;
its report evidence link therefore cannot honestly be claimed as an exact
Report -> Viewer deep link yet.

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

1. GP9-B02 cannot be completed from the canonical local fixture because the
   authenticated project contains no persisted scientific table/composition
   object (only Structure/XRD objects); no fake table was inserted.
2. GP9-B04 exact Phase 8 Report → Figure/Evidence → Viewer cannot be completed
   because the project has zero grounded `ScientificReportSnapshot` rows. The
   legacy XRD report rendered successfully, but it is not evidence of the new
   grounded report route.
3. The selection bridge passed focused tests and returned `202 Accepted` from
   the authenticated ResearchTurn API. A fresh worker/context snapshot
   completion was not claimed because this local API queue was not running to
   advance the new turn beyond `RECEIVED`.
4. Authenticated browser evidence is real for the available canonical data,
   but GP9-B02 (scientific table) and GP9-B04 (grounded Phase 8 Report → Viewer)
   remain unverified because the canonical project has no such persisted
   fixtures. A fresh Agent2 worker was also not running locally, so the
   successful `202 Accepted` selection submission is not claimed as a completed
   worker/context-snapshot handoff.

## Post-closure compatibility fix

The authenticated rerun exposed a separate legacy-history defect: an older
`AnalysisPlan` row without `analysis_plan_json` made the project history route
return HTTP 500. The history projection now treats that row as a readable job
with no plan payload, while new-plan validation remains strict. Focused
project-history regression: `34 passed, 1 skipped`.
