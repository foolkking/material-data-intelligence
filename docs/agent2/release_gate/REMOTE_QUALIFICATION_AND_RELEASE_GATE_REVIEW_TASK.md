# Remote Qualification and Release Gate Review

## Status and scope

This task performs final release qualification after source architecture,
physical ownership, capability parity, and residual ownership have closed.
It does not reopen migration. The frozen accepted facts are:

- source architecture migration complete;
- physical ownership migration complete;
- full pre/post capability parity established;
- residual ownership review repaired and passed;
- duplicate business implementations: zero;
- unresolved residuals: zero;
- canonical-to-compatibility imports: zero;
- six frozen handlers and six queue names preserved;
- Tool inventory: 62;
- Adapter inventory: 50;
- migration phase closed.

The accepted residual source and review commits are `8e91432` and `b761517`.

## Repository and Git constraints

- Use only `E:/1project/mdi-b0-5a1`.
- Do not create a branch or worktree.
- Do not push.
- Resolve and record the exact final release-candidate SHA.
- All qualification claims must be tied to the final exact SHA. If a
  correction creates a new commit, invalidate older exact-SHA claims and
  resolve HEAD again.
- Distinguish source migration completion from release qualification.

## Evidence reconciliation

Reconcile the residual-review counts recorded in `results.md`,
`PROJECT_STATE.md`, and the residual review. Determine whether `25 passed` is
an ownership-specific subset and `57 passed` is the total focused suite count,
or whether a record is stale. Preserve stronger specialized evidence and
record the scopes explicitly.

## Local release preflight

On the final local candidate run:

- `git diff --check`;
- the repository architecture guard and deterministic architecture report;
- dynamic-contract and public-surface/compatibility checks;
- worker/queue manifest checks;
- Tool and Adapter registry checks.

Required retained identities are: zero cycles, zero forbidden edges, zero
canonical-to-compatibility edges, handlers 6/6, six unchanged queues, 62
Tools, and 50 Adapters. Four existing bounded frozen allowlist edges may
remain but must not increase.

## Mandatory real-service qualification

Use the checked-in runbook, same-stack configuration, and qualification
harness. Unit or in-memory substitutes are not release authority.

### PostgreSQL

Prove connectivity, pool lifecycle, expected Alembic migration head, schema
identity, repository read/write, and transaction behavior. If migration head
cannot be safely observed, report it unresolved rather than fabricating PASS.

### Redis and workers

Prove Redis connectivity, expected queue registration, unchanged queue names,
visible worker registration, and resolution of all six persisted handler
dotted paths.

### MinIO

Prove connectivity and safe bucket/object put/get/delete behavior using only
qualification-owned disposable objects. Verify Artifact locator/read behavior
when required. Never mutate user-owned objects.

## Service-backed critical path

Exercise release-critical, real PostgreSQL/Redis/MinIO/worker chains covering:

Project -> Dataset/Data -> Research/Planning -> Job/Tool execution -> Artifact
-> ScientificResult -> Interpretation -> Report -> Viewer/Workspace.

Verify stable IDs, exact ScientificObject version behavior, Artifact
grounding, Result provenance, Report grounding, queue dispatch, worker
completion, and reopen/reuse behavior.

## Authenticated browser/runtime qualification

Prefer the existing Playwright/browser qualification harness. Cover the
authenticated shell and representative project, data, research,
planner/workbench, reports, scientific viewer, workspace, tasks, and
notifications surfaces where safely supported. Require successful real API
requests, persisted-ID reopen, no fatal React errors, and no chunk/import
failures. If a safe arbitrary-ID authenticated harness is unavailable, report
`NOT_RUNTIME_VERIFIED` with the exact reason and classify it against the
existing release contract without inventing evidence.

## Regression and supply-chain checks

Confirm current backend regression status, frontend tests, frontend
typecheck, and production build. Historical backend baseline is
`2212 passed, 76 failed, 75 skipped`; only new failing node IDs are new
regressions. Inspect dependency locks, CI pins, build provenance, release-SHA
exposure, expected migration head, runtime configuration validation, and
secret redaction without printing secrets.

## Remote exact-SHA gate

Inspect the configured remote, workflows, GitHub authentication, and whether
the final exact SHA exists remotely. Do not push. If absent, report:

- `REMOTE_PUSH_REQUIRED = YES`;
- `REMOTE_PUSH_AUTHORIZATION_REQUIRED = YES`;
- `REMOTE_CI_STATUS = NOT_RUN`.

Stop actions that require a push and state the minimum separately authorized
push/workflow action. If the exact SHA already exists remotely, run the
existing exact-SHA CI only when safe and verify `REMOTE_CI_SHA` equals the
release-candidate SHA.

## Permitted correction

A bounded code/config/test/docs release defect may be fixed forward in a
cohesive local commit if behavior, API/auth, schema/Alembic, transactions,
persisted identities, scientific authority, and compatibility remain
unchanged. Re-resolve HEAD and rerun affected qualification afterward.

## Required records

At completion update specialized release-gate evidence, `results.md`, and
`PROJECT_STATE.md`. Preserve `TASKS.md` as queue authority and `results.md` as
the detailed result authority. Final worktree must be clean. Do not push.

## Final decision

Return `PASS`, `REPAIRED_AND_PASS`, `CONDITIONAL`, or `BLOCKED`.
Full PASS requires all mandatory local/service checks and exact-SHA remote CI
to pass with no release-blocking unknowns. If local and real-service
qualification pass but the exact SHA is not on the remote, the required
decision is `CONDITIONAL`, with local release readiness true and remote
release readiness false pending separate push authorization.
