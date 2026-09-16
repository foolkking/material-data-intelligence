# Scientific Knowledge Authority

## Purpose

Workstream H adds scholarly evidence to Research without changing the existing
scientific authorities:

```text
ScientificResult
!= LiteratureEvidence
!= Interpretation
!= Hypothesis
!= CapabilityQualification
```

`ScientificResult` remains the normalized output of platform computation.
`LiteratureEvidence` is an externally reported passage or bounded metadata
reference from an immutable scholarly snapshot. It can support or contradict a
research claim, but cannot become a computed Result or promote Capability
qualification.

## Canonical model

```text
LiteratureWork
  canonical DOI, arXiv identity, or provider record identity
        ↓
LiteratureSnapshot
  immutable provider metadata, publication/access state, retrieval time,
  provider field lineage, optional exact retrieved passages
        ↓
LiteratureEvidence
  the exact bounded evidence selected for one Project/ResearchTurn
        ↓
Context / Strategy / Interpretation / Report
  opaque provider-facing refs plus exact server-side lineage
```

DOI owns canonical identity when present. Exact arXiv identity is retained
otherwise. Title similarity may produce `POSSIBLE_DUPLICATE`; it never silently
merges works. Preprint, publication, correction and retraction relationships
remain explicit.

## Evidence scopes

- `METADATA_ONLY`: bibliographic/context use; no passage or numeric claim.
- `ABSTRACT_ONLY`: the passage must be present in the retrieved abstract.
- `OPEN_FULL_TEXT`: both OA authority and an exact snapshot-retrieved passage
  are required.
- `USER_PROVIDED_FULL_TEXT`: exact uploaded content hash plus an exact parsed
  snapshot passage are required.
- `STRUCTURED_REPOSITORY_FULL_TEXT`: same exact-passage rule under supported OA
  repository authority.
- `REFERENCE_ONLY`: identity/citation only.

Only evidence selected into Research becomes `LiteratureEvidence`. Search
candidates do not become evidence automatically.

## Research integration

Strategy first identifies an evidence gap. It may satisfy that gap with:

1. an existing authoritative ScientificResult;
2. a new qualified scientific Capability;
3. authorized LiteratureEvidence;
4. user clarification.

Existing evidence remains first. Literature search is not automatic. Provider
strategy output can request `SEARCH_LITERATURE`, but deterministic validation
requires a real evidence gap and purpose and forbids treating retrieval as
Capability execution.

Context manifests classify scholarly material as:

```text
kind = LITERATURE_EVIDENCE
authority = SCIENTIFIC_EVIDENCE
epistemic status = REPORTED
```

Provider-facing synthesis receives opaque refs such as `literature_1`; a model
cannot create DOI, paper, author, source, Result, or qualification authority.
Every claim must reference an allowed evidence/Result alias, and numeric claims
must occur in the referenced evidence projection.

## Persistence and historical replay

Migration `0033_scientific_knowledge` adds canonical work, immutable snapshot,
search, and selected-evidence records. Historical Research and Reports reopen
the exact snapshot/evidence identity they used. New retrieval may discover a
later correction or retraction, but does not rewrite prior history.

Reports store deterministic citation text together with exact evidence, work,
and snapshot IDs, evidence scope, publication status, support type, and claim
refs. Bibliographic identity comes from the snapshot, never from generated
prose.

## Explicit limits

H is query-driven scholarly integration, not a crawler, generic browser,
vector database, literature warehouse, citation-quality score, paywall
bypass, or generic RAG rewrite. OCR and broad publisher full-text parsing are
not claimed. Full-text evidence is accepted only after an authorized parser or
repository path has placed exact passages into an immutable snapshot.

