# Phase 10M-0 Report and Recipe Integration Decision

Status: REVIEWER-SEALED RECOMMENDATION

## Current facts

`reports` and `visualization_recipes` are existing first-class persisted records. Current PlannerWorkbench exposes report/recipe artifact summaries and inert previews, but it has no report composition route, recipe composition workflow, or Workspace ownership.

## Report seal

```text
REPORT_IS_FIRST_CLASS_PERSISTED_ENTITY = YES
RECIPE_IS_FIRST_CLASS_PERSISTED_ENTITY = YES
REPORT_RECIPE_DATABASE_MIGRATION_REQUIRED = NO
REPORT_RECIPE_API_REQUIRED = YES
```

The existing Report record remains the first-class persisted object. Phase 10M-5 adds a versioned Workspace report composition inside `report_json`; no replacement report table is created.

`WorkspaceReportComposition 1.0` stores selected panel IDs, selected grounded claim IDs, exact evidence/lineage refs, disclosure blocks for partial/failed/blocked work, deterministic ordering, export formats, source Workspace revision, and source hashes. It never copies raw artifact payloads. PDF/Markdown/HTML exports are inert generated outputs and retain all failure/limitation disclosures.

Reports support selecting panels and findings, preserve partial execution, include evidence and lineage links, and use existing report storage/export ownership. A report cannot modify its source Workspace or scientific records.

## Recipe seal

The existing visualization recipe record remains owner. `WorkspaceRecipe 1.0` is an additive strict contract inside `recipe_json` containing exact dataset/resource version, DataProfile, Intent, AnalysisPlan, tool/adapter versions, parameters and provenance, dependency bindings, Artifact contracts, renderer versions, and Workspace presentation state.

Recipe replay creates a new user-reviewed canonical analysis request. It never reuses a stale Artifact as execution input and never silently upgrades versions. Unsupported historical recipes remain read-only.

```text
recommendation != executable plan
```

Interpretation recommendations remain non-executable text/structured suggestions. Workspace supplies no Run button, enqueue token, ToolCall, tool parameters, or hidden conversion from recommendation to plan.

## API and migration impact

Phase 10M-5 implements the exact Report/Recipe routes, request fields,
responses, idempotency, ETag, status codes, caps, and authorization sealed in
`phase10m0_workspace_persistence_api_migration_decision.md`. Existing tables
are reused; the contracts are stored in existing JSON fields. No Phase 10M-1
migration beyond Workspace tables is required for report/recipe ownership.
