# Research Context / Memory / Message Provenance 2.0

## Current implementation

Bounded candidate assembly, authorization, lexical retrieval, memory pins,
constraints, goals, immutable ContextSnapshots and deterministic compaction
are implemented in:

* `apps/api/mdi_api/research_agent/context/schemas.py`
* `apps/api/mdi_api/research_agent/context/assembler.py`
* `apps/api/mdi_api/research_agent/context/compiler.py`
* `apps/api/mdi_api/research_agent/memory/{schemas,service}.py`
* `apps/api/mdi_api/db.py` (`research_context_snapshots`,
  `research_session_states`, `research_session_context_items`)

## Required 2.0 semantics

Every meaningful provider operation must be explainable by an immutable
manifest containing:

```text
manifest id, operation, project/session/turn ids, policy version,
included and excluded items, token budget/estimate, compaction/truncation
state, fingerprint, creation time
```

Each included item retains server-side identity, opaque provider reference,
authority class, exact object/version and Result/Finding/message revision
references, inclusion reason, authorization result, content fingerprint,
token estimate, compaction/truncation flags and superseded state.

The provider receives bounded opaque references and grounded content only;
server-side records retain exact identities. User assertions, preferences and
constraints never become scientific facts. Fresh Research resets working
conversation context; Continue reuses explicit session state; historical turns
reopen their original snapshot.

The checked-in `ContextBudgetPolicy 2.0` in
`apps/api/mdi_api/research_agent/context/policy.py` computes:

```text
min(provider_context_limit, product_global_limit, operation_specific_limit)
- reserved_output_tokens
- repair_margin
```

Current effective input budgets are 12,000 tokens for orchestration, 10,000
for planning, 12,000 for interpretation, and 8,000 for bounded data context.
The compiler compacts deterministically and preserves exact scientific
identities. Current qualification covers deterministic boundary behavior,
real persisted provider-operation manifests and authenticated historical
browser replay.

## Authenticated exact-context replay evidence (2026-08-30)

The current same-stack browser reopened ResearchTurn
`7c65deb0-5791-4340-b6e6-ead5a8733445` and expanded its user-facing
`本次研究使用的上下文` disclosure. It exposed three recorded operation
manifests:

```text
理解问题
解释结果
整理报告
```

The disclosure retained exact scientific version
`8859cb49-0766-48cd-8a56-e44f5332e0c5` and exact prior Result
`14ce2fd1-e5bc-4798-906f-3333df2f7a91`, and reported `无需压缩` plus
`关键上下文完整`. The UI disclosed authority and inclusion purpose without
exposing prompts, provider transcripts or private chain-of-thought. This
closes the canonical Structure browser replay of ContextManifest 2.0; the
broader near/over-budget, large Dataset and edited-branch stress matrix remains
open.

## Current budget and replay closure (2026-09-01)

The operation-manifest suite now exercises every checked-in operation
(`ORCHESTRATOR`, `PLANNER`, `INTERPRETER`, `DATA`, `REPORT`) at five explicit
payload boundaries:

```text
well below budget
near budget
exactly at budget
over budget
significantly over budget
```

Non-critical overflow is recorded as deterministic compaction. Critical
scientific context that cannot fit fails closed. The focused suite is
`11 passed`.

PostgreSQL inspection of the current same-stack qualification database found
`458` persisted ContextManifests:

```text
ORCHESTRATOR 317 · max 241 / budget 12000
PLANNER       60 · max 476 / budget 10000
INTERPRETER   60 · max 1157 / budget 12000
REPORT        21 · max 1802 / budget 10000
```

No persisted manifest reported truncation. The authenticated historical
Research page for Turn `fb72c2ad-bed1-47d7-b557-f398f04a8ede` exposes
understanding, planning, interpretation and two Report composition manifests.
Its audit disclosure shows manifest
`c4785024-6027-42af-9a1f-52143afd7303`, policy
`agent2.context-policy/2.0`, budget `12000`, estimate `60`, fingerprint
`6daaf41b284e5ce5211b62c6555b9d471e2769c96c6d635c14b731fbe6c35369`
and exact version `a22745f2-17b6-434f-ba4c-3fe6bd244841`.

The earlier 2026-08-30 “stress matrix remains open” sentence is retained as a
historical checkpoint; the current contract is `PASS`.

## Long-manifest inspection affordance (2026-09-04)

The Research disclosure keeps the first eight included context items as its
default bounded preview, but now exposes an accessible expand/collapse control
when the persisted manifest contains more than eight items. The expanded view
reads the same authorized `included_items` projection and does not change
selection, provider payloads, scientific authority, or execution. Expansion is
reset when the selected ResearchTurn changes, so a branch cannot inherit the
previous Turn's display state.
