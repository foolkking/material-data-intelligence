# Scientist Product Acceptance

Date: 2026-09-10  
Runtime: canonical API/frontend from `E:\1project\mdi-b0-5a1`

## Evidence

Acceptance combined:

- real authenticated browser walkthroughs using persisted PostgreSQL state;
- canonical API on port 8007 with PostgreSQL, Redis/RQ, and MinIO;
- canonical production frontend on port 3025;
- focused React/Vitest and backend tests;
- production typecheck/build;
- 390×844 responsive measurement.

The machine-readable record is
`docs/product-maturity/generated/scientist_ux_acceptance.json`.

## Journey coverage

Fifteen scientist journeys were evaluated. Real browser evidence covered
historical Research reopen, Result/limitation inspection, mobile pane switching,
unsupported/no-run behavior, Report reopen, and Task Center return-to-Research.
Deterministic integration tests covered active multi-cycle progress,
clarification, cross-family rationale, Result reuse, comparison compatibility,
hypothesis evolution, failure/recovery, cancellation, edit/branch, and bounded
long-history rendering.

## Acceptance conclusions

- The current question, current evidence gap, continuation reason, and stop
  reason have scientist-facing projections.
- Research Map and hypothesis states are derived from durable strategy evidence
  and do not expose hidden reasoning.
- Stop, cancel, continue, retry, rerun, reinterpret, and branch semantics are
  distinct.
- Scientific Results lead with meaning, limitations, and source labels.
- Exact identities remain available in advanced provenance.
- Unsupported scope creates no run and no stale previous plan remains visible.
- Failed or cancelled research preserves completed science.
- Identity-shaped project/dataset/object names no longer dominate default
  Research, Report, Task, Notification, or composition-space surfaces.
- Mobile Research has no blocking horizontal page overflow at 390×844.

## Verdict

```text
SCIENTIST_PRODUCT_MATURITY = READY_FOR_BOUNDED_SCIENTIST_USE
```

This is a product-maturity assessment, not release qualification.

## Remaining limitations

1. Universal cross-domain Result comparison is intentionally not computed in
   the browser; comparison remains contract-specific.
2. Historical runs created before ResearchTurn linkage remain read-only and
   cannot reconstruct a missing question.
3. Specialist-viewer localization is incomplete.

These are bounded limitations rather than blockers to controlled scientist use.

