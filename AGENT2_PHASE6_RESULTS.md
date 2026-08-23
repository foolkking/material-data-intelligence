# AGENT2_PHASE6_RESULTS

## Verdict

**PARTIAL - current-head CI pending**

All local implementation, deterministic, live-provider, service-backed,
browser, migration, backend, and frontend gates pass. The only remaining
closure item is the pushed current-head GitHub Actions result.

## Starting State

- Starting HEAD and `origin/master`:
  `a16a911567db99c84c5e6e8ad15f6fda5a3d29c8`.
- Alembic starting head: `0021_agent2_scientific_result_projection`.
- Phase 5 closure current-head CI was verified as run `32617347658`; older
  Phase 5 runs remain historical evidence.

## Migration And Persistence

- Added `0022_agent2_scientific_interpretation`, down revision
  `0021_agent2_scientific_result_projection`.
- `agent2_scientific_interpretations` is immutable and unique by
  `research_turn_id`. Multiple new turns may interpret the same historical
  result snapshot.
- Persisted identity includes source result snapshot, input fingerprint,
  contract/prompt/provider/model metadata, bounded structured output,
  grounding status, and repair flag.
- SQLite `0022 -> 0021 -> 0022` round-trip and clean PostgreSQL migration from
  base through `0022` passed.

## Interpreter And Grounding

- `InterpreterInputAssembler` supplies only bounded ScientificResult facts,
  result items, compact figure/table metadata, evidence, methods,
  limitations, warnings, the question, and effective relevance. It never
  supplies raw Artifact payloads.
- Prompt version: `scientific-interpreter/1.0`.
- The existing server-managed DeepSeek/OpenAI-compatible transport is reused;
  provider calls assert there is no open DB transaction.
- Normal output takes one call; schema or grounding failure permits one repair
  and no third call.
- Every positive finding needs a valid Fact or Evidence reference. Numeric
  tokens must equal referenced scalar Fact values and units must match without
  conversion. Unknown references, invented numbers, unit substitutions, and
  new `answer_lead` numbers are rejected.
- The deterministic AssistantResponseProjector injects PARTIAL, STALE,
  SOURCE_MISSING, and INVALIDATED notices and renders only validated output.

## Lifecycle And Product Path

- Normal path: `RESULT_READY -> INTERPRETING -> COMPLETED / PARTIAL`.
- Phase 5 publishes an identity-only interpretation task only after the
  RESULT_READY transaction commits. Queue failure leaves RESULT_READY durable
  and recoverable.
- A fresh worker reloads all authority from PostgreSQL using only `turn_id`.
- Phase 2 `INTERPRET_RESULT` turns reuse the authorized opaque result reference
  and create no plan, Job, ToolCall, Artifact, or result snapshot.
- One grounded interpretation, one existing ASSISTANT ResearchMessage, and one
  terminal transition are persisted per turn. Duplicate delivery reuses the
  stored record; stale worker claims can be republished.
- Product APIs expose only the bounded interpretation/message view. Provider
  prompt, raw output, request IDs, tokens, and runtime IDs remain internal.

## No-Mutation Evidence

During interpretation:

```text
AnalysisPlan delta = 0
Job delta = 0
ToolCall delta = 0
Artifact delta = 0
ScientificResultSnapshot delta = 0
```

The previous-result test interprets one existing snapshot from two independent
new ResearchTurns and verifies the same zero-delta contract.

## Tests

- Phase 6 deterministic: `8 passed, 1 skipped` (the skip is the explicitly
  gated live test).
- Agent2 Phase 2-6 focused regression: `89 passed, 6 skipped`.
- Live DeepSeek: `1 passed, 8 deselected`; schema/reference/numeric/unit
  grounding passed.
- Fresh service-backed RDF and two-step XRD: `2 passed`, selected skip `0`.
  Fresh PostgreSQL, Redis, MinIO, execution workers, result workers, and two
  independent interpretation workers were used.
- Full backend non-integration: `1731 passed, 65 skipped`.
- Frontend Vitest: `85 files, 570 passed`.
- Frontend typecheck and isolated production build: passed.
- `compileall`, `uv lock --check`, Alembic heads/current, migration round-trip,
  and `git diff --check`: passed.
- Browser: authenticated Research view at `390x844`; document and body
  `scrollWidth=390`, no horizontal overflow.
- `npm run lint` is not claimed: the repository command still invokes the
  deprecated interactive `next lint` path.

## Current-Head CI

Pending the implementation push. This section and the verdict must be updated
only after the exact pushed SHA has passed all current workflow jobs.

## Not Implemented In Phase 6

Full multi-turn Research Memory; semantic long-session retrieval; general
continuation/re-analysis memory; Report Composer; Data Management mutations;
full 62-tool capability mapping; professional Viewer expansion; Viewer
linked-selection expansion; Tool/plugin ecosystem; and the Phase 2
ORCHESTRATING lease/reaper.
