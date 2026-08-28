# Agent-2.0 Phase 13 — Scientific Presentation 2.0

## Mandatory Phase 12 Product-Lifecycle & Release Closure Gate

This is the repository-persisted authority for the user-authorized two-stage
execution on 2026-08-26. The stages are strictly ordered.

```text
STAGE 0
Close the remaining Phase 12 product-lifecycle and release debt

        ↓ only if COMPLETE

STAGE 1
Agent-2.0 Phase 13 — Scientific Presentation 2.0
```

Phase 13 main implementation is conditionally authorized only after Stage 0
has reached all functional, release, exact-SHA CI, and repository-state gates.
If Stage 0 fails, Phase 13 must not start.

## 1. Incoming authority

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL
AGENT2_PHASE12 = PARTIAL
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL
READY_FOR_PHASE13 = NO
```

Reported baseline:

```text
HEAD = f1e59b0e6b23a9533b59cff9b3049cab2cad7ce0
origin/master = f1e59b0e6b23a9533b59cff9b3049cab2cad7ce0
branch = master
Alembic head = 0025_agent2_scientific_selection
```

The repository is authoritative. Legitimate later work must be inspected and
preserved. Do not reset, clean, blindly stage, discard Phase 12 changes, or
overwrite unrelated user files.

## 2. Frozen Phase 12 authorities

```text
ScientificObject = logical scientific identity
ScientificObjectVersion = immutable scientific state
duplicate authority = NO
in-place scientific mutation = NO
silent latest substitution = NO
```

The following remain authoritative:

```text
scientific_objects
scientific_object_versions
scientific_object_relationships
exact semantic-profile references
ScientificResultSnapshot.source_object_refs
Report → Result → exact source version
```

Preserve:

```text
PATCH /api/scientific-objects/{object_id}
```

for display metadata, archive, and restore with project write authorization.
Archive/restore must not create a version or change scientific content/source
authority.

Preserve:

```text
POST /api/scientific-objects/{object_id}/versions/{version_id}/query
```

with exact version, checksum validation, typed bounded filters, a 500-row cap,
stable sample identity, and no arbitrary SQL.

Canonical Dataset:

```text
object = b8a1a55b-d32f-45f3-b421-df075dc3c05d
version = 622ef3d7-301c-420a-aa75-7dda551cf7ef
band_gap > 2 → mat-2, mat-3
```

The worker/interpretation root cause is frozen as:

```text
TEST_HARNESS_INTERPRETATION_QUEUE_SCOPE_CROSS_CONSUMPTION
```

The durable production path reached Result projection and `RESULT_READY`; a
separate interpretation consumer lacked its provider fixture. Preserve both
the isolated Result-projection boundary test and the full interpretation-
enabled production-style proof. Do not redesign worker, Result, or
Interpretation architecture.

## 3. Stage 0 exact scope

Only close:

```text
A. legitimate Structure v1 → v2 production lifecycle
B. historical Result/Viewer exact-v1 proof after v2
C. archive historical Result/Viewer proof
D. Dataset → Research exact identity handoff
E. final current-worktree service-backed/full regression
F. P12-A exact-SHA CI
G. P12-B exact-current-head CI
```

No new Phase 12 capabilities or architecture.

## 4. Version-update authority audit

Audit every real path for upload, resource ingestion, re-upload, source
replacement, reparse/reprofile, `create_version`, ScientificObject services,
version APIs, and Data Platform actions.

Classify:

```text
VERSION_UPDATE_AUTHORITY =
  EXISTING_PRODUCT_PATH
  | EXISTING_API_NOT_EXPOSED_IN_UI
  | EXISTING_DOMAIN_SERVICE_NOT_EXPOSED_IN_API
  | MISSING_MINIMAL_PRODUCT_BRIDGE
  | ARCHITECTURAL_GAP
