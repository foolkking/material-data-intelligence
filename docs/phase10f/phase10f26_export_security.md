# Phase 10F-26 Export Security Review

## Threats and controls

| Threat | Control |
| --- | --- |
| giant canvas/GPU allocation | strict dimensions, DPR, pixel, and byte caps before resize |
| concurrent or stale export | one active request and generation-token rejection |
| filename/path injection | normalized fixed-length stem and suffix allowlist |
| HTML/Markdown injection | control characters and angle brackets removed from text fields |
| external exfiltration | local Blob/Object URL only; browser audit observed zero external requests |
| object URL leak | microtask revocation after each download |
| renderer state corruption | complete save/restore in `finally` |
| artifact execution | no JS, HTML, shader, module, URL, callback, or renderer bundle in outputs |

Normal UI errors expose only fixed `VIEWER_EXPORT_*` codes and retain existing
scene artifacts. No raw stack, local path, payload, token, or renderer diagnostic
is shown. No dependency or lockfile changed.
