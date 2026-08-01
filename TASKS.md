---TASK---
Status: completed / awaiting verified queue archive
状态：处理中
# Phase 10M-1
## Scientific Workspace Domain Contract + Persistence

Implement only the reviewer-approved Phase 10M-1 scope from the verified
Phase 10M-0 seal.

### Required Delivery

- Implement strict, versioned `ScientificWorkspace 1.0`, `WorkspacePanel 1.0`,
  and `WorkspaceSelectionContext 1.0` Python, checked-in JSON Schema, and
  TypeScript contracts with deterministic canonical identities and sealed caps.
- Add Alembic `0007_phase10m1_workspace_domain` with exactly
  `scientific_workspaces`, `workspace_panels`, and
  `workspace_layout_revisions`; support SQLite/PostgreSQL
  upgrade/downgrade/re-upgrade and no bulk backfill.
- Add repository protocols plus in-memory and SQLAlchemy implementations for
  idempotent one-Workspace-per-Job creation, immutable source bindings,
  bounded panels, append-only layout revisions, optimistic concurrency,
  deterministic history, conflict translation, and project isolation.
- Add an explicit, idempotent historical Job projection service. Ordinary Job
  reads must not write or infer modern scientific identities for legacy data.
- Add the sealed additive Workspace create/get/patch/project-list,
  historical-job candidate, panel, and layout-history APIs with
  `Idempotency-Key`, ETag/`If-Match`, bounded metadata-only responses, typed
  errors, and no Artifact payload copy.
- Add TypeScript API contracts/client functions only. Do not add a Workspace
  page, shell, panel renderer, navigation, selection propagation, report/recipe
  composition, or save/recovery UX.
- Prove exact M1 acceptance IDs `M1-A01` through `M1-A08`, security,
  compatibility, migration, repository/API behavior, PostgreSQL + Redis +
  MinIO no-skipped service evidence, browser regressions, evidence integrity,
  and the standard implementation/completion/archive exact-SHA lifecycle.

### Frozen Decisions and Caps

- Preserve M-D001 through M-D025 without redesign.
- One Workspace per exact `(projectId, sourceJobId)`.
- Workspace stores references and durable presentation state only; it never
  copies scientific values or Artifact payloads and has no execution authority.
- Migration tables and columns, nullable legacy refs, indexes, uniqueness,
  foreign-key deletion rules, API routes/status codes, `/workspaces/{id}` M2
  route ownership, panel kinds, selection identities, and source authority are
  those sealed in `docs/phase10m/`.
- `MAX_PANELS_PER_WORKSPACE = 32`.
- `MAX_LAYOUT_REVISIONS = 128`; revision 129 returns
  `REVISION_CAP_EXCEEDED` without deletion or compaction.
- Explicit pinned selection is durable; ephemeral selection is not canonical
  server state. M1 implements selection contracts/validation only, not UI
  propagation.
- Historical 0.1/0.2 plans, Jobs, Artifacts, lineage, interpretations,
  reports, and recipes remain readable and unchanged.

### Required Boundaries

No Planner, Intent, Eligibility, AnalysisPlan, Runtime, Registry, Adapter,
scientific calculation, interpretation, provider, or root-route behavior
change. No new dependency or lockfile change. No real LLM call. No arbitrary
code, shell, filesystem, HTML/JavaScript, external Artifact URL, cross-project
source, stale identity rebinding, bulk backfill, hidden GET write, Workspace
UI, Phase 10N science, or Phase 10M-2 work.

### Lifecycle

Keep this block active through implementation exact-SHA CI. After that, append
the complete result to `results.md`, mark the block complete but retain it,
verify completion-record exact-SHA CI, then remove only this block in a
separate queue-archive commit and verify archive exact-SHA CI.

Do not create, queue, or execute Phase 10M-2 automatically.

### Completion Record

- Completed: 2026-08-01 23:32:58 +08:00.
- Modified: Workspace contracts/schemas, Alembic 0007, repositories,
  projection/API/client, tests/CI, evidence, docs, and persistent records.
- Summary: Implemented the sealed reference-only Workspace domain with exact
  source binding, bounded panels/revisions, idempotent projection, and
  optimistic concurrency; no Workspace UI or M2 behavior was added.
- Verification: focused M1 26 passed; full local backend 1103 passed with 39
  unavailable local integration skips; frontend 333 passed plus typecheck/build;
  corrected exact-SHA CI 30705503707 passed all jobs, including service-backed
  37 passed, 0 skipped, 0 failed, 0 errors.
- Lifecycle: completion-record CI and verified queue archive remain required.
---END TASK---

REVIEWER GATE AFTER PHASE 10M-1

Phase 10M-2: REVIEWER_GATE / AWAITING REVIEWER PROMPT
TASK_BLOCK_COUNT: 1

Phase 10M-2 requires a new reviewer prompt based on the real Phase 10M-1
contracts, migration, repositories, API, historical projection,
service-backed evidence, completion record, and verified queue archive.