```

Use the existing path. If only a bridge is missing, implement the smallest
correct bridge. Stop on a genuine architectural gap. The previous synthetic
`system_fixture` version
`8dcb6e0e-fb47-4af0-a1ef-a7f6b89fe708` is not qualifying evidence.

A legitimate Structure v2 must follow the repository equivalent of:

```text
real scientific source
→ storage
→ parse
→ profile
→ exact immutable ScientificObjectVersion
→ current-version update
```

It must have independent source references, content hash, and legitimately
generated profile. No direct database insertion, direct current pointer edit,
copied readiness, or fake fixture authority.

Canonical Structure:

```text
object A = 773089f9-3ce8-4645-92dd-2f62c64cba89
v1 = 65f56d10-008d-445d-ab2f-228aebf1835b
```

Reuse an existing completed v1 Turn/Result only when exact source refs prove it
uses A/v1. Create a real v2 through production authority, execute a supported
authenticated Research request on exact A/v2, and prove:

```text
R1 → A/v1
R2 → A/v2
R1 identity/source unchanged
R1 Viewer → A/v1 after v2 is current
R2 Viewer → A/v2
SILENT_LATEST_SUBSTITUTION = NO
```

## 5. Archive/restore historical safety

Archive an object with historical Result/Viewer evidence through the real Data
Management API/UI. While archived:

```text
status = ARCHIVED
excluded from default new-work discovery
exact historical object/version remains authorized
historical Result remains accessible
historical Viewer remains accessible
no ScientificObjectVersion is created
```

Restore and prove:

```text
status = ACTIVE
new-work discovery restored
object/version/Result/Viewer identities unchanged
ARCHIVE_CREATED_VERSION = NO
RESTORE_CREATED_VERSION = NO
```

## 6. Dataset → Research exact handoff

Run the canonical typed query, select `mat-2` or another returned stable sample,
and use the real Data Platform → Research handoff. The immutable context must
preserve:

```text
ScientificObject ID
ScientificObjectVersion ID
semantic locator / sample_id
```

The path must reach ResearchTurn, ContextSnapshot, deterministic eligibility,
and CapabilityPlan. Prefer full execution where scientifically appropriate;
exact Result reuse is allowed only with explicit identity and zero Job,
ToolCall, Artifact, and Result deltas.

Repeat the canonical handoff at `390x844` with no global overflow and usable
object/version identity, typed query, rows, selection, and handoff.

## 7. Required regressions

Keep the historical Silicon exact version fail-closed:

```text
CAPABILITY_REQUIREMENT_UNSATISFIED
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
Result delta = 0
```

Preserve Phase 11 trusted Packs:

```text
core.structure
core.electronic
core.data
core.trajectory
core.other
raw Tool exposure = NO
```

Requalify Structure, Electronic, and Dataset after final Data Platform changes.

## 8. Stage 0 service, browser, and test gates

Use real PostgreSQL, Redis, MinIO, API, workers, authenticated frontend, and
browser. No SQLite, fake queue, or all-skipped qualification.

Exercise:

```text
legitimate version creation
exact v1/v2 resolution
historical Result refs
historical Viewer source
archive/restore
Dataset query and selection handoff
Research Context exact refs
Job/ToolCall/Artifact
ScientificResult
interpretation-enabled terminal Turn
```

Record selected/passed/failed/errors/skipped. After the campaign record active,
idle, idle-in-transaction, pool timeouts, engine lifecycle, and ensure no
monotonic growth.

Run fresh:

```text
Phase 12 focused
Phase 1–11 focused
Agent2
Capability Pack regression
full backend
full frontend
typecheck
production build
compileall
uv lock --check
git diff --check
touched Ruff
```

The Stage 0 functional gate requires every product, service, browser, database,
backend, frontend, build, and static item above to pass before committing.

## 9. Phase 12 release closure

Create P12-A only after the functional gate is green. Explicitly stage only
legitimate Phase 12 implementation/test/fixture-boundary/minimal-bridge files,
push normally, and require exact-SHA CI with service-backed CI:

```text
P12_A_CI_SHA == P12_A_SHA
```

After P12-A CI passes, update `AGENT2_PHASE12_RESULTS.md` and only authoritative
state/evidence files. Create P12-B, push, and require:

```text
HEAD == origin/master
CI SHA == HEAD
required jobs PASS
```

Only then:

```text
FUNCTIONAL_PHASE12_CLOSURE = PASS
AGENT2_PHASE12 = COMPLETE
SCIENTIFIC_DATA_PLATFORM_V2 = COMPLETE
READY_FOR_PHASE13 = YES
PHASE13_BASE_SHA = exact sealed HEAD
```

If any Stage 0 gate fails, stop without Phase 13 implementation.

## 10. Stage 1 mission

After Stage 0 COMPLETE, implement Scientific Presentation 2.0 as a deterministic
communication layer:

```text
Scientific facts
→ ScientificResult
→ presentation projection
→ Finding / Figure / Table / Viewer / Evidence
→ Research response
→ Report
```

Presentation is neither computation nor provenance/scientific authority.

## 11. Presentation audit and bounded contract

Audit Viewer Registry/Shell, Result renderers, Workbench, assistant blocks,
Report/Evidence, tables, figures, Structure/Band/DOS/Materials viewers, and
mobile layouts. Classify each as authoritative, reusable, duplicated,
inconsistent, legacy, or missing.

Normalize a bounded presentation contract only where existing contracts are
insufficient. Supported semantic block kinds may include:

```text
finding
metric
text
table
figure
viewer_reference
evidence_reference
warning
limitation
```

Do not persist arbitrary React component names. Every block must reference
authoritative Result items, Artifacts, exact object versions, or evidence.

## 12. Fidelity and provenance

Displayed numbers originate from Tool output, Artifact, ScientificResult, or
Dataset values. Formatting is allowed; semantic recalculation is not. Preserve
authoritative units and unknown-unit status. Findings must expose supporting
Result/evidence and legitimate limitations without invented confidence.

Figures reference persisted data/specifications and exact sources; opening
them does not rerun Tools. Tables preserve typed columns, units, stable row
identity, and source refs across sorting/filtering.

Evidence inspection must provide the bounded path:

```text
Finding → ScientificResult → ToolCall/Artifact → ScientificObjectVersion
```

with project authorization and no sensitive infrastructure leakage.

## 13. Viewer, response, and Report integration

Reuse the professional Viewer authority for Structure, Band Structure, and
Scientific Table/Materials Explorer, plus already healthy viewers. Do not
rewrite Viewer science.

Mandatory:

```text
open Viewer
→ 0 new ToolCalls
→ 0 new scientific Artifacts
→ 0 new ScientificResults
```

Compose grounded Research responses as concise narrative, findings, metrics,
inline Figure/Table references, Viewer links, evidence, and limitations.
Progress remains separate from final scientific presentation and never exposes
chain-of-thought.

Reports assemble authoritative presentation elements and retain exact Result,
object/version, and presentation snapshot identity. They are not a second
Result model. Historical and archived sources remain renderable when
authorized; newer versions may be disclosed but never substituted.

## 14. Phase 11/Agent/security boundaries

Capability Packs may reference bounded trusted presentation descriptors but
cannot ship arbitrary frontend code, component paths, prompts, HTML, script, or
remote UI plugins. The Agent emits grounded semantic content, not arbitrary UI
trees. Deterministic presentation code selects rendering.

Presentation must fail closed for cross-project Result/Artifact/version/evidence
access, arbitrary HTML/script, executable Pack UI, scientific data mutation,
version mutation/substitution, and Tool execution from Viewer navigation.

## 15. Layout, mobile, and accessibility

Reuse current design-system tokens and normalize hierarchy, spacing, Viewer
placement, evidence disclosure, warning/limitation, and metadata treatment.
Maintain scientific workbench density rather than marketing-dashboard cards.

At `390x844`:

```text
no global overflow
bounded tables
viewport-fitting figures
Viewer/evidence reachable
findings readable
Report navigation usable
```

Preserve semantic headings, keyboard controls, accessible disclosures,
meaningful labels, non-color-only charts, and table semantics.

## 16. Canonical Phase 13 acceptance

Use real authenticated same-stack paths for:

1. Multi-capability Structure (CrystalNN + VoronoiNN) with independently
   attributable findings, metrics/table where available, Structure Viewer,
   evidence, limitations, and zero recomputation.
2. Electronic Band result with narrative, Band Viewer/Figure, authoritative
   units/Fermi/source metadata, and no fabricated band conclusions.
3. Dataset/Materials Explorer with bounded table, stable sample identity,
   selection, typed columns, Research handoff, evidence, and exact version.
4. Historical R1/v1 after R2/v2, with no silent upgrade.
5. Archived historical Result/Viewer/Report where available.
6. Exact Result reuse with zero Job/ToolCall/Artifact/Result deltas.
7. Research and Report/Data acceptance at desktop `1280x720` and representative
   mobile `390x844`.

Browser valid paths require zero fatal console errors, unhandled rejections,
unexpected critical API failures, and authorization failures. Screenshots are
supplemental, never a substitute for persisted identity/provenance proof.

## 17. Phase 13 service/tests/release

Run real PostgreSQL/Redis/MinIO service-backed coverage for Result loading,
presentation projection, Viewer resolution, Report snapshot, historical exact
version, and evidence resolution.

Focused deterministic coverage includes Result mapping, numeric/unit fidelity,
Finding/Figure/Table provenance, Viewer no-recompute, historical/archived
presentation, Report exact refs, reuse, unsupported types fail-closed, and Pack
UI injection rejection.

After final implementation run:

```text
Phase 1–12 regression
Phase 13 focused
Agent2
Capability Packs
service-backed
full backend
full frontend
typecheck
production build
compileall
uv lock --check
git diff --check
touched Ruff
```

Create P13-A only after functional closure, push normally, and require exact-SHA
CI. After P13-A CI passes, update `AGENT2_PHASE13_RESULTS.md` and authoritative
state/evidence only, create P13-B, push, and require exact-current-head CI:

```text
HEAD == origin/master
CI SHA == HEAD
required jobs PASS
```

Only then:

```text
FUNCTIONAL_PHASE13_CLOSURE = PASS
AGENT2_PHASE13 = COMPLETE
SCIENTIFIC_PRESENTATION_V2 = COMPLETE
READY_FOR_PHASE14 = YES
```

Do not begin Phase 14.

## 18. Non-goals and stop rules

Do not implement a new Agent/Data/Result/Viewer authority, new scientific
algorithms, mass Tool activation, public/remote plugin systems, arbitrary code,
internet/autonomous research, collaborative editor, notebook, office suite,
deployment, or Phase 14.

If Stage 0 fails:

```text
FUNCTIONAL_PHASE12_CLOSURE = FAIL | BLOCKED
AGENT2_PHASE12 = PARTIAL | BLOCKED
SCIENTIFIC_DATA_PLATFORM_V2 = PARTIAL | BLOCKED
READY_FOR_PHASE13 = NO
PHASE13_MAIN_IMPLEMENTATION = NOT_STARTED
```

Stop immediately and report the exact remaining blockers.

## 19. Required final report

The final report must use the user-required A/B structure:

```text
A. Phase 12 Stage 0 Closure
  A1. Version Authority
  A2. Structure Lifecycle
  A3. Archive / Restore
  A4. Dataset → Research
  A5. Phase 12 Service-backed
  A6. Phase 12 Tests
  A7. P12 Provenance
  A8. Phase 12 Verdict

B. Phase 13 Scientific Presentation
  B1. Base
  B2. Presentation Audit
  B3. Presentation Contract
  B4. Fidelity
  B5. Research Presentation
  B6. Historical Presentation
  B7. Report
  B8. Viewer Regression
  B9. Browser
  B10. Service-backed
  B11. Tests
  B12. Security
  B13. Git
  B14. Remaining Gaps
  B15. Final
```

When `READY_FOR_PHASE13 != YES`, stop the report after A8 plus the exact
remaining blockers.
