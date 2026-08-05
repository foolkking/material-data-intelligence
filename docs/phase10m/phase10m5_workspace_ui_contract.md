# Phase 10M-5 Workspace Report UI

The existing Workspace `REPORT` panel now owns source inventory, session-only
draft, preview, finalize, immutable history, Report detail, Recipe detail, and
JSON/Markdown export. It reuses the M2 shell, M3 selection authority, and M4
Gallery identities; it does not create a separate Report application or
selection store.

Draft title/captions and ordering remain in memory. Preview explicitly shows
zero persistence and renders all twelve sections plus the non-executable Recipe
summary. Finalize is an explicit user action. History lists every immutable
snapshot instead of hiding records behind “latest”.

At 390x844 the source picker is a modal sheet with focus trap, Escape close,
focus restoration, 44px targets, and no horizontal overflow. Keyboard controls
add/remove and move sources. Warnings and status use semantic announcements.
All content renders as React text; no `innerHTML`, iframe, dynamic module,
remote script/style, or Artifact-provided executable markup is accepted.
