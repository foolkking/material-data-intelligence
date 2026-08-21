# Production Semantic Accessibility Audit

Date: 2026-08-20

## Verified in source and production DOM

- Public/authenticated shell landmarks, headings and navigation.
- Login and model-settings dialogs with `role="dialog"`, modal labelling,
  Escape handling, focus trapping and restoration.
- Research conversation as a labelled log with user/assistant articles.
- Research workbench and splitter semantics, including bounded keyboard values.
- Data table name, caption, row selection semantics and Inspector region.
- Loading, error, limitation and run-process states exposed as status/alert
  content where appropriate.
- Scientific canvases have user-facing labels and preserve canonical units.

## Not verified by available tooling

- A real NVDA, VoiceOver or equivalent hardware screen-reader session.
- Browser capture of a non-terminal incremental Artifact while a later Worker
  step is still active. The server-side event-order contract is covered by the
  two-step registered-adapter regression; the local Worker completes too
  quickly for an honest intermediate screenshot.
