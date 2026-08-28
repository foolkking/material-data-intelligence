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

Current gap: no explicit persisted `ContextManifest`/`ContextItem` model or
user-facing “Used context” disclosure is present in the sealed Phase 14 code.
This document is therefore a contract and gap record, not a claim of closure.

