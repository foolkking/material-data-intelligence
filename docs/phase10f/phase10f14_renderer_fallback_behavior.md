# Phase 10F-14 Renderer Fallback Behavior

- invalid canonical scene: validation errors shown; renderer module and canvas are not initialized.
- unsupported Canvas/WebGL: unavailable message; JSON and Manifest remain usable.
- initialization failure: safe summary without stack trace; artifact remains downloadable.
- context loss: context-lost fallback, owned canvas removed, JSON retained.
- old Phase 10D scene: existing JSON-only preview; no canonical renderer tab.
- empty/missing payload: existing artifact fallback.

Renderer failure does not change the persisted job status.
