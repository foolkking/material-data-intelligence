# Phase 10K-1 Material Data Profile 2.0 Implementation

## Status

Material Data Profile 2.0 extends the existing `DataProfile` envelope. It does
not create a parallel profile type, change Planner routing, add a tool, or run a
scientific analysis. The legacy `schemaVersion: "0.1"`, table/structure
summaries, persistence path, and API endpoints remain readable. New profiles
declare `profileContractVersion: "2.0"` and `semanticRulesVersion`.

## Data Flow

```text
bounded parser / normalized object
  -> existing DataProfile builder
  -> observed table/resource facts
  -> deterministic semantic roles and groups
  -> data readiness + separate platform availability
  -> existing profile repository/API serialization
  -> read-only PlannerWorkbench profile surface
```

The semantic hash covers dataset/version binding, object hashes, semantic
columns/groups, resource semantics, readiness, identity, and coverage. The
request-time `createdAt` timestamp is intentionally excluded. No filename,
private path, external lookup, LLM response, or mutable display state is an
authority input.

## Implemented Surface

- table facts: bounded rows/columns, dtype, missing/unique/finite counts, units
  only when explicit metadata provides them;
- material roles: formula, conservative numeric property allowlist, sample ID;
- regression: target, multiple predictions, multi-target grouping, uncertainty;
- classification: target, prediction, bounded probability columns and row-sum
  validation;
- resources: table, composition/structure, trajectory, phonon, and volumetric;
- readiness: `READY`, `MISSING_REQUIRED_DATA`, `AMBIGUOUS`, or
  `UNSUPPORTED_DATA_KIND`, independently paired with `AVAILABLE`,
  `NOT_IMPLEMENTED`, or `NOT_EVALUATED`; platform status is resolved only when
  the application supplies its actual Tool Registry snapshot;
- stable identity: one complete unique explicit sample-ID column, otherwise
  dataset version + normalized object hash + row index;
- compatibility: legacy `tableSummary.columns[].inferredRole` remains exact and
  existing Planner/Registry/Runtime contracts are unchanged.

## Bounded Policy

| Resource | Limit | Behavior |
| --- | ---: | --- |
| inspected table rows | 4096 | deterministic evenly-spaced sample plus warning |
| inspected columns | 512 | deterministic prefix plus warning |
| inspected formula values | 1024 | explicit coverage metadata |
| formula length | 256 | value rejected as invalid, never evaluated |
| probability columns/group | 64 | group remains incomplete above cap |
| normalized resources | 256 | stable sort, bounded prefix, warning |
| column-name length | 256 | no semantic classification above cap |
| semantic group ID | 128 | oversized metadata is rejected and disclosed |
| explicit unit | 64 | oversized metadata is omitted and disclosed |

There is no silent truncation claim: `profileCoverage` reports totals,
inspected counts, policy, limits, and warning codes.

## API and UI

The existing `POST /datasets/upload`, `GET /datasets/{id}/profile`, and
`POST /datasets/{id}/profile` paths serialize the additive contract. The
frontend displays detected semantics, data-ready analyses, implemented versus
planned platform capabilities, coverage, and warnings. It remains a compact
profile surface, not the Phase 10K-2 Dataset Explorer.

## Evidence

Evidence is stored under
`docs/phase10k/evidence/phase10k1_material_data_profile_2/`. The captures prove
real in-process FastAPI upload/profile persistence, deterministic hashes,
ambiguous regression handling, classification, structure resources, bounded
performance, Chromium/Firefox/WebKit, mobile layout, and zero external network.

## Explicit Limits

Profile 2.0 reports eligibility facts; it does not evaluate models, generate a
dataset dashboard, calculate anomalies, run PCA/clustering, select Planner
tools, compose multi-tool plans, redesign the workspace, or implement Phase 10N
professional science.
