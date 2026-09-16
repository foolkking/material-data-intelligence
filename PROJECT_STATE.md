# PROJECT_STATE

> Compact human-readable current-project snapshot. Specialized authorities
> remain authoritative in their own domains; this file summarizes and points
> to them. It is not a replacement for task, result, architecture,
> qualification, runtime, or historical ledgers.

## 1. Current Status

- `PROJECT_PHASE`: Source/physical migration and capability parity are closed;
  Workstreams A-I now provide lifecycle reliability, provenance-aware Context
  and Memory, explicit and qualified scientific capabilities, bounded
  evidence-driven autonomy/strategy, a scientist-facing Research product, an
  authorized provenance-preserving scholarly knowledge layer, and bounded
  claim-level scientific reasoning assessment. Remote
  exact-SHA CI remains a separately authorized release gate.
- `CURRENT_PRODUCT_RELEASE_SCOPE`: `V0`
- `CURRENT_PRODUCT_DEFINITION`: natural-language-driven materials research
  analysis and visualization workbench
- `CURRENT_ACCEPTED_COMMIT`: `2727e94ba6adaaf0c6ff9914f8137d130b34c777`
- `SNAPSHOT_BASE_COMMIT`: `2727e94ba6adaaf0c6ff9914f8137d130b34c777`
- `WORKTREE_EXPECTATION`: existing migration worktree, detached HEAD, with
  locally verified Workstream H/I/J preparation changes not yet committed or
  pushed
- `LAST_ACCEPTED_REVIEW`: Pre-M0 attempt-02,
  `ACCEPTED`, 2026-09-12
- `LAST_UPDATED_AT`: `2026-09-12`
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

- The current roadmap defines the first complete product release scope as
  `V0`. Historical documents may call earlier milestones `V1` or
  `Initial Release`; those names are retained as history and do not override
  the current V0 route.
- Workstreams A-I are complete. Workstream I is a bounded structured
  scientific reasoning guard, not a runtime expert reviewer or scientific
  certification authority.
- Workstream J is `REVIEW_READY` with frozen responses and pending independent
  human review. It is an offline parallel validation lane, not a runtime
  feature or an engineering blocker.
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

- `CURRENT_WORKSTREAM`: Pre-M1 through Pre-M3 executed in chained attempts;
  external review remains pending and Pre-M4 has not started.
- `CURRENT_TASK`: Pre-M1 → Pre-M2 → Pre-M3 chained execution,
  `READY_FOR_REVIEW` / `PARTIAL` evidence sealed.
- `NEXT_ENGINEERING_STAGE`: external review of Pre-M1/2/3, then Pre-M4;
  M0-M6 remains the required later V0 long-running/scale/fault-tolerance
  stage after Pre-M completion.
- `PARALLEL_VALIDATION`: Workstream J remains `REVIEW_READY`; its frozen
  independent-scientist packets may be distributed and imported independently
  of the engineering route.
- `WORKSTREAM_K`: `CONDITIONAL_ONLY` on reproducible major/critical defects
  established by actual J reviewers.
- `BLOCKED_ITEMS`: no unresolved product-direction blocker. Independent human
  review remains pending but does not block Pre-M or M. Do not claim
  `INDEPENDENT_HUMAN_EXPERT_VALIDATION=YES` or a scientist maturity verdict
  while the ledger is empty.
- `G_BEHAVIORAL_SEMANTIC_READINESS`: `COMPLETE`.
- `DEEP_VISUAL_COMPLEX_CONTENT_QUALIFICATION`:
  `PENDING_PRE_M4_PRE_M5`.
- `UI_LAYOUT_SYSTEM_V2`: `FROZEN_DESIGN_ACCEPTANCE_BASELINE`.
- `CURRENT_UI_LAYOUT_CONFORMANCE`:
  `PENDING_PRE_M3_PRE_M4_BROWSER_QUALIFICATION`.
- `ATTACHMENT_CONTEXT_EXPERIENCE`: `IMPLEMENTED_WITH_TARGETED_EVIDENCE`;
  full Pre-M qualification remains pending.
- `COMPLEX_MATERIAL_DATA_QUALIFICATION`: `PENDING_PRE_M5`.
- `SCIENTIST_UI_UX`: `PARTIAL_PRE_M3_EVIDENCE`; current replay does not
  constitute a human usability certification.
- `PRE_M_BLOCKERS`: `NOT_YET_ASSESSED_FOR_PRE_M1_PRE_M3_CHAIN`.
- `READY_FOR_M`: `NO_PRE_M_NOT_COMPLETE`.
- `FINAL_V0_REQUIRES_NEW_J_CANDIDATE`: `YES`; the existing frozen J candidate
  remains preserved as `PRE-CORRECTION_SCIENTIFIC_CANDIDATE`.
