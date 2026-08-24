# Agent 2.0 Grounded Scientific Report v1

Phase 8 adds an on-demand, persisted scientific communication layer above the
immutable `ScientificResultSnapshot` and validated Phase 6 interpretation. A
report is editorial output, not a new scientific fact authority and not a
scientific execution path.

## Existing authority and compatibility

The existing `reports` table remains the stable product Report identity and
legacy Workspace `ReportCompositionSnapshot 1.0` / `RecipeReplayManifest 1.0`
routes remain readable. Phase 8 does not create a competing top-level report
universe. Revision `0024_agent2_scientific_reports` adds:

- `agent2_scientific_report_generations`, the recoverable independent
  `REQUESTED | COMPOSING | READY | FAILED` lifecycle;
- `agent2_scientific_report_snapshots`, the immutable exact binding from the
  existing Report row to one ScientificResultSnapshot and one validated
  interpretation.

Legacy reports are displayed through the retained legacy reader and are not
mislabelled as grounded Agent2 reports.

## Contract

`ScientificReportOutput 1.0` contains a scientific title, research question,
bounded summary, grounded main findings, selected validated figures,
supporting result items, method summary, limitations, opaque data-source and
evidence references, and a reproducibility summary. The output is accepted
only after strict Pydantic validation and `ReportGroundingValidator`.

The immutable snapshot records exact upstream identities, result execution
status, relevance at generation, composer/prompt versions, input/source
fingerprints, grounding status, bounded provider/model metadata and creation
time. Existing snapshots are never updated. Phase 8 v1 creates at most one
authoritative report for one ResearchTurn; a future explicit revision API must
append a new immutable snapshot rather than edit the old one.

## Composer input boundary

`ReportComposerInputAssembler` sends only bounded semantic projections from:

- the research question and result execution/effective relevance status;
- result-item, fact, figure, table, method, limitation and warning metadata;
- the validated interpretation findings and limitations;
- evidence relationships and server-issued opaque references.

Raw Artifact payloads, MinIO bytes, large arrays, database UUIDs, Job/ToolCall
identities, provider transcripts, secrets and hidden reasoning are excluded.
The provider receives `source_N` and validated scientific IDs, never runtime
database identifiers. Truncated supporting scope is disclosed through
`omitted_supporting_items`.

## Structured composition and grounding

The versioned prompt is `scientific-report-composer/1.0`. It uses the existing
server-managed DeepSeek structured transport outside database transactions.
Normal composition uses one provider call; schema or grounding failure may use
one bounded repair and never a third semantic call.

The deterministic validator requires every finding, fact, evidence, figure,
result item, limitation source and data source reference to resolve in the
supplied authority. Numeric tokens must be supported by referenced Facts and
units must match exactly; LLM unit conversion and visual estimation are not
accepted. PARTIAL and historical relevance semantics cannot be presented as a
complete current analysis. Invalid output is never persisted or shown as a
grounded report.

## Lifecycle and recovery

```text
completed/partial ResearchTurn
  -> persist report generation request
  -> commit
  -> enqueue generation identity
  -> fresh report worker
  -> reload PostgreSQL authority
  -> provider outside transaction
  -> validate
  -> persist existing Report + immutable Agent2 snapshot
  -> READY
```

Redis/RQ carries only the generation identity. Publication failure leaves a
durable `REQUESTED` row and does not alter the completed scientific analysis.
Duplicate queue delivery is claimed through persisted generation state and
reopening an existing report performs zero provider calls and zero scientific
computation.

## Authorization and relevance

Generate, read and list routes reauthorize the ResearchTurn/Report Project for
the current user. Provider input is assembled only after authorization and
cannot include cross-project sources.

`relevance_at_generation` is immutable historical evidence. Read APIs also
recompute `current_effective_relevance` from exact source versions using the
Phase 5 evaluator. A report can therefore become `STALE`, `SOURCE_MISSING` or
`INVALIDATED` without rewriting its content or silently upgrading sources.

## Product presentation

The Reports index lists grounded reports by scientific title, research
question, date, finding/figure count and current relevance. The reader follows
meaning-first hierarchy: research question and summary, figures, findings,
limitations, supporting results, then collapsible method, evidence, sources
and reproducibility. Figure references link back to the authorized Scientific
Result. The legacy report reader remains the fallback for historical IDs.

Phase 8 deliberately does not add scientific computation, Artifact ingestion
into the report LLM, Report-driven Tool calls, rich-text editing, multi-project
meta-reports, literature search, Recipe execution or Phase 9 behavior.
