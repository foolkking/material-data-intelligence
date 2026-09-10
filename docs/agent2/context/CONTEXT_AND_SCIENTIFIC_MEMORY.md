# Context and Scientific Memory

状态：Workstream B canonical continuation record  
日期：2026-09-10

## Scope and authority

This record applies to the active repository
`E:\1project\mdi-b0-5a1`. Context is a bounded, authorized input projection;
it is not a second scientific authority and it is not generic chat memory.

```text
ScientificObjectVersion  exact scientific input authority
Artifact                 execution-output authority
ScientificResult         normalized scientific knowledge authority
Interpretation / Report  grounded projections
ResearchTurn             lifecycle authority
ContextSnapshot          record of what one operation saw
Research Memory          typed continuation aid, never source truth
```

## Pipeline

The current implementation extends the existing pipeline:

```text
candidate discovery
→ project/identity authorization
→ typed ReferenceCandidate
→ source/authority/freshness classification
→ existing ranking and budget policy
→ deterministic manifest/compiler
→ ContextSnapshot / operation manifest
→ orchestrator, planner, interpreter or report operation
```

Canonical implementation owners are:

```text
apps/api/mdi_api/research_agent/context/
  assembler.py       candidate discovery and authorization boundary
  schemas.py         candidate/manifest contracts
  policy.py          purpose-specific budgets
  compiler.py        bounded provider view
  manifest.py        deterministic operation manifest
  provenance.py      source, authority and freshness projections

apps/api/mdi_api/research_agent/memory/
  service.py         session-scoped memory writes and pins
  retriever.py       bounded authorized retrieval
  schemas.py         memory reference contract
```

## Provenance and authority

Candidates and memory references retain source class, authority class,
freshness, epistemic status and stable source references where available.
Exact object/version and Result references remain server-side. Scientific
input/knowledge outranks memory or presentation prose; explicit current user
intent controls what the user asks for but does not become computed fact.

Unauthorized or cross-project memory candidates are excluded before provider
context construction. Invalidated or missing-source memories are excluded
from current retrieval. Historical-valid information remains referenceable as
historical rather than being treated as current.

## Budget and degradation

Existing purpose-specific `ContextBudgetPolicy` remains authoritative.
Manifest/compiler output includes provenance metadata without sending internal
database identity or hidden reasoning to the provider. Existing deterministic
compaction preserves mandatory exact references before lower-value material.
The lifecycle projection exposes selected/excluded counts, source categories,
budget and degradation state.

Large scientific payload policy remains projection-first: metadata, bounded
summaries and exact references should enter provider context instead of raw
datasets or artifact blobs.

## Memory and continuation

Memory remains session/project scoped and typed. Pins increase retrieval
priority only; they do not override scientific authority or freshness.
Continuation can reuse prior Results and exact versions without implicitly
upgrading a historical Turn to a newer version. Fresh research remains
primarily driven by the current request and explicit selections.

## User/operator visibility

The Research context disclosure accepts source class, freshness and epistemic
metadata and renders freshness beside authority in the existing disclosure.
The lifecycle correlation projection exposes a bounded context summary. No
prompts, provider transcripts, credentials or hidden chain-of-thought are
persisted or displayed by this change.

## Reconciliation status

Recovered from the old tree into canonical owners:

```text
complete:
  provenance vocabulary and source mapping
  candidate/manifest/memory contract metadata
  project-scoped memory filtering and freshness-aware ranking
  lifecycle/context observability seam
  focused unit/API coverage
  end-to-end persisted context provenance through a live worker path
  continuation/reuse with exact historical-version preservation
  canonical PostgreSQL/Redis/MinIO/worker verification
```

Canonical verification evidence:

```text
focused backend reliability/context suite  83 passed
Research provenance UI                     93 passed
Phase 2 service flow                       exact-version manifest persisted
Phase 3 service flow                       planning passed
Phase 4 service flow                       worker execution passed
Phase 7 service flow                       continuation and stale-version fixture passed
canonical stack check                      PostgreSQL/Redis/MinIO/API/frontend PASS
canonical workers                          6/6 queues discovered
```

## Known limitations

- Existing storage contracts do not yet provide a universal durable graph for
  every memory-to-source relationship; absent provenance must remain
  untrusted rather than being inferred as scientific truth.
- Provider token estimates can vary by provider even though source identity
  and snapshot semantics do not.
- Broader near/over-budget, very large Dataset and edited-branch stress
  coverage remains a follow-up quality/scale evaluation, not a blocker for
  the bounded context and memory foundation.
