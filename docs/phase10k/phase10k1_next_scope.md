# Phase 10K-1 Material Data Profile 2.0 Entry Scope

Status: next approved Phase 10K scope; not started by Phase 10K-0.

## Entry Gates

- Phase 10K-0 is archived with result history retained.
- `master` and `origin/master` match.
- working tree is clean.
- the audit/completion/archive exact-SHA CI gates are successful.
- no overlapping profile task is processing.
- the complete executable task prompt is present before status changes.

## Objective

Turn the deterministic profile from a narrow table/structure summary into a
bounded material capability-discovery contract that can truthfully state what a
dataset contains, what analyses are available, and why other analyses are not.

## Required Contract Decisions

- profile schema versioning and old-profile compatibility;
- Python/TypeScript dataset-kind parity;
- normalized resource/capability vocabulary;
- table role and material-property identity, units, and confidence;
- regression, uncertainty, and classification task semantics;
- stable sample identity and source-row provenance;
- trajectory, phonon, and volumetric summary semantics;
- available/unavailable analysis reasons and warning ordering;
- deterministic caps, truncation, and serialized-size policy;
- failure behavior when real profile retrieval is unavailable.

## Implementation Boundary

Phase 10K-1 may update schemas, deterministic profile generation, persistence/API
serialization, tests, and the existing frontend profile surface. It must not:

- implement the Dataset Materials Explorer (10K-2);
- implement ML evaluation products (10K-3);
- implement composition projection/clustering (10K-4);
- implement capability-aware multi-tool planning or LLM interpretation (10L);
- redesign the unified workspace (10M);
- implement professional science (10N);
- add Future or Not Planned capabilities.

## Likely Repository Areas

- `packages/schemas/`
- `packages/material-parsers/`
- profile repositories and Phase 2 API serialization
- `apps/web/app/lib/planner-api.ts`
- the existing data-context/profile component path
- focused backend/frontend/integration fixtures and tests
- shared schema and Phase 10K documentation

The exact file set must be established by the Phase 10K-1 pre-implementation
audit.

## Acceptance Direction

A representative supported input must produce a deterministic profile with
stable identities, capability facts, available/unavailable analyses, and bounded
warnings that agree across Python, persisted JSON, API, TypeScript, and the
frontend. Unsupported capabilities must remain explicit rather than inferred.

No Phase 10K-1 implementation is included in this document.
