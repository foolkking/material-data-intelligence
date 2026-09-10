# PROJECT_STATE

> Compact human-readable current-project snapshot. Specialized authorities
> remain authoritative in their own domains; this file summarizes and points
> to them. It is not a replacement for task, result, architecture,
> qualification, runtime, or historical ledgers.

## 1. Current Status

- `PROJECT_PHASE`: Source/physical migration and capability parity are closed;
  Workstreams A-C now provide lifecycle reliability, context/scientific-memory,
  and a validated scientific-capability extension foundation in the canonical
  migrated repository. Remote exact-SHA CI remains a separately authorized
  release gate.
- `CURRENT_ACCEPTED_COMMIT`: `aac8ef4`
- `SNAPSHOT_BASE_COMMIT`: `aac8ef4`
- `WORKTREE_EXPECTATION`: existing migration worktree, detached HEAD, clean
- `LAST_ACCEPTED_REVIEW`: Workstream C — Scientific Capability Extension
  Platform, `PASS`, 2026-09-10
- `LAST_UPDATED_AT`: `2026-09-10`
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

- `CURRENT_WORKSTREAM`: Workstream C scientific capability extension platform
  is complete in the canonical migrated repository.
- `CURRENT_TASK`: no active queued task after canonical recovery closeout;
  `TASKS.md` remains the task queue authority.
- `NEXT_ACTION`: prioritize Workstream D — Scientific Quality & Evaluation;
  multi-step Agent autonomy should build on capability-specific quality
  evidence rather than structural completeness alone. Remote release
  qualification remains a separate exact-SHA/push-authorized operation.
- `BLOCKED_ITEMS`: no unresolved Workstream A/B/C blocker. Broader scientific
  benchmark coverage, context quality and scale stress remain future
  evaluation rather than authority defects.

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
  `0`. Two scientific-result runtime residues were mechanically relocated.
  Ownership-specific queue/worker tests passed (`25 passed`); the expanded
  residual-review focused suites passed (`57 passed` total).
- Release preflight: architecture guard/report, dynamic/public compatibility,
  six handlers/queues, 62 Tools, 50 Adapters, lock/provenance checks, and
  `git diff --check` pass. The bounded allowlist remains four.
- Mandatory same-stack services: PostgreSQL connection/pool/repository/rollback
  pass; Alembic head is `0032_provider_connections`; Redis and live worker
  registration are `6/6`; MinIO qualification-owned put/get/delete passes.
- Service-backed critical path: `74 passed, 0 failed, 0 errors, 0 skipped`
  across real PostgreSQL/Redis/MinIO/subprocess workers.
- Authenticated browser runtime: representative project/data/research/reports/
  tasks/notifications routes, real API proxy, and persisted-ID reopen pass with
  zero fatal page, server, chunk, or import errors.
- Canonical worktree recovery: lifecycle/context focused backend suites
  `83 passed`; Research provenance UI `93 passed`; Ruff, compileall, typecheck,
  production build, architecture guard/report and diff checks pass.
- Canonical A/B service verification: Phase 2 exact ContextSnapshot provenance,
  Phase 3 planning, Phase 4 worker execution and Phase 7 continuation with an
  exact historical version pass against PostgreSQL, Redis/RQ and MinIO.
  Canonical runtime check reports API/frontend/storage/database healthy and all
  six worker queues discovered.
- Capability extension health: `17/17` Capability manifests valid across five
  trusted Packs; Tool Registry `62`, Adapter Registry `50`, duplicate
  capability authorities `0`, missing Tool/Adapter/projector/typed-port
  contracts `0`. Generated machine/human inventories classify 45
  non-Capability-reachable Tools without granting cleanup authority.
- Workstream C focused verification: capability/Pack/registry/planner,
  cross-domain Adapter/Result suites `221 passed` with one pre-existing
  optional skip; canonical isolated PostgreSQL/Redis/MinIO fresh-worker
  Agent paths passed `2/2` for RDF and two-step XRD projection. A canonical
  API process on port 8006 reported PostgreSQL/Redis/MinIO/worker backends
  healthy.
- Remote CI: workflow and authenticated CLI are available, but the final SHA is
  not on the remote because push was not authorized. Exact-SHA CI is not run.
  Local/service readiness is PASS; overall release readiness is CONDITIONAL.

## 7. Current Debt and Risks

- **Architecture debt:** four bounded frozen architecture allowlist edges.
- **Compatibility debt:** legacy facades and frozen worker/public paths remain.
- **Verification debt:** the final local SHA has not been pushed and therefore
  has no exact-SHA remote CI result.
- **Environmental/historical debt:** 76 accepted backend baseline failures
  remain historical/environmental; no current runtime observation is unresolved.
- **Context quality/scale debt:** provider token estimates vary and broader
  near-budget, very-large-Dataset and edited-branch stress evaluation remains
  future work; source authority and bounded behavior are established.
- **Capability quality debt:** structural completeness is now machine-checked,
  but scientific quality levels remain capability-specific and most manifests
  conservatively declare `STRUCTURAL_ONLY`.
- **Extension coupling debt:** built-in Requirement, Capability, Tool, Adapter,
  Artifact-port, projector and Viewer authorities remain explicit centralized
  registration points. The path is bounded and documented, but not a
  zero-central-edit plugin system.

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
- 2026-09-09: release qualification repaired retained same-stack worker startup,
  Windows PID-reuse validation, and production frontend proxy/SHA build wiring.
  Mandatory real-service `74/74`, authenticated browser runtime, frontend
  `950/950`, typecheck/build, migration head, worker registration, architecture,
  supply-chain, and provenance gates pass. Remote exact-SHA CI remains pending
  separately authorized push.
- 2026-09-10: corrected the active engineering lineage to
  `E:\1project\mdi-b0-5a1`, semantically recovered Workstream A and partial
  Workstream B into migrated canonical owners, completed provenance/freshness/
  memory/context visibility work, and reverified the canonical API, frontend,
  six workers and service-backed Agent paths. The old repository is now
  comparison/recovery source only.
- 2026-09-10: completed Workstream C with CapabilityManifest 1.2 extension
  metadata, deterministic cross-registry completeness validation, generated
  inventory/orphan classification, explicit optional presentation semantics,
  project-scope fail-closed resolution, developer guidance and canonical
  real-service RDF/XRD verification.

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
- Capability extension:
  [`docs/capabilities/SCIENTIFIC_CAPABILITY_EXTENSION_PLATFORM.md`](docs/capabilities/SCIENTIFIC_CAPABILITY_EXTENSION_PLATFORM.md),
  [`docs/capabilities/generated/capability_inventory.md`](docs/capabilities/generated/capability_inventory.md)

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
