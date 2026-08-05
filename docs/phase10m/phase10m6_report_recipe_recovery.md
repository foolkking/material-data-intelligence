# Phase 10M-6 Report and Recipe Recovery

Finalized immutable Report history, exact Report detail, paired Recipe identity/hash, warnings/limitations/failures, and canonical JSON/Markdown export reload through the existing M5 APIs. Recovery never substitutes the latest pair or recomposes from current Workspace state.

The unfinalized composition draft is explicitly session-only. The Report panel states that it is not saved until Finalize and that refresh/close discards it. Dirty drafts install standard `beforeunload` protection and controlled internal navigation confirmation. No local browser store, server draft, autosave, or automatic finalize is introduced.

```text
REPORT_DRAFT_PERSISTENCE = SESSION_ONLY
REPORT_DRAFT_SERVER_WRITES = 0
REPORT_DRAFT_LOCALSTORAGE_WRITES = 0
REPORT_DRAFT_AUTOMATIC_FINALIZE = 0
PREVIEW_REPORT_WRITES = 0
PREVIEW_RECIPE_WRITES = 0
```
