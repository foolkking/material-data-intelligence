# Phase 10M-1 Workspace Persistence

Status: current M1 implementation sidecar. Migration and repository tests plus
corrected service-backed exact-SHA CI are verified; completion and archive
lifecycle gates remain.

## Tables

The additive Alembic revision is
`apps/api/alembic/versions/0007_phase10m1_workspace_domain.py`.
It creates:

1. `scientific_workspaces`, with one-row-per-`(project_id, source_job_id)`,
   immutable source references, title, durable revision pointer, and bounded
   metadata fields.
2. `workspace_panels`, keyed by `(workspace_id, panel_id)`, with strict panel
   descriptor metadata and no Artifact payload column.
3. `workspace_layout_revisions`, keyed by `(workspace_id, revision)`, with
   immutable layout/selection JSON and semantic hash.

Project, Job, Dataset, Profile, Intent, and Plan source references use
restricting foreign keys where the sealed M0 decision requires them. Panels
and layout revisions are owned by their Workspace. Project/update and source
Job indexes are included for the sealed lookup paths.

The migration does not backfill historical Jobs. It does not use
`metadata.create_all()` as migration authority.

## Repository layer

`apps/api/mdi_api/repositories.py` contains the Workspace repository protocol,
an in-memory implementation, and a SQLAlchemy implementation. Both expose
create/get/list/update operations, panel persistence, layout history, and
compare-and-set revision updates. The repository translates duplicate,
immutable, scope, not-found, and capacity conditions into typed Workspace
repository errors.

Create is idempotent for the same project and source Job. A conflicting
semantic create is rejected. Source identity fields are not latest-wins
mutable fields. Workspace updates use the expected revision and append a new
layout record instead of overwriting historical layout state.

The repository persists the complete bounded panel descriptor through its
metadata representation so it can round-trip without copying scientific
payloads. Storage keys, bucket names, local paths, and Artifact bodies are not
part of the Workspace snapshot.

## Migration verification status

The focused migration tests exercise the actual `0007` upgrade, downgrade,
and re-upgrade against an explicit `0006` parent fixture and a fresh SQLite
`0001 -> 0007` chain. Historical PostgreSQL-specific DDL is normalized only
for SQLite execution; the PostgreSQL path remains unchanged. Full PostgreSQL
migration, foreign-key/index inspection, and service-backed no-skipped
evidence passed exact-SHA CI run `30705503707`.

## Caps

- 32 panels per Workspace.
- 128 layout revisions per Workspace.
- 16 secondary selections.
- 2,048-byte selection URL representation.
- 131,072-byte mutation payload.
- 524,288-byte metadata-first snapshot.
- JSON depth 14.

Cap overflow is typed rejection; old revisions are not silently deleted to
make room for a new one.

## Compatibility

Existing Job, Plan, Artifact, Interpretation, Report, Recipe, and Runtime
records remain authoritative and are not rewritten. SQLite and in-memory
repository tests are focused coverage; PostgreSQL and full migration/service
evidence are verified by corrected exact-SHA CI.
