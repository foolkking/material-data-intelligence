# Phase 10M-0 Persistence, API, and Migration Decision

Status: REVIEWER-SEALED RECOMMENDATION
Production status: NOT IMPLEMENTED

## Database

```text
DATABASE_MIGRATION_REQUIRED = YES
TARGET_MIGRATION = 0007_phase10m1_workspace_domain
```

### Tables

1. `scientific_workspaces`: exact columns `workspace_id String(96) PK NOT NULL`, `schema_version String(16) NOT NULL`, `project_id String(64) FK RESTRICT NOT NULL`, `source_job_id String(64) FK RESTRICT NOT NULL`, `source_reference_hash String(64) UNIQUE NOT NULL`, legacy-compatible `dataset_id String(64) FK RESTRICT NULL`, `dataset_version String(128) NULL`, `profile_id String(64) FK RESTRICT NULL`, `profile_semantic_hash String(64) NULL`, `intent_id String(96) FK RESTRICT NULL`, `intent_semantic_hash String(64) NULL`, `plan_id String(96) FK RESTRICT NULL`, `plan_hash String(64) NULL`, `plan_schema_version String(16) NULL`, `title String(256) NOT NULL`, `active_panel_id String(64) NULL`, `pinned_selection_json JSON NULL`, `revision Integer NOT NULL DEFAULT 0`, `created_by String(64) NOT NULL`, `created_at DateTime(tz) NOT NULL DEFAULT now`, and `updated_at DateTime(tz) NOT NULL DEFAULT now`. Scientific source references are immutable. `UNIQUE(project_id, source_job_id)` enforces one Workspace per Job.
2. `workspace_panels`: exact columns `workspace_id String(96) FK CASCADE NOT NULL`, `panel_id String(64) NOT NULL`, `panel_kind String(32) NOT NULL`, `title String(256) NOT NULL`, `ordinal SmallInteger NOT NULL`, `visible Boolean NOT NULL DEFAULT true`, `source_refs_json JSON NOT NULL`, `renderer_contract String(128) NOT NULL`, `accepted_selection_kinds_json JSON NOT NULL`, `layout_json JSON NOT NULL`, `panel_state_hash String(64) NOT NULL`, `created_at DateTime(tz) NOT NULL DEFAULT now`, and `updated_at DateTime(tz) NOT NULL DEFAULT now`. Primary key is `(workspace_id, panel_id)`; no artifact payload exists.
3. `workspace_layout_revisions`: exact columns `workspace_id String(96) FK CASCADE NOT NULL`, `revision Integer NOT NULL`, `layout_json JSON NOT NULL`, `selection_json JSON NULL`, `semantic_hash String(64) NOT NULL`, `created_by String(64) NOT NULL`, and `created_at DateTime(tz) NOT NULL DEFAULT now`. Primary key is `(workspace_id, revision)` and `(workspace_id, semantic_hash)` is unique.

Foreign keys bind Project and Job with `ON DELETE RESTRICT`; Workspace and
source Job physical deletion is rejected and source tombstone state is
projected without invalidating the reference. Dataset/Profile/Intent/Plan
references follow existing repository ownership and remain nullable only for
explicit legacy projection. Indexes are
`idx_workspaces_project_updated(project_id, updated_at)`,
`idx_workspaces_source_job(source_job_id)`, and
`idx_workspace_panels_order(workspace_id, ordinal)`. Check constraints enforce
`revision >= 0`, `ordinal >= 0`, and the 32-panel/128-revision limits at the
repository boundary. Upgrade, downgrade, and re-upgrade are mandatory for
SQLite and PostgreSQL. No historical Job is bulk backfilled.

Compatibility impact: existing tables and records are unchanged. A Workspace is additive and never becomes the source of scientific truth.

Acceptance: strict migration tests, one-Workspace-per-Job idempotency, conflicting write rejection, immutable source refs, optimistic revision conflict, and PostgreSQL service-backed round trip.

## API

```text
NEW_WORKSPACE_API_REQUIRED = YES
```

Exact Phase 10M endpoints:

| Method | Route | Request | Response |
| --- | --- | --- | --- |
| `POST` | `/workspaces` | `Idempotency-Key` header; JSON `sourceJobId`, bounded title | `201` new or `200` same request; snapshot + ETag |
| `GET` | `/workspaces/{workspace_id}` | `If-None-Match` header | `200` metadata-first snapshot + ETag or `304` |
| `PATCH` | `/workspaces/{workspace_id}` | `If-Match` required; JSON title, active panel, panel/layout changes, pinned selection | `200` next revision + snapshot + ETag |
| `GET` | `/projects/{project_id}/workspaces` | bounded cursor/page | authorized Workspace summaries |
| `GET` | `/projects/{project_id}/analysis-jobs` | bounded cursor/page, projection state | exact historical Job candidates |