- `M_ROUTE`: `REQUIRED_V0_STAGE`, after Pre-M and before Final V0
  Integrated Acceptance.

## 6. Verification State

- Pre-M Context/Result-reuse correction: `17 passed`.
- Pre-M complex-family production regression excluding immutable historical
  raw-byte manifest checks: `380 passed, 1 skipped`.
- Current frontend: `119 files / 961 tests PASS`; typecheck and production
  build PASS.
- Current Chromium layout replay: desktop and `390x844` PASS with no global
  horizontal overflow, browser errors or frontend scientific recomputation.
- Pre-M integrated verdict:
  `COMPLEX_MATERIAL_DATA=PASS_WITH_EXPLICIT_LIMITS`,
  `PRE_M_BLOCKERS=0`, `READY_FOR_M=YES`.
- Historical evidence-manifest raw byte assertions remain sensitive to
  Windows LF/CRLF checkout conversion; their historical content was not
  rewritten to manufacture a green result.

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
  pass; Alembic head is `0033_scientific_knowledge`; Redis and live worker
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
- Scientific quality inventory: all `17` capabilities have explicit,
  evidence-backed, version-aware status: `6 DOMAIN_VALIDATED`,
  `3 REFERENCE_VALIDATED`, and
  `8 EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED`; validation errors `0`.
  Evidence totals are `9` reference, `8` invariant, `17` domain-negative,
  `2` Result-projection, `7` interpretation and `2` report cases.
- Workstream D focused verification: scientific quality/capability contracts
  `20 passed`; cross-domain Adapter/scientific suites `196 passed`; bounded
  Result/Interpretation/Report quality suites `111 passed, 4 skipped,
  1 deselected`; frontend scientific presentation semantics `41 passed`;
  architecture checks `9 passed` plus zero forbidden canonical edges.
- Workstream D canonical real-service verification: `6 passed` across
  qualification-owned PostgreSQL, Redis/RQ and MinIO, covering RDF/XRD
  Research execution and coordination, trajectory, electronic and phonon
  semantics through fresh subprocess workers.
- Workstream E bounded autonomy: explicit `STANDARD` versus
  `BOUNDED_AUTONOMOUS`, policy caps `4` cycles / `8` executions / `4`
  dependency steps / `8` LLM decisions, current qualification-fingerprint
  enforcement, semantic duplicate prevention, typed stop outcomes, one
  ContextSnapshot per child Turn and read-only lifecycle projection.
- Workstream E focused verification: backend autonomy/lifecycle/context/
  planning/worker/capability/quality suites `218 passed, 7 skipped`; Research
  frontend `101 passed`; Ruff, compileall, typecheck, production build,
  architecture report/guard and diff checks pass. The generated autonomy
  evaluation passes `7/7` cases with qualified-selection violations `0`,
  redundant executions `0`, loop-prevention events `1`, correct scientific
  stops `4/4` and unsupported-claim violations `0`.
- Workstream E canonical real-service verification: qualification-owned
  PostgreSQL, Redis/RQ and MinIO path passed through fresh canonical workers.
  It reused the exact persisted MSD Artifact, derived diffusion parameters from
  durable MSD Result facts, recovered the same child Turn after publication
  failure, executed diffusion without recomputing MSD and stopped with
  `GOAL_SATISFIED`. A sanitized live DeepSeek ingress case passed and selected
  the bounded trajectory entry; downstream autonomy remained deterministic.
- Workstream F scientific strategy: a derived `ResearchEvidenceState`, typed
  scientific questions/evidence gaps/hypotheses, comparison/contradiction
  semantics, minimum-sufficient evidence rules and bounded validated provider
  proposals are integrated into the existing autonomy lifecycle. The progress
  API/UI expose the current question, evidence gap, tentative hypothesis,
  continuation basis or typed stop reason without hidden reasoning.
- Workstream F focused verification: deterministic strategy corpus `12/12`;
  correct scientific stops `7/7`; correct cross-family transitions `1/1`;
  irrelevant Capability executions, redundant executions, hypothesis
  overclaims, comparison violations, qualification violations and unsupported
  claims all `0`. Focused A-F backend suites passed `105` with `3` expected
  skips; API progress tests passed `31`; Research strategy UI passed `13`;
  typecheck, Ruff, compileall and generated strategy report pass.
