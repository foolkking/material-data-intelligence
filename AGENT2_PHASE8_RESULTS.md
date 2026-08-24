# AGENT2_PHASE8_RESULTS

## Verdict

`COMPLETE`

## Starting State

- Starting HEAD and `origin/master`: `c8156cd96b9b46e237a7471245a7031df03ae3c7`
- Starting Alembic head: `0023_agent2_research_memory`
- Phase 7 was accepted as complete before Phase 8 began.

## Existing Report Infrastructure Audit

The existing `reports` aggregate remains the product Report authority and the
legacy Report/Recipe reader remains available for historical deep links. Phase
8 extends that authority with an immutable Agent2 scientific-report snapshot;
it does not create a parallel report product.

## Migration And Persistence

- Alembic revision: `0024_agent2_scientific_reports`
- New durable records: report-generation lifecycle and immutable grounded
  report snapshot.
- Every snapshot binds one exact `ScientificResultSnapshot`, one validated
  Agent2 interpretation, one ResearchTurn, one Project, the generation-time
  relevance, the report contract/prompt/composer versions, and a stable source
  fingerprint.
- SQLite and fresh PostgreSQL both passed `base -> 0024 -> 0023 -> 0024`.

## Report Contract

`ScientificReportOutput 1.0` contains a scientific title, research question,
summary, grounded findings, validated figure references, supporting result
references, method summary, limitations, data-source references, evidence
references, reproducibility summary, and explicit omitted-supporting-item
metadata. Existing snapshots are never updated in place.

## Report Composer Input Boundary

The composer receives only bounded ScientificResult and validated
interpretation projections: facts, result items, figure/table metadata,
evidence references, methods, limitations, warnings, execution status, and
effective relevance. Raw Artifact payloads, MinIO bytes, provider transcripts,
database UUIDs, Job internals, secrets, and chain-of-thought are excluded.

## Grounding Validator

`ReportGroundingValidator` rejects unknown finding, fact, evidence, figure,
result-item, limitation, and data-source references. Positive findings require
grounding. Numeric and unit claims reuse the Phase 6 claim extraction boundary;
unsupported values, hidden rounding, and unit substitution are rejected.

## Numeric / Unit Grounding

- Invented numeric tokens: `0` in accepted deterministic/live reports.
- Unit substitutions: `0` in accepted deterministic/live reports.
- Unknown refs: `0` in accepted deterministic/live reports.
- Normal provider policy: one call; maximum one bounded repair.

## Figure / Evidence Grounding

Reports can select only supplied ScientificFigure and Evidence identities.
The reader links the scientific figure plate back to the authorized Research
result instead of copying raw arrays or rendering an Artifact dump.

## Lifecycle And Queue

Report generation is on demand. The API persists an identity-only generation
request, commits it, then publishes the generation id to Redis/RQ. A fresh
report worker reloads PostgreSQL authority. Publication or composition failure
does not alter the completed/partial research lifecycle or rerun science.

## Idempotency And Revisions

Duplicate delivery converges on one authoritative report for a ResearchTurn
and source fingerprint. The immutable snapshot is reopenable without a second
provider call. A future explicit regenerate operation must append a new
revision rather than overwrite this snapshot; collaborative editing is outside
Phase 8.

## Exact-version / Relevance

The report binds exact upstream snapshot and source-version identities.
`relevance_at_generation` remains immutable while the read API calculates
`current_effective_relevance` as `CURRENT`, `STALE`, `SOURCE_MISSING`, or
`INVALIDATED`. Historical reports are never silently upgraded.

## Authorization Boundary

Generate, read, and list routes reuse authenticated Project authorization.
Cross-project result, interpretation, report generation, and report reads are
rejected before provider work.

## Provider Boundary

Phase 8 reuses the existing DeepSeek/OpenAI-compatible structured transport
with purpose `REPORT_COMPOSITION`. Provider-facing references are opaque and
the call occurs outside a database transaction. The prompt and output contract
are versioned as `scientific-report-composer/1.0` and `1.0`.

## Report List

The Project Reports page separates grounded scientific reports from legacy
run reports. Grounded rows show a scientific title, research question, date,
finding/figure counts, and effective relevance without exposing internal IDs.