Phase 10M-5 adds these exact additive endpoints over existing Report/Recipe
ownership: `POST/GET /workspaces/{workspace_id}/reports`,
`GET/PATCH /workspaces/{workspace_id}/reports/{report_id}`,
`POST /workspaces/{workspace_id}/reports/{report_id}/export`,
`POST/GET /workspaces/{workspace_id}/recipes`,
`GET /workspaces/{workspace_id}/recipes/{recipe_id}`, and
`POST /workspaces/{workspace_id}/recipes/{recipe_id}/review-replay`.
Report create/update requests contain `If-Match` and exact panel/claim/evidence
refs; export requests contain only an allowlisted format; recipe review-replay
returns a non-enqueued canonical request draft. Each write uses
`Idempotency-Key`; each read returns source hashes and ETag. No endpoint accepts
raw artifact content, custom prompts, tool IDs, or enqueue authority. The
Workspace endpoint never proxies raw artifact payloads; existing bounded
artifact routes remain authoritative.

Exact M5 request and response contracts:

| Endpoint | Request | Success response |
| --- | --- | --- |
| `POST /workspaces/{id}/reports` | headers `Idempotency-Key`, `If-Match`; body `schemaVersion=1.0`, title, ordered panelIds<=32, claimIds<=32, includeEvidence, includeLineage, exportFormats<=3 | `201`/idempotent `200`: reportId, reportVersion, reportHash, workspaceId/revision, sourceReferenceHash, status, createdAt, ETag |
| `GET /workspaces/{id}/reports` | cursor and limit<=100 | report summaries, nextCursor, count, sourceReferenceHash |
| `GET /workspaces/{id}/reports/{reportId}` | `If-None-Match` | exact composition, disclosure state, evidence/lineage refs, exports, reportHash, ETag |
| `PATCH /workspaces/{id}/reports/{reportId}` | headers `Idempotency-Key`, report `If-Match`; body expectedReportHash, title, ordered panelIds<=32, claimIds<=32, includeEvidence, includeLineage, exportFormats<=3 | `200`: next reportVersion/reportHash, sourceReferenceHash, report ETag |
| `POST /workspaces/{id}/reports/{reportId}/export` | headers `Idempotency-Key`, `If-Match`; body expectedReportHash and format=`MARKDOWN|HTML|PDF` | `201`/idempotent `200`: exportId, reportId/hash, artifactId/checksum/contract/mediaType, status |
| `POST /workspaces/{id}/recipes` | headers `Idempotency-Key`, `If-Match`; body `schemaVersion=1.0`, title, sourceWorkspaceRevision, includePresentationState | `201`/idempotent `200`: recipeId/version/hash, sourceReferenceHash, exact source identities, createdAt, ETag |
| `GET /workspaces/{id}/recipes` | cursor and limit<=100 | recipe summaries, nextCursor, count, sourceReferenceHash |
| `GET /workspaces/{id}/recipes/{recipeId}` | `If-None-Match` | exact Recipe contract, source identities/hashes, replaySupport, ETag |
| `POST /workspaces/{id}/recipes/{recipeId}/review-replay` | headers `Idempotency-Key`, `If-Match`; body expectedRecipeHash and `reviewMode=DRAFT_ONLY` | `200`: draftRequestId, exact Profile ref, bounded Intent draft, diagnostics, `planCreated=false`, `jobCreated=false`, `enqueued=false` |

All request bodies reject unknown fields. List responses never include raw
artifact payloads. Export Artifact identity comes from the platform export
service and cannot be supplied by the request. Review-replay never creates an
Intent, Plan, Job, ToolCall, or queue message.

Workspace creation requires project authorization and `Idempotency-Key`; it
has no `If-Match` because no Workspace projection exists yet. Workspace PATCH,
Report POST, and Recipe POST use the Workspace projection ETag. Report PATCH
and export use the Report ETag. Recipe review-replay uses the Recipe ETag.
Every write requires project authorization, `Idempotency-Key`, unknown-field
rejection, and the table-defined precondition. `201` means created, `200`
means idempotent replay, `304` means unchanged GET, `400` means malformed or
oversized request, `401` means unauthenticated, `403` means project scope
failure, `404` means unknown resource, `409` means idempotency or source
semantic conflict, `412` means ETag mismatch, `415` means unsupported
contract/media request, `422` means exact identity/contract validation
failure, and `410` means a retained source tombstone. Reads recompute source
availability and projection integrity.

## Frontend state persistence

The model is fixed:

- server: title, active panel, ordered panel state, layout, pinned selection, revision;
- URL: active panel and bounded exact selection for deep links;
- React memory: hover, camera, playback frame, open drawers, transient filters;
- localStorage: not authoritative and not used for Workspace identity or scientific state;
- sessionStorage: not used for canonical Workspace state.

On navigation, a valid URL panel/selection overrides the saved active view for that browser history entry without mutating the server until the user performs an explicit save-producing action.

## Cache

`WORKSPACE_PROJECTION_CACHE_ENABLED = YES`. API and browser caches cache only the metadata-first projection under:

```text
workspace:{workspaceId}:revision:{revision}:source:{sourceReferenceHash}
```

ETag is the projection hash. Workspace revision changes, Job/ToolCall/execution
state changes, artifact/interpretation/report/recipe additions, and source
tombstones invalidate it. Artifact payload caching remains owned by existing
artifact endpoints and storage policy. Stale cache entries are never used
after ETag/source-hash mismatch. `Idempotency-Key` hashes are retained with
the response identity and a different semantic request under the same key
returns `409`.
