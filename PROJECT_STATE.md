# PROJECT_STATE

> Compact human-readable current-project snapshot. Specialized authorities
> remain authoritative in their own domains; this file summarizes and points
> to them. It is not a replacement for task, result, architecture,
> qualification, runtime, or historical ledgers.

## 1. Current Status

- `PROJECT_PHASE`: Source and physical ownership migration closed; capability
  parity and residual ownership accepted; remote qualification/release gate
  pending.
- `CURRENT_ACCEPTED_COMMIT`: `8e91432`
- `SNAPSHOT_BASE_COMMIT`: `8e91432`
- `WORKTREE_EXPECTATION`: existing migration worktree, detached HEAD, clean
- `LAST_ACCEPTED_REVIEW`: Final Residual Ownership and Repository Hygiene
  Review, `REPAIRED_AND_PASS`, 2026-09-09
- `LAST_UPDATED_AT`: `2026-09-09`
- `STATE_STATUS`: `CURRENT`
- `PROJECT_STATE_ACTIVE`: `YES`
- `HIGH_LEVEL_DUAL_READ_ACTIVE`: `YES`
- `RETENTION_POLICY_ACTIVE`: `YES`

Freshness is based on the snapshot base and represented-authority changes, not
on a self-referential commit hash. A later commit that only synchronizes this
snapshot does not make it stale. A material change to a represented
specialized authority requires explicit reconciliation and may set
`STATE_STATUS: STALE`.

## 2. Current Product State

- The current roadmap records Phase 13 as
  `COMPLETE / INITIAL_RELEASE_COMPLETE`.
- Implemented product areas include project/data workflows, planning and
  execution, artifacts, research, scientific viewers, reports/recipes, and
  unified workspace surfaces, subject to the explicit limits in the roadmap
  and release evidence.
- Future and not-planned scope remain governed by
  `docs/FUTURE_SCOPE.md` and `docs/NOT_PLANNED_SCOPE.md`.

## 3. Current Architecture

- **Backend:** `bootstrap`, `transport`, `application`, `domain`, and
  `infrastructure` ownership is physically established; legacy public and
  worker paths remain only where compatibility requires them.
- **Frontend:** `app/` owns thin routes; `features/` owns product features;
  `scientific-viewers/` owns viewer engines and colocated workers;
  `shared/` owns shared layout/UI/workspace/observability.
- **Compatibility:** canonical-to-compatibility imports are zero; remaining
  legacy surfaces are bounded by frozen public, dynamic, worker, test, or
  qualification contracts.

## 4. Frozen Runtime and Identity Contracts

- Frozen handlers resolve `6/6`; queue names and persisted handler paths are
  unchanged.
- Tool inventory: `62`, unchanged.
- Adapter inventory: `50`, unchanged.
- API contracts, authorization, schema/Alembic identity, transaction
  semantics, persisted identities, scientific authority, and UI behavior are
  frozen.

## 5. Active Work

- `CURRENT_WORKSTREAM`: residual ownership is closed; remote qualification and
  release gate review is next.
- `CURRENT_TASK`: no follow-on execution is authorized after this review;
  `TASKS.md` remains the queue authority.
- `NEXT_ACTION`: run a separately authorized current-HEAD remote CI and
  mandatory service/runtime qualification before any remote release.
- `BLOCKED_ITEMS`: live runtime registration and live database migration head
  remain `CURRENT_UNKNOWN` where the runtime reconciliation could not safely
  query them.

## 6. Verification State

- Backend current rerun: `2212 passed, 76 failed, 75 skipped`.
- New backend regressions: `0`; the 76 failures remain historical or
  environmental baseline failures.
- Frontend: `117 files / 950 tests PASS`.
- Frontend typecheck: `PASS`.
- Production build: `PASS`.
- Architecture: cycles `0`; forbidden edges `0`; dynamic contract errors `0`;
  public surface errors `0`; canonical-to-compatibility edges `0`.
- Residual ownership: 85 backend and 138 frontend production-path files
  classified; unresolved residuals `0`; duplicate business implementations
  `0`. Two scientific-result runtime residues were mechanically relocated and
  focused verification passed (`25 passed`).
- Remote CI: available through the repository GitHub workflow and authenticated
  local CLI, but not run and no commit was pushed. Remote release requires a
  separately authorized current-HEAD workflow plus mandatory service/runtime
  qualification.

## 7. Current Debt and Risks

- **Architecture debt:** four bounded frozen architecture allowlist edges.
- **Compatibility debt:** legacy facades and frozen worker/public paths remain.
- **Verification debt:** no remote CI for the migration/transition/stabilization
  commits.
- **Environmental/historical debt:** 76 baseline backend failures and
  unresolved live runtime registration/database-head observations.

## 8. State Authorities