- Workstream F canonical provider/service evidence: three sanitized live
  DeepSeek strategy cases pass; a fresh-worker MSD → diffusion recovery/reuse
  path, an ML evaluation → composition-space Result-driven cross-family
  planning path and the real composition-space capability path pass against
  qualification-owned PostgreSQL, Redis/RQ and MinIO. Canonical API port 8007
  reports all backends and six queues healthy.
- Workstream G scientist product maturity: `15` acceptance journeys, including
  five canonical persisted browser journeys and two mobile journeys; default
  raw-ID exposure, blocking mobile overflow, fatal browser errors and frontend
  scientific-authority violations are all `0`. Focused backend `59 passed,
  1 skipped`; focused frontend `177/177`; production build/typecheck PASS.
- Workstream H scientific knowledge authority: canonical `LiteratureWork`,
  immutable `LiteratureSnapshot`, selected `LiteratureEvidence`, bounded
  `LiteratureQuery`, explicit scope/publication/access/support semantics,
  deterministic DOI/arXiv identity and cross-provider reconciliation are
  integrated with existing Context, strategy, Research, Report and Workbench
  projections without creating ScientificResult or qualification authority.
- Workstream H evaluation: deterministic corpus `15/15`; live OpenAlex `1`,
  live Crossref `1`, live DeepSeek literature synthesis `2`; exact identity
  `2/2`, cross-provider reconciliation `1/1`, and all irrelevant-source,
  unsupported-claim, citation-support, abstract-scope, retraction-support,
  unauthorized-query, Result-authority and qualification-mutation violations
  are `0`.
- Workstream H focused verification: backend scientific-knowledge/report/
  Context/strategy suites `89 passed, 5 skipped`; bounded autonomy/product
  regression `28 passed, 1 skipped`; Research literature UI `111 passed`;
  Ruff, compileall, typecheck, production build and diff check PASS. Real
  PostgreSQL/API persistence verified search → evidence selection → exact
  historical snapshot reopen and deterministic Report citation; canonical
  API runtimes on ports 8005/8009 and frontend on 3014 were healthy. An
  authenticated H browser interaction was not recreated because no reusable
  local browser session was available; UI authority is covered by focused
  component/integration tests and the real authorized API path.
- Workstream I expert scientific reasoning: `scientific-reasoning/1.0` adds
  claim type/support/scope/method/comparison assessment over existing Results
  and LiteratureEvidence without a new truth authority. It fails closed for
  unsupported causal or universal claims, abstract overreach, evidence double
  count, authority escalation and LLM numeric derivation; Interpretation 1.1
  and Report 2.0 carry only accepted assessments.
- Workstream I evaluation: 27 repository-owned cases preserved a pre-fix
  baseline of 22 invalid acceptances; final deterministic violations are all
  zero, with insufficient-evidence `17/17`, method-dependence `1/1` and
  contradiction `2/2` outcomes correct. Five sanitized live DeepSeek cases
  passed under one bounded repair and deterministic validation. Independent
  human expert validation is explicitly `NO`.
- Workstream I focused verification: reasoning/knowledge/interpretation/report
  suites `108 passed, 5 skipped`; autonomy/strategy/product regressions
  `36 passed, 2 skipped`; Ruff, compileall and diff checks PASS. A real
  rollback-only PostgreSQL smoke persisted/reopened a Result, Interpretation
  1.1 and Report 2.0 with an unchanged assessment fingerprint and no hidden
  reasoning persisted.
- Workstream J preparation: one frozen baseline, `24` formal responses, `4`
  calibration cases, `6` optional shadow slots, `8` anchors and `56` balanced
  assignments are present under `docs/scientist-evaluation/`. The human ledger
  has `0` records; `J_STATUS=REVIEW_READY`,
  `J_FORMAL_RESPONSES=FROZEN`,
  `INDEPENDENT_HUMAN_EXPERT_VALIDATION=PENDING` and
  `SCIENTIST_VALIDATION_MATURITY=NOT_YET_ASSESSED`. Preparation/focused
  regression verification passed `52` tests plus Ruff, compile and generated
  integrity checks.
- V0 production semantic audit: reviewed `56` modified production files and
  all production LLM call sites. No secondary reviewer/critic runtime,
  AI-as-human-expert runtime, or J-evaluation production dependency was found.
  One real authority-boundary defect was fixed: Report ContextManifest
  previously labeled validated Interpretation prose as `SCIENTIFIC_RESULT`;
  it now uses `INTERPRETATION` / `DERIVED_SUMMARY`, with fail-closed manifest
  compatibility checks. Frozen J artifacts remain unchanged, so the current
  J candidate is `PRE-CORRECTION_SCIENTIFIC_CANDIDATE`.
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
- **Capability quality debt:** all capabilities now have explicit evidence
  status and none are anonymously structural-only. Eight library/solver-backed
  capabilities remain deliberately scoped to platform-owned parsing, units,
  projection and limitation semantics; independent validation of the upstream
  scientific implementation is not claimed.
