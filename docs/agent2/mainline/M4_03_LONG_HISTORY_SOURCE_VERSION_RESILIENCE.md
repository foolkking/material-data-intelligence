# MDI V0 — M4-03 F14 Long-History / Source-Version Change Resilience

## Authority

- Committed base: `c4e74f922947be96833d0e276ad20f23241d6707`.
- M4-01/F11 and M4-02/F13 are externally accepted and intentionally remain
  uncommitted in the current worktree.
- Preserve all accepted M4-01 and M4-02 production/test changes.
- Do not reset, restore, clean, stash, commit, push, tag, release, run Phase D,
  run Phase E, start M5, or start a later M4 slice.

## F14 contract

- Exact historical name: `Longhistory after sourceversionchange`.
- Normalized name: `Long history after source version change`.
- Historical description:
  `20+distinctuserturns withboundedautonomouscycles; newsourceversion, priorreport/memory.`
- Required invariant:
  `Contextbudgetbounded; explicitoriginalvsnewversion; no self-citationescalation.`
- Historical owner: `M4`.

F14 asks whether one durable Research history remains truthful after 20 or more
distinct real user Turns when an immutable original source version (V1), its
prior Report/Interpretation/context projection, and a later version (V2) of the
same logical source coexist.

## Execution rule

Test current behavior before editing. Two valid outcomes exist:

1. If the current product satisfies every F14 invariant, make no production
   change and classify `SATISFIED_EXISTING_WITH_CURRENT_EVIDENCE`.
2. If a defect is reproduced, prove the earliest divergence, classify the
   exact owner, implement only the smallest generic version-exact, bounded,
   durable, idempotent correction, add focused tests, and rerun the same live
   campaign.

Do not force a product change merely because this is a new milestone slice.

## Entry baseline

Before M4-03 work:

1. Capture HEAD, status, unstaged diff, and staged diff.
2. Require HEAD
   `c4e74f922947be96833d0e276ad20f23241d6707`.
3. Record M4-01 paths as `M4_01_ACCEPTED_EXISTING` and M4-02 paths as
   `M4_02_ACCEPTED_EXISTING`.
4. Create `M4_03_ENTRY_WORKTREE_BASELINE.json`.

## Live F14 model

Use one isolated task-owned project and a supported scientific source family
with a deterministic independently verifiable change:

1. Create immutable V1 through the supported product path.
2. Build at least 20 distinct real user Turns in one durable Research history
   using normal submission paths and current autonomous-cycle limits.
3. Before V2, retain the current product equivalents of prior Report,
   Interpretation, context projection, and memory/summary, with exact
   source/version references.
4. Create V2 through the supported product version/update path. V1 and V2 must
   differ factually while retaining the logical source lineage represented by
   the product.
5. Continue the original Research history with a question requiring explicit
   V1-versus-V2 reasoning grounded in authorized facts.
6. Perform a negative rebound test: old V1 provenance must remain V1 and must
   never silently become V2.
7. Perform full reload and, where supported, new browser tab/context recovery
   using the built-in browser.

No direct DB insertion, fake Turns, identical prompt repetition, fixture-
specific response, latest-version fallback, in-place V1 mutation, DOM/storage
injection, or manual product-state repair is allowed.

## Hard invariants

- V1 and V2 are independently identifiable.
- Old Report/Interpretation/history provenance remains bound to V1.
- New V2-derived facts remain bound to V2.
- Context construction respects current configured bounds; 20+ durable Turns
  must not inject all raw history forever or increase public limits.
- Prior assistant prose, Interpretation, Report, Memory, and summaries remain
  projections and cannot become scientific fact authority.
- `SELF_CITATION_AS_AUTHORITY = 0`.
- `PROJECTION_TO_FACT_ESCALATION = 0`.
- History reconstruction/reload/version distinction causes zero Tool
  recomputations unless a real post-V2 request legitimately requires new
  science.
- duplicate admission, unexpected Jobs, duplicate authoritative Results,
  orphan scientific entities, and cross-workflow contamination are zero.
- ScientificResult remains fact authority; Interpretation remains a grounded
  projection.
- Current provider retry, schema, grounding, Tool, Context, and autonomous
  limits remain unchanged.
- Migration is expected to be `NO`; if exact durable version binding cannot be
  represented by current schema, stop with `M4_ARCHITECTURAL_BLOCKER` before
  adding a migration.

## Evidence

Use:

`_qualification/evidence/mainline_m4/m4_03_long_history_source_version_20260920/`

Classify it as `MAINLINE_MILESTONE_EVIDENCE`. Produce at minimum:

- `M4_03_ENTRY_WORKTREE_BASELINE.json`
- `M4_03_F14_AUTHORITY.json`
- `M4_03_CURRENT_BEHAVIOR_AUDIT.json`
- `M4_03_V1_V2_FIXTURE_AND_ORACLE.json`
- `M4_03_LONG_HISTORY_TRACE.json`
- `M4_03_CONTEXT_BUDGET_AUDIT.json`
- `M4_03_SOURCE_VERSION_BINDING_AUDIT.json`
- `M4_03_SUPPORT_AUTHORITY_AUDIT.json`
- `M4_03_EFFECT_AUDIT.json`
- `M4_03_IDENTITY_AUDIT.json`
- `M4_03_BROWSER_EVIDENCE.json`
- `M4_03_REGRESSION_RESULT.json`
- `M4_03_WORKTREE_CLASSIFICATION.json`
- `M4_03_SECRET_SCAN.json`
- `M4_03_FINAL_RESULT.json`

If production code changes, also create `M4_03_ROOT_CAUSE.json` and
`M4_03_IMPLEMENTATION_SUMMARY.md`.

Preserve raw test, API, worker, browser DOM/accessibility, screenshot, context,
and source-version traces. Package stable evidence with path, byte size, and
SHA256; explicitly classify dynamic logs. Require stable missing/hash mismatch
and unclassified package-member counts to be zero.

## Regressions and debt carry-forward

Run focused affected regressions for M4-01/F11, M4-02/F13, M1
ownership/fencing, M2 recovery/publication, and M3 Result-preserving
interpretation retry. Do not run Phase D, Phase E, or the 16-case campaign.

Carry forward:

- `NONBLOCKING_EVIDENCE_POINTER_ERRATUM`: M4-02 referenced
  `browser_f13_final_recheck.png` although it was absent from the reviewed ZIP.
- `NONBLOCKING_TEST_ENVIRONMENT_DEBT`: broad phase2 product-loop pytest retains
  an environment/SQLite coupling observation while task PostgreSQL/MinIO paths
  passed.

Do not claim either fixed unless this slice actually fixes it.

## Completion

`READY_FOR_EXTERNAL_M4_03_REVIEW` requires a real live campaign with at least
20 distinct Turns, supported V1/V2 creation, bounded context, explicit
original/new distinction, exact historical provenance, no silent rebound, no
self-citation escalation, durable reload/new-session recovery, zero unexpected
duplicate/orphan effects, affected regressions passing, no shared-resource
damage, and whole-worktree `UNKNOWN = 0`.

M4-01, M4-02, and M4-03 remain one accumulated uncommitted M4 worktree. Stop
after M4-03 for external review.
