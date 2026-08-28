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
identities. Provider/runtime benchmarking and browser-scale performance
evidence remain open qualification work.