- **Scientific reasoning debt:** bounded deterministic claim assessment now
  constrains the evaluated corpus and live-provider projection, but it is not
  independent materials-scientist validation. Broad-domain semantic edge cases,
  richer causal designs and human review remain future/parallel work; they do
  not turn I into a runtime expert reviewer.
- **Extension coupling debt:** built-in Requirement, Capability, Tool, Adapter,
  Artifact-port, projector and Viewer authorities remain explicit centralized
  registration points. The path is bounded and documented, but not a
  zero-central-edit plugin system.
- **Scientific strategy breadth debt:** the durable finite strategy model is
  ready, including selected cross-family transitions, hypotheses,
  contradiction handling and minimum-sufficient stopping. It remains
  intentionally typed for current capability families; arbitrary scientific
  strategy, causal inference and universal method comparison are not claimed.
- **Scientific knowledge debt:** the scholarly layer is deliberately
  query-driven and limited to OpenAlex/Crossref metadata plus exact
  user-provided or authorized retrieved passages. It does not claim OCR,
  unrestricted publisher full text, broad offline indexing, generic web
  authority or a vector database. Deterministic identity/numeric grounding and
 bounded qualitative claim assessment are in place; independent human expert
 review remains an explicitly parallel validation uncertainty.
- **Independent scientist evaluation debt:** the reviewer-blinded J corpus,
  frozen responses and import/report infrastructure are ready, but no real
  independent scientist submissions have been imported. Scientist validation
  maturity is therefore intentionally not assessed. This does not block the
  Pre-M/M engineering route.

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
- 2026-09-10: completed Workstream D with evidence-backed qualification levels,
  reference provenance and tolerance contracts, applicability/invariant/
  negative evidence, version-aware scientific fingerprints, bounded
  interpretation/report rubrics, generated quality inventory and canonical
  cross-domain real-service verification.
- 2026-09-10: completed Workstream E with explicitly activated finite autonomy,
  quality-aware Result-driven continuation, exact persisted Artifact reuse,
  Result-grounded downstream parameters, duplicate/loop prevention, typed stop
  reasons, durable child-Turn recovery, cancellation preservation, lifecycle
  observability and bounded golden/real-provider/service-backed evidence.
- 2026-09-10: completed Workstream F with Result-first evidence-state
  projection, typed questions/gaps/hypotheses, objective-driven cross-family
  strategy, comparison/contradiction safeguards, minimum-sufficient stopping,
  one-repair structured provider validation, concise Research strategy
  visibility and canonical real-provider/service-backed evidence.
- 2026-09-10: completed Workstream G with a scientist-facing Research
  timeline/map, visible current question and evidence gaps, non-authoritative
  hypothesis treatment, explicit continuation/stop/control semantics,
  result-first source/version/limitation disclosure, safer comparison and
  recovery states, identity-safe project/dataset labels, mobile continuity and
  five canonical persisted browser journeys. Product maturity is
  `READY_FOR_BOUNDED_SCIENTIST_USE`; no scientific or execution authority
  moved into the frontend.
- 2026-09-11: completed Workstream H with deterministic scholarly identity,
  immutable retrieval snapshots, explicit evidence scope/access/publication
  status, allowlisted OpenAlex/Crossref clients, privacy-safe bounded queries,
  selected LiteratureEvidence, claim/citation lineage, Report bibliography,
  literature Workbench UX, exact historical reopen, provider-failure recovery
  and live provider/DeepSeek verification. Literature remains non-Result,
  non-qualification authority.
- 2026-09-11: completed Workstream I with a repository-owned 27-case
  evaluation corpus, immutable 22-failure baseline, bounded claim-support and
  method/scope/lineage/contradiction assessment, Interpretation/Report
  propagation, deterministic final zero-violation evidence, five sanitized
  live-provider cases and real PostgreSQL rollback persistence verification.
  Maturity is `BOUNDED_EXPERT_REVIEW_READY`; independent human expert
  validation remains `NO`.
- 2026-09-11: reconciled V0 product direction without changing runtime
  scientific behavior. Secondary LLM reviewer/critic behavior is absent from
  the active runtime; I remains a structured reasoning guard, J is parallel
  external human validation, K is conditional only, Pre-M0 is next and M0-M6
  remains required for V0.

