# Phase 10M-3 URL and Navigation

The Workspace route preserves two independent query parameters:

- `panel`: exact active panel ID;
- `selection`: canonical base64url-encoded `WorkspaceSelectionContext 1.0`.

Selection tokens are limited to 2,048 UTF-8 bytes. Decoding rejects invalid
base64url, duplicate JSON keys at any depth, unknown fields, non-canonical key
ordering, invalid UTF-8, excessive depth, stale scope, foreign identities, and
over-cap content. Invalid state receives no substitute selection.

Panel changes preserve valid selection. Explicit clear removes only the
selection query and not the active panel. Browser refresh, back, and forward
re-run exact validation. Inspector navigation opens only panels with an `EXACT`
delivery. Copy link always embeds the current canonical token.
