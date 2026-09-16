# Workstream H — Scientific Knowledge & Literature Integration

## Scope

Build a bounded, provenance-preserving scholarly knowledge layer on top of
the A–G authorities. Literature is an external evidence class; it is not a
`ScientificResult`, a hypothesis, an interpretation, or Capability
qualification evidence.

## Execution contract

- Active repository: `E:\1project\mdi-b0-5a1`.
- Providers are explicitly allowlisted and limited to OpenAlex and Crossref
  for discovery/metadata in the initial foundation.
- External access is opt-in, query-projected, bounded, HTTPS-only, and
  project-authorized.
- DOI/provider identity is deterministic; preprint/published relationships
  remain explicit.
- Immutable snapshots and bounded LiteratureEvidence retain retrieval,
  publication-status, access-scope, passage, and claim lineage.
- Metadata-only, abstract-only, full-text, and user-provided evidence are
  distinct scopes.
- Provider output is untrusted data and cannot execute code, alter policy,
  mutate ScientificResult authority, or promote Capability qualification.
- Existing platform Results remain first-class. Literature search is not
  automatic when current evidence is sufficient.
- Default tests use recorded/fake provider responses. Live provider checks are
  separate and never required for ordinary CI.

## Bounded delivery

1. Establish domain contracts and deterministic identity/scope/status rules.
2. Add provider clients with network and privacy boundaries.
3. Add a service for query projection, reconciliation, evidence selection and
   comparison compatibility.
4. Integrate literature evidence with the existing Context/strategy/report
   projections without creating a second scientific authority.
5. Add persistence only where immutable work/snapshot/evidence history cannot
   be represented safely by existing authorities.
6. Add deterministic golden cases, generated evaluation evidence and focused
   canonical-runtime verification.

## Explicit non-goals

No generic web search, crawler, browser authority, arbitrary URL fetch,
vector database, generic RAG rewrite, paywall bypass, unrestricted full-text
retention, automatic qualification mutation, or hidden reasoning persistence.