## 11. Source Pointers

- Queue: [`TASKS.md`](TASKS.md)
- Results: [`results.md`](results.md)
- V0 scope alignment:
  [`docs/alignment/V0_SCOPE_ALIGNMENT.md`](docs/alignment/V0_SCOPE_ALIGNMENT.md)
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
- Scientific quality:
  [`docs/scientific-quality/SCIENTIFIC_QUALITY_AND_QUALIFICATION.md`](docs/scientific-quality/SCIENTIFIC_QUALITY_AND_QUALIFICATION.md),
  [`docs/scientific-quality/ADDING_REFERENCE_EVIDENCE.md`](docs/scientific-quality/ADDING_REFERENCE_EVIDENCE.md),
  [`docs/scientific-quality/generated/scientific_quality_inventory.md`](docs/scientific-quality/generated/scientific_quality_inventory.md)
- Bounded scientific autonomy:
  [`docs/agent2/autonomy/BOUNDED_SCIENTIFIC_AUTONOMY.md`](docs/agent2/autonomy/BOUNDED_SCIENTIFIC_AUTONOMY.md),
  [`docs/agent2/autonomy/AUTONOMY_POLICY_AND_QUALITY_RULES.md`](docs/agent2/autonomy/AUTONOMY_POLICY_AND_QUALITY_RULES.md),
  [`docs/agent2/autonomy/generated/autonomy_evaluation.json`](docs/agent2/autonomy/generated/autonomy_evaluation.json)
- Scientific research strategy:
  [`docs/agent2/strategy/SCIENTIFIC_RESEARCH_STRATEGY.md`](docs/agent2/strategy/SCIENTIFIC_RESEARCH_STRATEGY.md),
  [`docs/agent2/strategy/HYPOTHESIS_AND_EVIDENCE_POLICY.md`](docs/agent2/strategy/HYPOTHESIS_AND_EVIDENCE_POLICY.md),
  [`docs/agent2/strategy/generated/strategy_evaluation.json`](docs/agent2/strategy/generated/strategy_evaluation.json)
- Scientist product maturity:
  [`docs/product-maturity/SCIENTIST_RESEARCH_EXPERIENCE.md`](docs/product-maturity/SCIENTIST_RESEARCH_EXPERIENCE.md),
  [`docs/product-maturity/RESEARCH_CONTROL_SEMANTICS.md`](docs/product-maturity/RESEARCH_CONTROL_SEMANTICS.md),
  [`docs/product-maturity/SCIENTIST_PRODUCT_ACCEPTANCE.md`](docs/product-maturity/SCIENTIST_PRODUCT_ACCEPTANCE.md),
  [`docs/product-maturity/generated/scientist_ux_acceptance.json`](docs/product-maturity/generated/scientist_ux_acceptance.json)
- Scientific knowledge and literature:
  [`docs/scientific-knowledge/SCIENTIFIC_KNOWLEDGE_AUTHORITY.md`](docs/scientific-knowledge/SCIENTIFIC_KNOWLEDGE_AUTHORITY.md),
  [`docs/scientific-knowledge/LITERATURE_PROVIDER_AND_ACCESS_POLICY.md`](docs/scientific-knowledge/LITERATURE_PROVIDER_AND_ACCESS_POLICY.md),
  [`docs/scientific-knowledge/LITERATURE_EVIDENCE_AND_CITATION.md`](docs/scientific-knowledge/LITERATURE_EVIDENCE_AND_CITATION.md),
  [`docs/scientific-knowledge/generated/literature_integration_evaluation.json`](docs/scientific-knowledge/generated/literature_integration_evaluation.json)
- Expert scientific reasoning:
  [`docs/scientific-reasoning/SCIENTIFIC_CLAIM_AND_SUPPORT_MODEL.md`](docs/scientific-reasoning/SCIENTIFIC_CLAIM_AND_SUPPORT_MODEL.md),
  [`docs/scientific-reasoning/METHOD_COMPARISON_AND_INFERENCE_POLICY.md`](docs/scientific-reasoning/METHOD_COMPARISON_AND_INFERENCE_POLICY.md),
  [`docs/scientific-reasoning/EXPERT_REASONING_EVALUATION.md`](docs/scientific-reasoning/EXPERT_REASONING_EVALUATION.md),
  [`docs/scientific-reasoning/generated/expert_reasoning_evaluation.json`](docs/scientific-reasoning/generated/expert_reasoning_evaluation.json)

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
