# Phase 10M-2 Workspace State UI

Workspace and panel states are rendered from the M1 contracts without
inventing a new execution enum. Running, initializing, partial, failed,
stale, source-missing, unsupported, and legacy read-only Workspaces receive a
prominent status surface. Partial panels state that only successful branches
are represented; blocked or failed output is never shown as complete.

Panel states preserve `PRODUCED`, `PARTIAL`, `FAILED`,
`BLOCKED_BY_DEPENDENCY`, `CONTRACT_UNSUPPORTED`, `SOURCE_DELETED`, `STALE`,
and the remaining sealed values. Unsupported text is React-escaped inert
content. Error responses are bounded and do not expose stack, SQL, path,
storage, or provider data.

Findings, Evidence, Provenance, and Report are metadata navigation surfaces.
They do not duplicate interpretation, evidence, lineage, Report, or Recipe
authority.