| DOMAIN | AUTHORITY | ROLE | PROJECT_STATE REPLACES? |
|---|---|---|---|
| Active task queue | `TASKS.md` | task/execution queue | NO |
| Detailed results | `results.md` | result ledger | NO |
| Architecture rationale | `persistent/ARCHITECTURE_DECISIONS.md` | ADR/history | NO |
| Tool/Adapter identity | `persistent/TOOL_REGISTRY_NOTES.md` and registry manifests | specialized authority | NO |
| Roadmap/scope | `docs/ROADMAP.md`, `docs/FUTURE_SCOPE.md`, `docs/NOT_PLANNED_SCOPE.md` | product planning/boundary | NO |
| Qualification/CI | `docs/qualification/**`, `_qualification/**`, CI records | qualification authority | NO |
| Dynamic/runtime identity | `docs/DYNAMIC_CONTRACT_MANIFEST.md`, runtime manifests | identity authority | NO |
| Historical provenance | phase records, migration reports, evidence | immutable history | NO |
| Runtime/user data | databases, queues, object stores, uploads, sessions | runtime/user authority | NO |

## 9. Retention Notes

- Runtime, user-owned/unknown, historical, qualification, and operational
  ledgers remain protected.
- The retention review passed; no files were deleted or archived.
- Safe-cleanup dry-run currently yields `candidateCount = 0`.
- Generated caches/dependencies remain future candidates only after active
  process, reader, ownership, evidence, and rebuild gates pass.

## 10. Recent Execution History

- 2026-09-08: source architecture migration accepted at `f3c6fa0`.
- 2026-09-08: retention and PROJECT_STATE transition review passed.
- 2026-09-08: additive PROJECT_STATE snapshot, high-level dual-read workflow,
  freshness rules, reverse-reference audit, and bounded-cleanup no-op passed;
  specialized authorities remain active.
- 2026-09-08: stabilization detected and reconciled one bounded Active Work
  drift after task archival; static Case A-D freshness behavior passed. Release
  readiness is conditional on current-HEAD remote and service qualification.
- 2026-09-09: final residual ownership review classified every requested
  legacy-looking production surface, moved scientific-result queue/reconciler
  implementations to infrastructure, retained old identity-preserving facades,
  and closed physical ownership with zero unresolved or duplicate authority.

## 11. Source Pointers

- Queue: [`TASKS.md`](TASKS.md)
- Results: [`results.md`](results.md)
- Project rules: [`AGENTS.md`](AGENTS.md)
- ADR: [`persistent/ARCHITECTURE_DECISIONS.md`](persistent/ARCHITECTURE_DECISIONS.md)
- Progress/board: [`persistent/DESIGN_PROGRESS.md`](persistent/DESIGN_PROGRESS.md),
  [`persistent/TASK_BOARD.md`](persistent/TASK_BOARD.md)
- Roadmap/scope: [`docs/ROADMAP.md`](docs/ROADMAP.md),
  [`docs/FUTURE_SCOPE.md`](docs/FUTURE_SCOPE.md),
  [`docs/NOT_PLANNED_SCOPE.md`](docs/NOT_PLANNED_SCOPE.md)
- Dynamic contracts: [`docs/DYNAMIC_CONTRACT_MANIFEST.md`](docs/DYNAMIC_CONTRACT_MANIFEST.md)
- Runtime reconciliation: [`docs/RUNTIME_BASELINE_RECONCILIATION.md`](docs/RUNTIME_BASELINE_RECONCILIATION.md)
- Transition design: [`docs/PROJECT_STATE_TRANSITION_PLAN.md`](docs/PROJECT_STATE_TRANSITION_PLAN.md)
- Tool Registry notes: [`persistent/TOOL_REGISTRY_NOTES.md`](persistent/TOOL_REGISTRY_NOTES.md)
- Qualification: [`docs/qualification/`](docs/qualification/), [`_qualification/`](_qualification/)

## 12. Controlled Update and Freshness Rules

- Refresh this snapshot after an accepted phase/review, major workstream
  transition, qualification or remote-CI state change, architecture-acceptance
  change, or material risk/debt change.
- `TASKS.md`, `results.md`, qualification records, CI records, ADRs, manifests,
  and runtime authorities are written by their existing workflows first.
  PROJECT_STATE is updated afterward only for the compact fields it summarizes.
- No automated dual writer is introduced. A human/Agent synchronization step
  is sufficient; specialized writers are never replaced or redirected.
- Set `STATE_STATUS: STALE` when a post-base change materially affects a field
  represented here and has not been reconciled. A commit that only updates
  PROJECT_STATE or records this transition does not itself make the snapshot
  stale.
- High-level readers must compare represented fields with their source
  authorities even when the stored status is `CURRENT`. A mismatch is
  effective stale and must be surfaced before reconciliation.
- On conflict, surface the discrepancy and follow the specialized authority
  named in the State Authorities table. Never silently overwrite stronger
  evidence.
