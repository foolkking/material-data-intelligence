# Phase 10M-7 Browser, Mobile, and Accessibility Closure

The M7 runner executes Chromium, Firefox, WebKit, and Chromium at 390x844. It
tests explicit Save, no-op suppression, typed conflict with local edit
preservation, explicit server reload, Report source selection, no-write
preview, finalize/idempotency/history/export, refresh/reopen, and Back/Forward.
M3-M6 runners execute in the same exact-SHA CI for canonical selection,
Gallery/Viewers, Inspector, and recovery regressions.

```text
unexpected console errors = 0
unexpected page errors = 0
unexpected failed responses = 0
unapproved external requests = 0
mobile horizontal overflow = 0
minimum touch target = 44x44 CSS px
```

Keyboard, focus trap/return, named statuses, non-color states, table/chart/WebGL
alternatives, reduced motion, and 200% reflow remain covered by the sealed M3-
M6 suites. Browser screenshots are current local live replays over inert,
route-fulfilled API fixtures; service-backed API proof is a separate CI gate.
