# Scientific Report Quality Rubric

Reports are communication projections over immutable `ScientificResult`
records. A valid schema is necessary but not sufficient for quality.

Score each criterion 0 (absent), 1 (partial), or 2 (clear and evidence-backed):

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

Minimum release bar for a report marked `QUALITY_PASS`: no criterion is 0,
total score is at least 34/40, and criteria 3, 6, 9, 12, 13 and 20 are 2.
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