## Report Reader

The reader uses four levels: conclusion/question/summary and primary figures;
findings and limitations; supporting results; then collapsible method,
evidence, sources, and reproducibility. Canonical methods are presented in
human-readable scientific language. Equivalent limitations are deduplicated.

## Research Integration

Completed or partial Agent2 turns expose an on-demand report action. The UI
checks existing persisted reports, requests identity-only generation, polls
the durable status, and links the ready report. Report generation is described
separately from scientific execution.

## Zero-computation Evidence

Fresh service-backed generation preserved these scientific counts:

- AnalysisPlan delta: `0`
- Job delta: `0`
- ToolCall delta: `0`
- Artifact delta: `0`
- ScientificResultSnapshot delta: `0`
- ReportGeneration delta: `+1` per source turn
- ScientificReportSnapshot delta: `+1` per source turn

## Fresh Service-backed Qualification

With real PostgreSQL, Redis, MinIO, Phase 4 execution, Phase 5 projection,
Phase 6 interpretation, and a separate Phase 8 report worker:

- RDF report: PASS
- XRD report: PASS
- Fresh-process reopen with zero provider calls: PASS
- Dedicated selection: `4 passed, 0 failed, 0 errors, 0 skipped`

## Live DeepSeek

Gated local qualification with the configured DeepSeek provider:

- RDF: PASS, one provider call, no repair
- XRD: PASS, one provider call, no repair
- STALE: PASS, one provider call, no repair
- Controlled grounding repair: PASS, two semantic attempts total and one live
  provider call after the deliberately invalid first response

Invented refs, invented numbers, unit violations, and authorization violations:
`0`.

## Tests

- Phase 8 deterministic: `14 passed, 4 live deselected`
- Phase 6-8 focused: `31 passed, 8 deselected`
- Agent2 Phase 2-8 focused: `112 passed, 13 deselected`
- Full backend: `1754 passed, 80 skipped, 75 warnings`
- `uv lock --check`: PASS
- compileall: PASS
- Ruff targeted checks: PASS
- `git diff --check`: PASS
- frontend focused report tests: `5 passed`
- frontend full Vitest: `87 files, 576 passed`
- frontend typecheck: PASS
- production build: PASS (isolated `MDI_NEXT_DIST_DIR`)
- independent `npm run lint`: NOT CLAIMED; the repository still uses the
  deprecated interactive `next lint` command.

## Browser

Authenticated in-app-browser qualification used a persisted grounded RDF
report:

- Desktop `1280x720`: PASS
- Mobile `390x844`: PASS
- `document.scrollWidth <= innerWidth`: PASS
- `body.scrollWidth <= innerWidth`: PASS
- Legacy report route/read compatibility: PASS
- Semantic accessibility audit: article/heading/figure/figcaption/list/details
  structure present. No screen-reader certification is claimed.

## Current-head CI

- Implementation SHA: `57041f38240b6c8d50ca3bc44813da0a15deed87`
- Documentation closure SHA: `41f2b102bd122fe50e34bcfe033639688a195fb2`
- Final recorded SHA: `05720f882877e03c76e3499a5708b9df3276d6e7`
- Final current-head GitHub Actions run: `32690181703`
- Unit Tests: PASS
- Frontend Typecheck & Build: PASS
- PostgreSQL/Redis/MinIO service-backed integration: PASS; Phase 8 selection
  ran with `4 passed, 0 skipped`
- Linux Scientific Replay: PASS
- Windows Scientific Replay: PASS

The final closure commit is the exact CI head; all required jobs are green on
that SHA.

## Legacy Report Compatibility

Legacy report rows and routes remain readable and are labeled as historical
run reports. They are not mislabeled as grounded Agent2 scientific reports.

## Not Implemented In Phase 8

- full professional Data Viewer expansion
- full Viewer linked-selection platform
- full 62-tool capability mapping
- Data Management mutations
- Tool/Parser/Viewer plugin ecosystem
- global or cross-project personal memory
- multi-project meta-report composition
- collaborative rich-text report editing
- internet literature research
- BYOK
- Phase 2 ORCHESTRATING lease/reaper
- deployment
