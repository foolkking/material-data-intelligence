# Phase 10M-6 Deep Link and History

The canonical route remains `/workspaces/{workspaceId}`. Only `panel` and the bounded versioned exact selection codec are shareable query state. Copied links exclude transient state, payloads, temporary URLs, secrets, and private paths.

Refresh and Back/Forward restore or clear exact URL state without duplicate history entries, automatic Pin, Workspace Save, revision growth, or stale async response commits. A missing URL selection may use the exact pinned fallback; malformed, unsupported-version, stale-hash, cross-scope, duplicate, and over-cap explicit values are typed failures without identity substitution.

The selection byte cap remains 2,048. Over-cap state is rejected as `URL_SIZE_EXCEEDED`; it is never truncated.
