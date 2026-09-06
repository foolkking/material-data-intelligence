# Scientific Report Quality Rubric

Reports are communication projections over immutable `ScientificResult`
records. A valid schema is necessary but not sufficient for quality.

Score each applicable criterion 0 (absent), 1 (partial), or 2 (clear and
evidence-backed). A criterion may be `N/A` only when the authoritative Result
does not contain that scientific communication form (for example, no persisted
Figure exists); `N/A` is not allowed to hide missing supported content.

1. Research question/background
2. Research objective
3. Exact data and source-version scope
4. Methods and analyses performed
5. Key findings
6. Quantitative metrics with authoritative units
7. Relevant figures
8. Relevant typed tables
9. Evidence/provenance path
10. Cross-result synthesis without unsupported causality
11. Scientific discussion
12. Limitations and warnings
13. Uncertainty/partial-result disclosure
14. Conclusion
15. Bounded next steps
16. Readability and hierarchy
17. Scientific coherence
18. No raw JSON/artifact dump
19. No unsupported scientific claim
20. Exact Result/object/version preservation

Minimum release bar for a report marked `QUALITY_PASS`: no applicable
criterion is 0, normalized score is at least 85%, and applicable criteria 3,
6, 9, 12, 13 and 20 are 2. Figures/Tables marked `N/A` require an explicit
Result-level absence check; the composer must never manufacture them merely to
satisfy the rubric.
Evaluation must use the same persisted Results before and after narrative
improvement; report generation itself must not create a Job, ToolCall,
Artifact, or ScientificResult.

## ReportContextBundle 2.0 (bounded contract)

The composer may receive only authorized, operation-specific data:

```text
intent/question/objective
exact source object/version refs
selected Result refs and grounded Findings/Metrics
trusted Figure/Table/Viewer descriptors
Evidence refs
methods/execution summary
validated Interpretation
limitations/warnings
selected prior-result comparisons
user-selected report scope
```

It must exclude raw provider transcripts, hidden prompts, credentials,
unbounded artifacts, unrelated Results, and internal queue/storage details.

## Bounded narrative sections

The immutable `ScientificReportOutput` contract now supports optional,
provenance-aware `discussion`, `conclusion`, and `next_steps` sections. Each
section carries text plus bounded `fact_refs` and `evidence_refs`. Scientific
numbers and units in discussion/conclusion are validated against their
referenced Result facts; unsupported claims remain fail-closed. `next_steps`
is explicitly editorial guidance and cannot add scientific facts.

## Current real-report evidence

The current same-stack acceptance set includes both a Structure report and a
Dataset report. Structure retained two independent CrystalNN/VoronoiNN
findings, exact source version `8859cb49-0766-48cd-8a56-e44f5332e0c5`,
discussion, limitations, conclusion and next steps. Dataset retained exact
version `809a6825-5bfe-4820-81fc-b589ba447abc`, stable sample `mat-2`, three
findings and the same hierarchy. Browser checks found no raw capability IDs or
JSON dumps. A missing Figure/Table is scored `N/A` only after the Result has
been checked for the corresponding authoritative persisted form.

## Deterministic scientific-authority projection (2026-08-30)

Provider-composed Report JSON is a candidate communication structure, not a
fact source. The Report service now:

1. validates the candidate schema and numeric/evidence grounding;
2. resolves the exact persisted Interpretation and ScientificResult;
3. deterministically projects summary, findings, discussion, conclusion,
   methods, limitations, sources, evidence and reproducibility text from those
   authorities;
4. retains only bounded editorial next steps that do not assert new scientific
   facts.

The authenticated canonical Structure Report
`agent2_report_4f8320601e99ec9e3a78597f9973aa4c` demonstrates the boundary:
its source label is `Phase13 Fresh Structure`, exact version is
`8859cb49-0766-48cd-8a56-e44f5332e0c5`, its two findings remain independently
attributable, and the unsupported provider conclusion that both methods were
“有效且可靠” is absent. With no upstream method limitation supplied, the
Report explicitly states that it will not add unsourced algorithm folklore.
Opening the Report through the Research link produced no console errors or
warnings.

## Report finding provenance disclosure remediation (2026-09-04)

The authenticated Report reader now gives every main finding a bounded
`查看科学依据` disclosure. The collapsed report body remains readable, while
the disclosure exposes the exact `ScientificResult` snapshot, exact source
object/version, Result fact refs, evidence refs, and any finding refs supplied
by the immutable report snapshot. These are read-only references; opening the
disclosure cannot create a Job, ToolCall, Artifact, or ScientificResult.

This closes the R2 product gap where report findings were readable but their
per-finding provenance was only available indirectly through the generic
evidence section. The implementation reuses the existing report snapshot and
does not add a report-side scientific fact store.

Verification:

```text
ScientificReportRoute focused = 25 passed
Report / presentation focused suite = 62 passed
exact Result/source/fact/evidence refs rendered in the disclosure = PASS
mobile layout remains bounded by existing report responsive rules = PASS
```
