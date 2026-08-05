# Phase 10M-5 Composition API

The additive Workspace-scoped routes are:

```text
GET  /workspaces/{workspaceId}/report-composition/sources
POST /workspaces/{workspaceId}/report-compositions/preview
POST /workspaces/{workspaceId}/report-compositions
GET  /workspaces/{workspaceId}/report-compositions
GET  /workspaces/{workspaceId}/report-compositions/{reportId}
GET  /workspaces/{workspaceId}/report-compositions/{reportId}/recipe
GET  /workspaces/{workspaceId}/report-compositions/{reportId}/exports/{format}
```

`format` is `json` or `markdown`. Preview validates exact sources and performs
zero writes. Finalize requires the expected Workspace revision and bounded
`Idempotency-Key`, reloads all sources, and transactionally writes one immutable
Report/Recipe pair. Same key and semantics returns the same pair; a conflicting
semantic request returns `REPORT_IDEMPOTENCY_CONFLICT`.

All routes enforce Project -> Workspace -> Job -> source membership. Typed
errors cover not found, revision conflict, stale/integrity failure,
unsupported selection, cap/validation/authorization failure, pair mismatch,
legacy read-only, and export format/size. No error exposes SQL, stack, path,
bucket key, secret, or signed URL.
