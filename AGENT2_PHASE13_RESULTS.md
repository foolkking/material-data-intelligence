# Agent-2.0 Phase 13 — Scientific Presentation 2.0

## A. Phase 12 Baseline

Phase 12 sealed base: `49398ecfb630d83301a38a647b94ae5b97f55a59`.
P12-A CI: run `33038096797`, exact SHA `40ebb4d65c76ef0c44fdde2923c901c97efa2257`.
P12-B CI: run `33040374649`, exact SHA
`49398ecfb630d83301a38a647b94ae5b97f55a59`.
Alembic head: `0025_agent2_scientific_selection`.

```text
PHASE12_REOPEN_REQUIRED = NO
```

## B. Phase 13 Scientific Presentation

### B1. Base

Initial Phase 13 base is the sealed Phase 12 SHA above. The current worktree
uses the same ScientificObject, ScientificObjectVersion, ScientificResult,
Artifact, Viewer, Evidence, and Report authorities.

### B2. Presentation Audit

The implementation reuses the existing ScientificResult projector,
ScientificViewerRegistry/Shell, Materials Explorer/table renderer, Research
Workbench, and Report snapshot APIs. The bounded compiler and renderer are
new communication-layer code only; no second scientific or provenance store
was introduced. Legacy Report rendering remains as a compatibility fallback.

### B3. Presentation Contract

Supported bounded blocks are `narrative`, `finding`, `metric`, `table`,
`figure`, `viewer_reference`, `evidence_reference`, `limitation`, and
`warning`. Blocks carry exact Result/fact/evidence/artifact/object-version
references. Unsafe HTML/JavaScript-like labels and unsupported executable UI
descriptors fail closed.

### B4. Fidelity

Numeric values and units are passed through from persisted facts/evidence;
unknown units remain absent. Historical source references are retained
exactly and a newer-version notice is non-destructive. Presentation code has
no Tool, queue, mutation, or latest-version lookup hook.

### B5. Research Presentation

- Structure: authenticated Chromium capture
  `phase13-structure-presentation-1280.png`; bounded findings/metrics,
  exact source, Structure Viewer and evidence path visible.
- Electronic: Phase 10N5 PostgreSQL/Redis/MinIO service-backed path and
  Band/DOS renderer tests provide the authoritative persisted artifact/viewer
  qualification; no unsupported band conclusions are fabricated.
- Dataset: authenticated Chromium capture
  `phase13-dataset-presentation-1280.png`; typed table, stable `mat-2`
  selection, exact Dataset version, grounded facts and report link visible.

### B6. Historical Presentation

Canonical Phase 12 evidence remains:

```text
R1 → object 773089f9-3ce8-4645-92dd-2f62c64cba89 / v1
R2 → the same object / production v2 2538cd12-ffd5-473f-8c77-69e6d1700243
SILENT_LATEST_SUBSTITUTION = NO
```

Historical and archived Viewers retain exact source versions and show a
non-destructive historical notice where applicable.

### B7. Report

The authenticated report route renders the shared presentation projection,
evidence, exact source identity and report snapshot. Current Dataset report:
`agent2_report_819f458171ba2d3219717895bf12eaf9`, snapshot
`bd1a3fad-eb49-5212-b6bf-e1f92fac03a8`.

### B8. Viewer Regression

Existing Viewer/service regressions and the read-only compiler path preserve
zero scientific recomputation. Viewer opening does not enqueue work or create
Artifacts/Results; exact object/version resolution is retained.

### B9. Result Reuse

Agent2 Phase 2/7 reuse regressions cover exact-result reuse and zero Job,
ToolCall, Artifact, and Result deltas when presentation changes only.

### B10. Browser

Authenticated Chromium used the requested executable and existing signed-in
session. Desktop captures cover Structure, Dataset/Research, Report and
archive/restore. Dataset mobile capture
`phase13-dataset-mobile-390x844.png` records inner/document/body width 390
and no horizontal overflow. The only console entry was the expected auth
bootstrap `401`; no page errors, 5xx responses or unexpected critical
failures were observed.

### B11. Service-backed

Current same-stack runtime:

```text
PostgreSQL = PASS
Redis = PASS
MinIO = PASS
DeepSeek provider = configured
Phase 13 selected = 14
passed = 14
failed = 0
errors = 0
skipped = 0
```

The broader Phase 12 mandatory service campaign remains `19/19 passed`.
Observed DB pool state after qualification: active `1`, idle `6`,
idle-in-transaction `0`, pool timeouts `0`.

### B12. Tests

```text
Phase 13 focused frontend = 25 passed
Phase 13/Agent2 focused backend = 85 passed, 4 historical compatibility skips
full frontend = 593 passed
full backend = 1813 passed, 83 historical skips
typecheck = PASS
production build = PASS
compileall = PASS
uv lock --check = PASS
touched Ruff = PASS
git diff --check = PASS
```

### B13. Security

Bounded block labels reject executable HTML/JavaScript-like content.
Cross-project authorization remains server-enforced for Result, Artifact,
Evidence and exact versions. Capability Packs cannot provide executable
frontend code. Viewer navigation is read-only.

### B14. Git / CI

P13-A implementation candidate:

```text
SHA = 4bfdacd
CI run = 33134862435
CI tested SHA = 4bfdacd
result = PASS
required jobs = Unit Tests, Frontend Typecheck & Build,
Service-backed Integration (PostgreSQL + Redis + MinIO),
Phase 11-3 Scientific Replay (Linux), Phase 11-3 Scientific Replay (Windows)
```

P13-B is the commit containing this final evidence record; its exact SHA and
current-head CI are recorded in the release report after the commit completes.

### B15. Remaining Gaps

At the time this record was created, only the P13-B exact-current-head CI
remained.

### B16. Final Verdict

Functional implementation and same-stack qualification are green locally and
P13-A exact-SHA CI has passed. The final COMPLETE verdict is deferred only
until P13-B exact-current-head CI and `HEAD == origin/master` are observed.
