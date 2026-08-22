# Agent 2.0 Phase 2 Results

Date: 2026-08-22
Verdict: `COMPLETE`

## Scope

Implemented deterministic authorized context candidate assembly, compact
context/fingerprint, immutable context reuse, opaque reference validation,
`ResearchTurnDecision 1.0`, StructuredLLMClient with DeepSeek adapter,
versioned orchestration prompt, one bounded repair, action validation/routing,
decision persistence, Turn wakeup queue, product SSE projections, and strict
C01-C15 evaluation fixtures.

## Migration

The verified pre-change Alembic head was `0017_agent2_scientific_results`.
Revision `0018_agent2_orchestration_decisions` has down revision
`0017_agent2_scientific_results` and creates `research_turn_decisions` with one
validated decision per ResearchTurn, input fingerprint, prompt and bounded
provider metadata, repair/validation fields, and an independent downstream
dispatch status.

## Context system

Candidate sources are exact UI selection/current scope, exact refs in up to six
recent terminal context snapshots, up to six persisted Result snapshots, and
bounded visible messages. Server authorization verifies Project, logical
object, exact version and object type. Priority is explicit > UI selection >
scope > previous Result > pinned > recent. Equal highest-priority object refs
clarify before DeepSeek; lower-priority decisions fail validation.

UI input and assembled candidate counts are explicitly capped. The compiler
measures serialized UTF-8 size against the conservative token budget and
deterministically removes oldest/lowest-priority optional context until it
fits, failing closed if the required context itself cannot fit.

The context fingerprint includes Project/Turn identity, opaque keys, exact
object/version IDs, Result identity/relevance, constraints, retained Turn IDs
and compiler version. Snapshot persistence commits before the provider call and
does not include secrets.

## Orchestrator

Prompt version is `research-orchestrator/1.0`. The adapter reuses the existing
server-managed DeepSeek OpenAI-compatible transport and `DEEPSEEK_KEY`; no key
or provider configuration is persisted. Output schema is generated from
Pydantic. Schema/semantic failure receives one bounded repair, then a typed safe
Turn failure. Instrumented tests prove the provider call has no open UnitOfWork
transaction.

## Actions

| Action | Phase 2 status |
|---|---|
| `ANSWER` | fully routed to one final Message and `ANSWERED` |
| `CLARIFY` | fully routed to one question and `NEEDS_CLARIFICATION` |
| `ANALYZE` | fully routed to validated requirements and `READY_TO_PLAN` |
| `CONTINUE_ANALYSIS` | fully routed to prior Turn/Result plus `READY_TO_PLAN` |
| `INTERPRET_RESULT` | classification only, ready for downstream |
| `QUERY_DATA` | classification only, ready for downstream |
| `MANAGE_DATA` | classification only; no mutation |
| `OPEN_OBJECT` | classification only; no storage URL |
| `CREATE_REPORT` / `UPDATE_REPORT` | classification only; no composition |
| `EXPORT` | classification only; no export |

## Evaluation and local verification

- Deterministic C01-C15 fixture contract: 15/15.
- Deterministic canonical/paraphrase matrix: 60/60.
- Live DeepSeek canonical qualification C01/C02/C03/C05/C07: 5/5.
- Live DeepSeek full eligible canonical/paraphrase routing: 48/48 (100%).
- SQLite migration upgrade/downgrade/re-upgrade: 1 passed.
- Isolated PostgreSQL + Redis Phase 2 service gate: 1 passed.
- Combined Phase 1 + Phase 2 service-backed gate: 2 passed.
- Focused Agent 2.0 checkpoint: 48 passed, 2 live-gated skipped; later focused
  contract/API additions also pass.
- Complete backend non-integration/non-qualification suite: 1638 passed, 5
  skipped, 84 deselected, 75 warnings.
- Complete frontend Vitest suite: 84 files, 565 tests passed.
- Frontend typecheck and isolated Next.js production build: passed.
- `uv lock --check`, Python `compileall`, Alembic head, SQLite migration
  round-trip, and `git diff --check`: passed.
- Current-HEAD implementation CI run `32573620585`: 1638 Unit tests passed,
  service-backed integration 52 passed/0 skipped/0 failed/0 errors, Frontend
  tests/typecheck/build/Phase 12-6/12-7 passed, and Linux/Windows scientific
  replay passed.

## No-execution evidence

For ANSWER, CLARIFY, ANALYZE, CONTINUE_ANALYSIS, result reuse and downstream
classification acceptance cases:

```text
AnalysisPlan delta = 0
Job delta = 0
ToolCall delta = 0
```

## Explicitly not implemented

`NOT IMPLEMENTED`: Capability Resolver; Capability eligibility; CapabilityPlan;
Capability-to-Tool binding; AnalysisPlan creation from ResearchTurn; Job
attachment; Execution Supervisor integration; JobEvent scientific progress;
production ScientificResult projection; Scientific Interpreter; grounded final
scientific response; full multi-turn memory; Report Composer; Data Management
execution; professional Viewer integration; full 62-Tool capability mapping.

## Risks / open items

- Production orchestration is explicitly enabled and requires a separately
  running RQ worker. A process loss after the ORCHESTRATING claim has no lease
  reaper in Phase 2; automatic recovery remains a later supervisor concern.
- Semantic retrieval beyond the bounded recent-window and exact supplied refs
  is intentionally absent.

## Verdict

`COMPLETE` - deterministic context, structured orchestration, decision routing,
local/live qualification, regression and current-HEAD CI acceptance gates pass.
